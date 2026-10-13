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
- **Interactive Web App**: Streamlit 1.28+, Altair, Interactive SQL Playground
- **Automated Ingestion**: GitHub Actions CI/CD (`.github/workflows/daily_pipeline.yml`)
- **Cloud Deployment**: Render Cloud Web Service (`render.yaml`)
- **Visualization Layer**: **Microsoft Power BI Desktop** (Star Schema Model + DAX Measures) & **Streamlit Dashboard**

---

## 📂 Repository File Structure

```
job-market-analysis/
├── launch.bat                         # Windows 1-Click Double-Click Launcher
├── run.py                             # Cross-Platform CLI Task Runner (web, pipeline, sql, report)
├── app.py                             # Interactive Streamlit Web Dashboard & SQL Playground
├── render.yaml                        # Cloud Deployment Configuration (Render)
├── README.md                          # Repository Documentation & Setup Guide
├── FULL_PROJECT_PORTFOLIO.md          # Comprehensive Single-File Project Master Document
├── requirements.txt                   # Pinned Python Dependencies
├── .env.example                       # Environment Configuration Template (copy to .env locally)
├── config.py                          # Config Loader & Path Definitions
├── .github/
│   └── workflows/
│       └── daily_pipeline.yml         # GitHub Actions Daily CI/CD Workflow
├── data/
│   ├── raw/                           # Raw Timestamped JSON API Responses
│   ├── processed/                     # Cleaned CSV Datasets (jobs, skills, junction)
│   └── job_market.db                  # SQLite Analytical Database
├── src/
│   ├── __init__.py                    # Source Package Initializer
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
    └── job_market_insights.html       # Standalone Zero-Dependency Interactive HTML Report
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
streamlit>=1.28.0
altair>=5.0.0
```

### 2. `.env.example`
```env
# Copy this file to .env and fill in your own Adzuna credentials.
# Never commit .env — it is gitignored.

ADZUNA_APP_ID=your_app_id_here
ADZUNA_APP_KEY=your_app_key_here

COUNTRY=in
RESULTS_PER_PAGE=50
MAX_PAGES=10

DB_TYPE=sqlite
SQLITE_PATH=data/job_market.db
```

### 3. `config.py`
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

### 4. `src/__init__.py`
```python
"""
Source package for Data Analyst Job Market Analysis.
"""
```

### 5. `src/skills_dictionary.py`
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
        "patterns": [r"\bmachine learning\b", r"\bpredictive modeling\b", r"\bml models?\b", r"\bml algorithms?\b", r"\bpython\s*/\s*ml\b"]
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

### 6. `src/collect.py`
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


def generate_mock_jobs(count: int = 500) -> List[Dict[str, Any]]:
    import random
    logger.info(f"Generating {count} realistic mock job postings for testing...")
    titles = [
        "Data Analyst", "Junior Data Analyst", "Senior Data Analyst", "Lead Data Analyst",
        "Business Intelligence Analyst", "Data Analytics Engineer", "Financial Data Analyst",
        "Healthcare Data Analyst", "Marketing Data Analyst", "Data Scientist",
        "Product Data Analyst", "Operations Data Analyst", "Staff Data Analyst"
    ]
    companies = [
        "Acme Analytics", "TechCorp Global", "FinData Solutions", "HealthPlus Systems",
        "RetailIQ", "CloudScale Media", "BioGen Labs", "Apex Financial"
    ]
    locations = [
        "Bengaluru, Karnataka", "Mumbai, Maharashtra", "Delhi, NCR", "Hyderabad, Telangana",
        "Pune, Maharashtra", "Chennai, Tamil Nadu", "Remote, India"
    ]
    skills_pool = ["SQL", "Python", "R", "Excel", "Tableau", "Power BI", "AWS", "Snowflake", "dbt", "Machine Learning"]

    mock_jobs = []
    for i in range(1, count + 1):
        title = random.choice(titles)
        company = random.choice(companies)
        location = random.choice(locations)
        remote_status = "Remote" if "Remote" in location or random.random() < 0.3 else ("Hybrid" if random.random() < 0.25 else "Onsite")
        req_skills = random.sample(skills_pool, k=random.randint(2, 5))
        exp_years = random.randint(1, 6)
        desc_text = f"We require a {title} at {company} with {exp_years}+ years of experience in {', '.join(req_skills)}. Strong analytical skills needed."
        
        sal_min = random.choice([400000, 600000, 800000, 1200000, 1500000]) if random.random() > 0.3 else None
        sal_max = (sal_min + random.randint(200000, 500000)) if sal_min else None

        mock_jobs.append({
            "id": f"mock-{100000 + i}",
            "title": title,
            "company": company,
            "location": location,
            "remote_status": remote_status,
            "created": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "salary_min": sal_min,
            "salary_max": sal_max,
            "description": desc_text,
            "redirect_url": f"https://example.com/jobs/mock-{100000 + i}",
            "category": "IT Jobs",
            "search_term": title,
            "fetched_at": datetime.utcnow().isoformat()
        })
    return mock_jobs


def main() -> None:
    parser = argparse.ArgumentParser(description="Collect job postings from Adzuna API.")
    parser.add_argument("--mock", action="store_true", help="Generate mock job data for offline testing.")
    parser.add_argument("--count", type=int, default=500, help="Number of mock postings to generate.")
    args = parser.parse_args()

    has_credentials = bool(config.ADZUNA_APP_ID and config.ADZUNA_APP_KEY)

    if args.mock or not has_credentials:
        if not has_credentials and not args.mock:
            logger.warning("No ADZUNA_APP_ID or ADZUNA_APP_KEY found in .env file! Generating mock data.")
        jobs = generate_mock_jobs(count=args.count)
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

### 7. `src/clean.py`
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

try:
    from src.skills_dictionary import extract_skills_from_text, SKILL_PATTERNS
except (ImportError, ModuleNotFoundError):
    from skills_dictionary import extract_skills_from_text, SKILL_PATTERNS

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

