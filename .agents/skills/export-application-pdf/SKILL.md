---
name: export-application-pdf
description: >-
  Use this skill when the user asks to print, convert, or export a cover letter and resume (CV) to PDF for a specific application.
---

# Export Application to PDF

This skill generates PDF versions of the user's Markdown resume (`cv.md`) and cover letter (`cover_letter.md`).

## Steps

1. Determine the application directory. It should be inside `private/applications/<application_name>`.
2. Verify that `cv.md` and `cover_letter.md` exist in the target application directory.
3. Use the provided Python script `tools/md_to_pdf.py` to generate the PDFs.
4. Run the script for `cv.md`:
   `python tools/md_to_pdf.py private/applications/<application_name>/cv.md private/applications/<application_name>/cv.pdf`
5. Run the script for `cover_letter.md`:
   `python tools/md_to_pdf.py private/applications/<application_name>/cover_letter.md private/applications/<application_name>/cover_letter.pdf`
6. Verify that the `.pdf` files were successfully created.
7. Provide the user with the paths to the generated PDF files so they can open them.
