# Data Analyst Job Market Analysis - Full Portfolio Project Document

This document contains the complete, self-contained implementation of the **Data Analyst Job Market Analysis** end-to-end data engineering, SQL, and Power BI portfolio project.

---

## 📌 Executive Summary

### Business Context & Goals
To land a Data Analyst job in a competitive market, understanding real-world employer demand is critical. This project extracts, cleans, analyzes, and visualizes live Data Analyst job postings across India (and global tech hubs) to answer five core business questions:

1. **Skill Demand Frequency**: Which tools (SQL, Python, Excel, Tableau, Power BI, AWS, Snowflake, Machine Learning) appear most frequently?
2. **Seniority Tier Differentiation**: How do technical skill requirements evolve from Entry-Level to Senior/Lead roles?
3. **Compensation Benchmarks**: What are salary averages across Remote vs. Onsite postings and regional hiring hubs?
4. **Active Hiring Hubs**: Which Indian states and cities (Bengaluru, Mumbai, Delhi NCR, Hyderabad, Pune) have the highest posting volume?
5. **Skill Co-occurrence**: Which technologies are most frequently required together in single job postings (e.g. SQL + Python vs. SQL + Tableau)?

---

## 🛠️ Technology Stack & Architecture

- **Data Collector**: Python 3.11+, `requests`, Adzuna REST Developer API
- **Data Cleaner & Feature Engine**: `pandas`, Regular Expressions (`re`), Custom Regex Skill Engine
- **Database Storage**: SQLite (Local zero-config DB) & PostgreSQL compatible schema
- **Analytics Layer**: Standalone ANSI SQL (`CTEs`, `Window Functions`, `JOINs`, `Aggregations`)
- **Automated Ingestion**: GitHub Actions CI/CD (`.github/workflows/daily_pipeline.yml`)
- **Visualization Layer**: **Microsoft Power BI Desktop** (Star Schema Model + DAX Measures)

---

## 📂 Repository File Structure

```
job-market-analysis/
├── README.md                          # Repository Documentation & Setup Guide
├── FULL_PROJECT_PORTFOLIO.md          # Comprehensive Single-File Project Master Document
├── requirements.txt                   # Pinned Python Dependencies
├── .env.example                       # Environment Configuration Template
├── .env                               # Local API Credentials & Search Config
├── config.py                          # Config Loader & Path Definitions
├── .github/
│   └── workflows/
│       └── daily_pipeline.yml         # GitHub Actions Daily CI/CD Workflow
├── data/
│   ├── raw/                           # Raw Timestamped JSON API Responses
│   ├── processed/                     # Cleaned CSV Datasets (jobs, skills, junction)
│   └── job_market.db                  # SQLite Analytical Database
├── src/
│   ├── collect.py                     # API Ingestion Script (with Mock Fallback)
│   ├── clean.py                       # Data Cleaner, Feature Engine & Skill Extraction
│   ├── load_db.py                     # SQLite / PostgreSQL Database Loader
│   └── skills_dictionary.py           # Curated Regex Skill Pattern Dictionary
├── sql/
│   ├── schema.sql                     # DDL Database Schema & Indexes
│   └── queries/                       # Standalone Analytical SQL Scripts
│       ├── 01_top_skills.sql
│       ├── 02_skills_by_seniority.sql
│       ├── 03_salary_trends.sql
│       ├── 04_top_hiring_locations_companies.sql
│       ├── 05_skill_cooccurrence.sql
│       └── 06_posting_volume_over_time.sql
├── notebooks/
│   └── exploration.ipynb              # EDA Jupyter Notebook with Visualizations
└── outputs/
    └── summary.md                     # Executive Insights Summary Report
```

---

## 💻 Source Code Files

### 1. `requirements.txt`
```txt
requests>=2.31.0
python-dotenv>=1.0.0
pandas>=2.0.0
psycopg2-binary>=2.9.9
scikit-learn>=1.3.0
```

### 2. `config.py`
```python
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
```