### 8. `src/load_db.py`
```python
"""
Database Loader for Data Analyst Job Market Analysis.
Loads cleaned CSV datasets with feature engineered columns into SQLite / PostgreSQL.
"""

import os
import sys
import sqlite3
import logging
from pathlib import Path
from typing import Tuple, Any, Optional
import pandas as pd

sys.path.append(str(os.path.dirname(os.path.dirname(__file__))))
import config

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)


def load_sqlite_db(
    df_jobs: pd.DataFrame,
    df_job_skills: pd.DataFrame,
    df_skills_master: pd.DataFrame,
    db_path: Path = config.SQLITE_PATH,
    schema_path: Path = config.SQL_DIR / "schema.sql"
) -> None:
    """Loads cleaned job data into SQLite database."""
    logger.info(f"Connecting to SQLite database at: {db_path}")
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("DROP TABLE IF EXISTS posting_skills")
    cursor.execute("DROP TABLE IF EXISTS jobs")
    cursor.execute("DROP TABLE IF EXISTS skills")
    conn.commit()

    with open(schema_path, "r", encoding="utf-8") as f:
        schema_sql = f.read()

    cursor.executescript(schema_sql)
    conn.commit()
    logger.info("Database schema applied successfully.")

    skills_records = df_skills_master.to_dict(orient="records")
    cursor.executemany(
        """
        INSERT OR REPLACE INTO skills (skill_name, category)
        VALUES (:skill_name, :category)
        """,
        skills_records
    )

    jobs_records = df_jobs.to_dict(orient="records")
    cursor.executemany(
        """
        INSERT OR REPLACE INTO jobs (
            job_id, title, company, location_raw, city, state, country,
            remote_status, seniority_level, years_exp_min, years_exp_max,
            salary_min, salary_max, salary_avg, salary_imputed, is_salary_imputed,
            posted_date, redirect_url, search_term
        ) VALUES (
            :job_id, :title, :company, :location_raw, :city, :state, :country,
            :remote_status, :seniority_level, :years_exp_min, :years_exp_max,
            :salary_min, :salary_max, :salary_avg, :salary_imputed, :is_salary_imputed,
            :posted_date, :redirect_url, :search_term
        )
        """,
        jobs_records
    )

    valid_job_ids = set(df_jobs["job_id"])
    valid_skills = set(df_skills_master["skill_name"])

    df_filtered_skills = df_job_skills[
        df_job_skills["job_id"].isin(valid_job_ids) & 
        df_job_skills["skill_name"].isin(valid_skills)
    ][["job_id", "skill_name"]].drop_duplicates()

    posting_skills_records = df_filtered_skills.to_dict(orient="records")
    cursor.executemany(
        """
        INSERT OR REPLACE INTO posting_skills (job_id, skill_name)
        VALUES (:job_id, :skill_name)
        """,
        posting_skills_records
    )

    conn.commit()

    cursor.execute("SELECT COUNT(*) FROM jobs")
    job_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM skills")
    skill_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM posting_skills")
    junction_count = cursor.fetchone()[0]

    logger.info("SQLite Load Complete:")
    logger.info(f" - jobs table: {job_count} rows")
    logger.info(f" - skills table: {skill_count} rows")
    logger.info(f" - posting_skills table: {junction_count} rows")

    conn.close()


def load_postgres_db(
    df_jobs: pd.DataFrame,
    df_job_skills: pd.DataFrame,
    df_skills_master: pd.DataFrame,
    schema_path: Path = config.SQL_DIR / "schema.sql"
) -> None:
    """Loads cleaned job data into PostgreSQL database."""
    try:
        import psycopg2
        from psycopg2.extras import execute_batch
    except ImportError:
        logger.error("psycopg2 is not installed. Run 'pip install psycopg2-binary' for PostgreSQL support.")
        return

    logger.info(f"Connecting to PostgreSQL at {config.DB_HOST}:{config.DB_PORT}/{config.DB_NAME} as {config.DB_USER}...")
    try:
        conn = psycopg2.connect(
            host=config.DB_HOST,
            port=config.DB_PORT,
            dbname=config.DB_NAME,
            user=config.DB_USER,
            password=config.DB_PASSWORD
        )
    except Exception as exc:
        logger.error(f"Failed to connect to PostgreSQL: {exc}")
        logger.info("Ensure PostgreSQL is running and credentials in .env are correct.")
        return

    cursor = conn.cursor()

    with open(schema_path, "r", encoding="utf-8") as f:
        schema_sql = f.read()

    cursor.execute("DROP TABLE IF EXISTS posting_skills CASCADE;")
    cursor.execute("DROP TABLE IF EXISTS jobs CASCADE;")
    cursor.execute("DROP TABLE IF EXISTS skills CASCADE;")
    cursor.execute(schema_sql)
    conn.commit()
    logger.info("PostgreSQL schema created successfully.")

    skills_data = [
        (row["skill_name"], row["category"])
        for _, row in df_skills_master.iterrows()
    ]
    execute_batch(
        cursor,
        """
        INSERT INTO skills (skill_name, category)
        VALUES (%s, %s)
        ON CONFLICT (skill_name) DO UPDATE SET category = EXCLUDED.category;
        """,
        skills_data
    )

    jobs_cols = [
        "job_id", "title", "company", "location_raw", "city", "state", "country",
        "remote_status", "seniority_level", "years_exp_min", "years_exp_max",
        "salary_min", "salary_max", "salary_avg", "salary_imputed", "is_salary_imputed",
        "posted_date", "redirect_url", "search_term"
    ]
    df_jobs_clean = df_jobs.where(pd.notnull(df_jobs), None)
    jobs_data = [tuple(row[col] for col in jobs_cols) for _, row in df_jobs_clean.iterrows()]

    execute_batch(
        cursor,
        """
        INSERT INTO jobs (
            job_id, title, company, location_raw, city, state, country,
            remote_status, seniority_level, years_exp_min, years_exp_max,
            salary_min, salary_max, salary_avg, salary_imputed, is_salary_imputed,
            posted_date, redirect_url, search_term
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (job_id) DO NOTHING;
        """,
        jobs_data
    )

    valid_job_ids = set(df_jobs["job_id"])
    valid_skills = set(df_skills_master["skill_name"])
    df_filtered_skills = df_job_skills[
        df_job_skills["job_id"].isin(valid_job_ids) &
        df_job_skills["skill_name"].isin(valid_skills)
    ][["job_id", "skill_name"]].drop_duplicates()

    ps_data = [(row["job_id"], row["skill_name"]) for _, row in df_filtered_skills.iterrows()]
    execute_batch(
        cursor,
        """
        INSERT INTO posting_skills (job_id, skill_name)
        VALUES (%s, %s)
        ON CONFLICT (job_id, skill_name) DO NOTHING;
        """,
        ps_data
    )

    conn.commit()

    cursor.execute("SELECT COUNT(*) FROM jobs;")
    job_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM skills;")
    skill_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM posting_skills;")
    junction_count = cursor.fetchone()[0]

    logger.info("PostgreSQL Load Complete:")
    logger.info(f" - jobs table: {job_count} rows")
    logger.info(f" - skills table: {skill_count} rows")
    logger.info(f" - posting_skills table: {junction_count} rows")

    cursor.close()
    conn.close()


def main() -> None:
    jobs_csv = config.PROCESSED_DATA_DIR / "jobs_cleaned.csv"
    job_skills_csv = config.PROCESSED_DATA_DIR / "job_skills_cleaned.csv"
    skills_master_csv = config.PROCESSED_DATA_DIR / "skills_master_cleaned.csv"

    if not jobs_csv.exists() or not job_skills_csv.exists():
        logger.error("Processed CSV files not found. Run clean.py first.")
        sys.exit(1)

    logger.info("Loading processed CSV datasets...")
    df_jobs = pd.read_csv(jobs_csv)
    df_job_skills = pd.read_csv(job_skills_csv)
    df_skills_master = pd.read_csv(skills_master_csv)

    if config.DB_TYPE in ("postgres", "postgresql"):
        load_postgres_db(df_jobs, df_job_skills, df_skills_master)
    else:
        load_sqlite_db(df_jobs, df_job_skills, df_skills_master)


if __name__ == "__main__":
    main()
```

