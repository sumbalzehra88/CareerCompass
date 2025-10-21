import os
import sqlite3
import csv

DB_FILE = "career_compass.db"

# CSV files are in the same folder as this script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# List of (CSV file, table name)
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

# === CREATE TABLE QUERIES ===
TABLE_CREATION_QUERIES = [
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
    """,
]


def insert_data_from_csv(csv_path, table_name, conn):
    with open(csv_path, 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        next(reader, None)  # skip header
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


def main():
    db_path = os.path.join(BASE_DIR, DB_FILE)

    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON;")

    # Create tables
    for query in TABLE_CREATION_QUERIES:
        conn.execute(query)

    # Import CSV data
    for csv_name, table_name in CSV_TABLE_MAP:
        csv_path = os.path.join(BASE_DIR, csv_name)
        if os.path.exists(csv_path):
            insert_data_from_csv(csv_path, table_name, conn)
        else:
            print(f"⚠️ Skipping {csv_name} (not found)")

    conn.close()
    print("\n🎉 All CSV data imported successfully!")


if __name__ == "__main__":
    main()