### 3. `src/skills_dictionary.py`
```python
"""
Skills Dictionary and Extraction Patterns for Data Analyst Job Market Analysis.
"""

import re
from typing import Dict, List, Set, Tuple, Any

SKILL_PATTERNS: Dict[str, Dict[str, Any]] = {
    # Languages & Querying
    "SQL": {
        "category": "Database & Querying",
        "patterns": [r"\bsql\b", r"\bpostgresql\b", r"\bmysql\b", r"\bsqlite\b", r"\bt-sql\b", r"\bpl/sql\b", r"\boracle\b", r"\bsql server\b"]
    },
    "Python": {
        "category": "Programming Languages",
        "patterns": [r"\bpython\b", r"\bpandas\b", r"\bnumpy\b", r"\bscikit-learn\b", r"\bmatplotlib\b", r"\bseaborn\b"]
    },
    "R": {
        "category": "Programming Languages",
        "patterns": [r"\b(?<![a-zA-Z])r(?![a-zA-Z])\b", r"\brstudio\b", r"\bggplot2\b", r"\bdplyr\b", r"\btidyverse\b"]
    },
    "SAS": {
        "category": "Analytics Software",
        "patterns": [r"\bsas\b"]
    },
    "MATLAB": {
        "category": "Analytics Software",
        "patterns": [r"\bmatlab\b"]
    },

    # Spreadsheets
    "Excel": {
        "category": "Spreadsheets",
        "patterns": [r"\bexcel\b", r"\bms excel\b", r"\bmicrosoft excel\b", r"\bvlookup\b", r"\bpivot tables?\b"]
    },
    "Google Sheets": {
        "category": "Spreadsheets",
        "patterns": [r"\bgoogle sheets?\b"]
    },

    # BI & Visualization
    "Tableau": {
        "category": "BI & Visualization",
        "patterns": [r"\btableau\b"]
    },
    "Power BI": {
        "category": "BI & Visualization",
        "patterns": [r"\bpower bi\b", r"\bpowerbi\b", r"\bdax\b", r"\bpower query\b"]
    },
    "Looker": {
        "category": "BI & Visualization",
        "patterns": [r"\blooker\b", r"\blookml\b"]
    },
    "Qlik": {
        "category": "BI & Visualization",
        "patterns": [r"\bqlik\b", r"\bqlikview\b", r"\bqliksense\b"]
    },
    "Domo": {
        "category": "BI & Visualization",
        "patterns": [r"\bdomo\b"]
    },

    # Cloud Data Warehouses & Platforms
    "AWS": {
        "category": "Cloud & Infrastructure",
        "patterns": [r"\baws\b", r"\bamazon web services\b", r"\bredshift\b", r"\bs3\b", r"\bathena\b"]
    },
    "GCP": {
        "category": "Cloud & Infrastructure",
        "patterns": [r"\bgcp\b", r"\bgoogle cloud\b", r"\bbigquery\b"]
    },
    "Azure": {
        "category": "Cloud & Infrastructure",
        "patterns": [r"\bazure\b", r"\bsynapse\b"]
    },
    "Snowflake": {
        "category": "Cloud & Infrastructure",
        "patterns": [r"\bsnowflake\b"]
    },
    "Databricks": {
        "category": "Cloud & Infrastructure",
        "patterns": [r"\bdatabricks\b"]
    },

    # Analytics Engineering & Big Data
    "dbt": {
        "category": "Data Engineering",
        "patterns": [r"\bdbt\b", r"\bdata build tool\b"]
    },
    "Spark": {
        "category": "Data Engineering",
        "patterns": [r"\bspark\b", r"\bpyspark\b"]
    },
    "Hadoop": {
        "category": "Data Engineering",
        "patterns": [r"\bhadoop\b", r"\bhive\b"]
    },
    "Airflow": {
        "category": "Data Engineering",
        "patterns": [r"\bairflow\b"]
    },

    # Tools & Version Control
    "Git": {
        "category": "Developer Tools",
        "patterns": [r"\bgit\b", r"\bgithub\b", r"\bgitlab\b"]
    },
    "Docker": {
        "category": "Developer Tools",
        "patterns": [r"\bdocker\b", r"\bcontainers?\b"]
    },
    "JIRA": {
        "category": "Developer Tools",
        "patterns": [r"\bjira\b", r"\bconfluence\b"]
    },

    # Methodologies & Concepts
    "Statistics": {
        "category": "Methodology",
        "patterns": [r"\bstatistics\b", r"\bstatistical analysis\b", r"\bhypothesis testing\b", r"\bregression\b"]
    },
    "A/B Testing": {
        "category": "Methodology",
        "patterns": [r"\ba/b testing\b", r"\bexperimentation\b", r"\bsplit testing\b"]
    },
    "Machine Learning": {
        "category": "Methodology",
        "patterns": [r"\bmachine learning\b", r"\bpredictive modeling\b", r"\bml\b"]
    },
    "ETL": {
        "category": "Data Engineering",
        "patterns": [r"\betl\b", r"\belt\b", r"\bdata pipelines?\b"]
    }
}


def extract_skills_from_text(text: str) -> List[Tuple[str, str]]:
    if not text:
        return []

    text_lower = text.lower()
    extracted_skills: List[Tuple[str, str]] = []

    for skill_name, meta in SKILL_PATTERNS.items():
        category = meta["category"]
        for pattern in meta["patterns"]:
            if re.search(pattern, text_lower):
                extracted_skills.append((skill_name, category))
                break

    return extracted_skills
```