### 9. `app.py`
```python
"""
Data Analyst Job Market Analysis - Interactive Web App & Portfolio Explorer
Run with: streamlit run app.py
"""

import os
import sys
import sqlite3
import subprocess
from pathlib import Path
import pandas as pd
import streamlit as st

import altair as alt

# Set page config
st.set_page_config(
    page_title="Data Analyst Job Market Intelligence",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Base Path
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "data" / "job_market.db"
QUERIES_DIR = BASE_DIR / "sql" / "queries"

# Custom Styling (Dark Glassmorphism Theme)
st.markdown("""
<style>
    .main {
        background-color: #0f172a;
        color: #f8fafc;
    }
    .stMetric {
        background: rgba(30, 41, 59, 0.7);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 15px;
        border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    .metric-card {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
    }
    .metric-value {
        font-size: 2.2rem;
        font-weight: 700;
        color: #38bdf8;
    }
    .metric-label {
        font-size: 0.9rem;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .badge {
        background-color: #0284c7;
        color: white;
        padding: 4px 8px;
        border-radius: 6px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    div.stButton > button {
        background: linear-gradient(135deg, #0284c7 0%, #2563eb 100%);
        color: white;
        border: none;
        padding: 10px 24px;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    div.stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(2, 132, 199, 0.4);
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data(ttl=600)
def run_sql_query(query: str, params=None) -> pd.DataFrame:
    if not DB_PATH.exists():
        st.error(f"Database not found at `{DB_PATH}`. Please run data pipeline first.")
        return pd.DataFrame()
    conn = sqlite3.connect(DB_PATH)
    try:
        df = pd.read_sql_query(query, conn, params=params)
        return df
    finally:
        conn.close()


def get_db_summary():
    if not DB_PATH.exists():
        return 0, 0, 0, 0
    total_jobs = run_sql_query("SELECT COUNT(*) as c FROM jobs")['c'].iloc[0]
    total_skills = run_sql_query("SELECT COUNT(*) as c FROM skills")['c'].iloc[0]
    avg_salary = run_sql_query("SELECT AVG(salary_imputed) as c FROM jobs")['c'].iloc[0]
    top_skill = run_sql_query("""
        SELECT skill_name, COUNT(*) as cnt 
        FROM posting_skills 
        GROUP BY skill_name ORDER BY cnt DESC LIMIT 1
    """)
    top_skill_name = top_skill['skill_name'].iloc[0] if not top_skill.empty else "N/A"
    return total_jobs, total_skills, avg_salary, top_skill_name


# Header & Banner
st.title("📊 Data Analyst Job Market Intelligence")
st.markdown("##### *Live Data Engineering, SQL Analytics, & Interactive Market Dashboard Portfolio*")
st.markdown("---")

# Sidebar Controls
st.sidebar.title("📌 Navigation & Controls")
nav_option = st.sidebar.radio(
    "Explore Dashboard",
    [
        "🏆 Executive Overview",
        "🎯 Skill Demand Explorer",
        "💰 Salary Benchmarks",
        "🗺️ Hiring Hubs & Companies",
        "🔍 Job Postings Search",
        "⚡ Interactive SQL Playground",
        "🔄 Data Pipeline Runner"
    ]
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 💼 Candidate Portfolio")
st.sidebar.info("""
**Target Role**: Data Analyst / BI Analyst  
**Tech Stack**: Python, SQL, SQLite, Pandas, Streamlit, Power BI  
**Data Source**: Adzuna REST API (India Tech Market)
""")

# Top Level Summary Cards
total_jobs, total_skills, avg_salary, top_skill = get_db_summary()

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Total Job Postings</div>
        <div class="metric-value">{total_jobs:,}</div>
    </div>
    """, unsafe_allow_html=True)
with col2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Skills Tracked</div>
        <div class="metric-value">{total_skills}</div>
    </div>
    """, unsafe_allow_html=True)
with col3:
    formatted_sal = f"₹{avg_salary/100000:.2f} L" if avg_salary else "N/A"
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Avg Salary Benchmark</div>
        <div class="metric-value">{formatted_sal}</div>
    </div>
    """, unsafe_allow_html=True)
with col4:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">#1 In-Demand Skill</div>
        <div class="metric-value">{top_skill}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# NAV 1: EXECUTIVE OVERVIEW
if nav_option == "🏆 Executive Overview":
    st.subheader("💡 Executive Insights Summary")
    st.write("""
    This project provides real-world market intelligence on what employers require from Data Analysts.
    By parsing job descriptions across top tech hiring hubs, we extract hard skills, seniority tier requirements,
    and compensation benchmarks.
    """)
    
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.markdown("### 🔝 Top 10 Technical Skills")
        q1_df = run_sql_query("""
            SELECT 
                s.skill_name AS Skill,
                s.category AS Category,
                COUNT(ps.job_id) AS Postings,
                ROUND(COUNT(ps.job_id) * 100.0 / (SELECT COUNT(*) FROM jobs), 1) AS Market_Pct
            FROM skills s
            JOIN posting_skills ps ON s.skill_name = ps.skill_name
            GROUP BY s.skill_name, s.category
            ORDER BY Postings DESC
            LIMIT 10
        """)
        st.dataframe(q1_df, use_container_width=True)
        skill_chart = alt.Chart(q1_df).mark_bar(cornerRadiusTopRight=5, cornerRadiusBottomRight=5).encode(
            x=alt.X('Postings:Q', title='Job Postings'),
            y=alt.Y('Skill:N', sort='-x', title='Skill'),
            color=alt.Color('Category:N', legend=alt.Legend(title="Category")),
            tooltip=['Skill', 'Category', 'Postings', 'Market_Pct']
        ).properties(height=320)
        st.altair_chart(skill_chart, use_container_width=True)
        
    with col_b:
        st.markdown("### 🏢 Seniority Tier Distribution")
        sen_df = run_sql_query("""
            SELECT seniority_level AS Seniority, COUNT(*) AS Postings
            FROM jobs
            GROUP BY seniority_level
            ORDER BY Postings DESC
        """)
        st.dataframe(sen_df, use_container_width=True)
        sen_chart = alt.Chart(sen_df).mark_bar(cornerRadiusTopLeft=5, cornerRadiusTopRight=5).encode(
            x=alt.X('Seniority:N', sort='-y', title='Seniority Tier'),
            y=alt.Y('Postings:Q', title='Job Postings'),
            color=alt.value('#38bdf8'),
            tooltip=['Seniority', 'Postings']
        ).properties(height=320)
        st.altair_chart(sen_chart, use_container_width=True)


# NAV 2: SKILL DEMAND EXPLORER
elif nav_option == "🎯 Skill Demand Explorer":
    st.subheader("🎯 Skill Demand & Co-occurrence Matrix")
    
    categories = run_sql_query("SELECT DISTINCT category FROM skills")['category'].tolist()
    selected_cat = st.multiselect("Filter by Skill Category", options=categories, default=categories)
    
    if selected_cat:
        cat_str = "', '".join(selected_cat)
        skills_df = run_sql_query(f"""
            SELECT 
                s.skill_name AS Skill,
                s.category AS Category,
                COUNT(ps.job_id) AS Postings,
                ROUND(COUNT(ps.job_id) * 100.0 / (SELECT COUNT(*) FROM jobs), 2) AS Market_Share_Pct
            FROM skills s
            JOIN posting_skills ps ON s.skill_name = ps.skill_name
            WHERE s.category IN ('{cat_str}')
            GROUP BY s.skill_name, s.category
            ORDER BY Postings DESC
        """)
        st.dataframe(skills_df, use_container_width=True)
    
    st.markdown("---")
    st.subheader("🔗 Most Frequently Paired Tech Skills (Co-occurrence)")
    co_df = run_sql_query("""
        WITH SkillPairs AS (
            SELECT 
                ps1.skill_name AS Skill_A,
                ps2.skill_name AS Skill_B,
                COUNT(DISTINCT ps1.job_id) AS Pair_Frequency
            FROM posting_skills ps1
            JOIN posting_skills ps2 
                ON ps1.job_id = ps2.job_id 
               AND ps1.skill_name < ps2.skill_name
            GROUP BY ps1.skill_name, ps2.skill_name
        )
        SELECT Skill_A, Skill_B, Pair_Frequency
        FROM SkillPairs
        ORDER BY Pair_Frequency DESC
        LIMIT 15
    """)
    st.dataframe(co_df, use_container_width=True)


# NAV 3: SALARY BENCHMARKS
elif nav_option == "💰 Salary Benchmarks":
    st.subheader("💰 Compensation Breakdown (INR)")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### Salary by Remote Work Mode")
        sal_remote = run_sql_query("""
            SELECT 
                remote_status AS Work_Mode,
                COUNT(*) AS Postings,
                ROUND(AVG(salary_imputed), 2) AS Avg_Salary_INR,
                ROUND(MIN(salary_imputed), 2) AS Min_Salary_INR,
                ROUND(MAX(salary_imputed), 2) AS Max_Salary_INR
            FROM jobs
            GROUP BY remote_status
            ORDER BY Avg_Salary_INR DESC
        """)
        st.dataframe(sal_remote, use_container_width=True)
        st.bar_chart(sal_remote.set_index("Work_Mode")["Avg_Salary_INR"])
        
    with col2:
        st.markdown("### Salary by Seniority Tier")
        sal_sen = run_sql_query("""
            SELECT 
                seniority_level AS Seniority,
                COUNT(*) AS Postings,
                ROUND(AVG(salary_imputed), 2) AS Avg_Salary_INR
            FROM jobs
            GROUP BY seniority_level
            ORDER BY Avg_Salary_INR DESC
        """)
        st.dataframe(sal_sen, use_container_width=True)
        st.bar_chart(sal_sen.set_index("Seniority")["Avg_Salary_INR"])


# NAV 4: HIRING HUBS & COMPANIES
elif nav_option == "🗺️ Hiring Hubs & Companies":
    st.subheader("🗺️ Active Hiring Hubs in Tech")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### Top Cities for Data Analyst Jobs")
        city_df = run_sql_query("""
            SELECT 
                city AS City,
                state AS State,
                COUNT(*) AS Postings,
                ROUND(AVG(salary_imputed), 2) AS Avg_Salary
            FROM jobs
            WHERE city IS NOT NULL AND city != 'Unspecified'
            GROUP BY city, state
            ORDER BY Postings DESC
            LIMIT 15
        """)
        st.dataframe(city_df, use_container_width=True)
        st.bar_chart(city_df.set_index("City")["Postings"])
        
    with col2:
        st.markdown("### Top Recruiting Companies")
        comp_df = run_sql_query("""
            SELECT 
                company AS Company,
                COUNT(*) AS Active_Postings,
                remote_status AS Remote_Preference
            FROM jobs
            WHERE company IS NOT NULL AND company != 'Unknown'
            GROUP BY company
            ORDER BY Active_Postings DESC
            LIMIT 15
        """)
        st.dataframe(comp_df, use_container_width=True)


# NAV 5: JOB POSTINGS SEARCH
elif nav_option == "🔍 Job Postings Search":
    st.subheader("🔍 Live Job Search & Filter Engine")
    
    keyword = st.text_input("Search Job Title or Company", "")
    all_skills = run_sql_query("SELECT DISTINCT skill_name FROM skills")['skill_name'].tolist()
    selected_skill = st.selectbox("Filter by Skill", ["All"] + sorted(all_skills))
    
    query = """
        SELECT DISTINCT j.job_id, j.title, j.company, j.city, j.remote_status, j.seniority_level, j.salary_imputed, j.redirect_url
        FROM jobs j
        LEFT JOIN posting_skills ps ON j.job_id = ps.job_id
        WHERE 1=1
    """
    params = []
    if keyword:
        query += " AND (j.title LIKE ? OR j.company LIKE ?)"
        params.extend([f"%{keyword}%", f"%{keyword}%"])
    if selected_skill != "All":
        query += " AND ps.skill_name = ?"
        params.append(selected_skill)
        
    query += " ORDER BY j.job_id DESC LIMIT 50"
    
    results = run_sql_query(query, params)
    st.markdown(f"**Found {len(results)} Matching Postings:**")
    st.dataframe(results, use_container_width=True)


# NAV 6: INTERACTIVE SQL PLAYGROUND
elif nav_option == "⚡ Interactive SQL Playground":
    st.subheader("⚡ SQL Query Sandbox & Gallery")
    st.write("Test ANSI SQL queries directly against `job_market.db` SQLite database.")
    
    preloaded_queries = {
        "1. Overall Skill Demand": "01_top_skills.sql",
        "2. Skills by Seniority": "02_skills_by_seniority.sql",
        "3. Salary Benchmarks": "03_salary_trends.sql",
        "4. Top Cities & Companies": "04_top_hiring_locations_companies.sql",
        "5. Skill Co-occurrence Matrix": "05_skill_cooccurrence.sql",
        "6. Posting Volume Overview": "06_posting_volume_over_time.sql"
    }
    
    selected_preset = st.selectbox("Load Preset Business Query:", ["Custom SQL"] + list(preloaded_queries.keys()))
    
    default_sql = "SELECT * FROM jobs LIMIT 10;"
    if selected_preset != "Custom SQL":
        sql_filename = preloaded_queries[selected_preset]
        sql_file_path = QUERIES_DIR / sql_filename
        if sql_file_path.exists():
            with open(sql_file_path, "r", encoding="utf-8") as f:
                default_sql = f.read()
                
    sql_input = st.text_area("SQL Editor", value=default_sql, height=220)
    
    if st.button("Execute SQL Query"):
        try:
            df_result = run_sql_query(sql_input)
            st.success(f"Executed successfully. Returned {len(df_result)} rows.")
            st.dataframe(df_result, use_container_width=True)
            
            # Export CSV Option
            csv = df_result.to_csv(index=False).encode('utf-8')
            st.download_button(
                "📥 Download Results as CSV",
                csv,
                "sql_query_result.csv",
                "text/csv",
                key='download-csv'
            )
        except Exception as e:
            st.error(f"SQL Execution Error: {e}")


# NAV 7: DATA PIPELINE RUNNER
elif nav_option == "🔄 Data Pipeline Runner":
    st.subheader("🔄 Live Data Pipeline Controller")
    st.write("Trigger data collection, regex skill extraction, feature engineering, and database refresh.")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("1️⃣ Run Data Collector"):
            with st.spinner("Fetching job postings from Adzuna / Mock API..."):
                res = subprocess.run([sys.executable, str(BASE_DIR / "src" / "collect.py")], capture_output=True, text=True)
                st.code(res.stdout or res.stderr)
                st.success("Data collection completed.")
                
    with col2:
        if st.button("2️⃣ Run Data Cleaner"):
            with st.spinner("Cleaning & parsing skills..."):
                res = subprocess.run([sys.executable, str(BASE_DIR / "src" / "clean.py")], capture_output=True, text=True)
                st.code(res.stdout or res.stderr)
                st.success("Data cleaning completed.")
                
    with col3:
        if st.button("3️⃣ Reload Database"):
            with st.spinner("Refreshing SQLite database..."):
                res = subprocess.run([sys.executable, str(BASE_DIR / "src" / "load_db.py")], capture_output=True, text=True)
                st.code(res.stdout or res.stderr)
                st.success("Database reloaded successfully.")

# Footer
st.markdown("---")
st.markdown("💡 *Built by Data Analyst Graduate | Designed for Seamless Recruitment Review*")
```

