## Purpose

Provides an interactive HTML dashboard for exploring job evaluation data, enabling users to quickly assess fit scores across multiple dimensions and identify priority roles for application.

## ADDED Requirements

### Requirement: Load evaluation data from JSON source
The system SHALL load job evaluation data from a JSON file and parse it into an in-memory data structure suitable for rendering and filtering.

#### Scenario: Successfully load valid evaluation JSON
- **WHEN** user opens the dashboard HTML file
- **THEN** system loads `data/job_evaluations.json` (or URL specified in configuration)
- **AND** displays a list of job evaluations without errors

#### Scenario: Handle missing or invalid JSON gracefully
- **WHEN** JSON file is unavailable or malformed
- **THEN** system displays an error message to the user explaining the problem
- **AND** provides instructions on how to provide the data (file upload, URL input, etc.)

### Requirement: Display job list with key metrics
The system SHALL render a sortable, scannable list of jobs showing title, company, overall fit score, and fit category (high/medium/low).

#### Scenario: Render job list on load
- **WHEN** dashboard loads with evaluation data
- **THEN** system displays a table/list with columns: Job Title, Company, Skill Match %, Experience Match %, Overall Fit %, Fit Category
- **AND** each row is visually distinct and readable

#### Scenario: Visual fit indicators
- **WHEN** rendering fit scores
- **THEN** system uses color coding: high fit (green), medium fit (yellow), low fit (red)
- **AND** fit category badge matches the color scheme

### Requirement: Sort job list by any column
The system SHALL allow users to click column headers to sort jobs ascending or descending by that column's values.

#### Scenario: Sort by overall fit score
- **WHEN** user clicks "Overall Fit %" column header
- **THEN** system sorts jobs by overall_fit score in descending order (highest first)
- **AND** clicking again reverses the sort direction

#### Scenario: Sort by company name
- **WHEN** user clicks "Company" column header
- **THEN** system sorts jobs alphabetically by company name
- **AND** visual indicator shows sort direction (↑/↓)

### Requirement: Filter jobs by fit category
The system SHALL provide filter controls allowing users to show/hide jobs in specific fit categories (high/medium/low).

#### Scenario: Filter by category
- **WHEN** user selects "High Fit" checkbox
- **THEN** system displays only jobs with fit_category = "high"
- **AND** job count is updated to reflect filtered results

#### Scenario: Multiple category filters
- **WHEN** user selects both "High Fit" and "Medium Fit"
- **THEN** system displays jobs matching either category
- **AND** filter state persists while browsing

### Requirement: View job detail panel
The system SHALL display a side panel or modal showing full job details when a job is selected.

#### Scenario: Open job detail view
- **WHEN** user clicks a job row
- **THEN** system shows a detail panel with: title, company, URL, all fit scores, key strengths (bullet list), skill gaps, red flags, recommendation, and evaluation date
- **AND** panel remains visible until user closes it

#### Scenario: Navigate between jobs
- **WHEN** user clicks next/previous buttons in detail panel
- **THEN** system displays details for the adjacent job in filtered list
- **AND** maintains filter and sort state

### Requirement: Display summary metrics
The system SHALL render a metrics summary showing total count of evaluations by fit category and key statistics.

#### Scenario: Show fit category counts
- **WHEN** dashboard loads or filters change
- **THEN** system displays: "High: N | Medium: N | Low: N" showing job count per category
- **AND** updates in real-time when filters change

#### Scenario: Display skill gap patterns
- **WHEN** user views the summary section
- **THEN** system displays the top 5 most common skill gaps across all jobs
- **AND** shows frequency count for each gap

### Requirement: Search jobs by company or title
The system SHALL provide a search input allowing users to filter jobs by company name or job title keywords.

#### Scenario: Search by company name
- **WHEN** user types "Celonis" in search box
- **THEN** system filters to show only jobs from Celonis
- **AND** search is case-insensitive

#### Scenario: Search by job title keyword
- **WHEN** user types "director" in search box
- **THEN** system filters to show jobs with "director" in the title
- **AND** search works with partial matches

### Requirement: Export or download data
The system SHALL allow users to export the filtered job list as CSV or JSON for external analysis.

#### Scenario: Export filtered jobs as CSV
- **WHEN** user clicks "Export as CSV" button
- **THEN** system generates a CSV file with columns matching the job list display
- **AND** downloads the file with filename including export date

#### Scenario: Export respects active filters
- **WHEN** user applies filters and clicks "Export"
- **THEN** exported file contains only jobs matching current filters
- **AND** export filename indicates filter state (e.g., "jobs_high-fit_2026-09-17.csv")

### Requirement: Responsive and accessible design
The system SHALL display correctly on mobile, tablet, and desktop screens and follow WCAG accessibility guidelines.

#### Scenario: Mobile layout
- **WHEN** dashboard is viewed on a mobile device
- **THEN** layout adapts to portrait orientation with stacked columns
- **AND** all controls remain accessible (no horizontal scroll required)

#### Scenario: Keyboard navigation
- **WHEN** user navigates with keyboard only
- **THEN** all interactive elements are focusable (sort buttons, filters, job rows)
- **AND** focus indicator is visible