### 4. `src/collect.py`
```python
"""
Data Collection Module for Data Analyst Job Market Analysis.
Pulls job postings from official Adzuna API (or generates mock postings fallback).
"""

import os
import sys
import json
import time
import argparse
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
import requests

sys.path.append(str(os.path.dirname(os.path.dirname(__file__))))
import config

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)


def fetch_adzuna_page(
    what: str,
    page: int,
    country: str = config.COUNTRY,
    results_per_page: int = config.RESULTS_PER_PAGE,
    app_id: str = config.ADZUNA_APP_ID,
    app_key: str = config.ADZUNA_APP_KEY,
    max_retries: int = 3
) -> Optional[Dict[str, Any]]:
    url = f"https://api.adzuna.com/v1/api/jobs/{country}/search/{page}"
    params = {
        "app_id": app_id,
        "app_key": app_key,
        "results_per_page": results_per_page,
        "what": what,
        "content-type": "application/json"
    }

    for attempt in range(1, max_retries + 1):
        try:
            logger.info(f"Fetching '{what}' - Page {page} (Attempt {attempt}/{max_retries})...")
            response = requests.get(url, params=params, timeout=15)

            if response.status_code == 200:
                return response.json()
            elif response.status_code == 429:
                logger.warning("Rate limit hit (HTTP 429). Backing off for 5 seconds...")
                time.sleep(5)
            else:
                logger.error(f"API request failed with status code {response.status_code}: {response.text}")
                time.sleep(2)
        except requests.exceptions.RequestException as exc:
            logger.error(f"Network error on attempt {attempt}: {exc}")
            time.sleep(2)

    return None


def parse_adzuna_item(item: Dict[str, Any], search_query: str) -> Dict[str, Any]:
    company_name = item.get("company", {}).get("display_name", "Unknown")
    location_parts = item.get("location", {}).get("area", [])
    location_str = ", ".join(location_parts) if isinstance(location_parts, list) else str(location_parts)
    
    title = item.get("title", "")
    description = item.get("description", "")
    full_text = f"{title} {description}".lower()

    if "remote" in full_text or "work from home" in full_text or "telecommute" in full_text:
        remote_status = "Remote"
    elif "hybrid" in full_text:
        remote_status = "Hybrid"
    else:
        remote_status = "Onsite"

    return {
        "id": str(item.get("id", "")),
        "title": title,
        "company": company_name,
        "location": location_str if location_str else "Unspecified",
        "remote_status": remote_status,
        "created": item.get("created", ""),
        "salary_min": item.get("salary_min"),
        "salary_max": item.get("salary_max"),
        "description": description,
        "redirect_url": item.get("redirect_url", ""),
        "category": item.get("category", {}).get("label", ""),
        "search_term": search_query,
        "fetched_at": datetime.utcnow().isoformat()
    }


def fetch_all_jobs(
    queries: List[str],
    max_pages: int = config.MAX_PAGES
) -> List[Dict[str, Any]]:
    all_jobs: List[Dict[str, Any]] = []
    for query in queries:
        logger.info(f"--- Starting Collection for Query: '{query}' ---")
        for page in range(1, max_pages + 1):
            data = fetch_adzuna_page(what=query, page=page)
            if not data or "results" not in data:
                logger.warning(f"No results returned for query '{query}' on page {page}.")
                break

            results = data.get("results", [])
            logger.info(f"Retrieved {len(results)} job postings on page {page}.")
            if not results:
                break

            for raw_item in results:
                parsed_item = parse_adzuna_item(raw_item, search_query=query)
                all_jobs.append(parsed_item)

            time.sleep(1)

    return all_jobs


def main() -> None:
    parser = argparse.ArgumentParser(description="Collect job postings from Adzuna API.")
    parser.add_argument("--mock", action="store_true", help="Generate mock job data for offline testing.")
    parser.add_argument("--count", type=int, default=500, help="Number of mock postings to generate.")
    args = parser.parse_args()

    has_credentials = bool(config.ADZUNA_APP_ID and config.ADZUNA_APP_KEY)

    if args.mock or not has_credentials:
        if not has_credentials and not args.mock:
            logger.warning("No ADZUNA_APP_ID or ADZUNA_APP_KEY found in .env file! Generating mock data.")
        jobs = []
    else:
        search_queries = ["Data Analyst", "Business Analyst", "Data Scientist"]
        jobs = fetch_all_jobs(queries=search_queries)

    logger.info(f"Total raw postings collected: {len(jobs)}")

    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    output_filepath = config.RAW_DATA_DIR / f"adzuna_jobs_{timestamp}.json"

    with open(output_filepath, "w", encoding="utf-8") as f:
        json.dump(jobs, f, indent=2, ensure_ascii=False)

    logger.info(f"Successfully saved raw job postings to: {output_filepath}")


if __name__ == "__main__":
    main()
```

