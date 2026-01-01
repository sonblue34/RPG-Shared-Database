"""
Add character_level_rewards table for flexible level-up rewards
Supports both SQLite and PostgreSQL
"""
import asyncio
from sqlalchemy import text
from database.db_manager import DatabaseManager


async def run_migration():
    """Create character_level_rewards table"""
    print("\n[MIGRATION] Adding Character Level Rewards Table...")

    await DatabaseManager.initialize()

    async with DatabaseManager.engine.begin() as conn:
        dialect = DatabaseManager.engine.dialect.name
        print(f"   Database: {dialect}")

        try:
            # Check if table exists
            if dialect == 'postgresql':
                check_query = text("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables
                        WHERE table_name = 'character_level_rewards'
                    )
                """)
                result = await conn.execute(check_query)
                table_exists = result.scalar()
            else:  # sqlite
                check_query = text("""
                    SELECT name FROM sqlite_master
                    WHERE type='table' AND name='character_level_rewards'
                """)
                result = await conn.execute(check_query)
                table_exists = result.first() is not None

            if not table_exists:
                print("   Creating character_level_rewards table...")

                if dialect == 'postgresql':
                    await conn.execute(text("""
                        CREATE TABLE character_level_rewards (
                            id BIGSERIAL PRIMARY KEY,
                            guild_id BIGINT NOT NULL,
                            level INTEGER NOT NULL,
                            reward_type VARCHAR NOT NULL,
                            reward_data JSONB NOT NULL,
                            display_order INTEGER DEFAULT 0
                        )
                    """))

                    # Create index
                    await conn.execute(text("""
                        CREATE INDEX idx_character_level_reward ON character_level_rewards (guild_id, level)
                    """))
                else:  # sqlite
                    await conn.execute(text("""
                        CREATE TABLE character_level_rewards (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            guild_id INTEGER NOT NULL,
                            level INTEGER NOT NULL,
                            reward_type TEXT NOT NULL,
                            reward_data TEXT NOT NULL,
                            display_order INTEGER DEFAULT 0
                        )
                    """))

                    # Create index
                    await conn.execute(text("""
                        CREATE INDEX idx_character_level_reward ON character_level_rewards (guild_id, level)
                    """))

                print("   [OK] Created character_level_rewards table")
            else:
                print("   [OK] character_level_rewards table already exists")

            print("\n[SUCCESS] Character level rewards table migration completed!")

        except Exception as e:
            print(f"\n[ERROR] Migration failed: {e}")
            raise


if __name__ == "__main__":
    asyncio.run(run_migration())
