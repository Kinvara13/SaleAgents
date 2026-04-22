"""
Migration: Add bidding company fields to projects table
Run once to add new columns to existing SQLite database.
"""
from sqlalchemy import text
from app.db.session import engine


def migrate():
    with engine.connect() as conn:
        # Check existing columns
        result = conn.execute(text("PRAGMA table_info(projects)"))
        existing = {row[1] for row in result.fetchall()}
        
        new_columns = [
            ("bidding_company", "TEXT DEFAULT ''"),
            ("agent_name", "TEXT DEFAULT ''"),
            ("agent_phone", "TEXT DEFAULT ''"),
            ("agent_email", "TEXT DEFAULT ''"),
            ("company_address", "TEXT DEFAULT ''"),
            ("bank_name", "TEXT DEFAULT ''"),
            ("bank_account", "TEXT DEFAULT ''"),
            ("confirm_status", "TEXT DEFAULT '待确认'"),
            ("confirm_feedback", "TEXT DEFAULT ''"),
            ("confirmed_by", "TEXT DEFAULT ''"),
            ("confirmed_at", "TEXT DEFAULT ''"),
        ]
        
        for col_name, col_def in new_columns:
            if col_name not in existing:
                conn.execute(text(f"ALTER TABLE projects ADD COLUMN {col_name} {col_def}"))
                print(f"Added column: {col_name}")
            else:
                print(f"Column already exists: {col_name}")
        
        conn.commit()
    print("Migration completed!")


if __name__ == "__main__":
    migrate()
