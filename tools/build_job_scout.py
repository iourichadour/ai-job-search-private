import os

def create_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")
    print(f"[*] Generated: {path}")

def build_project():
    print("Initializing Job Scout Agent Architecture...\n")

    # 1. The Core Claude Instruction File
    create_file("CLAUDE.md", """
# Job Scout Agent: Global Context

You are an autonomous executive career agent. Your primary role is to monitor Gmail for curated job opportunities from LinkedIn and Indeed, evaluate them against your profile, and orchestrate application materials.

## Workflow Rules
* When asked to check for jobs, invoke the `/fetch-inbox` skill to poll Gmail for new LinkedIn/Indeed alerts.
* The skill automatically fetches job posting content from the URLs in email alerts and stores them in `data/inbox_queue.json`.
* Read `data/profile.md` as the ultimate source of truth for the user's background. Do not hallucinate skills not present in this file.
* Evaluate each job against the profile using these criteria: technical skill alignment, experience match, company/industry fit, role level appropriateness.
* When instructed to `/apply`, run the drafting and review workflow to create a tailored markdown resume, placing the final artifact in `applications/YYYY-MM_Company/`.

## Important Directives
* Leverage Gmail's curated job alerts instead of scraping job boards directly — LinkedIn and Indeed already filtered these for relevance.
* Provide clear fit assessments (skills match %, experience gap analysis, culture/stage alignment) before recommending application.
* Strictly evaluate roles based on alignment with Microsoft Fabric, OneLake, Power BI, data mesh architecture, and team leadership capabilities.
* Flag roles that are below your level, legacy-stack focused, or siloed IT positions.
    """)

    # 2. The Fetch Inbox Skill Definition
    create_file(".claude/skills/fetch-inbox/SKILL.md", """
---
name: fetch-inbox
description: Polls Gmail for unread LinkedIn/Indeed job alerts, fetches job posting content from URLs, and evaluates fit against candidate profile.
user-invocable: true
disable-model-invocation: true
---
## What This Skill Does
1. Authenticates with Gmail API and polls for unread emails from LinkedIn and Indeed
2. Extracts job posting URLs from email alerts
3. Fetches the actual job description from LinkedIn and Indeed job pages
4. Stores extracted jobs with title, description, and source in `data/inbox_queue.json`

## How to Use
Execute the python script located at `tools/fetch_inbox.py`:
\`\`\`bash
python tools/fetch_inbox.py
\`\`\`

Once the script completes, read the output from `data/inbox_queue.json`. For each new job found in the queue, evaluate its fit against the candidate profile by comparing:
- Technical skills (Microsoft Fabric, Snowflake, Power BI, Python, SQL, Cloud)
- Experience level (Director/VP alignment, team leadership, enterprise data architecture)
- Company and industry fit (financial services, tech, consulting)
- Role scope (strategic + hands-on, not purely operational)

Summarize the match analysis in the chat with: skills fit %, experience match, and recommendation (strong/moderate/pass).
    """)

    # 3. The Python Gmail Parser (Enhanced with Job Fetching & Profile Matching)
    create_file("tools/fetch_inbox.py", """
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
    \"\"\"Fetch LinkedIn job posting details.\"\"\"
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
    \"\"\"Fetch Indeed job posting details.\"\"\"
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
        q="is:unread from:(jobalerts-noreply@linkedin.com OR alert@indeed.com)"
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

    # Save the queue for Claude to read
    os.makedirs('data', exist_ok=True)
    with open('data/inbox_queue.json', 'w') as f:
        json.dump(job_queue, f, indent=4)

    print(f"\\nExtraction complete. {len(job_queue)} roles fetched and queued for evaluation.")

if __name__ == "__main__":
    main()
    """)

    # 4. Data Scaffolding
    create_file("data/profile.md", """
# User Executive Profile
[Insert your thick profile here: Focus heavily on Data Engineering, Microsoft Fabric DP-600/DP-700, CI/CD, and cross-functional leadership achievements.]
    """)
    
    create_file("data/master_resume.md", """
# Iouri Chadour
West Palm Beach, FL | Data Architecture Leader

## Executive Summary
[Insert base summary]

## Experience
[Insert bullet points]
    """)

    create_file("requirements.txt", """
google-api-python-client>=2.0.0
google-auth-httplib2>=0.1.0
google-auth-oauthlib>=1.0.0
beautifulsoup4>=4.12.0
requests>=2.31.0
lxml>=4.9.0
    """)

    print("\n✅ Architecture successfully built!")
    print("Next Steps:")
    print("1. Place your Google Cloud 'credentials.json' in the root folder.")
    print("2. Update 'data/profile.md' with your executive profile and core competencies.")
    print("3. Run 'pip install -r requirements.txt'.")
    print("4. Run 'python tools/fetch_inbox.py' to test Gmail integration and fetch jobs from alerts.")
    print("5. Start the agent session with 'claude' and use '/fetch-inbox' to monitor LinkedIn/Indeed emails.")

if __name__ == "__main__":
    build_project()