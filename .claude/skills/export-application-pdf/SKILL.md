---
name: export-application-pdf
description: >
  Converts a tailored application's Markdown resume (cv.md) and cover letter (cover_letter.md)
  into PDF files using tools/md_to_pdf.py. Triggers on: export to pdf, convert to pdf, pdf resume,
  pdf cover letter, print application, download as pdf.
allowed-tools: Bash, Read, Glob
---

# Export Application to PDF

Converts a specific application's `cv.md` and `cover_letter.md` (written by `/apply`) into PDF
files with `tools/md_to_pdf.py` (Markdown -> HTML -> Chromium print, via Playwright).

## Steps

1. Determine the application directory: `private/applications/<YYYY-MM_Company>/`. If the user
   didn't name one, use Glob on `private/applications/*/cv.md` and ask which application if more
   than one plausible match exists.
2. Confirm `cv.md` and `cover_letter.md` exist in that directory.
3. Run for each file:
   ```bash
   python tools/md_to_pdf.py private/applications/<YYYY-MM_Company>/cv.md private/applications/<YYYY-MM_Company>/cv.pdf
   python tools/md_to_pdf.py private/applications/<YYYY-MM_Company>/cover_letter.md private/applications/<YYYY-MM_Company>/cover_letter.pdf
   ```
4. If the script errors with a missing browser (`Executable doesn't exist`), run
   `python -m playwright install chromium` once, then retry.
5. Confirm both `.pdf` files exist and report their paths to the user.

## Notes

- The output is a single-column, real-text (non-image) PDF — this is what makes it ATS-parseable.
  Do not add multi-column CSS, tables, icons, or text boxes to the template in `md_to_pdf.py`;
  those are what break resume parsers, not the PDF format itself.
