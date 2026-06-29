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
```bash
python tools/fetch_inbox.py
```

Once the script completes, read the output from `data/inbox_queue.json`. For each new job found in the queue, evaluate its fit against the candidate profile by comparing:
- Technical skills (Microsoft Fabric, Snowflake, Power BI, Python, SQL, Cloud)
- Experience level (Director/VP alignment, team leadership, enterprise data architecture)
- Company and industry fit (financial services, tech, consulting)
- Role scope (strategic + hands-on, not purely operational)

Summarize the match analysis in the chat with: skills fit %, experience match, and recommendation (strong/moderate/pass).