### 10. `run.py`
```python
"""
One-Click Launcher & Task Manager for Data Analyst Job Market Analysis.
Provides quick access to web dashboard, data pipeline, SQL queries, and static HTML reports.

Usage:
    python run.py              -> Launch Web Dashboard
    python run.py web          -> Launch Interactive Web Dashboard
    python run.py pipeline     -> Run Full Data Pipeline (Collect -> Clean -> Load DB)
    python run.py sql          -> Execute Analytical SQL Queries in Terminal
    python run.py report       -> Generate Standalone Interactive HTML Insights Report
"""

import os
import sys
import sqlite3
import subprocess
from pathlib import Path

# Force UTF-8 encoding on Windows console
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "data" / "job_market.db"
QUERIES_DIR = BASE_DIR / "sql" / "queries"
OUTPUTS_DIR = BASE_DIR / "outputs"



def launch_web_dashboard():
    """Launch Streamlit web application."""
    print("🚀 Launching Data Analyst Job Market Interactive Web Dashboard...")
    app_path = BASE_DIR / "app.py"
    try:
        subprocess.run([sys.executable, "-m", "streamlit", "run", str(app_path)], check=True)
    except KeyboardInterrupt:
        print("\n👋 Web Dashboard stopped.")
    except Exception as e:
        print(f"❌ Error launching Streamlit dashboard: {e}")


def run_full_pipeline():
    """Run data ingestion, cleaning, and DB loading."""
    print("🔄 Executing Full Data Pipeline...")
    scripts = [
        BASE_DIR / "src" / "collect.py",
        BASE_DIR / "src" / "clean.py",
        BASE_DIR / "src" / "load_db.py"
    ]
    for script in scripts:
        print(f"\n▶️ Running {script.name}...")
        res = subprocess.run([sys.executable, str(script)], check=False)
        if res.returncode != 0:
            print(f"❌ Pipeline stopped at {script.name} due to error.")
            return
    print("\n✅ Data pipeline execution complete! Database is updated.")


def execute_sql_queries():
    """Run all analytical SQL queries and print formatted results."""
    if not DB_PATH.exists():
        print(f"❌ Database file not found at {DB_PATH}. Running pipeline first...")
        run_full_pipeline()

    print("\n📊 Executing Analytical SQL Queries on SQLite Database...\n" + "=" * 60)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    query_files = sorted(list(QUERIES_DIR.glob("*.sql")))
    if not query_files:
        print("No SQL query files found in sql/queries/")
        return

    for qfile in query_files:
        print(f"\n📂 Query: {qfile.name}")
        print("-" * 50)
        with open(qfile, "r", encoding="utf-8") as f:
            sql = f.read()

        try:
            cursor.execute(sql)
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            print(" | ".join(columns))
            print("-" * 50)
            for row in rows[:10]:  # Limit output preview
                print(" | ".join(str(val) for val in row))
            if len(rows) > 10:
                print(f"... ({len(rows) - 10} more rows)")
        except Exception as e:
            print(f"❌ Error executing {qfile.name}: {e}")

    conn.close()
    print("\n✅ SQL Queries executed successfully.")


def generate_html_report():
    """Generate a standalone zero-dependency interactive HTML report in outputs/."""
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    report_path = OUTPUTS_DIR / "job_market_insights.html"
    
    if not DB_PATH.exists():
        print(f"❌ Database file not found at {DB_PATH}. Running pipeline first...")
        run_full_pipeline()

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM jobs")
    total_jobs = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM skills")
    total_skills = cursor.fetchone()[0]
    
    cursor.execute("SELECT AVG(salary_imputed) FROM jobs")
    avg_sal = cursor.fetchone()[0] or 0
    
    cursor.execute("""
        SELECT s.skill_name, s.category, COUNT(ps.job_id) as cnt
        FROM skills s JOIN posting_skills ps ON s.skill_name = ps.skill_name
        GROUP BY s.skill_name, s.category ORDER BY cnt DESC LIMIT 10
    """)
    top_skills = cursor.fetchall()
    
    cursor.execute("""
        SELECT city, COUNT(*) as cnt, AVG(salary_imputed) as avg_sal
        FROM jobs WHERE city IS NOT NULL AND city != 'Unspecified'
        GROUP BY city ORDER BY cnt DESC LIMIT 10
    """)
    top_cities = cursor.fetchall()

    conn.close()

    skill_labels = [row[0] for row in top_skills]
    skill_counts = [row[2] for row in top_skills]
    
    city_labels = [row[0] for row in top_cities]
    city_counts = [row[1] for row in top_cities]

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Data Analyst Job Market Insights - Portfolio Report</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        :root {{
            --bg-color: #0f172a;
            --card-bg: #1e293b;
            --text-color: #f8fafc;
            --accent-color: #38bdf8;
            --border-color: #334155;
        }}
        body {{
            font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            background-color: var(--bg-color);
            color: var(--text-color);
            margin: 0;
            padding: 30px;
        }}
        .header {{
            text-align: center;
            margin-bottom: 40px;
        }}
        .header h1 {{
            color: var(--accent-color);
            margin-bottom: 8px;
            font-size: 2.5rem;
        }}
        .header p {{
            color: #94a3b8;
            font-size: 1.1rem;
        }}
        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }}
        .card {{
            background: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 24px;
            text-align: center;
            box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
        }}
        .card-value {{
            font-size: 2.5rem;
            font-weight: bold;
            color: var(--accent-color);
            margin-top: 10px;
        }}
        .card-label {{
            color: #94a3b8;
            text-transform: uppercase;
            font-size: 0.85rem;
            letter-spacing: 0.05em;
        }}
        .chart-container {{
            background: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 24px;
            margin-bottom: 30px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }}
        th, td {{
            padding: 12px 16px;
            text-align: left;
            border-bottom: 1px solid var(--border-color);
        }}
        th {{
            background-color: #0284c7;
            color: white;
        }}
        tr:hover {{
            background-color: #334155;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>📊 Data Analyst Job Market Analysis</h1>
        <p>Interactive Market Intelligence Report & Key Portfolio Findings</p>
    </div>

    <div class="grid">
        <div class="card">
            <div class="card-label">Total Job Postings Analyzed</div>
            <div class="card-value">{total_jobs:,}</div>
        </div>
        <div class="card">
            <div class="card-label">Skills Tracked</div>
            <div class="card-value">{total_skills}</div>
        </div>
        <div class="card">
            <div class="card-label">Average Benchmark Salary</div>
            <div class="card-value">₹{avg_sal/100000:.2f} Lakhs</div>
        </div>
        <div class="card">
            <div class="card-label">Top Hiring Hub</div>
            <div class="card-value">{top_cities[0][0] if top_cities else 'Bengaluru'}</div>
        </div>
    </div>

    <div class="chart-container">
        <h2>🔥 Top 10 Technical Skills Requested by Employers</h2>
        <canvas id="skillsChart" height="100"></canvas>
    </div>

    <div class="chart-container">
        <h2>🏙️ Top Hiring Hub Cities in India</h2>
        <canvas id="citiesChart" height="100"></canvas>
    </div>

    <div class="chart-container">
        <h2>📋 Technical Skill Demand Table</h2>
        <table>
            <thead>
                <tr>
                    <th>Skill Name</th>
                    <th>Category</th>
                    <th>Job Postings Count</th>
                    <th>Market Demand %</th>
                </tr>
            </thead>
            <tbody>
                {''.join([f"<tr><td><strong>{s[0]}</strong></td><td>{s[1]}</td><td>{s[2]}</td><td>{s[2]*100.0/total_jobs:.1f}%</td></tr>" for s in top_skills])}
            </tbody>
        </table>
    </div>

    <script>
        const ctxSkills = document.getElementById('skillsChart').getContext('2d');
        new Chart(ctxSkills, {{
            type: 'bar',
            data: {{
                labels: {skill_labels},
                datasets: [{{
                    label: 'Job Postings Count',
                    data: {skill_counts},
                    backgroundColor: 'rgba(56, 189, 248, 0.7)',
                    borderColor: 'rgba(56, 189, 248, 1)',
                    borderWidth: 1
                }}]
            }},
            options: {{
                responsive: true,
                scales: {{
                    y: {{ beginAtZero: true, grid: {{ color: '#334155' }} }},
                    x: {{ grid: {{ color: '#334155' }} }}
                }},
                plugins: {{ legend: {{ labels: {{ color: '#f8fafc' }} }} }}
            }}
        }});

        const ctxCities = document.getElementById('citiesChart').getContext('2d');
        new Chart(ctxCities, {{
            type: 'bar',
            data: {{
                labels: {city_labels},
                datasets: [{{
                    label: 'Postings Count',
                    data: {city_counts},
                    backgroundColor: 'rgba(168, 85, 247, 0.7)',
                    borderColor: 'rgba(168, 85, 247, 1)',
                    borderWidth: 1
                }}]
            }},
            options: {{
                responsive: true,
                scales: {{
                    y: {{ beginAtZero: true, grid: {{ color: '#334155' }} }},
                    x: {{ grid: {{ color: '#334155' }} }}
                }},
                plugins: {{ legend: {{ labels: {{ color: '#f8fafc' }} }} }}
            }}
        }});
    </script>
</body>
</html>
"""
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(html_content)
        
    print(f"✅ Static HTML Report successfully generated at: {report_path}")
    print("👉 Open this file directly in any web browser to view the interactive report!")


def print_help():
    print("""
===================================================================
🌟 Data Analyst Job Market Analysis - Quick Access CLI
===================================================================
Commands:
  python run.py web        Launch Interactive Streamlit Web Dashboard
  python run.py pipeline   Run Full Pipeline (Collect -> Clean -> Load DB)
  python run.py sql        Execute Analytical SQL Queries in Terminal
  python run.py report     Generate Zero-Dependency HTML Insights Report
===================================================================
""")


def main():
    arg = sys.argv[1].lower() if len(sys.argv) > 1 else "web"
    
    if arg in ["web", "app", "dashboard"]:
        launch_web_dashboard()
    elif arg in ["pipeline", "data", "run"]:
        run_full_pipeline()
    elif arg in ["sql", "queries"]:
        execute_sql_queries()
    elif arg in ["report", "html"]:
        generate_html_report()
    elif arg in ["help", "-h", "--help"]:
        print_help()
    else:
        print(f"Unknown command: '{arg}'")
        print_help()


if __name__ == "__main__":
    main()
```

