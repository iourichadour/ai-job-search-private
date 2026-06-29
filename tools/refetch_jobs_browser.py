#!/usr/bin/env python3
"""
Refetch job details using Playwright headless browser.
Handles LinkedIn's anti-bot detection and JavaScript-rendered content.

Install first:
  pip install playwright
  playwright install chromium
"""

import os
import json
import re
import sys
import time
import random
import logging
from datetime import datetime

try:
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
except ImportError:
    print("[!] Playwright not installed. Run:")
    print("    pip install playwright")
    print("    playwright install chromium")
    sys.exit(1)

# ============================================
# CONFIGURATION - Adjust these values as needed
# ============================================
MIN_DELAY_BETWEEN_REQUESTS = 3      # Minimum seconds between requests
MAX_DELAY_BETWEEN_REQUESTS = 8      # Maximum seconds between requests
BATCH_SIZE = 5                       # Number of jobs before taking a break
MIN_BATCH_PAUSE = 30                 # Minimum break time (seconds)
MAX_BATCH_PAUSE = 60                 # Maximum break time (seconds)
PAGE_LOAD_TIMEOUT = 30000            # Page load timeout (milliseconds)
EXTRA_PAGE_WAIT = 2000               # Extra wait after page loads (ms)
# ============================================

def setup_logging(timestamp: str) -> logging.Logger:
    os.makedirs('logs', exist_ok=True)
    log_path = f'logs/refetch_jobs_{timestamp}.log'
    logger = logging.getLogger('refetch_jobs')
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
    """Extract job ID from LinkedIn tracking URL."""
    match = re.search(r'/jobs/view/(\d+)', url)
    return match.group(1) if match else None

def fetch_linkedin_with_browser(url, logger, timeout=None):
    """
    Fetch LinkedIn job using headless Chromium browser.
    Returns dict with title, company, description.
    """
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

            # Wait for content to render
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
                    # Remove noise
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
                    from bs4 import BeautifulSoup
                    soup = BeautifulSoup(full_text, 'html.parser')
                    # Remove script and style tags
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
    """Fetch Indeed job using headless browser."""
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

    inbox_file = 'data/inbox_queue.json'

    if not os.path.exists(inbox_file):
        logger.info(f"[!] {inbox_file} not found")
        return

    with open(inbox_file, 'r', encoding='utf-8') as f:
        queue = json.load(f)

    # Find entries with missing descriptions
    failed = [job for job in queue if job.get('description') == 'N/A' or 'Could not fetch' in job.get('description', '')]

    if not failed:
        logger.info("[✓] No failed jobs to refetch")
        return

    logger.info(f"\n[+] Refetching {len(failed)} jobs with browser...")
    logger.info(f"[~] Using random delays between requests to avoid bot detection\n")
    refetched = 0

    for i, job in enumerate(failed, 1):
        logger.info(f"\n[{i}/{len(failed)}] Job ID: {extract_linkedin_job_id(job['url']) or 'N/A'}")

        result = None
        if job['source'] == 'linkedin':
            result = fetch_linkedin_with_browser(job['url'], logger)
        elif job['source'] == 'indeed':
            result = fetch_indeed_with_browser(job['url'], logger)

        if result and result['title'] != 'N/A' and result['description'] != 'N/A':
            # Update original entry
            for original_job in queue:
                if original_job['url'] == job['url']:
                    original_job.update({
                        'title': result['title'],
                        'company': result.get('company', 'N/A'),
                        'description': result['description'],
                        'refetched_at': datetime.now().isoformat()
                    })
                    refetched += 1
                    logger.info(f"  [✓] Success: {result['title'][:50]}")
                    break

        # Add delay between requests (randomized, human-like)
        if i < len(failed):  # Don't delay after last job
            delay = random.uniform(MIN_DELAY_BETWEEN_REQUESTS, MAX_DELAY_BETWEEN_REQUESTS)
            logger.info(f"  [⏳] Waiting {delay:.1f}s before next request...")
            time.sleep(delay)

            # Add longer pause every N jobs to mimic human behavior (checking email, etc.)
            if i % BATCH_SIZE == 0:
                batch_pause = random.uniform(MIN_BATCH_PAUSE, MAX_BATCH_PAUSE)
                logger.info(f"\n  [⏸️] Taking a break ({batch_pause:.0f}s) after {i} jobs...\n")
                time.sleep(batch_pause)

    # Save updated queue
    with open(inbox_file, 'w', encoding='utf-8') as f:
        json.dump(queue, f, indent=4, ensure_ascii=False)

    logger.info(f"\n[✓] Refetch complete. Successfully updated {refetched}/{len(failed)} jobs")
    logger.info(f"[+] Updated {inbox_file}")

if __name__ == "__main__":
    main()