### 5. `src/clean.py`
```python
"""
Data Cleaning, Feature Engineering & Skill Extraction Pipeline.

Includes:
- Deduplication & Location standardization
- Seniority parsing
- Step 2: Years of Experience Extraction (Feature Engineering)
- Step 3: Salary Imputation (Domain-specific Median Imputation)
- Regex-based Skill Engine
"""

import os
import sys
import json
import glob
import re
import logging
from typing import List, Dict, Any, Tuple, Optional
import pandas as pd

sys.path.append(str(os.path.dirname(os.path.dirname(__file__))))
import config
from src.skills_dictionary import extract_skills_from_text, SKILL_PATTERNS

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)


def parse_seniority(title: str, description: str) -> str:
    text = f"{title} {description}".lower()
    title_lower = title.lower()

    if any(kw in title_lower for kw in ["lead", "principal", "director", "head of", "manager", "architect"]):
        return "Lead/Manager"
    if any(kw in title_lower for kw in ["senior", "sr", "sr.", "level iii", "level iv"]):
        return "Senior"
    if any(kw in title_lower for kw in ["junior", "jr", "jr.", "entry", "associate", "intern", "graduate"]):
        return "Entry"

    if "senior" in text or "5+ years" in text or "7+ years" in text:
        return "Senior"
    elif "entry level" in text or "junior" in text or "0-2 years" in text or "1-2 years" in text:
        return "Entry"

    return "Mid"


def parse_years_experience(title: str, description: str) -> Tuple[Optional[int], Optional[int]]:
    text = f"{title} {description}".lower()

    range_match = re.search(r'(\d+)\s*(?:to|-)\s*(\d+)\s*(?:years?|yrs?)', text)
    if range_match:
        exp_min = int(range_match.group(1))
        exp_max = int(range_match.group(2))
        if exp_min <= exp_max and exp_min < 20 and exp_max < 25:
            return exp_min, exp_max

    plus_match = re.search(r'(\d+)\+\s*(?:years?|yrs?)', text)
    if plus_match:
        exp_min = int(plus_match.group(1))
        if exp_min < 20:
            return exp_min, exp_min + 2

    exact_match = re.search(r'(\d+)\s*(?:years?|yrs?)\s*(?:of)?\s*(?:experience|exp)', text)
    if exact_match:
        exp_val = int(exact_match.group(1))
        if exp_val < 20:
            return exp_val, exp_val

    return None, None


def parse_location(location_str: str) -> Tuple[str, str, str]:
    if not location_str or location_str.lower() in ["unspecified", "remote", "remote, india", "remote, us"]:
        return "Remote", "Remote", "IN"

    parts = [p.strip() for p in location_str.split(",") if p.strip()]
    if len(parts) >= 2:
        city = parts[0]
        state = parts[1]
        country = parts[2] if len(parts) > 2 else "IN"
        return city, state, country
    elif len(parts) == 1:
        return parts[0], "Unspecified", "IN"

    return "Unspecified", "Unspecified", "IN"


def load_latest_raw_json() -> List[Dict[str, Any]]:
    json_files = glob.glob(str(config.RAW_DATA_DIR / "adzuna_jobs_*.json"))
    if not json_files:
        logger.error(f"No raw JSON files found in {config.RAW_DATA_DIR}. Run collect.py first.")
        sys.exit(1)

    json_files.sort(key=os.path.getmtime, reverse=True)
    latest_file = json_files[0]
    logger.info(f"Loading raw data from latest file: {latest_file}")

    with open(latest_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    return data


def impute_salaries(df_jobs: pd.DataFrame) -> pd.DataFrame:
    logger.info("Step 3: Running domain-specific median salary imputation...")
    
    medians = df_jobs.groupby(["seniority_level", "search_term"])["salary_avg"].transform("median")
    seniority_medians = df_jobs.groupby("seniority_level")["salary_avg"].transform("median")
    
    overall_median = df_jobs["salary_avg"].median()
    if pd.isna(overall_median):
        overall_median = 800000.0

    combined_medians = medians.fillna(seniority_medians).fillna(overall_median)

    df_jobs["is_salary_imputed"] = df_jobs["salary_avg"].isna()
    df_jobs["salary_imputed"] = df_jobs["salary_avg"].fillna(combined_medians)

    imputed_count = df_jobs["is_salary_imputed"].sum()
    logger.info(f"Imputed missing salaries for {imputed_count} out of {len(df_jobs)} postings.")

    return df_jobs


def clean_and_process_jobs(raw_jobs: List[Dict[str, Any]]) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    cleaned_jobs: List[Dict[str, Any]] = []
    job_skills_records: List[Dict[str, Any]] = []
    seen_dedup_keys: set = set()

    for job in raw_jobs:
        job_id = job.get("id", "")
        title = job.get("title", "").strip()
        company = job.get("company", "").strip()
        location_raw = job.get("location", "").strip()
        description = job.get("description", "")
        remote_status = job.get("remote_status", "Onsite")
        created_date = job.get("created", "")
        redirect_url = job.get("redirect_url", "")

        dedup_key = (title.lower(), company.lower(), location_raw.lower())
        if dedup_key in seen_dedup_keys:
            continue
        seen_dedup_keys.add(dedup_key)

        seniority = parse_seniority(title, description)
        exp_min, exp_max = parse_years_experience(title, description)
        city, state, country = parse_location(location_raw)

        sal_min = job.get("salary_min")
        sal_max = job.get("salary_max")
        sal_min = float(sal_min) if sal_min is not None else None
        sal_max = float(sal_max) if sal_max is not None else None

        if sal_min and sal_max:
            sal_avg = (sal_min + sal_max) / 2.0
        elif sal_min:
            sal_avg = sal_min
        elif sal_max:
            sal_avg = sal_max
        else:
            sal_avg = None

        cleaned_jobs.append({
            "job_id": job_id,
            "title": title,
            "company": company,
            "location_raw": location_raw,
            "city": city,
            "state": state,
            "country": country,
            "remote_status": remote_status,
            "seniority_level": seniority,
            "salary_min": sal_min,
            "salary_max": sal_max,
            "salary_avg": sal_avg,
            "posted_date": created_date,
            "redirect_url": redirect_url,
            "search_term": job.get("search_term", ""),
            "years_exp_min": exp_min,
            "years_exp_max": exp_max
        })

        full_text = f"{title} {description}"
        skills_matched = extract_skills_from_text(full_text)

        for skill_name, category in skills_matched:
            job_skills_records.append({
                "job_id": job_id,
                "skill_name": skill_name,
                "category": category
            })

    df_jobs = pd.DataFrame(cleaned_jobs)
    df_job_skills = pd.DataFrame(job_skills_records)

    df_jobs = impute_salaries(df_jobs)

    master_skills_data = [
        {"skill_name": k, "category": v["category"]} for k, v in SKILL_PATTERNS.items()
    ]
    df_skills_master = pd.DataFrame(master_skills_data)

    return df_jobs, df_job_skills, df_skills_master


def main() -> None:
    logger.info("Starting Data Cleaning Phase...")
    raw_jobs = load_latest_raw_json()
    df_jobs, df_job_skills, df_skills_master = clean_and_process_jobs(raw_jobs)

    jobs_csv_path = config.PROCESSED_DATA_DIR / "jobs_cleaned.csv"
    job_skills_csv_path = config.PROCESSED_DATA_DIR / "job_skills_cleaned.csv"
    skills_master_csv_path = config.PROCESSED_DATA_DIR / "skills_master_cleaned.csv"

    df_jobs.to_csv(jobs_csv_path, index=False)
    df_job_skills.to_csv(job_skills_csv_path, index=False)
    df_skills_master.to_csv(skills_master_csv_path, index=False)

    logger.info("Export complete.")


if __name__ == "__main__":
    main()
```