### 11. `launch.bat`
```bat
@echo off
TITLE Data Analyst Job Market Analysis - Launcher
echo ===================================================================
echo 🚀 Launching Data Analyst Job Market Interactive Dashboard...
echo ===================================================================
echo.
cd /d "%~dp0"

python -c "import streamlit" >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️  Streamlit is not installed. Installing required dependencies...
    pip install -r requirements.txt streamlit pandas
)

echo Starting Web Dashboard on http://localhost:8501 ...
python run.py web

pause
```

### 12. `render.yaml`
```yaml
services:
  - type: web
    name: job-market-analysis
    env: python
    plan: free
    buildCommand: "pip install -r requirements.txt"
    startCommand: "streamlit run app.py --server.port $PORT --server.address 0.0.0.0"
    envVars:
      - key: ADZUNA_APP_ID
        sync: false
      - key: ADZUNA_APP_KEY
        sync: false
      - key: COUNTRY
        value: in
      - key: RESULTS_PER_PAGE
        value: "50"
      - key: MAX_PAGES
        value: "10"
      - key: DB_TYPE
        value: sqlite
      - key: SQLITE_PATH
        value: data/job_market.db
```

### 13. `.github/workflows/daily_pipeline.yml`
```yaml
name: Daily Job Market Data Pipeline

on:
  schedule:
    # Run daily at 00:00 UTC
    - cron: '0 0 * * *'
  workflow_dispatch: # Allows manual trigger from GitHub UI

jobs:
  run-pipeline:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout Repository
        uses: actions/checkout@v3

      - name: Set up Python 3.11
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
          cache: 'pip'

      - name: Install Dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt

      - name: Run Data Collector
        env:
          ADZUNA_APP_ID: ${{ secrets.ADZUNA_APP_ID }}
          ADZUNA_APP_KEY: ${{ secrets.ADZUNA_APP_KEY }}
          COUNTRY: 'in'
        run: python src/collect.py

      - name: Run Data Cleaner & Skill Extractor
        run: python src/clean.py

      - name: Load Database
        run: python src/load_db.py

      - name: Commit & Push Updated Data
        run: |
          git config --global user.name 'github-actions[bot]'
          git config --global user.email 'github-actions[bot]@users.noreply.github.com'
          git add data/processed/ data/job_market.db
          git diff --quiet && git diff --staged --quiet || git commit -m "auto: Daily job market data ingestion [skip ci]"
          git push
```

