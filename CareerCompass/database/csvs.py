import os
import csv
import sqlite3
from sqlite3 import Connection
import pandas as pd

# ─────────────────────────────────────────────────────────────
# CONFIGURATION
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ✅ Use the first script's DB path style
DB_FILE = os.path.join(BASE_DIR, "..", "career_compass.db")
DB_FILE = os.path.abspath(DB_FILE)  # recommended absolute path

# CSV → Table mapping
CSV_TABLE_MAP = [
    ("users_table.csv", "users"),
    ("user_profile.csv", "user_profile"),
    ("user_session.csv", "user_session"),
    ("roadmaps.csv", "roadmaps"),
    ("roadmap_steps.csv", "roadmap_steps"),
    ("user_selected_roadmaps.csv", "user_selected_roadmaps"),
    ("companies.csv", "companies"),
    ("internships.csv", "internships"),
    ("application.csv", "applications"),
    ("hackathons.csv", "hackathons"),
    ("HACKATHON_TEAMS.csv", "hackathon_teams"),
    ("notifications.csv", "notifications"),
]

# ─────────────────────────────────────────────────────────────
# 1️⃣ TABLE CREATION STATEMENTS (from second script, fixed)
CREATE_STATEMENTS = [
    """
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT NOT NULL UNIQUE,
        password CHAR(64) NOT NULL
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS user_profile (
        profile_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        username TEXT,
        education TEXT,
        degree TEXT,
        skills TEXT,
        country TEXT,
        work_experience TEXT,
        user_interest TEXT,
        industry TEXT,
        career_goals TEXT,
        time_frame INTEGER,
        FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS user_session (
        session_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        login_time DATETIME,
        logout_time DATETIME,
        ip_address TEXT,
        device_info TEXT,
        FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS roadmaps (
        roadmap_id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        created_by INTEGER,
        FOREIGN KEY (created_by) REFERENCES users(user_id) ON DELETE SET NULL
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS roadmap_steps (
        step_id INTEGER PRIMARY KEY AUTOINCREMENT,
        roadmap_id INTEGER NOT NULL,
        step_number INTEGER NOT NULL,
        step_content TEXT,
        FOREIGN KEY (roadmap_id) REFERENCES roadmaps(roadmap_id) ON DELETE CASCADE,
        UNIQUE(roadmap_id, step_number)
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS user_selected_roadmaps (
        user_roadmap_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        roadmap_id INTEGER NOT NULL,
        selected_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
        FOREIGN KEY (roadmap_id) REFERENCES roadmaps(roadmap_id) ON DELETE CASCADE
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS user_step_progress (
        progress_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        step_id INTEGER NOT NULL,
        roadmap_id INTEGER NOT NULL,
        is_completed INTEGER DEFAULT 0,
        completed_at DATETIME,
        FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
        FOREIGN KEY (step_id) REFERENCES roadmap_steps(step_id) ON DELETE CASCADE,
        FOREIGN KEY (roadmap_id) REFERENCES roadmaps(roadmap_id) ON DELETE CASCADE,
        UNIQUE(user_id, step_id)
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS companies (
        company_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS internships (
        internship_id INTEGER PRIMARY KEY AUTOINCREMENT,
        company_id INTEGER,
        title TEXT NOT NULL,
        duration TEXT,
        location TEXT,
        skills_required TEXT,
        deadline DATE,
        description TEXT,
        stipend INTEGER CHECK (stipend BETWEEN 500 AND 1500),
        FOREIGN KEY (company_id) REFERENCES companies(company_id) ON DELETE SET NULL
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS applications (
        app_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        internship_id INTEGER NOT NULL,
        applied_on DATETIME DEFAULT CURRENT_TIMESTAMP,
        status TEXT DEFAULT 'Pending',
        FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
        FOREIGN KEY (internship_id) REFERENCES internships(internship_id) ON DELETE CASCADE
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS hackathons (
        hackathon_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        start_date DATE,
        end_date DATE,
        details TEXT,
        registration_date DATE,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        required_skills TEXT
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS hackathon_teams (
        team_id INTEGER PRIMARY KEY AUTOINCREMENT,
        hackathon_id INTEGER NOT NULL,
        team_name TEXT,
        team_members TEXT,
        user_id INTEGER,
        FOREIGN KEY (hackathon_id) REFERENCES hackathons(hackathon_id) ON DELETE CASCADE,
        FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE SET NULL
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS notifications (
        notif_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        type TEXT,
        message TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        is_read INTEGER DEFAULT 0,
        FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
    );
    """
]

