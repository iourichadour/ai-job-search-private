---
description: Export a tailored application's cv.md and cover_letter.md to PDF
---

# /export-pdf

`$ARGUMENTS` is the application folder name or company name (e.g. `2026-09_Acme-Corp` or `Acme Corp`).

1. Resolve the target directory under `private/applications/`. If `$ARGUMENTS` doesn't match a
   folder exactly, use Glob (`private/applications/*`) to find the closest match and confirm with
   the user if more than one is plausible.
2. Verify `cv.md` and `cover_letter.md` exist in that directory.
3. Run:
   ```bash
   python tools/md_to_pdf.py private/applications/<dir>/cv.md private/applications/<dir>/cv.pdf
   python tools/md_to_pdf.py private/applications/<dir>/cover_letter.md private/applications/<dir>/cover_letter.pdf
   ```
4. If the script errors with a missing browser (`Executable doesn't exist`), run
   `python -m playwright install chromium` once, then retry.
5. Report the resulting PDF paths to the user.
