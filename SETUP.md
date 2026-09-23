# Setup Guide

Step-by-step instructions for getting the AI Job Search framework running.

## 1. Prerequisites

### Claude Code

Install Claude Code (Anthropic's CLI for Claude):

```bash
npm install -g @anthropic-ai/claude-code
```

You'll need an Anthropic API key or a Claude Pro/Team subscription. See the [Claude Code docs](https://docs.anthropic.com/en/docs/claude-code) for details.

### Python

Python 3.10+ is required for the salary lookup tool and job processing. Check with:

```bash
python --version
```

### Create a dedicated Gmail account for job search

Create a new, separate Gmail address used only for job-search alerts — not your personal/primary Gmail. This matters for a few reasons:

- Isolates the OAuth grant scope (`gmail.readonly`) to job-alert mail only
- Keeps the OAuth consent screen's test-user list, and any future scope audit, scoped to one purpose
- Lets you revoke API access later without touching your personal account
- Avoids hardcoding a personal address anywhere (see the config step below)

Once created, subscribe that new address to job alerts from LinkedIn and Indeed.

### Configure Gmail API access

`tools/fetch_inbox.py` reads mail via the Gmail API with `SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']`. To set this up:

1. In [Google Cloud Console](https://console.cloud.google.com/), create a new project (e.g. "ai-job-search")
2. Enable the **Gmail API** for that project (APIs & Services -> Library)
3. Configure the **OAuth consent screen** (External, Testing mode is sufficient for personal use) and add the dedicated job-search Gmail address as a test user
4. Create an **OAuth 2.0 Client ID** (Application type: Desktop app)
5. Download the credential JSON and save it as `private/credentials.json` (the whole `private/` folder is gitignored — never commit it)
6. Required scope: `https://www.googleapis.com/auth/gmail.readonly` (read-only; the tooling never sends or modifies mail)
7. Copy `config.example.json` (repo root) to `private/config.json` and set `job_search_email` to your dedicated address — this is what `tools/fetch_inbox.py`'s query filter reads via `tools/config.py`; never hardcode it into a `.py` file
8. Run `/fetch-inbox` (or `python tools/fetch_inbox.py`) once — this opens a browser window for the OAuth consent flow; sign in with the **dedicated job-search account**, not your personal one. On success, `private/token.json` is created (gitignored) and reused on subsequent runs without re-prompting.

## 2. Fork and clone

```bash
gh repo fork iourichadour/ai-job-search-private --clone
cd ai-job-search-private
```

Or manually: fork on GitHub, then clone your fork.

## 3. Run the setup interview

Start Claude Code in the repository:

```bash
claude
```

Then run the onboarding:

```
/setup
```

Claude will offer paths to populate your profile:

- **Path A (recommended):** Share your existing CV (mention the file with `@` or paste the text). Claude extracts your information and asks follow-up questions for anything missing.
- **Path B:** Answer structured interview questions section by section.

Both paths produce the same result: fully populated profile files.

### What gets populated

| File | Content |
|------|---------|
| `CLAUDE.md` | Your full candidate profile |
| `01-candidate-profile.md` | Structured education, experience, skills |
| `02-behavioral-profile.md` | Behavioral assessment |
| `04-job-evaluation.md` | Personalized skill match areas and career goals |
| `05-cv-templates.md` | Profile statement templates for your background |
| `07-interview-prep.md` | STAR examples from your experience |

### Re-running setup

You can update specific sections later:

```
/setup --section skills
/setup --section experience
```

## 4. Monitor job alerts

Once your profile is set up, monitor Gmail for job alerts:

```
/fetch-inbox
```

This command:
1. Polls your Gmail inbox for unread job alerts from LinkedIn and Indeed
2. Fetches full job descriptions from the URLs in those alerts
3. Stores them in `private/inbox_queue.json`
4. Presents each job with a quick fit assessment against your profile

**Gmail authentication:** The first time you run `/fetch-inbox`, you'll be prompted to authenticate with Gmail. Claude Code will open a browser window to authorize access to your inbox. This is a one-time setup.

## 5. Optional: Set up salary benchmarking

If you have salary data (from a union, salary survey, Glassdoor, or personal research):

1. **Option A:** Create `private/salary_data.json` manually (see `tools/README_SALARY_TOOL.md` for the format)
2. **Option B:** Convert from Excel:
   ```bash
   pip install openpyxl
   python tools/convert_salary_excel.py path/to/salary-data.xlsx --source "My Salary Data 2025"
   ```

This creates `private/salary_data.json` which the `/apply` workflow uses for salary benchmarking. If you skip this step, salary lookup is simply omitted.

## 6. Test the workflow

Find a job posting (from your `/fetch-inbox` queue or elsewhere), then:

```
/apply https://www.linkedin.com/jobs/view/1234567890/
```

Or paste the job description directly:

```
/apply [paste job posting text here]
```

Claude will:
1. Evaluate the fit against your profile
2. Ask if you want to proceed
3. Draft a tailored CV and cover letter (in markdown)
4. Have a reviewer agent critique the drafts
5. Revise and present the final output

Confirm the output landed under `private/applications/YYYY-MM_<Company>/` — you should see `cv.md` and `cover_letter.md` there, ready to read directly or convert to PDF before submitting.

## Troubleshooting

### "salary_data.json not found"
This is expected if you haven't set up salary benchmarking. The `/apply` workflow skips this step automatically.

### "/fetch-inbox returns no results"
- Check that Gmail alerts are enabled in your LinkedIn and Indeed settings
- Verify that emails from these services are reaching your inbox (not spam folder)
- Run `/fetch-inbox` again a few moments later

### "Missing private/config.json"
`tools/fetch_inbox.py` requires `private/config.json` with your `job_search_email`. Copy `config.example.json` (repo root) to `private/config.json` and fill in your dedicated job-search address (see Prerequisites above).