### 6. `sql/schema.sql`
```sql
-- Schema definition for Data Analyst Job Market Analysis Database
-- Updated with feature engineering: years of experience and salary imputation

CREATE TABLE IF NOT EXISTS jobs (
    job_id VARCHAR(100) PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    company VARCHAR(255),
    location_raw VARCHAR(255),
    city VARCHAR(100),
    state VARCHAR(100),
    country VARCHAR(50),
    remote_status VARCHAR(50),
    seniority_level VARCHAR(50),
    salary_min REAL,
    salary_max REAL,
    salary_avg REAL,
    posted_date VARCHAR(100),
    redirect_url TEXT,
    search_term VARCHAR(100),
    years_exp_min INTEGER,
    years_exp_max INTEGER,
    salary_imputed REAL,
    is_salary_imputed BOOLEAN
);

CREATE TABLE IF NOT EXISTS skills (
    skill_name VARCHAR(100) PRIMARY KEY,
    category VARCHAR(100) NOT NULL
);

CREATE TABLE IF NOT EXISTS posting_skills (
    job_id VARCHAR(100) NOT NULL,
    skill_name VARCHAR(100) NOT NULL,
    PRIMARY KEY (job_id, skill_name),
    FOREIGN KEY (job_id) REFERENCES jobs(job_id) ON DELETE CASCADE,
    FOREIGN KEY (skill_name) REFERENCES skills(skill_name) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_jobs_company ON jobs(company);
CREATE INDEX IF NOT EXISTS idx_jobs_seniority ON jobs(seniority_level);
CREATE INDEX IF NOT EXISTS idx_jobs_remote ON jobs(remote_status);
CREATE INDEX IF NOT EXISTS idx_jobs_city ON jobs(city);
CREATE INDEX IF NOT EXISTS idx_posting_skills_skill ON posting_skills(skill_name);
```

