"""
Migration: Create technical_cases table
Run once to add the new table to existing SQLite database.
"""
from sqlalchemy import text
from app.db.session import engine


def migrate():
    with engine.connect() as conn:
        # Check if table already exists
        result = conn.execute(text(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='technical_cases'"
        ))
        if result.fetchone():
            print("Table 'technical_cases' already exists. Skipping.")
            return

        conn.execute(text("""
            CREATE TABLE technical_cases (
                id VARCHAR(64) PRIMARY KEY,
                project_id VARCHAR(64) NOT NULL,
                title VARCHAR(255) NOT NULL,
                primary_review_item VARCHAR(128) NOT NULL DEFAULT '',
                secondary_review_item VARCHAR(128) NOT NULL DEFAULT '',
                case_type VARCHAR(64) NOT NULL DEFAULT '项目案例',
                scene_tags TEXT NOT NULL DEFAULT '[]',
                keywords TEXT NOT NULL DEFAULT '[]',
                summary TEXT NOT NULL DEFAULT '',
                contract_name VARCHAR(255) NOT NULL DEFAULT '',
                contract_amount VARCHAR(64) NOT NULL DEFAULT '',
                client_name VARCHAR(255) NOT NULL DEFAULT '',
                contract_overview TEXT NOT NULL DEFAULT '',
                key_highlights TEXT NOT NULL DEFAULT '',
                content TEXT NOT NULL DEFAULT '',
                score VARCHAR(32) NOT NULL DEFAULT '0.80',
                status VARCHAR(32) NOT NULL DEFAULT '可用',
                source VARCHAR(255) NOT NULL DEFAULT '',
                video_url VARCHAR(512) NOT NULL DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))

        # Create index on project_id
        conn.execute(text(
            "CREATE INDEX ix_technical_cases_project_id ON technical_cases(project_id)"
        ))
        conn.commit()
    print("Migration completed! Table 'technical_cases' created.")


if __name__ == "__main__":
    migrate()