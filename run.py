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
