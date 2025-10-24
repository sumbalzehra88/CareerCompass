import os
import sqlite3
import csv
import pandas as pd
from sqlite3 import Connection

# ─────────────────────────────────────────────────────────────
# CONFIGURATION
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = r"C:\Users\user\OneDrive\Desktop\CareerCompass\career_compass.db"

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
# 1️⃣ TABLE CREATION STATEMENTS
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
        name TEXT,
        education TEXT,
        degree TEXT,
        skills TEXT,
        country TEXT,
        work_experience TEXT,
        user_interest TEXT,
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
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
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
        next(reader, None)
        data = [tuple(row) for row in reader]

    if not data:
        print(f"⚠️ No data in {os.path.basename(csv_path)}")
        return

    placeholders = ", ".join(["?"] * len(data[0]))
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
    # USERS × APPLICATIONS × INTERNSHIPS
    run_query(conn, """
        SELECT u.user_id, u.email, i.title AS internship_title, a.status, a.applied_on
        FROM applications a
        JOIN users u ON a.user_id = u.user_id
        JOIN internships i ON a.internship_id = i.internship_id
        ORDER BY a.applied_on DESC
        LIMIT 10;
    """, "Users with their Internship Applications")

    # INTERNSHIPS × COMPANIES
    run_query(conn, """
        SELECT c.name AS company_name, i.title AS internship_title, i.deadline
        FROM internships i
        LEFT JOIN companies c ON i.company_id = c.company_id
        LIMIT 10;
    """, "Internships with their Companies")

    # USERS × USER_PROFILE × APPLICATIONS
    run_query(conn, """
        SELECT u.user_id, up.name, up.degree, i.title AS internship_title, a.status
        FROM applications a
        JOIN users u ON a.user_id = u.user_id
        LEFT JOIN user_profile up ON up.user_id = u.user_id
        JOIN internships i ON a.internship_id = i.internship_id
        LIMIT 10;
    """, "Applicants with Profile and Internship Details")

    # HACKATHONS × TEAMS × USERS
    run_query(conn, """
        SELECT h.name AS hackathon_name, t.team_name, u.email AS created_by
        FROM hackathon_teams t
        JOIN hackathons h ON t.hackathon_id = h.hackathon_id
        LEFT JOIN users u ON t.user_id = u.user_id
        LIMIT 10;
    """, "Hackathon Teams with Creator Info")

    # ROADMAP × ROADMAP_STEPS
    run_query(conn, """
        SELECT r.title AS roadmap_title, s.step_number, s.step_content
        FROM roadmaps r
        JOIN roadmap_steps s ON r.roadmap_id = s.roadmap_id
        ORDER BY r.roadmap_id, s.step_number
        LIMIT 10;
    """, "Roadmaps with Their Steps")

    # INTERNSHIP POPULARITY
    run_query(conn, """
        SELECT i.title AS internship_title, COUNT(a.app_id) AS total_applications
        FROM internships i
        LEFT JOIN applications a ON i.internship_id = a.internship_id
        GROUP BY i.internship_id
        ORDER BY total_applications DESC
        LIMIT 10;
    """, "Top 10 Most Applied Internships")

    # HACKATHON TEAM COUNT
    run_query(conn, """
        SELECT h.name AS hackathon_name, COUNT(t.team_id) AS total_teams
        FROM hackathons h
        LEFT JOIN hackathon_teams t ON h.hackathon_id = t.hackathon_id
        GROUP BY h.hackathon_id
        ORDER BY total_teams DESC
        LIMIT 10;
    """, "Hackathons with Most Teams")

    # USERS × NOTIFICATIONS
    run_query(conn, """
        SELECT u.email, n.type, n.message, n.created_at, n.is_read
        FROM notifications n
        JOIN users u ON n.user_id = u.user_id
        ORDER BY n.created_at DESC
        LIMIT 10;
    """, "Recent Notifications per User")

    # USERS × USER_SESSION
    run_query(conn, """
        SELECT u.email, s.login_time, s.logout_time, s.ip_address
        FROM user_session s
        JOIN users u ON s.user_id = u.user_id
        ORDER BY s.login_time DESC
        LIMIT 10;
    """, "User Session History")

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
