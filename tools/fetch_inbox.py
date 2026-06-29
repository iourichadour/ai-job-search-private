import os
import json
import base64
import re
import time
import random
import sys
import logging
from bs4 import BeautifulSoup
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from datetime import datetime

try:
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
except ImportError:
    print("[!] Playwright not installed. Run:")
    print("    pip install playwright")
    print("    playwright install chromium")
    sys.exit(1)

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

# ============================================
# CONFIGURATION - Browser Fetch Settings
# ============================================
MIN_DELAY_BETWEEN_REQUESTS = 3
MAX_DELAY_BETWEEN_REQUESTS = 8
BATCH_SIZE = 5
MIN_BATCH_PAUSE = 30
MAX_BATCH_PAUSE = 60
PAGE_LOAD_TIMEOUT = 30000
EXTRA_PAGE_WAIT = 2000
# ============================================

def setup_logging(timestamp: str) -> logging.Logger:
    os.makedirs('logs', exist_ok=True)
    log_path = f'logs/fetch_inbox_{timestamp}.log'
    logger = logging.getLogger('fetch_inbox')
    logger.setLevel(logging.DEBUG)
    fmt = logging.Formatter('%(asctime)s %(message)s', datefmt='%H:%M:%S')
    fh = logging.FileHandler(log_path, encoding='utf-8')
    fh.setFormatter(fmt)
    logger.addHandler(fh)
    sh = logging.StreamHandler(sys.stdout)
    sh.setFormatter(fmt)
    logger.addHandler(sh)
    logger.info(f'Log file: {log_path}')
    return logger

def extract_linkedin_job_id(url):
    match = re.search(r'/jobs/view/(\d+)', url)
    return match.group(1) if match else None

def normalize_linkedin_url(url):
    """Normalize LinkedIn URL to base form (strip tracking params)."""
    job_id = extract_linkedin_job_id(url)
    if job_id:
        return f"https://www.linkedin.com/comm/jobs/view/{job_id}/"
    return url

def fetch_linkedin_with_browser(url, logger, timeout=None):
    job_id = extract_linkedin_job_id(url)
    if not job_id:
        return None

    simplified_url = f"https://www.linkedin.com/jobs/view/{job_id}/"
    timeout = timeout or PAGE_LOAD_TIMEOUT

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )
            page = context.new_page()

            logger.info(f"  [→] Loading: {simplified_url}")
            try:
                page.goto(simplified_url, wait_until='load', timeout=timeout)
            except PlaywrightTimeoutError:
                logger.info(f"  [!] Page load timeout (may need manual review)")
                browser.close()
                return None

            page.wait_for_timeout(EXTRA_PAGE_WAIT)

            # Extract title
            title_text = 'N/A'
            try:
                title = page.query_selector('h1')
                if title:
                    title_text = title.text_content().strip()
                    if title_text:
                        logger.info(f"  [✓] Title: {title_text[:60]}")
            except:
                pass

            # Extract company
            company_text = 'N/A'
            try:
                company = page.query_selector('a[data-test="company-link"], [class*="company"]')
                if company:
                    company_text = company.text_content().strip()
                    if company_text:
                        logger.info(f"  [✓] Company: {company_text[:40]}")
            except:
                pass

            # Extract description - try multiple strategies
            description = 'N/A'

            # Strategy 1: Look for show-more-less-html (main description container)
            logger.info(f"  [→] Extracting description...")
            try:
                desc_element = page.query_selector('div.show-more-less-html')
                if desc_element:
                    description = desc_element.text_content().strip()
                    if description and len(description) > 100:
                        logger.info(f"  [✓] Found description ({len(description)} chars)")
                        browser.close()
                        return {
                            'title': title_text,
                            'company': company_text,
                            'description': description[:3000]
                        }
            except Exception as e:
                logger.info(f"  [~] Strategy 1 failed: {e}")

            # Strategy 2: Get all text content from main article
            try:
                desc_element = page.query_selector('article, main, [role="main"]')
                if desc_element:
                    description = desc_element.text_content().strip()
                    lines = description.split('\n')
                    cleaned = '\n'.join(line.strip() for line in lines if line.strip())
                    if len(cleaned) > 200:
                        logger.info(f"  [✓] Found description from article ({len(cleaned)} chars)")
                        browser.close()
                        return {
                            'title': title_text,
                            'company': company_text,
                            'description': cleaned[:3000]
                        }
            except Exception as e:
                logger.info(f"  [~] Strategy 2 failed: {e}")

            # Strategy 3: Get full page text if other strategies failed
            try:
                full_text = page.content()
                if len(full_text) > 1000:
                    soup = BeautifulSoup(full_text, 'html.parser')
                    for tag in soup.find_all(['script', 'style', 'nav', 'header']):
                        tag.decompose()

                    text = soup.get_text(separator='\n', strip=True)
                    lines = [line.strip() for line in text.split('\n') if line.strip() and len(line.strip()) > 20]
                    if lines:
                        description = '\n'.join(lines)
                        if len(description) > 200:
                            logger.info(f"  [✓] Found description from page text ({len(description)} chars)")
                            browser.close()
                            return {
                                'title': title_text,
                                'company': company_text,
                                'description': description[:3000]
                            }
            except Exception as e:
                logger.info(f"  [~] Strategy 3 failed: {e}")

            browser.close()

            if description != 'N/A':
                return {
                    'title': title_text,
                    'company': company_text,
                    'description': description[:3000]
                }
            else:
                logger.info(f"  [!] Could not extract description")
                return None

    except Exception as e:
        logger.info(f"  [ERROR] Browser error: {e}")
        import traceback
        traceback.print_exc()
        return None

def fetch_indeed_with_browser(url, logger, timeout=None):
    timeout = timeout or PAGE_LOAD_TIMEOUT
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            logger.info(f"  [→] Loading: {url}")
            page.goto(url, wait_until='load', timeout=timeout)
            page.wait_for_timeout(EXTRA_PAGE_WAIT)

            # Extract title
            title_text = 'N/A'
            try:
                title = page.query_selector('h1')
                if title:
                    title_text = title.text_content().strip()
            except:
                pass

            # Extract company
            company_text = 'N/A'
            try:
                company = page.query_selector('[data-company-name], .company')
                if company:
                    company_text = company.text_content().strip()
            except:
                pass

            # Extract description
            description = 'N/A'
            try:
                desc_element = page.query_selector('#jobDescriptionText, [id*="description"]')
                if desc_element:
                    description = desc_element.text_content().strip()
                    if len(description) > 100:
                        logger.info(f"  [✓] Found description ({len(description)} chars)")
                        browser.close()
                        return {
                            'title': title_text,
                            'company': company_text,
                            'description': description[:3000]
                        }
            except:
                pass

            # Fallback: extract main content
            try:
                content = page.query_selector('article, main, [role="main"]')
                if content:
                    description = content.text_content().strip()
                    if len(description) > 200:
                        logger.info(f"  [✓] Found description from content ({len(description)} chars)")
            except:
                pass

            browser.close()
            return {
                'title': title_text,
                'company': company_text,
                'description': description[:3000] if description != 'N/A' else 'N/A'
            }

    except Exception as e:
        logger.info(f"  [ERROR] {e}")
        return None

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
                    normalized_url = normalize_linkedin_url(href)
                    raw_jobs.append({'source': 'linkedin', 'url': normalized_url})
                    logger.info(f'  [URL] linkedin: {normalized_url[:80]}')
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

if __name__ == "__main__":
    main()
