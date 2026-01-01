"""
Add hand_message_id column to continental_players table
"""
import asyncio
from sqlalchemy import text
from database.db_manager import DatabaseManager

async def run_migration():
    """Add hand_message_id column to continental_players"""
    await DatabaseManager.initialize()
    async with DatabaseManager.get_session() as session:
        try:
            # Detect database type from engine
            db_name = DatabaseManager.engine.dialect.name

            # Check if column exists
            if db_name == "sqlite":
                result = await session.execute(text("PRAGMA table_info(continental_players)"))
                columns = [row[1] for row in result.fetchall()]
            else:  # PostgreSQL
                result = await session.execute(text("""
                    SELECT column_name
                    FROM information_schema.columns
                    WHERE table_name = 'continental_players'
                """))
                columns = [row[0] for row in result.fetchall()]

            if 'hand_message_id' not in columns:
                # Add hand_message_id column
                await session.execute(text("""
                    ALTER TABLE continental_players
                    ADD COLUMN hand_message_id BIGINT
                """))

                await session.commit()
                print(f"Added hand_message_id column to continental_players ({db_name})")
            else:
                print(f"Column hand_message_id already exists ({db_name})")

        except Exception as e:
            print(f"Migration failed: {e}")
            await session.rollback()

if __name__ == "__main__":
    print("Running migration: add_hand_message_id_to_continental_players")
    asyncio.run(run_migration())
    print("Migration complete!")
