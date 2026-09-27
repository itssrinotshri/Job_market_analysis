"""
Database Loader for Data Analyst Job Market Analysis.
Loads cleaned CSV datasets with feature engineered columns into SQLite / PostgreSQL.
"""

import os
import sys
import sqlite3
import logging
from pathlib import Path
from typing import Tuple, Any
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
    logger.info(f"Connecting to SQLite database at: {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Drop old table if schema changed
    cursor.execute("DROP TABLE IF EXISTS jobs")
    cursor.execute("DROP TABLE IF EXISTS skills")
    cursor.execute("DROP TABLE IF EXISTS posting_skills")
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

    logger.info(f"SQLite Load Complete:")
    logger.info(f" - jobs table: {job_count} rows")
    logger.info(f" - skills table: {skill_count} rows")
    logger.info(f" - posting_skills table: {junction_count} rows")

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

    load_sqlite_db(df_jobs, df_job_skills, df_skills_master)


if __name__ == "__main__":
    main()
