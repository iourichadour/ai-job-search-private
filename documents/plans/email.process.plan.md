---
title: Refactor fetch_inbox.py into two-phase pipeline with per-run logs
status: ready
---

## Context

`tools/fetch_inbox.py` currently fetches job descriptions inline during the Gmail email loop — every URL triggers a Playwright browser launch immediately. This wastes browser time on URLs already in the queue and makes it hard to audit runs.

New flow:

1. Collect all new URLs from Gmail first (no browser)
2. Deduplicate against `data/inbox_queue.json`
3. Browser-fetch descriptions only for truly new jobs
4. Write a timestamped log file per run

---

## Implementation — `tools/fetch_inbox.py` (full rewrite)

### Imports (keep all existing, add `logging`)

```python
import os, json, base64, re, time, random, sys, logging
from bs4 import BeautifulSoup
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from datetime import datetime
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
```

### Constants (copy from `refetch_jobs_browser.py`)

```python
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
MIN_DELAY_BETWEEN_REQUESTS = 3
MAX_DELAY_BETWEEN_REQUESTS = 8
BATCH_SIZE = 5
MIN_BATCH_PAUSE = 30
MAX_BATCH_PAUSE = 60
PAGE_LOAD_TIMEOUT = 30000
EXTRA_PAGE_WAIT = 2000
```

### Logging setup — call at top of `main()`

```python
def setup_logging(timestamp: str) -> logging.Logger:
    os.makedirs('logs', exist_ok=True)
    log_path = f'logs/fetch_inbox_{timestamp}.log'
    logger = logging.getLogger('fetch_inbox')
    logger.setLevel(logging.DEBUG)
    fmt = logging.Formatter('%(asctime)s %(message)s', datefmt='%H:%M:%S')
    # file handler
    fh = logging.FileHandler(log_path, encoding='utf-8')
    fh.setFormatter(fmt)
    logger.addHandler(fh)
    # stdout handler
    sh = logging.StreamHandler(sys.stdout)
    sh.setFormatter(fmt)
    logger.addHandler(sh)
    logger.info(f'Log file: {log_path}')
    return logger
```

### Helper — extract job ID (same as now)

```python
def extract_linkedin_job_id(url):
    match = re.search(r'/jobs/view/(\d+)', url)
    return match.group(1) if match else None
```

### Browser helpers — copy verbatim from `tools/refetch_jobs_browser.py`

Copy these two functions exactly as they appear in `refetch_jobs_browser.py`:

- `fetch_linkedin_with_browser(url, timeout=None)` → returns `{title, company, description}` or `None`
- `fetch_indeed_with_browser(url, timeout=None)` → returns `{title, company, description}` or `None`

Replace all `print(...)` calls in those functions with `logger.info(...)` — pass `logger` as a parameter to each function (add `logger` as second argument).

Function signatures become:

```python
def fetch_linkedin_with_browser(url, logger, timeout=None): ...
def fetch_indeed_with_browser(url, logger, timeout=None): ...
```

### `main()` — new structure