### 14. `sql/schema.sql`
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

### `sql/queries/03_salary_trends.sql`
```sql
-- Business Question 3:
-- What are the compensation benchmarks across Remote vs Onsite roles, Seniority Tiers, and Hiring Locations?

SELECT 
    remote_status,
    COALESCE(city, 'Unspecified') AS city,
    seniority_level,
    COUNT(*) AS posting_count,
    ROUND(AVG(salary_imputed), 2) AS avg_salary_inr,
    ROUND(MIN(salary_imputed), 2) AS min_salary_inr,
    ROUND(MAX(salary_imputed), 2) AS max_salary_inr
FROM jobs
WHERE city IS NOT NULL AND city != 'Unspecified'
GROUP BY remote_status, city, seniority_level
HAVING COUNT(*) >= 3
ORDER BY posting_count DESC, avg_salary_inr DESC;
```

### `sql/queries/04_top_hiring_locations_companies.sql`
```sql
-- Business Question 4:
-- Which cities and companies have the highest posting volume for Data Analysts?

WITH TopCities AS (
    SELECT 
        'City' AS entity_type,
        city || ', ' || COALESCE(state, 'India') AS entity_name,
        COUNT(*) AS total_postings,
        ROUND(AVG(salary_imputed), 2) AS avg_salary_inr,
        DENSE_RANK() OVER (ORDER BY COUNT(*) DESC) AS ranking
    FROM jobs
    WHERE city IS NOT NULL AND city != 'Unspecified'
    GROUP BY city, state
),
TopCompanies AS (
    SELECT 
        'Company' AS entity_type,
        company AS entity_name,
        COUNT(*) AS total_postings,
        ROUND(AVG(salary_imputed), 2) AS avg_salary_inr,
        DENSE_RANK() OVER (ORDER BY COUNT(*) DESC) AS ranking
    FROM jobs
    WHERE company IS NOT NULL AND company != 'Unknown'
    GROUP BY company
)
SELECT entity_type, ranking, entity_name, total_postings, avg_salary_inr
FROM TopCities
WHERE ranking <= 10
UNION ALL
SELECT entity_type, ranking, entity_name, total_postings, avg_salary_inr
FROM TopCompanies
WHERE ranking <= 10
ORDER BY entity_type DESC, ranking ASC;
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

### `sql/queries/06_posting_volume_over_time.sql`
```sql
-- Business Question 6:
-- What is the posting volume trend over time, comparing daily volumes with previous periods (LAG) and moving averages?