# ─────────────────────────────────────────────────────────────
# 2️⃣ INDEX CREATION
INDEX_STATEMENTS = [
    "CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);",
    "CREATE INDEX IF NOT EXISTS idx_user_profile_user_id ON user_profile(user_id);",
    "CREATE INDEX IF NOT EXISTS idx_internships_company ON internships(company_id);",
    "CREATE INDEX IF NOT EXISTS idx_applications_user ON applications(user_id);",
    "CREATE INDEX IF NOT EXISTS idx_hackathon_teams_hackathon ON hackathon_teams(hackathon_id);",
    "CREATE INDEX IF NOT EXISTS idx_user_step_progress_user ON user_step_progress(user_id);",
    "CREATE INDEX IF NOT EXISTS idx_user_step_progress_step ON user_step_progress(step_id);",
]

# ─────────────────────────────────────────────────────────────
# 3️⃣ CONNECTION & CSV IMPORT
def create_connection(db_file: str) -> Connection:
    conn = sqlite3.connect(db_file)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def create_tables_and_indexes(conn: Connection):
    cur = conn.cursor()
    for stmt in CREATE_STATEMENTS:
        cur.executescript(stmt)
    for idx in INDEX_STATEMENTS:
        cur.execute(idx)
    conn.commit()
    print("✅ All tables and indexes created successfully.\n")

def insert_data_from_csv(csv_path, table_name, conn):
    with open(csv_path, 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        header = next(reader, None)
        expected_cols = len(header)
        data = [tuple(row[:expected_cols]) for row in reader]

    if not data:
        print(f"⚠️ No data in {os.path.basename(csv_path)}")
        return

    placeholders = ", ".join(["?"] * expected_cols)
    query = f"INSERT OR IGNORE INTO {table_name} VALUES ({placeholders})"
    try:
        conn.executemany(query, data)
        conn.commit()
        print(f"✅ Inserted {len(data)} rows into {table_name}.")
    except Exception as e:
        print(f"❌ Error inserting into {table_name}: {e}")

def import_all_csv(conn):
    for csv_name, table_name in CSV_TABLE_MAP:
        csv_path = os.path.join(BASE_DIR, csv_name)
        if os.path.exists(csv_path):
            insert_data_from_csv(csv_path, table_name, conn)
        else:
            print(f"⚠️ Skipping {csv_name} (not found)")
    print("\n🎉 All CSV data imported successfully!\n")

# ─────────────────────────────────────────────────────────────
# 4️⃣ VALIDATION QUERIES
def run_query(conn, query, title):
    print(f"\n🔹 {title}")
    try:
        df = pd.read_sql_query(query, conn)
        if df.empty:
            print("⚠️ No records found.")
        else:
            print(df.head(10).to_string(index=False))
    except Exception as e:
        print(f"❌ Query failed: {e}")

def validate_relationships(conn):
    run_query(conn, """
        SELECT u.user_id, u.email, i.title AS internship_title, a.status, a.applied_on
        FROM applications a
        JOIN users u ON a.user_id = u.user_id
        JOIN internships i ON a.internship_id = i.internship_id
        ORDER BY a.applied_on DESC
        LIMIT 10;
    """, "Users with their Internship Applications")

    run_query(conn, """
        SELECT r.title AS roadmap_title, s.step_number, s.step_content
        FROM roadmaps r
        JOIN roadmap_steps s ON r.roadmap_id = s.roadmap_id
        ORDER BY r.roadmap_id, s.step_number
        LIMIT 10;
    """, "Roadmaps with Steps")

    run_query(conn, """
        SELECT u.email, r.title AS roadmap_title, 
               COUNT(usp.progress_id) AS completed_steps,
               (SELECT COUNT(*) FROM roadmap_steps WHERE roadmap_id = r.roadmap_id) AS total_steps
        FROM users u
        JOIN user_step_progress usp ON u.user_id = usp.user_id
        JOIN roadmaps r ON usp.roadmap_id = r.roadmap_id
        WHERE usp.is_completed = 1
        GROUP BY u.user_id, r.roadmap_id
        LIMIT 10;
    """, "User Progress on Roadmaps")

    run_query(conn, """
        SELECT i.title AS internship_title, COUNT(a.app_id) AS total_applications
        FROM internships i
        LEFT JOIN applications a ON i.internship_id = a.internship_id
        GROUP BY i.internship_id
        ORDER BY total_applications DESC
        LIMIT 10;
    """, "Top 10 Most Applied Internships")

# ─────────────────────────────────────────────────────────────
# 5️⃣ MAIN
def main():
    conn = create_connection(DB_FILE)
    create_tables_and_indexes(conn)
    import_all_csv(conn)
    validate_relationships(conn)
    conn.close()
    print("\n🎯 Database setup, import, and analysis completed successfully!")

if __name__ == "__main__":
    main()
