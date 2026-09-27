"""
Configuration module for Data Analyst Job Market Analysis.
Loads environment variables from .env file and exposes path and setting constants.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Base project directory
BASE_DIR = Path(__file__).resolve().parent

# Load .env file
load_dotenv(BASE_DIR / ".env")

# Adzuna API credentials
ADZUNA_APP_ID: str = os.getenv("ADZUNA_APP_ID", "").strip()
ADZUNA_APP_KEY: str = os.getenv("ADZUNA_APP_KEY", "").strip()

# Search settings
COUNTRY: str = os.getenv("COUNTRY", "in").lower()
RESULTS_PER_PAGE: int = int(os.getenv("RESULTS_PER_PAGE", "50"))
MAX_PAGES: int = int(os.getenv("MAX_PAGES", "10"))

# Directory paths
DATA_DIR: Path = BASE_DIR / "data"
RAW_DATA_DIR: Path = DATA_DIR / "raw"
PROCESSED_DATA_DIR: Path = DATA_DIR / "processed"
SQL_DIR: Path = BASE_DIR / "sql"
OUTPUTS_DIR: Path = BASE_DIR / "outputs"

# Database Configuration
DB_TYPE: str = os.getenv("DB_TYPE", "sqlite").lower()
SQLITE_PATH: Path = BASE_DIR / os.getenv("SQLITE_PATH", "data/job_market.db")

DB_HOST: str = os.getenv("DB_HOST", "localhost")
DB_PORT: str = os.getenv("DB_PORT", "5432")
DB_NAME: str = os.getenv("DB_NAME", "job_market_db")
DB_USER: str = os.getenv("DB_USER", "postgres")
DB_PASSWORD: str = os.getenv("DB_PASSWORD", "postgres")

# Ensure required directories exist
RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
