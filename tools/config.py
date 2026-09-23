"""Centralized path and settings resolution for every tools/*.py script.

Loads private/config.json (gitignored) for personal settings and resolves every
path under private/ so no script hardcodes a path literal. See
config.example.json (repo root) for the expected config.json shape.
"""
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PRIVATE_DIR = REPO_ROOT / "private"
CONFIG_PATH = PRIVATE_DIR / "config.json"
CONFIG_EXAMPLE_PATH = REPO_ROOT / "config.example.json"


def _load_config():
    if not CONFIG_PATH.exists():
        raise FileNotFoundError(
            f"Missing {CONFIG_PATH}. Copy {CONFIG_EXAMPLE_PATH.name} to "
            f"private/config.json and fill in your own values (see SETUP.md)."
        )
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    if "job_search_email" not in data:
        raise KeyError(f"{CONFIG_PATH} is missing required key 'job_search_email'.")
    return data


_config = _load_config()
job_search_email = _config["job_search_email"]

# OAuth
CREDENTIALS_PATH = PRIVATE_DIR / "credentials.json"
TOKEN_PATH = PRIVATE_DIR / "token.json"

# Candidate data
PROFILE_PATH = PRIVATE_DIR / "profile.md"
CV_DIR = PRIVATE_DIR / "cv"

# Evaluation pipeline & tracker
INBOX_QUEUE_PATH = PRIVATE_DIR / "inbox_queue.json"
JOB_EVALUATIONS_PATH = PRIVATE_DIR / "job_evaluations.json"
JOB_EVALUATIONS_FAILED_PATH = PRIVATE_DIR / "job_evaluations.failed.json"
FETCH_STATE_PATH = PRIVATE_DIR / "fetch_state.json"
EVAL_BATCHES_DIR = PRIVATE_DIR / "eval_batches"
SCRATCH_GLOB = str(PRIVATE_DIR / "scratch_*.json")
JOB_SEARCH_TRACKER_PATH = PRIVATE_DIR / "job_search_tracker.csv"

# documents/ personal subfolders (cv, linkedin, diplomas, references, applications)
DOCUMENTS_DIR = PRIVATE_DIR / "documents"

# Future /apply output
APPLICATIONS_DIR = PRIVATE_DIR / "applications"

# Salary benchmarking (optional, user-provided)
SALARY_DATA_PATH = PRIVATE_DIR / "salary_data.json"