---

## 📊 Analytical SQL Queries

### `sql/queries/01_top_skills.sql`
```sql
-- Business Question 1:
-- Which skills/tools appear most frequently in Data Analyst postings overall?

WITH TotalPostings AS (
    SELECT COUNT(*) AS total_jobs FROM jobs
),
SkillCounts AS (
    SELECT 
        s.skill_name,
        s.category,
        COUNT(DISTINCT ps.job_id) AS posting_count
    FROM skills s
    JOIN posting_skills ps ON s.skill_name = ps.skill_name
    GROUP BY s.skill_name, s.category
)
SELECT 
    sc.skill_name,
    sc.category,
    sc.posting_count,
    ROUND(CAST(sc.posting_count AS REAL) * 100.0 / tp.total_jobs, 2) AS pct_of_total_jobs,
    DENSE_RANK() OVER (ORDER BY sc.posting_count DESC) AS skill_rank
FROM SkillCounts sc
CROSS JOIN TotalPostings tp
ORDER BY sc.posting_count DESC;
```

### `sql/queries/02_skills_by_seniority.sql`
```sql
-- Business Question 2:
-- How does the required skill set differ by seniority level (Entry / Mid / Senior / Lead)?

WITH SeniorityTotals AS (
    SELECT 
        seniority_level,
        COUNT(*) AS total_postings_in_tier
    FROM jobs
    GROUP BY seniority_level
),
SenioritySkillCounts AS (
    SELECT 
        j.seniority_level,
        s.skill_name,
        s.category,
        COUNT(DISTINCT j.job_id) AS skill_count
    FROM jobs j
    JOIN posting_skills ps ON j.job_id = ps.job_id
    JOIN skills s ON ps.skill_name = s.skill_name
    GROUP BY j.seniority_level, s.skill_name, s.category
),
RankedSkills AS (
    SELECT 
        ssc.seniority_level,
        ssc.skill_name,
        ssc.category,
        ssc.skill_count,
        st.total_postings_in_tier,
        ROUND(CAST(ssc.skill_count AS REAL) * 100.0 / st.total_postings_in_tier, 2) AS pct_in_tier,
        RANK() OVER (
            PARTITION BY ssc.seniority_level 
            ORDER BY ssc.skill_count DESC
        ) AS rank_within_tier
    FROM SenioritySkillCounts ssc
    JOIN SeniorityTotals st ON ssc.seniority_level = st.seniority_level
)
SELECT 
    seniority_level,
    rank_within_tier,
    skill_name,
    category,
    skill_count,
    total_postings_in_tier,
    pct_in_tier
FROM RankedSkills
WHERE rank_within_tier <= 10
ORDER BY seniority_level, rank_within_tier;
```