```python
def main():
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    logger = setup_logging(timestamp)

    # ── Phase 1: Gmail auth ──
    logger.info('Authenticating with Gmail API...')
    creds = None
    if os.path.exists('data/token.json'):
        creds = Credentials.from_authorized_user_file('data/token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('data/token.json', 'w') as f:
            f.write(creds.to_json())
    service = build('gmail', 'v1', credentials=creds)

    # ── Phase 1: Extract URLs from email ──
    gmail_query = "is:unread from:(jobalerts-noreply@linkedin.com OR alert@indeed.com OR iouri.chadour@gmail.com)"
    logger.info(f'Gmail query: {gmail_query}')
    results = service.users().messages().list(userId='me', q=gmail_query).execute()
    messages = results.get('messages', [])
    logger.info(f'Found {len(messages)} unread alert emails')

    raw_jobs = []  # [{source, url}]
    for msg in messages:
        msg_data = service.users().messages().get(userId='me', id=msg['id'], format='full').execute()
        payload = msg_data.get('payload', {})
        parts = payload.get('parts', [])
        html_body = ''
        if parts:
            for part in parts:
                if part.get('mimeType') == 'text/html':
                    html_body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
        else:
            body_data = payload.get('body', {}).get('data', '')
            if body_data:
                html_body = base64.urlsafe_b64decode(body_data).decode('utf-8')

        if html_body:
            soup = BeautifulSoup(html_body, 'html.parser')
            for link in soup.find_all('a', href=True):
                href = link['href']
                if 'linkedin.com/comm/jobs/view' in href:
                    raw_jobs.append({'source': 'linkedin', 'url': href})
                    logger.info(f'  [URL] linkedin: {href[:80]}')
                elif 'indeed.com' in href:
                    raw_jobs.append({'source': 'indeed', 'url': href})
                    logger.info(f'  [URL] indeed: {href[:80]}')

    # ── Phase 1: Write scratch file ──
    os.makedirs('data', exist_ok=True)
    scratch_path = f'data/scratch_{timestamp}.json'
    with open(scratch_path, 'w', encoding='utf-8') as f:
        json.dump(raw_jobs, f, indent=2)
    logger.info(f'Scratch file written: {scratch_path} ({len(raw_jobs)} raw URLs)')

    # ── Phase 1: Deduplicate within scratch ──
    seen = set()
    deduped = []
    for job in raw_jobs:
        if job['url'] not in seen:
            seen.add(job['url'])
            deduped.append(job)
    logger.info(f'After intra-batch dedup: {len(deduped)} unique URLs ({len(raw_jobs) - len(deduped)} removed)')

    # ── Phase 1: Filter against existing queue ──
    existing_queue = []
    queue_path = 'data/inbox_queue.json'
    if os.path.exists(queue_path):
        with open(queue_path, 'r', encoding='utf-8') as f:
            existing_queue = json.load(f)
    queue_urls = {job['url'] for job in existing_queue if 'url' in job}
    new_jobs = [job for job in deduped if job['url'] not in queue_urls]
    skipped = len(deduped) - len(new_jobs)
    logger.info(f'Already in queue: {skipped} URLs skipped')
    logger.info(f'New jobs to fetch: {len(new_jobs)}')

    if not new_jobs:
        logger.info('Nothing to fetch. Exiting.')
        return

    # ── Phase 2: Browser-fetch descriptions ──
    logger.info('Starting browser fetch phase...')
    fetched_ok = 0
    for i, job in enumerate(new_jobs, 1):
        logger.info(f'\n[{i}/{len(new_jobs)}] Fetching {job["source"]}: {job["url"][:80]}')
        result = None
        if job['source'] == 'linkedin':
            result = fetch_linkedin_with_browser(job['url'], logger)
        elif job['source'] == 'indeed':
            result = fetch_indeed_with_browser(job['url'], logger)

        entry = {
            'source': job['source'],
            'url': job['url'],
            'title': result['title'] if result else 'N/A',
            'company': result.get('company', 'N/A') if result else 'N/A',
            'description': result['description'] if result else 'Could not extract',
            'status': 'pending_evaluation',
            'fetched_at': datetime.now().isoformat(),
        }
        existing_queue.append(entry)
        # Save after every job so a crash mid-run doesn't lose work
        with open(queue_path, 'w', encoding='utf-8') as f:
            json.dump(existing_queue, f, indent=4, ensure_ascii=False)

        if result and result['title'] != 'N/A':
            fetched_ok += 1
            logger.info(f'  [✓] {result["title"][:60]} @ {result.get("company","N/A")[:40]}')
        else:
            logger.info(f'  [!] Extraction failed')

        # Rate-limit between requests
        if i < len(new_jobs):
            delay = random.uniform(MIN_DELAY_BETWEEN_REQUESTS, MAX_DELAY_BETWEEN_REQUESTS)
            logger.info(f'  [⏳] Waiting {delay:.1f}s...')
            time.sleep(delay)
            if i % BATCH_SIZE == 0:
                pause = random.uniform(MIN_BATCH_PAUSE, MAX_BATCH_PAUSE)
                logger.info(f'  [⏸] Batch pause {pause:.0f}s...')
                time.sleep(pause)

    # ── Summary ──
    logger.info(f'\n{"="*50}')
    logger.info(f'Run complete.')
    logger.info(f'  Emails processed : {len(messages)}')
    logger.info(f'  Raw URLs found   : {len(raw_jobs)}')
    logger.info(f'  Skipped (in queue): {skipped}')
    logger.info(f'  New jobs fetched : {len(new_jobs)}')
    logger.info(f'  Successful       : {fetched_ok}/{len(new_jobs)}')
    logger.info(f'  Queue total      : {len(existing_queue)}')
```

---

## Files changed

| File | Change |
|------|--------|
| `tools/fetch_inbox.py` | Full rewrite of `main()`, add `setup_logging()`, inline browser helpers from `refetch_jobs_browser.py` with `logger` param |
| `tools/refetch_jobs_browser.py` | Add same `setup_logging(timestamp)` helper; update `main()` to call it; pass `logger` into `fetch_linkedin_with_browser` and `fetch_indeed_with_browser`; replace all `print(...)` with `logger.info(...)`; log file goes to `logs/refetch_jobs_<timestamp>.log` |

### `refetch_jobs_browser.py` changes in detail

1. Add `import logging` to imports.
2. Add the same `setup_logging(timestamp)` function (identical to the one in `fetch_inbox.py`, but log filename is `logs/refetch_jobs_{timestamp}.log`).
3. Change `fetch_linkedin_with_browser(url, timeout=None)` → `fetch_linkedin_with_browser(url, logger, timeout=None)`.
4. Change `fetch_indeed_with_browser(url, timeout=None)` → `fetch_indeed_with_browser(url, logger, timeout=None)`.
5. In both functions replace every `print(...)` with `logger.info(...)`.
6. In `main()`:
   - First line: `timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')`
   - Second line: `logger = setup_logging(timestamp)`
   - Replace all `print(...)` with `logger.info(...)`
   - Pass `logger` to both browser-fetch calls.

---

## Verification

1. `python tools/fetch_inbox.py` — check `logs/fetch_inbox_<timestamp>.log` exists with full output
2. `data/scratch_<timestamp>.json` — contains raw URL list from emails
3. `data/inbox_queue.json` — grew only by net-new entries
4. Re-run immediately: log should show "0 new jobs to fetch" (all already in queue)
