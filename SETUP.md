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

### Gmail Account with Job Alerts

Set up job alerts from LinkedIn and Indeed to your Gmail inbox. Claude will monitor these alerts via `/fetch-inbox` and queue jobs for evaluation.

### LaTeX (Optional, for `/apply` workflow)

If you plan to use the `/apply` command to generate LaTeX CVs and cover letters, install a LaTeX distribution:

- **Windows:** [MiKTeX](https://miktex.org/download)
- **macOS:** [MacTeX](https://tug.org/mactex/)
- **Linux:** `sudo apt install texlive-full` or `sudo dnf install texlive-scheme-full`

The CV compiles with `lualatex` (pdflatex often fails on modern MiKTeX installs with `fontawesome5` font-expansion errors). The cover letter compiles with `xelatex` because `cover.cls` requires `fontspec` for its custom Lato/Raleway fonts.

**If you skip this step**, you can still use `/apply` for evaluation and drafting, but you'll need to compile the generated `.tex` files manually or not at all. Alternatively, use a markdown-based resume approach (see Customization in README.md).

## 2. Fork and clone

```bash
gh repo fork MadsLorentzen/ai-job-search --clone
cd ai-job-search
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
| `cv/main_example.tex` | Your LaTeX CV with actual details |

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
3. Stores them in `data/inbox_queue.json`
4. Presents each job with a quick fit assessment against your profile

**Gmail authentication:** The first time you run `/fetch-inbox`, you'll be prompted to authenticate with Gmail. Claude Code will open a browser window to authorize access to your inbox. This is a one-time setup.

## 5. Optional: Set up salary benchmarking

If you have salary data (from a union, salary survey, Glassdoor, or personal research):

1. **Option A:** Create `salary_data.json` manually in the repo root (see `tools/README_SALARY_TOOL.md` for the format)
2. **Option B:** Convert from Excel:
   ```bash
   pip install openpyxl
   python tools/convert_salary_excel.py path/to/salary-data.xlsx --source "My Salary Data 2025"
   ```

This creates `salary_data.json` which the `/apply` workflow uses for salary benchmarking. If you skip this step, salary lookup is simply omitted.

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
3. Draft a tailored CV and cover letter (in LaTeX)
4. Have a reviewer agent critique the drafts
5. Revise and present the final output

## 7. Compile your documents (if using LaTeX)

After `/apply` creates the LaTeX files:

```bash
# Compile CV
cd cv && lualatex main_<company>.tex && cd ..

# Compile cover letter
cd cover_letters && xelatex cover_<company>_<role>.tex && cd ..
```

The `/apply` workflow includes automatic PDF compilation and inspection in Step 5. If you have LaTeX installed, the workflow will verify the PDFs before presenting them to you.

## Troubleshooting

### "salary_data.json not found"
This is expected if you haven't set up salary benchmarking. The `/apply` workflow skips this step automatically.

### "/fetch-inbox returns no results"
- Check that Gmail alerts are enabled in your LinkedIn and Indeed settings
- Verify that emails from these services are reaching your inbox (not spam folder)
- Run `/fetch-inbox` again a few moments later

### LaTeX compilation errors (if you have LaTeX installed)
- CV: uses `lualatex` (pdflatex often fails on modern MiKTeX with `fontawesome5` font-expansion errors; lualatex handles the same sources cleanly)
- Cover letter: uses `xelatex` (for custom fonts in `OpenFonts/fonts/`)
- Make sure your LaTeX distribution includes the `moderncv` package

### Fonts not found in cover letter
The cover letter template expects fonts in `cover_letters/OpenFonts/fonts/`. Make sure this directory exists and contains the Lato and Raleway font files.

### LaTeX not installed, but `/apply` is generating files
If you don't have LaTeX installed, the workflow will still draft the `.tex` files. You can either:
1. Install LaTeX later and compile them
2. Use an online LaTeX compiler like Overleaf (upload the `.tex` file and fonts)
3. Convert the `.tex` to `.html` or `.markdown` for a simpler resume format
