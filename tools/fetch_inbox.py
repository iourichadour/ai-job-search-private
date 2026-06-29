import os
import json
import base64
import requests
from bs4 import BeautifulSoup
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from urllib.parse import urlparse, parse_qs

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def extract_job_from_linkedin(url):
    """Fetch LinkedIn job posting details."""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract job title and company
        title = soup.find('h1') or soup.find('h2')
        title_text = title.text.strip() if title else 'N/A'

        # Extract job description
        description = soup.find('div', {'class': 'show-more-less-html'})
        if description:
            desc_text = description.get_text(separator=' ', strip=True)[:500]
        else:
            desc_text = soup.find('div', {'id': 'job-details'})
            desc_text = desc_text.get_text(separator=' ', strip=True)[:500] if desc_text else 'N/A'

        return {'title': title_text, 'description': desc_text}
    except Exception as e:
        print(f"[!] Error fetching LinkedIn job: {e}")
        return {'title': 'N/A', 'description': 'Could not fetch'}

def extract_job_from_indeed(url):
    """Fetch Indeed job posting details."""
    try:
        # Indeed tracking URLs need to be converted to direct job URLs
        if 'indeed.com/rc/clk' in url:
            url = url.replace('indeed.com/rc/clk', 'indeed.com/jobs')

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract job title
        title = soup.find('h1', {'class': 'jobsearch-JobInfoHeader-title'})
        title_text = title.text.strip() if title else 'N/A'

        # Extract job description
        description = soup.find('div', {'id': 'jobDescriptionText'})
        if description:
            desc_text = description.get_text(separator=' ', strip=True)[:500]
        else:
            desc_text = 'N/A'

        return {'title': title_text, 'description': desc_text}
    except Exception as e:
        print(f"[!] Error fetching Indeed job: {e}")
        return {'title': 'N/A', 'description': 'Could not fetch'}

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
            for link in soup.find_all('a', href=True):
                href = link['href']
                job_data = None

                if "linkedin.com/comm/jobs/view" in href:
                    print(f"[+] Fetching LinkedIn job: {href}")
                    job_data = extract_job_from_linkedin(href)
                    source = 'linkedin'
                elif "indeed.com" in href:
                    print(f"[+] Fetching Indeed job: {href}")
                    job_data = extract_job_from_indeed(href)
                    source = 'indeed'
                else:
                    continue

                if job_data:
                    job_queue.append({
                        "source": source,
                        "url": href,
                        "title": job_data.get('title'),
                        "description": job_data.get('description'),
                        "status": "pending_evaluation"
                    })

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

    print(f"\nExtraction complete. Saved {len(existing_queue)} total deduplicated roles queued for evaluation.")

if __name__ == "__main__":
    main()