WITH DailyPostings AS (
    SELECT 
        SUBSTR(posted_date, 1, 10) AS posting_date,
        COUNT(*) AS daily_volume
    FROM jobs
    WHERE posted_date IS NOT NULL AND posted_date != ''
    GROUP BY SUBSTR(posted_date, 1, 10)
),
VolumeWithTrends AS (
    SELECT 
        posting_date,
        daily_volume,
        LAG(daily_volume, 1) OVER (ORDER BY posting_date) AS prev_day_volume,
        daily_volume - LAG(daily_volume, 1, daily_volume) OVER (ORDER BY posting_date) AS day_over_day_change,
        ROUND(AVG(daily_volume) OVER (
            ORDER BY posting_date 
            ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
        ), 2) AS moving_avg_7d
    FROM DailyPostings
)
SELECT 
    posting_date,
    daily_volume,
    prev_day_volume,
    day_over_day_change,
    moving_avg_7d
FROM VolumeWithTrends
ORDER BY posting_date DESC
LIMIT 30;
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

## ⚠️ Known Limitations & API Constraints

1. **Adzuna Free-Tier Rate Limits & Data Caps**:
   - The public Adzuna API developer account is capped at **25 to 50 calls/minute** and **250 to 500 calls/day**.
   - Paginating beyond 10-15 pages per search term or running parallel ingestion can trigger HTTP 429 (`Rate Limit Exceeded`).
   - The pipeline implements exponential backoff (`time.sleep`) and automatic fallback to realistic synthetic mock data (`--mock`) when credentials are unset or limits are exhausted.

