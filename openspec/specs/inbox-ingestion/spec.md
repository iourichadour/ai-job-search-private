# inbox-ingestion Specification

## Purpose
Defines ingestion filtering rules that extract high-quality individual job postings from Gmail alerts while filtering out search aggregation digests and non-job alert noise before saving to the inbox queue.

## Requirements

### Requirement: Search alert aggregations and digests are excluded at ingestion
The system SHALL detect and filter out email notifications that link to multi-job search result aggregations (such as LinkedIn search digests or aggregated query alert emails) during mailbox ingestion, preventing them from being stored in `data/inbox_queue.json`.

#### Scenario: Aggregated search alert header is skipped
- **WHEN** an alert email contains an aggregate summary title matching patterns like `\d+[\d,]*\+\s+.*Jobs` (e.g., "9,000+ Director of IT Jobs in United States")
- **THEN** the ingestion process drops the summary item and does not append it to `data/inbox_queue.json`

#### Scenario: Search URL link is excluded from job postings
- **WHEN** an extracted email link points to a general search query path (such as `/jobs/search/` or search result query strings) rather than a specific individual job posting ID path (such as `/jobs/view/{id}/` or `viewjob?jk={id}`)
- **THEN** the system ignores the search URL and only ingests valid individual job posting URLs

### Requirement: Ingestion reports dropped digest count
The system SHALL report how many search aggregation items or invalid non-posting alert links were filtered during the fetch process.

#### Scenario: Dropped digest summary logged
- **WHEN** `tools/fetch_inbox.py` encounters search aggregation links in the alert emails
- **THEN** it logs a summary of skipped search digests alongside the count of newly fetched individual jobs
