# import_csv.py
import sqlite3
import pandas as pd
import os

DB_FILE = "career_compass.db"

# Import order adjusted for foreign key dependencies
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
    ("hackathon_teams.csv", "hackathon_teams"),
    ("notifications.csv", "notifications"),
]

def import_csv_to_db(conn, csv_file, table_name):
    print(f"📥 Importing {csv_file} → {table_name}")
    try:
        df = pd.read_csv(csv_file)
        df.columns = [c.strip() for c in df.columns]

        df.to_sql(table_name, conn, if_exists="append", index=False)
        print(f"✅ Inserted {len(df)} rows into '{table_name}'.\n")

    except Exception as e:
        print(f"❌ Error inserting {csv_file} into {table_name}: {e}\n")

def main():
    if not os.path.exists(DB_FILE):
        print(f"⚠️ Database file '{DB_FILE}' not found. Run init_db.py first.")
        return

    conn = sqlite3.connect(DB_FILE)
    conn.execute("PRAGMA foreign_keys = ON;")

    for csv_file, table_name in CSV_TABLE_MAP:
        if os.path.exists(csv_file):
            import_csv_to_db(conn, csv_file, table_name)
        else:
            print(f"⚠️ Skipping '{csv_file}' — file not found.\n")

    conn.close()
    print("🎉 All CSV data successfully imported into the database!")

if __name__ == "__main__":
    main()
