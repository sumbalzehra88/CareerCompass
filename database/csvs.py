# init_db.py
import sqlite3
from sqlite3 import Connection

DB_FILE = "career_compass.db"

CREATE_STATEMENTS = [
    # USERS
    """
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT NOT NULL UNIQUE,
        password CHAR(64) NOT NULL  -- store SHA-256 hex digest
    );
    """,

    # USER_PROFILE
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

    # USER_SESSION
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

    # ROADMAPS
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

    # ROADMAP_STEPS
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

    # USER_SELECTED_ROADMAPS
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

    # TRACK_PROGRESS
    """
    CREATE TABLE IF NOT EXISTS track_progress (
        progress_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_roadmap_id INTEGER NOT NULL,
        step_id INTEGER NOT NULL,
        status TEXT DEFAULT 'pending',
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_roadmap_id) REFERENCES user_selected_roadmaps(user_roadmap_id) ON DELETE CASCADE,
        FOREIGN KEY (step_id) REFERENCES roadmap_steps(step_id) ON DELETE CASCADE
    );
    """,

    # COMPANIES
    """
    CREATE TABLE IF NOT EXISTS companies (
        company_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT
    );
    """,

    # INTERNSHIPS
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

    # APPLICATIONS
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

    # HACKATHONS
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

    # HACKATHON_TEAMS
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

    # NOTIFICATIONS
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

INDEX_STATEMENTS = [
    "CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);",
    "CREATE INDEX IF NOT EXISTS idx_user_profile_user_id ON user_profile(user_id);",
    "CREATE INDEX IF NOT EXISTS idx_user_selected_roadmaps_user ON user_selected_roadmaps(user_id);",
    "CREATE INDEX IF NOT EXISTS idx_applications_user ON applications(user_id);",
    "CREATE INDEX IF NOT EXISTS idx_internships_company ON internships(company_id);",
    "CREATE INDEX IF NOT EXISTS idx_track_progress_user_roadmap ON track_progress(user_roadmap_id);",
    "CREATE INDEX IF NOT EXISTS idx_hackathon_teams_hackathon ON hackathon_teams(hackathon_id);",
]


def create_connection(db_file: str) -> Connection:
    conn = sqlite3.connect(db_file)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def create_tables(conn: Connection):
    cur = conn.cursor()
    for stmt in CREATE_STATEMENTS:
        cur.executescript(stmt)
    for idx in INDEX_STATEMENTS:
        cur.execute(idx)
    conn.commit()


def main():
    conn = create_connection(DB_FILE)
    create_tables(conn)
    conn.close()
    print(f"✅ Database '{DB_FILE}' initialized with all tables successfully.")


if __name__ == "__main__":
    main()
