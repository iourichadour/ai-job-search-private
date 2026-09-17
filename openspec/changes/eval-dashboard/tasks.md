## 1. Project Setup and Structure

- [ ] 1.1 Create `dashboard.html` file in project root with basic HTML structure (head, body, style/script tags) and verify file can be opened in a browser without errors
- [ ] 1.2 Create `dashboard.css` (inline within HTML) with base styles for layout, typography, and color scheme; verify page displays readable content

## 2. HTML Layout and Multi-Page Navigation

- [ ] 2.1 Build HTML layout with: header (title + description), tab navigation (Evaluations | Applied Jobs), filters panel, search box, summary metrics section; verify all sections are visible on page load
- [ ] 2.2 Implement tab switching: clicking "Evaluations" tab shows evaluation page, "Applied Jobs" shows application tracker; verify tabs are clickable and content switches without page reload
- [ ] 2.3 Add detail panel (side drawer or modal) HTML structure for evaluation details with close button and content area; verify panel is initially hidden
- [ ] 2.4 Add export buttons (CSV, JSON) and file upload inputs for fallback data loading (JSON for evaluations, CSV for applications); verify buttons and inputs are clickable

## 3. Data Loading - Evaluations

- [ ] 3.1 Implement fetch-based data loading from `data/job_evaluations.json` on page load; verify data is logged to console and parsed correctly
- [ ] 3.2 Implement file upload fallback: allow user to select JSON file if fetch fails; verify selected file is parsed and data loads
- [ ] 3.3 Add error handling and user-friendly error messages for missing, invalid, or malformed JSON; verify error message displays when data fails to load

## 4. Data Loading - Applications (CSV)

- [ ] 4.1 Implement CSV parsing: load `job_search_tracker.csv` on Applied Jobs page; support both fetch() and file upload; verify CSV is parsed into array of objects
- [ ] 4.2 Implement CSV parser for standard format with headers (URL required; Company, Title, Applied Date; optional Status, Notes); verify all fields are captured and a per-row warning is raised when URL is missing
- [ ] 4.3 Add error handling for malformed CSV, missing critical columns, and empty files; display user-friendly error message with recovery options

## 5. Job Matching - Composite Key Join

- [ ] 5.1 Implement per-vendor key extractors: LinkedIn (`/jobs/view/(\d+)` path segment → `LKD<id>`) and Indeed (`jk=<token>` query param → `IND<token>`); verify each extractor returns the expected key against sample URLs from both vendors (Indeed samples are synthetic—see 19.6—since no real Indeed records exist in `job_evaluations.json` yet)
- [ ] 5.2 Implement composite-key matching: for each applied job (from CSV), extract its key and find the evaluation record with the matching key; verify matching works correctly for both vendors
- [ ] 5.3 Handle unmatched applied jobs (no evaluation record with a matching key, including missing/malformed URL or an unsupported vendor): mark as "unmatched" and allow display with partial data; verify unmatched jobs show appropriate messaging

## 6. Evaluations Page - Table Rendering

- [ ] 6.1 Render job list as a table with columns: Job Title, Company, Skill Match %, Experience Match %, Overall Fit %, Fit Category; verify all jobs appear as rows
- [ ] 6.2 Apply color coding to fit category badges (green=high, yellow=medium, red=low); verify colors display correctly for each category
- [ ] 6.3 Apply inline styling to fit score cells (e.g., show as badges or background colors based on threshold); verify all scores are visible and color-coded

## 7. Evaluations Page - Sorting

- [ ] 7.1 Make table column headers clickable; implement ascending/descending sort on click; verify jobs re-order when header is clicked
- [ ] 7.2 Add sort direction indicator (↑/↓ or similar) to active sort column; verify indicator appears and toggles with sort direction
- [ ] 7.3 Test sorting by each column (title, company, all fit scores) and verify correct ordering; verify secondary sorts or multi-column sorting if needed (or document as non-goal if deferred)

## 8. Evaluations Page - Filtering by Fit Category

- [ ] 8.1 Implement filter logic: when checkboxes for high/medium/low fit are toggled, update table to show only matching jobs; verify job list updates immediately
- [ ] 8.2 Update job count summary when filters change; verify count reflects filtered results
- [ ] 8.3 Test all combinations of filter states (all checked, some checked, none checked) and verify table updates correctly

## 9. Evaluations Page - Search Functionality

- [ ] 9.1 Implement search input that filters jobs by company name (case-insensitive, partial match); verify typing in search box filters table in real-time
- [ ] 9.2 Extend search to also match job title keywords; verify searching for "director" or other keywords returns matching jobs
- [ ] 9.3 Test search combined with category filters (both should work together); verify AND/OR logic is correct (e.g., matches search AND category filter)

## 10. Evaluations Page - Summary Metrics

- [ ] 10.1 Calculate and display high/medium/low fit counts at top of dashboard; verify counts are correct and match filtered results
- [ ] 10.2 Identify top 5 most common skill gaps across all jobs (or filtered set) and display as a list; verify skill gaps are accurate and update when filters change
- [ ] 10.3 Style metrics section as a visual summary panel (cards, badges, or other visual treatment); verify metrics are easy to scan

## 11. Evaluations Page - Job Detail View

- [ ] 11.1 Implement click handler on job rows to open detail panel; verify detail panel shows when job is clicked and displays correct job's data
- [ ] 11.2 Populate detail panel with: title, company, URL (as clickable link), all fit scores, key strengths (bullet list), skill gaps, red flags, recommendation, evaluated_at date; verify all fields are present and readable
- [ ] 11.3 Implement prev/next buttons to navigate between jobs in filtered list; verify adjacent jobs load correctly and sort/filter state is maintained
- [ ] 11.4 Implement close button on detail panel; verify panel closes and table is visible again

