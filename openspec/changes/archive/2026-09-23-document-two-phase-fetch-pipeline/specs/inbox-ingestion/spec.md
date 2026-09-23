## ADDED Requirements

### Requirement: Ingestion runs as a two-phase collect-then-fetch pipeline
The system SHALL separate URL collection from description fetching into two distinct phases: first collecting and deduplicating candidate job URLs from Gmail alerts with no browser cost, then browser-fetching full descriptions only for URLs not already present in `private/inbox_queue.json`. The system SHALL write a timestamped scratch file of raw collected URLs and a timestamped per-run log file for every run.

#### Scenario: Already-queued URLs are never re-fetched
- **WHEN** a fetch run collects a URL that already exists in `private/inbox_queue.json`
- **THEN** the system skips the browser-fetch phase for that URL and does not launch a browser session for it

#### Scenario: Every run produces an auditable scratch file and log
- **WHEN** `tools/fetch_inbox.py` completes a run
- **THEN** a timestamped scratch file (`private/scratch_<timestamp>.json`) containing every raw collected URL, and a timestamped log file (`logs/fetch_inbox_<timestamp>.log`) containing the full run trace, both exist on disk
