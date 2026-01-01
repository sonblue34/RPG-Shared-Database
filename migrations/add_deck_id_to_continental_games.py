"""
Add deck_id column to continental_games table for custom deck support
"""
import asyncio
from sqlalchemy import text
from database.db_manager import DatabaseManager

async def run_migration():
    """Add deck_id column to continental_games"""
    await DatabaseManager.initialize()
    async with DatabaseManager.get_session() as session:
        try:
            # Check if column exists
            result = await session.execute(text("PRAGMA table_info(continental_games)"))
            columns = [row[1] for row in result.fetchall()]

            if 'deck_id' not in columns:
                # Add deck_id column
                await session.execute(text("""
                    ALTER TABLE continental_games
                    ADD COLUMN deck_id INTEGER
                """))
                await session.commit()
                print("Added deck_id column to continental_games")
            else:
                print("Column deck_id already exists")

        except Exception as e:
            print(f"Migration failed: {e}")
            await session.rollback()

if __name__ == "__main__":
    print("Running migration: add_deck_id_to_continental_games")
    asyncio.run(run_migration())
    print("Migration complete!")
