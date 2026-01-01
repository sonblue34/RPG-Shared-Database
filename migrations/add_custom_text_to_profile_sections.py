"""
Migration: Add custom_text column to profile_sections
Date: 2025-12-20
Version: 1.7.21-beta

Adds:
1. custom_text column to profile_sections table for custom text sections
"""

from sqlalchemy import text
from database.db_manager import DatabaseManager


async def migrate_add_custom_text_column():
    """Add custom_text column to profile_sections table"""

    async with DatabaseManager.get_session() as session:
        try:
            dialect = session.bind.dialect.name
            print(f"[*] Database: {dialect}")

            # ================================================================
            # 1. Add custom_text column to profile_sections
            # ================================================================
            print("[*] Checking profile_sections.custom_text column...")
            if dialect == 'postgresql':
                # Check if column exists
                check_column = await session.execute(text("""
                    SELECT column_name
                    FROM information_schema.columns
                    WHERE table_name = 'profile_sections'
                    AND column_name = 'custom_text'
                """))
                if check_column.fetchone() is None:
                    print("[*] Adding custom_text column to profile_sections...")
                    await session.execute(text("""
                        ALTER TABLE profile_sections
                        ADD COLUMN IF NOT EXISTS custom_text TEXT
                    """))
                    await session.commit()
                    print("[+] Added custom_text column")
                else:
                    print("[✓] custom_text column already exists")
            else:  # SQLite
                # Try to query the column
                try:
                    await session.execute(text("SELECT custom_text FROM profile_sections LIMIT 1"))
                    print("[✓] custom_text column already exists")
                except:
                    await session.rollback()
                    print("[*] Adding custom_text column to profile_sections...")
                    await session.execute(text("""
                        ALTER TABLE profile_sections
                        ADD COLUMN custom_text TEXT
                    """))
                    await session.commit()
                    print("[+] Added custom_text column")

            print("[+] Migration completed successfully!")

        except Exception as e:
            print(f"[-] Migration failed: {e}")
            await session.rollback()
            raise


if __name__ == "__main__":
    import asyncio
    asyncio.run(migrate_add_custom_text_column())