## 12. Evaluations Page - Export Functionality

- [ ] 12.1 Implement CSV export: generate CSV from current filtered job list with columns matching table display; verify downloaded file opens in spreadsheet and has correct data and format
- [ ] 12.2 Implement JSON export: generate JSON file with full job objects from filtered list; verify downloaded file is valid JSON and contains all fields
- [ ] 12.3 Include export date in filename (e.g., `jobs_2026-09-17.csv`); verify filename reflects current date
- [ ] 12.4 Test exports with different filter states (all jobs, high-fit only, search results) and verify export respects active filters

## 13. Applied Jobs Page - Timeline Rendering

- [ ] 13.1 Render applied jobs as a list/timeline view sorted chronologically (most recent first); verify all applied jobs appear as rows with: Job Title, Company, Applied Date, Status (if available)
- [ ] 13.2 Apply visual styling to applied jobs (cards, timeline markers, or list rows with date grouping); verify applied jobs are distinct from evaluation view
- [ ] 13.3 Display applied job count and summary: "High Fit: N | Medium Fit: N | Low Fit: N" for applied jobs only; verify summary updates with filters

## 14. Applied Jobs Page - Filtering

- [ ] 14.1 Implement fit level filter for applied jobs (high/medium/low checkboxes); verify filtering works and updates job count
- [ ] 14.2 Implement date range filter (from/to date inputs) for applied jobs; verify filtering by applied date works correctly
- [ ] 14.3 Implement status filter for applied jobs (Applied, Phone Screen, Interview, Offer, Closed); verify status filtering works when status data is available in CSV
- [ ] 14.4 Test all filter combinations and verify AND logic (all active filters apply simultaneously)

## 15. Applied Jobs Page - Search and Sorting

- [ ] 15.1 Implement search for applied jobs by company name or title; verify search filters in real-time
- [ ] 15.2 Make applied jobs list column headers sortable (Applied Date, Title, Company, Fit Score); verify sort direction indicator appears
- [ ] 15.3 Test sorting combined with filtering; verify sort state persists when filters change

## 16. Applied Jobs Page - Evaluation Popup

- [ ] 16.1 Implement click handler on applied job rows to open evaluation popup/modal; verify popup shows when applied job is clicked
- [ ] 16.2 Populate evaluation popup with full details: title, company, URL (clickable link), all fit scores, key strengths, skill gaps, red flags, recommendation, evaluation date; verify all data displays correctly
- [ ] 16.3 For unmatched applied jobs (no evaluation), display popup with message "Evaluation data not available" and basic job info from CSV
- [ ] 16.4 Implement close button on popup and allow clicking outside to close; verify popup closes and returns to applied jobs list
- [ ] 16.5 Test popup with matched and unmatched jobs; verify both cases display appropriately

## 17. Responsive Design

- [ ] 17.1 Test dashboard on mobile viewport (e.g., 375px width) and adjust layout to stack columns/hide secondary columns if needed; verify all content is readable without horizontal scroll
- [ ] 17.2 Test on tablet and desktop viewports; verify layout adapts appropriately and no content is obscured
- [ ] 17.3 Ensure detail panels/popups work on mobile (full-width or bottom drawer); verify detail view is usable on small screens

## 18. Accessibility

- [ ] 18.1 Ensure all interactive elements (tabs, buttons, checkboxes, links, headers) are keyboard focusable; verify tab navigation works through all pages
- [ ] 18.2 Add visible focus indicators to all focusable elements; verify focus outline is clear and readable
- [ ] 18.3 Test with screen reader (NVDA, JAWS, or browser built-in) to verify page structure, tab switching, and labels are announced correctly; verify critical information (job title, fit score, applied date) is accessible

## 19. Testing and Verification

- [ ] 19.1 Load dashboard in multiple browsers (Chrome, Firefox, Safari) and verify all features work consistently; document any known compatibility issues
- [ ] 19.2 Test with sample data sets (job_evaluations.json and job_search_tracker.csv) and verify both pages display correctly
- [ ] 19.3 Manually test all filters, sorts, searches, export combinations on both pages to catch edge cases (empty results, unmatched jobs, etc.); verify graceful handling
- [ ] 19.4 Performance check: load dashboard with evaluation file and CSV; verify page loads in <2 seconds and interactions (filter, sort, search, popup) respond instantly
- [ ] 19.5 Test CSV with various formats (different delimiters, quoted fields, missing columns) and verify parser handles edge cases
- [ ] 19.6 Since `job_evaluations.json` currently contains zero Indeed records, hand-build a synthetic fixture (a few evaluation records with `linkedin.com` URLs and a few with `indeed.com` `jk=` URLs, plus matching applied-job CSV rows) to exercise the Indeed key extractor end-to-end; verify LinkedIn and Indeed composite-key matching both work correctly against it

## 20. Documentation and Finalization

- [ ] 20.1 Add inline comments to JavaScript explaining key functions (data loading, matching, filtering, rendering, popups, export); verify code is readable
- [ ] 20.2 Create a README or usage guide (either in comments or separate doc) explaining how to use both pages, data file format, prerequisites (e.g., HTTP server), and how to update CSV with applied jobs; verify instructions are clear
- [ ] 20.3 Verify `dashboard.html` is placed in the correct project location (root or `dashboards/` folder TBD); verify file is discoverable and linkable from project documentation