### `sql/queries/05_skill_cooccurrence.sql`
```sql
-- Business Question 5:
-- Which skills tend to co-occur in the same job posting (e.g., SQL + Tableau vs SQL + Python)?

WITH TotalJobs AS (
    SELECT COUNT(*) AS total_postings FROM jobs
),
SkillPairs AS (
    SELECT 
        ps1.skill_name AS skill_a,
        ps2.skill_name AS skill_b,
        COUNT(DISTINCT ps1.job_id) AS pair_frequency
    FROM posting_skills ps1
    JOIN posting_skills ps2 
        ON ps1.job_id = ps2.job_id 
       AND ps1.skill_name < ps2.skill_name
    GROUP BY ps1.skill_name, ps2.skill_name
)
SELECT 
    sp.skill_a,
    sp.skill_b,
    sp.pair_frequency,
    ROUND(CAST(sp.pair_frequency AS REAL) * 100.0 / tj.total_postings, 2) AS pct_of_all_jobs,
    DENSE_RANK() OVER (ORDER BY sp.pair_frequency DESC) AS pair_rank
FROM SkillPairs sp
CROSS JOIN TotalJobs tj
ORDER BY sp.pair_frequency DESC
LIMIT 25;
```

---

## 🟡 Power BI Data Model & DAX Formulas

### Star Schema Relationships
- **`jobs_cleaned`** (`job_id`) `1` ─────── `*` **`job_skills_cleaned`** (`job_id`)
- **`skills_master_cleaned`** (`skill_name`) `1` ─────── `*` **`job_skills_cleaned`** (`skill_name`)

### Key DAX Measures
```dax
// 1. Total Jobs Count
Total Jobs = COUNTROWS('jobs_cleaned')

// 2. Count of Jobs Requesting Selected Skill
Jobs With Skill = DISTINCTCOUNT('job_skills_cleaned'[job_id])

// 3. Skill Market Demand Percentage
Skill Demand Pct = DIVIDE([Jobs With Skill], [Total Jobs], 0)

// 4. Average Offered / Imputed Salary
Average Salary = AVERAGE('jobs_cleaned'[salary_imputed])

// 5. Skill Demand Rank
Skill Rank = RANKX(ALL('skills_master_cleaned'[skill_name]), [Jobs With Skill], , DESC, Dense)
```

---

## 🚀 How to Run the Project

```powershell
# 1. Clone repository & install requirements
git clone https://github.com/your-username/job-market-analysis.git
cd job-market-analysis
pip install -r requirements.txt

# 2. Add API Credentials to .env
# ADZUNA_APP_ID=b1aa4e47
# ADZUNA_APP_KEY=31530c64973bb308411c3c582e6308cf
# COUNTRY=in

# 3. Run Pipeline
python src/collect.py
python src/clean.py
python src/load_db.py

# 4. Refresh Power BI Desktop!
```
