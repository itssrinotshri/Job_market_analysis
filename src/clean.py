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
    """Parses job seniority level from job title and description text."""
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
    """
    Step 2: Feature Engineering - Parses min and max required years of experience from text using Regex.
    """
    text = f"{title} {description}".lower()

    # Pattern 1: Range "3 to 5 years" or "3-5 yrs"
    range_match = re.search(r'(\d+)\s*(?:to|-)\s*(\d+)\s*(?:years?|yrs?)', text)
    if range_match:
        exp_min = int(range_match.group(1))
        exp_max = int(range_match.group(2))
        if exp_min <= exp_max and exp_min < 20 and exp_max < 25:
            return exp_min, exp_max

    # Pattern 2: Minimum plus "5+ years"
    plus_match = re.search(r'(\d+)\+\s*(?:years?|yrs?)', text)
    if plus_match:
        exp_min = int(plus_match.group(1))
        if exp_min < 20:
            return exp_min, exp_min + 2

    # Pattern 3: Exact "3 years experience"
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
        logger.error(f"No raw JSON files found in {config.RAW_DATA_DIR}. Please run collect.py first.")
        sys.exit(1)

    json_files.sort(key=os.path.getmtime, reverse=True)
    latest_file = json_files[0]
    logger.info(f"Loading raw data from latest file: {latest_file}")

    with open(latest_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    return data


def impute_salaries(df_jobs: pd.DataFrame) -> pd.DataFrame:
    """
    Step 3: Domain-specific Median Salary Imputation.
    Imputes missing salary values using median salary grouped by (seniority_level, search_term).
    """
    logger.info("Step 3: Running domain-specific median salary imputation...")
    
    # Calculate median salary by (seniority_level, search_term)
    medians = df_jobs.groupby(["seniority_level", "search_term"])["salary_avg"].transform("median")
    
    # Fallback to overall median by seniority level if group median is NaN
    seniority_medians = df_jobs.groupby("seniority_level")["salary_avg"].transform("median")
    
    overall_median = df_jobs["salary_avg"].median()
    if pd.isna(overall_median):
        overall_median = 800000.0  # Fallback default (8 LPA INR)

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

    # Apply Step 3 Salary Imputation
    df_jobs = impute_salaries(df_jobs)

    master_skills_data = [
        {"skill_name": k, "category": v["category"]} for k, v in SKILL_PATTERNS.items()
    ]
    df_skills_master = pd.DataFrame(master_skills_data)

    return df_jobs, df_job_skills, df_skills_master


def main() -> None:
    logger.info("Starting Data Cleaning, Feature Engineering & Skill Extraction Phase...")

    raw_jobs = load_latest_raw_json()
    logger.info(f"Loaded {len(raw_jobs)} raw records.")

    df_jobs, df_job_skills, df_skills_master = clean_and_process_jobs(raw_jobs)

    logger.info(f"Deduplicated to {len(df_jobs)} unique job postings.")
    logger.info(f"Extracted {len(df_job_skills)} skill-to-job associations across postings.")

    jobs_csv_path = config.PROCESSED_DATA_DIR / "jobs_cleaned.csv"
    job_skills_csv_path = config.PROCESSED_DATA_DIR / "job_skills_cleaned.csv"
    skills_master_csv_path = config.PROCESSED_DATA_DIR / "skills_master_cleaned.csv"

    df_jobs.to_csv(jobs_csv_path, index=False)
    df_job_skills.to_csv(job_skills_csv_path, index=False)
    df_skills_master.to_csv(skills_master_csv_path, index=False)

    logger.info(f"Successfully exported cleaned data with new features to:")
    logger.info(f" - {jobs_csv_path}")
    logger.info(f" - {job_skills_csv_path}")
    logger.info(f" - {skills_master_csv_path}")


if __name__ == "__main__":
    main()
