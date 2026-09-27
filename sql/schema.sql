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
    years_exp_min INTEGER,
    years_exp_max INTEGER,
    salary_min REAL,
    salary_max REAL,
    salary_avg REAL,
    salary_imputed REAL,
    is_salary_imputed BOOLEAN,
    posted_date VARCHAR(100),
    redirect_url TEXT,
    search_term VARCHAR(100)
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
