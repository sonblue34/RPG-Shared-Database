"""
Add inactivity voting fields to continental_games table
Supports both SQLite and PostgreSQL
"""
import asyncio
from sqlalchemy import text
from database.db_manager import DatabaseManager


async def run_migration():
    """Add turn_start_time and vote_in_progress columns"""
    print("\n[MIGRATION] Adding Inactivity Voting Fields...")

    await DatabaseManager.initialize()

    async with DatabaseManager.engine.begin() as conn:
        dialect = DatabaseManager.engine.dialect.name
        print(f"   Database: {dialect}")

        try:
            # Check if columns exist
            if dialect == 'postgresql':
                check_query = text("""
                    SELECT column_name
                    FROM information_schema.columns
                    WHERE table_name='continental_games'
                    AND column_name IN ('turn_start_time', 'vote_in_progress')
                """)
            else:  # sqlite
                check_query = text("PRAGMA table_info(continental_games)")

            result = await conn.execute(check_query)

            if dialect == 'postgresql':
                existing_columns = [row[0] for row in result]
            else:  # sqlite
                existing_columns = [row[1] for row in result]  # Column name is at index 1

            # Add turn_start_time if not exists
            if 'turn_start_time' not in existing_columns:
                print("   Adding turn_start_time column...")
                await conn.execute(text("""
                    ALTER TABLE continental_games
                    ADD COLUMN turn_start_time TIMESTAMP NULL
                """))
                print("   [OK] Added turn_start_time")
            else:
                print("   [OK] turn_start_time already exists")

            # Add vote_in_progress if not exists
            if 'vote_in_progress' not in existing_columns:
                print("   Adding vote_in_progress column...")
                await conn.execute(text("""
                    ALTER TABLE continental_games
                    ADD COLUMN vote_in_progress BOOLEAN DEFAULT FALSE
                """))
                print("   [OK] Added vote_in_progress")
            else:
                print("   [OK] vote_in_progress already exists")

            print("\n[SUCCESS] Inactivity voting fields added successfully!")

        except Exception as e:
            print(f"\n[ERROR] Migration failed: {e}")
            raise


if __name__ == "__main__":
    asyncio.run(run_migration())
