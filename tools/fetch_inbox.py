import os
import json
import base64
import re
import time
import random
import sys
from bs4 import BeautifulSoup
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from urllib.parse import urlparse, parse_qs
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
MIN_DELAY_BETWEEN_REQUESTS = 2      # Minimum seconds between requests
MAX_DELAY_BETWEEN_REQUESTS = 5      # Maximum seconds between requests
BATCH_SIZE = 5                       # Number of jobs before taking a break
MIN_BATCH_PAUSE = 20                 # Minimum break time (seconds)
MAX_BATCH_PAUSE = 40                 # Maximum break time (seconds)
PAGE_LOAD_TIMEOUT = 30000            # Page load timeout (milliseconds)
EXTRA_PAGE_WAIT = 2000               # Extra wait after page loads (ms)
# ============================================

def extract_linkedin_job_id(url):
    """Extract job ID from LinkedIn tracking URL."""
    match = re.search(r'/jobs/view/(\d+)', url)
    return match.group(1) if match else None

def extract_job_from_linkedin(url):
    """Fetch LinkedIn job using headless browser (primary method)."""
    job_id = extract_linkedin_job_id(url)
    if not job_id:
        return {'title': 'N/A', 'company': 'N/A', 'description': 'Could not extract job ID'}

    simplified_url = f"https://www.linkedin.com/jobs/view/{job_id}/"

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )
            page = context.new_page()

            try:
                page.goto(simplified_url, wait_until='load', timeout=PAGE_LOAD_TIMEOUT)
            except PlaywrightTimeoutError:
                browser.close()
                return {'title': 'N/A', 'company': 'N/A', 'description': 'Page load timeout'}

            # Wait for content to render
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
                company = page.query_selector('a[data-test="company-link"], [class*="company"]')
                if company:
                    company_text = company.text_content().strip()
            except:
                pass

            # Extract description - multiple strategies
            description = 'N/A'

            # Strategy 1: show-more-less-html
            try:
                desc_element = page.query_selector('div.show-more-less-html')
                if desc_element:
                    description = desc_element.text_content().strip()
                    if description and len(description) > 100:
                        browser.close()
                        return {
                            'title': title_text,
                            'company': company_text,
                            'description': description[:3000]
                        }
            except:
                pass

            # Strategy 2: article/main content
            try:
                desc_element = page.query_selector('article, main, [role="main"]')
                if desc_element:
                    description = desc_element.text_content().strip()
                    lines = [line.strip() for line in description.split('\n') if line.strip()]
                    cleaned = '\n'.join(lines)
                    if len(cleaned) > 200:
                        browser.close()
                        return {
                            'title': title_text,
                            'company': company_text,
                            'description': cleaned[:3000]
                        }
            except:
                pass

            # Strategy 3: full page text
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
                            browser.close()
                            return {
                                'title': title_text,
                                'company': company_text,
                                'description': description[:3000]
                            }
            except:
                pass

            browser.close()

            return {
                'title': title_text,
                'company': company_text,
                'description': description if description != 'N/A' else 'Could not extract'
            }

    except Exception as e:
        return {'title': 'N/A', 'company': 'N/A', 'description': f'Error: {str(e)[:50]}'}

def extract_job_from_indeed(url):
    """Fetch Indeed job using headless browser."""
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            page.goto(url, wait_until='load', timeout=PAGE_LOAD_TIMEOUT)
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
                        browser.close()
                        return {
                            'title': title_text,
                            'company': company_text,
                            'description': description[:3000]
                        }
            except:
                pass

            # Fallback: main content
            try:
                content = page.query_selector('article, main, [role="main"]')
                if content:
                    description = content.text_content().strip()
                    if len(description) > 200:
                        pass  # Use it below
            except:
                pass

            browser.close()
            return {
                'title': title_text,
                'company': company_text,
                'description': description[:3000] if description != 'N/A' else 'Could not extract'
            }

    except Exception as e:
        return {'title': 'N/A', 'company': 'N/A', 'description': f'Error: {str(e)[:50]}'}

def main():
    print("Authenticating with Gmail API...")
    creds = None
    if os.path.exists('data/token.json'):
        creds = Credentials.from_authorized_user_file('data/token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('data/token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('gmail', 'v1', credentials=creds)

    print("Polling for unread LinkedIn/Indeed alerts...")
    results = service.users().messages().list(
        userId='me',
        q="is:unread from:(jobalerts-noreply@linkedin.com OR alert@indeed.com OR iouri.chadour@gmail.com)"
    ).execute()

    messages = results.get('messages', [])
    job_queue = []

    for msg in messages:
        msg_data = service.users().messages().get(userId='me', id=msg['id'], format='full').execute()
        payload = msg_data.get('payload', {})
        parts = payload.get('parts', [])

        html_body = ""
        if parts:
            for part in parts:
                if part.get('mimeType') == 'text/html':
                    html_body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
        else:
            html_body = base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8')

        if html_body:
            soup = BeautifulSoup(html_body, 'html.parser')

            links = soup.find_all('a', href=True)
            for link_idx, link in enumerate(links):
                href = link['href']
                job_data = None
                source = None

                if "linkedin.com/comm/jobs/view" in href:
                    print(f"[+] Fetching LinkedIn job: {href[:60]}...")
                    job_data = extract_job_from_linkedin(href)
                    source = 'linkedin'
                elif "indeed.com" in href:
                    print(f"[+] Fetching Indeed job: {href[:60]}...")
                    job_data = extract_job_from_indeed(href)
                    source = 'indeed'
                else:
                    continue

                if job_data:
                    job_queue.append({
                        "source": source,
                        "url": href,
                        "title": job_data.get('title'),
                        "company": job_data.get('company', 'N/A'),
                        "description": job_data.get('description'),
                        "status": "pending_evaluation",
                        "fetched_at": datetime.now().isoformat()
                    })

                    # Add delay between requests to avoid bot detection
                    if link_idx < len(links) - 1:
                        delay = random.uniform(MIN_DELAY_BETWEEN_REQUESTS, MAX_DELAY_BETWEEN_REQUESTS)
                        print(f"    [⏳] Waiting {delay:.1f}s before next request...")
                        time.sleep(delay)

    # Save the queue for Claude to read, deduplicating by URL
    os.makedirs('data', exist_ok=True)
    existing_queue = []
    if os.path.exists('data/inbox_queue.json'):
        try:
            with open('data/inbox_queue.json', 'r', encoding='utf-8') as f:
                existing_queue = json.load(f)
        except Exception as e:
            print(f"[!] Error reading existing queue: {e}")

    # Build index of existing URLs
    seen_urls = {job['url'] for job in existing_queue if 'url' in job}
    
    # Add new jobs if not already present in the queue
    for job in job_queue:
        if job['url'] not in seen_urls:
            existing_queue.append(job)
            seen_urls.add(job['url'])

    with open('data/inbox_queue.json', 'w', encoding='utf-8') as f:
        json.dump(existing_queue, f, indent=4)

    successful_fetches = sum(1 for job in job_queue if job['title'] != 'N/A' and job['description'] != 'N/A')
    print(f"\n[✓] Fetch complete (using browser automation).")
    print(f"[+] New jobs fetched: {len(job_queue)}")
    print(f"[+] Successful extractions: {successful_fetches}/{len(job_queue)}")
    print(f"[+] Total deduplicated queue size: {len(existing_queue)}")
    if successful_fetches < len(job_queue):
        print(f"[!] {len(job_queue) - successful_fetches} jobs with incomplete data (review in inbox_queue.json)")

if __name__ == "__main__":
    main()