2. **Salary Reporting Sparsity in Job Ads**:
   - Only approximately **25%–30%** of live employer postings in the Indian tech ecosystem disclose base compensation upfront.
   - To prevent skewed visualizations and maintain statistical integrity, the pipeline implements domain-specific median imputation partitioned by `seniority_level` and `remote_status`, with boolean tracking (`is_salary_imputed`).

3. **Free-Tier Cloud Inactivity Spin-Down**:
   - The live web application hosted on Render free tier spins down into sleep mode after 15 minutes of inactivity. First visits may take 30–45 seconds while the container initializes.

---

## 🚀 How to Run the Project

### ⚡ 1-Click Quick Access (3 Ways to View)

#### 1️⃣ Option A: Double-Click Launcher (Windows)
Double-click [`launch.bat`](launch.bat) in the project folder to open the interactive dashboard in your browser.

#### 2️⃣ Option B: Python CLI Runner (`run.py`)
```powershell
# Launch interactive Streamlit Web Dashboard
python run.py web

# Execute all 6 Analytical SQL Queries in terminal
python run.py sql

# Run the complete data ingestion & cleaning pipeline
python run.py pipeline

# Generate standalone zero-dependency HTML report
python run.py report
```

#### 3️⃣ Option C: Zero-Dependency Interactive HTML Report
Open [`outputs/job_market_insights.html`](outputs/job_market_insights.html) directly in any web browser (Chrome, Edge, Firefox).

---

### 🌐 Live Cloud Demo
The project is hosted and accessible online:  
👉 **[https://job-market-analysis-sdqp.onrender.com/](https://job-market-analysis-sdqp.onrender.com/)**

---

### 🛠️ Manual Step-by-Step Setup

```powershell
# 1. Clone repository & install requirements
git clone https://github.com/itssrinotshri/job-market-analysis.git
cd job-market-analysis
pip install -r requirements.txt

# 2. Configure credentials (optional for mock mode)
copy .env.example .env

# 3. Run Pipeline manually
python src/collect.py
python src/clean.py
python src/load_db.py

# 4. Refresh Power BI Desktop or launch Streamlit
streamlit run app.py
```
