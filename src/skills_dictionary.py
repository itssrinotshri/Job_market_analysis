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
    """Scans text for skills against dictionary patterns."""
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
