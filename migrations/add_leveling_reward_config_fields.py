"""
Add attribute_points_per_level and skill_points_per_level to server_config
Supports both SQLite and PostgreSQL
"""
import asyncio
from sqlalchemy import text
from database.db_manager import DatabaseManager


async def run_migration():
    """Add leveling reward configuration fields"""
    print("\n[MIGRATION] Adding Leveling Reward Configuration Fields...")

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
                    WHERE table_name='server_config'
                    AND column_name IN ('attribute_points_per_level', 'skill_points_per_level')
                """)
            else:  # sqlite
                check_query = text("PRAGMA table_info(server_config)")

            result = await conn.execute(check_query)

            if dialect == 'postgresql':
                existing_columns = [row[0] for row in result]
            else:  # sqlite
                existing_columns = [row[1] for row in result]

            # Add attribute_points_per_level if not exists
            if 'attribute_points_per_level' not in existing_columns:
                print("   Adding attribute_points_per_level column...")
                await conn.execute(text("""
                    ALTER TABLE server_config
                    ADD COLUMN attribute_points_per_level INTEGER DEFAULT 0
                """))
                print("   [OK] Added attribute_points_per_level")
            else:
                print("   [OK] attribute_points_per_level already exists")

            # Add skill_points_per_level if not exists
            if 'skill_points_per_level' not in existing_columns:
                print("   Adding skill_points_per_level column...")
                await conn.execute(text("""
                    ALTER TABLE server_config
                    ADD COLUMN skill_points_per_level INTEGER DEFAULT 0
                """))
                print("   [OK] Added skill_points_per_level")
            else:
                print("   [OK] skill_points_per_level already exists")

            print("\n[SUCCESS] Leveling reward configuration fields added successfully!")

        except Exception as e:
            print(f"\n[ERROR] Migration failed: {e}")
            raise


if __name__ == "__main__":
    asyncio.run(run_migration())
