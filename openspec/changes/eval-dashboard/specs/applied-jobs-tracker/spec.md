## Purpose

Enables users to track submitted job applications and instantly see their evaluation data (fit scores, strengths, gaps, recommendations) for each applied role, bridging the gap between evaluation decisions and application outcomes.

## ADDED Requirements

### Requirement: Load application tracker data from CSV
The system SHALL load job application records from `job_search_tracker.csv` and parse them into an in-memory data structure.

#### Scenario: Successfully load valid CSV
- **WHEN** user opens the Applied Jobs page
- **THEN** system loads `job_search_tracker.csv` (or accepts file upload)
- **AND** displays a list of applied jobs without errors

#### Scenario: Handle missing or invalid CSV gracefully
- **WHEN** CSV file is unavailable or malformed
- **THEN** system displays an error message to the user explaining the problem
- **AND** provides a file upload input to supply the CSV data

#### Scenario: CSV has required columns
- **WHEN** CSV is loaded
- **THEN** system expects columns: URL (required—used to match against evaluation data), Applied Date, Company, Title, and optionally Status, Notes
- **AND** displays a warning for any row missing URL (that row cannot be matched to an evaluation, but its Company/Title/Date still display) and for any missing critical column more broadly

### Requirement: Match applied jobs to evaluations by extracted job key
The system SHALL derive a composite job key from each record's URL—a vendor prefix plus the vendor's canonical job identifier—and join applied job records to evaluation records on that derived key rather than on the raw URL string. Raw URLs for the same job posting can differ in tracking parameters between the alert email that produced the evaluation and the URL later entered in the tracker, so matching on the extracted id is required for the join to be reliable.

#### Scenario: Extract composite key from LinkedIn URL
- **WHEN** a record's URL contains `linkedin.com` and a `/jobs/view/<id>` path segment
- **THEN** system extracts the numeric id and builds the key `LKD<id>` (e.g. `LKD4413352108`)

#### Scenario: Extract composite key from Indeed URL
- **WHEN** a record's URL contains `indeed.com` and a `jk=<token>` query parameter
- **THEN** system extracts the hex token and builds the key `IND<token>` (e.g. `INDa6f9bad38ae0449d`)

#### Scenario: Successful match by composite key
- **WHEN** an applied job's composite key matches an evaluation record's composite key
- **THEN** system links them together for display
- **AND** evaluation data (fit scores, strengths, gaps) become available for that applied job

#### Scenario: No matching evaluation found
- **WHEN** an applied job's composite key does not match any evaluation record's key—including when the URL is missing, malformed, or from a vendor other than LinkedIn/Indeed
- **THEN** system displays the job with an "Evaluation not available" indicator
- **AND** allows user to still view basic job info (title, company, applied date)

#### Scenario: Multiple matches for the same key
- **WHEN** a composite key matches more than one evaluation record (unlikely but possible)
- **THEN** system uses the first match and logs a warning
- **AND** considers adding confidence indicators in future iteration

### Requirement: Display applied jobs in chronological timeline
The system SHALL render applied jobs sorted by applied date (most recent first) with clear visual organization.

#### Scenario: Render applied jobs list
- **WHEN** dashboard loads with application data
- **THEN** system displays a chronological list/timeline of applied jobs
- **AND** each row shows: Job Title, Company, Applied Date, Status (if available)

#### Scenario: Visual timeline layout
- **WHEN** rendering applied jobs
- **THEN** system uses a timeline or card-based layout with applied date as primary sort
- **AND** most recent applications appear first
- **AND** grouped by date or status for visual scanning (optional enhancement)

### Requirement: Filter applied jobs by fit level
The system SHALL allow users to show/hide applied jobs based on evaluation fit category (high/medium/low).

#### Scenario: Filter by fit category
- **WHEN** user selects "High Fit" checkbox
- **THEN** system displays only applied jobs with fit_category = "high"
- **AND** applied job count is updated to reflect filtered results

#### Scenario: Multiple category filters
- **WHEN** user selects multiple categories (e.g., "High Fit" and "Medium Fit")
- **THEN** system displays jobs matching any selected category (OR logic)
- **AND** filter state persists while browsing

### Requirement: Filter applied jobs by application date range
The system SHALL allow users to filter applied jobs by a date range (from/to dates).

