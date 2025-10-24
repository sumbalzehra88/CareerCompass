import sqlite3
import pandas as pd

DB_FILE = "career_compass.db"

# ✅ Helper function to run queries and print clean results
def run_query(conn, query, title):
    print(f"\n🔹 {title}")
    try:
        df = pd.read_sql_query(query, conn)
        print(df.head(10).to_string(index=False))
    except Exception as e:
        print(f"❌ Query failed: {e}")

def main():
    conn = sqlite3.connect(DB_FILE)
    conn.execute("PRAGMA foreign_keys = ON;")
    print("✅ Connected to database and foreign keys enabled.\n")

    # ─────────────────────────────────────────────────────────────
    # 1️⃣ USERS × APPLICATIONS × INTERNSHIPS
    run_query(conn, """
        SELECT u.user_id, u.email, i.title AS internship_title, a.status, a.applied_on
        FROM applications a
        JOIN users u ON a.user_id = u.user_id
        JOIN internships i ON a.internship_id = i.internship_id
        ORDER BY a.applied_on DESC
        LIMIT 10;
    """, "Users with their Internship Applications")

    # ─────────────────────────────────────────────────────────────
    # 2️⃣ INTERNSHIPS × COMPANIES
    run_query(conn, """
        SELECT c.company_id, c.name AS company_name, i.internship_id, i.title AS internship_title, i.deadline
        FROM internships i
        LEFT JOIN companies c ON i.company_id = c.company_id
        ORDER BY c.company_id
        LIMIT 10;
    """, "Internships with their Companies")

    # ─────────────────────────────────────────────────────────────
    # 3️⃣ USERS × USER_PROFILE × APPLICATIONS
    run_query(conn, """
        SELECT u.user_id, up.name, up.degree, i.title AS internship_title, a.status
        FROM applications a
        JOIN users u ON a.user_id = u.user_id
        LEFT JOIN user_profile up ON up.user_id = u.user_id
        JOIN internships i ON a.internship_id = i.internship_id
        LIMIT 10;
    """, "Applicants with Profile and Internship Details")

    # ─────────────────────────────────────────────────────────────
    # 4️⃣ HACKATHONS × HACKATHON_TEAMS × USERS
    run_query(conn, """
        SELECT h.hackathon_id, h.name AS hackathon_name, t.team_id, t.team_name, u.email AS created_by
        FROM hackathon_teams t
        JOIN hackathons h ON t.hackathon_id = h.hackathon_id
        LEFT JOIN users u ON t.user_id = u.user_id
        LIMIT 10;
    """, "Hackathon Teams with Hackathon & Creator Info")

    # ─────────────────────────────────────────────────────────────
    # 4️⃣.1 HACKATHON_TEAMS × USER_PROFILE (via USERS)
    run_query(conn, """
        SELECT 
            h.name AS hackathon_name,
            t.team_id,
            t.team_name,
            up.name AS creator_name,
            up.skills AS creator_skills,
            up.degree AS creator_degree
        FROM hackathon_teams t
        JOIN hackathons h ON t.hackathon_id = h.hackathon_id
        LEFT JOIN users u ON t.user_id = u.user_id
        LEFT JOIN user_profile up ON up.user_id = u.user_id
        ORDER BY h.hackathon_id
        LIMIT 10;
    """, "Hackathon Teams with Creator's Profile Info")

    # ─────────────────────────────────────────────────────────────
    # 5️⃣ ROADMAP × ROADMAP_STEPS
    run_query(conn, """
        SELECT r.roadmap_id, r.title AS roadmap_title, s.step_number, s.step_content
        FROM roadmaps r
        JOIN roadmap_steps s ON r.roadmap_id = s.roadmap_id
        ORDER BY r.roadmap_id, s.step_number
        LIMIT 10;
    """, "Roadmaps with Their Steps")

    # ─────────────────────────────────────────────────────────────
    # 6️⃣ USER_SELECTED_ROADMAPS × TRACK_PROGRESS
    run_query(conn, """
        SELECT ur.user_id, r.title AS roadmap_title, s.step_number, t.status, t.updated_at
        FROM track_progress t
        JOIN user_selected_roadmaps ur ON ur.user_roadmap_id = t.user_roadmap_id
        JOIN roadmap_steps s ON t.step_id = s.step_id
        JOIN roadmaps r ON s.roadmap_id = r.roadmap_id
        LIMIT 10;
    """, "User Roadmap Progress Tracking")

    # ─────────────────────────────────────────────────────────────
    # 7️⃣ AGGREGATED INSIGHT: Internship popularity
    run_query(conn, """
        SELECT i.title AS internship_title, COUNT(a.app_id) AS total_applications
        FROM internships i
        LEFT JOIN applications a ON i.internship_id = a.internship_id
        GROUP BY i.internship_id
        ORDER BY total_applications DESC
        LIMIT 10;
    """, "Top 10 Most Applied Internships")

    # ─────────────────────────────────────────────────────────────
    # 8️⃣ AGGREGATED INSIGHT: Hackathon team count
    run_query(conn, """
        SELECT h.name AS hackathon_name, COUNT(t.team_id) AS total_teams
        FROM hackathons h
        LEFT JOIN hackathon_teams t ON h.hackathon_id = t.hackathon_id
        GROUP BY h.hackathon_id
        ORDER BY total_teams DESC
        LIMIT 10;
    """, "Hackathons with Most Teams")

    # ─────────────────────────────────────────────────────────────
    # 9️⃣ USERS × NOTIFICATIONS
    run_query(conn, """
        SELECT u.email, n.type, n.message, n.created_at, n.is_read
        FROM notifications n
        JOIN users u ON n.user_id = u.user_id
        ORDER BY n.created_at DESC
        LIMIT 10;
    """, "Recent Notifications per User")

    # ─────────────────────────────────────────────────────────────
    # 🔟 USERS × USER_SESSION
    run_query(conn, """
        SELECT u.user_id, u.email, s.login_time, s.logout_time, s.ip_address
        FROM user_session s
        JOIN users u ON s.user_id = u.user_id
        ORDER BY s.login_time DESC
        LIMIT 10;
    """, "User Session History")

    conn.close()
    print("\n🎯 All relationship queries executed successfully!")

if __name__ == "__main__":
    main()
