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
        st.bar_chart(data=q1_df.set_index("Skill")["Postings"], use_container_width=True)
        
    with col_b:
        st.markdown("### 🏢 Seniority Tier Distribution")
        sen_df = run_sql_query("""
            SELECT seniority_level AS Seniority, COUNT(*) AS Postings
            FROM jobs
            GROUP BY seniority_level
            ORDER BY Postings DESC
        """)
        st.dataframe(sen_df, use_container_width=True)
        st.bar_chart(data=sen_df.set_index("Seniority")["Postings"], use_container_width=True)


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
