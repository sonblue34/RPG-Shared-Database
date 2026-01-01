"""
Migration: Add has_gauge and uses_formula flags to stat_definitions
Date: 2025-12-21
Version: 1.8.0

Adds:
1. has_gauge column - boolean flag for stats with current/max values
2. uses_formula column - boolean flag for formula-calculated stats
3. Migrates existing stat_type values to new flags
"""

from sqlalchemy import text
from database.db_manager import DatabaseManager


async def migrate_add_stat_behavior_flags():
    """Add has_gauge and uses_formula columns to stat_definitions table"""

    async with DatabaseManager.get_session() as session:
        try:
            dialect = session.bind.dialect.name
            print(f"[*] Database: {dialect}")

            # ================================================================
            # 1. Add has_gauge column to stat_definitions
            # ================================================================
            print("[*] Checking stat_definitions.has_gauge column...")
            if dialect == 'postgresql':
                # Check if column exists
                check_column = await session.execute(text("""
                    SELECT column_name
                    FROM information_schema.columns
                    WHERE table_name = 'stat_definitions'
                    AND column_name = 'has_gauge'
                """))
                if check_column.fetchone() is None:
                    print("[*] Adding has_gauge column to stat_definitions...")
                    await session.execute(text("""
                        ALTER TABLE stat_definitions
                        ADD COLUMN IF NOT EXISTS has_gauge BOOLEAN DEFAULT FALSE
                    """))
                    await session.commit()
                    print("[+] Added has_gauge column")
                else:
                    print("[✓] has_gauge column already exists")
            else:  # SQLite
                # Try to query the column
                try:
                    await session.execute(text("SELECT has_gauge FROM stat_definitions LIMIT 1"))
                    print("[✓] has_gauge column already exists")
                except:
                    await session.rollback()
                    print("[*] Adding has_gauge column to stat_definitions...")
                    await session.execute(text("""
                        ALTER TABLE stat_definitions
                        ADD COLUMN has_gauge BOOLEAN DEFAULT 0
                    """))
                    await session.commit()
                    print("[+] Added has_gauge column")

            # ================================================================
            # 2. Add uses_formula column to stat_definitions
            # ================================================================
            print("[*] Checking stat_definitions.uses_formula column...")
            if dialect == 'postgresql':
                # Check if column exists
                check_column = await session.execute(text("""
                    SELECT column_name
                    FROM information_schema.columns
                    WHERE table_name = 'stat_definitions'
                    AND column_name = 'uses_formula'
                """))
                if check_column.fetchone() is None:
                    print("[*] Adding uses_formula column to stat_definitions...")
                    await session.execute(text("""
                        ALTER TABLE stat_definitions
                        ADD COLUMN IF NOT EXISTS uses_formula BOOLEAN DEFAULT FALSE
                    """))
                    await session.commit()
                    print("[+] Added uses_formula column")
                else:
                    print("[✓] uses_formula column already exists")
            else:  # SQLite
                # Try to query the column
                try:
                    await session.execute(text("SELECT uses_formula FROM stat_definitions LIMIT 1"))
                    print("[✓] uses_formula column already exists")
                except:
                    await session.rollback()
                    print("[*] Adding uses_formula column to stat_definitions...")
                    await session.execute(text("""
                        ALTER TABLE stat_definitions
                        ADD COLUMN uses_formula BOOLEAN DEFAULT 0
                    """))
                    await session.commit()
                    print("[+] Added uses_formula column")

            # ================================================================
            # 3. Migrate existing stat_type values to new flags
            # ================================================================
            print("[*] Migrating existing stat_type values...")

            # Set has_gauge=TRUE for stats with stat_type='gauge'
            await session.execute(text("""
                UPDATE stat_definitions
                SET has_gauge = TRUE
                WHERE stat_type = 'gauge'
            """))

            # Set uses_formula=TRUE for stats with stat_type='calculated'
            await session.execute(text("""
                UPDATE stat_definitions
                SET uses_formula = TRUE
                WHERE stat_type = 'calculated'
            """))

            await session.commit()
            print("[+] Migrated stat_type values to new flags")

            print("[+] Migration completed successfully!")

        except Exception as e:
            print(f"[-] Migration failed: {e}")
            await session.rollback()
            raise


if __name__ == "__main__":
    import asyncio
    asyncio.run(migrate_add_stat_behavior_flags())
