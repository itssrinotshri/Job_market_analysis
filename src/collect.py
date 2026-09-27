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