#### Scenario: Filter by date range
- **WHEN** user specifies a start date and end date
- **THEN** system displays only jobs with applied_date falling within that range (inclusive)
- **AND** applied job count updates to reflect filtered results

#### Scenario: Partial date range
- **WHEN** user specifies only a start date or only an end date
- **THEN** system interprets as "from date onwards" or "until date" respectively
- **AND** displays jobs matching the partial range

### Requirement: Filter applied jobs by status
The system SHALL allow users to filter applied jobs by application status (if available in data).

#### Scenario: Filter by single status
- **WHEN** user selects status filter (e.g., "Applied", "Phone Screen", "Interview", "Offer", "Closed")
- **THEN** system displays only jobs with that status
- **AND** applied job count updates

#### Scenario: Multiple status filters
- **WHEN** user selects multiple statuses
- **THEN** system displays jobs matching any selected status (OR logic)
- **AND** filter persists across page interactions

### Requirement: Show evaluation data popup on click
The system SHALL display a popup or modal with full evaluation details when user clicks on an applied job.

#### Scenario: Open evaluation popup
- **WHEN** user clicks on an applied job row
- **THEN** system displays a popup/modal with: Job Title, Company, URL (clickable link), all fit scores (skill match %, experience match %, company fit %, overall fit %), Key Strengths (bullet list), Skill Gaps, Red Flags, Overall Recommendation, Evaluated Date
- **AND** popup remains visible until user closes it

#### Scenario: Close popup
- **WHEN** user clicks close button or clicks outside the popup
- **THEN** system closes the popup and returns focus to the timeline list
- **AND** filter and sort state are preserved

#### Scenario: Evaluation not available
- **WHEN** user clicks on an applied job that has no matching evaluation
- **THEN** system displays a message "Evaluation data not available for this job"
- **AND** shows basic job info from CSV (title, company, applied date, status)

### Requirement: Sort applied jobs by any column
The system SHALL allow users to click column headers to sort the timeline by different fields.

#### Scenario: Sort by applied date
- **WHEN** user clicks "Applied Date" column header
- **THEN** system sorts by date in descending order (most recent first by default)
- **AND** clicking again reverses sort direction

#### Scenario: Sort by fit score
- **WHEN** user clicks "Overall Fit %" column header
- **THEN** system sorts applied jobs by overall fit score (highest first)
- **AND** clicking again reverses direction

#### Scenario: Sort by company or title
- **WHEN** user clicks "Company" or "Title" header
- **THEN** system sorts alphabetically by that column
- **AND** visual indicator shows sort direction (↑/↓)

### Requirement: Search applied jobs by company or title
The system SHALL provide a search input to filter applied jobs by company name or job title keywords.

#### Scenario: Search by company name
- **WHEN** user types "Celonis" in search box
- **THEN** system filters to show only applied jobs from Celonis
- **AND** search is case-insensitive

#### Scenario: Search by job title keyword
- **WHEN** user types "director" in search box
- **THEN** system filters to show applied jobs with "director" in the title
- **AND** search works with partial matches

#### Scenario: Search combined with other filters
- **WHEN** user applies search and also uses fit level or date filters
- **THEN** system applies all filters together (AND logic)
- **AND** result reflects intersection of all active filters

### Requirement: Display applied jobs count and summary
The system SHALL show a summary count of applied jobs and how many match active filters.

#### Scenario: Show applied jobs count
- **WHEN** dashboard loads applied jobs
- **THEN** system displays total applied jobs count and filtered count
- **AND** updates in real-time when filters change

#### Scenario: Display fit breakdown of applied jobs
- **WHEN** user views the applied jobs page
- **THEN** system shows: "High Fit: N | Medium Fit: N | Low Fit: N" for applied jobs only
- **AND** counts reflect current filtered results

### Requirement: Responsive and accessible design
The system SHALL display correctly on mobile, tablet, and desktop screens and follow WCAG accessibility guidelines.

#### Scenario: Mobile layout
- **WHEN** dashboard is viewed on a mobile device
- **THEN** layout adapts to portrait orientation with stacked or collapsible columns
- **AND** all controls remain accessible (no horizontal scroll required)

#### Scenario: Keyboard navigation
- **WHEN** user navigates with keyboard only
- **THEN** all interactive elements are focusable (sort buttons, filters, job rows, close popup)
- **AND** focus indicator is visible on all focusable elements
