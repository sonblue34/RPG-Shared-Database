"""
Migration: Fix missing columns and tables
Date: 2025-11-30
Version: 1.7.20-beta

Fixes:
1. Add is_active column to reaction_role_panels table
2. Create roleplay_info_categories table (if missing)
3. Create roleplay_info_pages table (if missing)
4. Create roleplay_info_access table (if missing)
"""

from sqlalchemy import text
from database.db_manager import DatabaseManager


async def migrate_fix_missing_schema():
    """Fix missing database schema elements"""

    async with DatabaseManager.get_session() as session:
        try:
            dialect = session.bind.dialect.name
            print(f"[*] Database: {dialect}")

            # ================================================================
            # 1. Add is_active column to reaction_role_panels
            # ================================================================
            print("[*] Checking reaction_role_panels.is_active column...")
            if dialect == 'postgresql':
                # Check if column exists
                check_column = await session.execute(text("""
                    SELECT column_name
                    FROM information_schema.columns
                    WHERE table_name = 'reaction_role_panels'
                    AND column_name = 'is_active'
                """))
                if check_column.fetchone() is None:
                    print("[*] Adding is_active column to reaction_role_panels...")
                    await session.execute(text("""
                        ALTER TABLE reaction_role_panels
                        ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE
                    """))
                    await session.commit()
                    print("[+] Added is_active column")
                else:
                    print("[✓] is_active column already exists")
            else:  # SQLite
                # Try to query the column
                try:
                    await session.execute(text("SELECT is_active FROM reaction_role_panels LIMIT 1"))
                    print("[✓] is_active column already exists")
                except:
                    await session.rollback()
                    print("[*] Adding is_active column to reaction_role_panels...")
                    await session.execute(text("""
                        ALTER TABLE reaction_role_panels
                        ADD COLUMN is_active INTEGER DEFAULT 1
                    """))
                    await session.commit()
                    print("[+] Added is_active column")

            # ================================================================
            # 2. Create roleplay_info_categories table
            # ================================================================
            print("[*] Checking roleplay_info_categories table...")
            if dialect == 'postgresql':
                check_table = await session.execute(text("""
                    SELECT table_name
                    FROM information_schema.tables
                    WHERE table_schema = 'public'
                    AND table_name = 'roleplay_info_categories'
                """))
                if check_table.fetchone() is None:
                    print("[*] Creating roleplay_info_categories table...")
                    await session.execute(text("""
                        CREATE TABLE roleplay_info_categories (
                            id SERIAL PRIMARY KEY,
                            guild_id BIGINT NOT NULL,
                            title VARCHAR(100) NOT NULL,
                            description TEXT,
                            emoji VARCHAR(50),
                            order_index INTEGER DEFAULT 0,
                            is_active BOOLEAN DEFAULT TRUE,
                            created_by BIGINT NOT NULL,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    """))
                    await session.execute(text("""
                        CREATE INDEX IF NOT EXISTS ix_roleplay_info_categories_guild_id
                        ON roleplay_info_categories(guild_id)
                    """))
                    await session.execute(text("""
                        CREATE INDEX IF NOT EXISTS ix_roleplay_info_categories_order_index
                        ON roleplay_info_categories(order_index)
                    """))
                    await session.commit()
                    print("[+] Created roleplay_info_categories table")
                else:
                    print("[✓] roleplay_info_categories table already exists")
            else:  # SQLite
                try:
                    await session.execute(text("SELECT 1 FROM roleplay_info_categories LIMIT 1"))
                    print("[✓] roleplay_info_categories table already exists")
                except:
                    await session.rollback()
                    print("[*] Creating roleplay_info_categories table...")
                    await session.execute(text("""
                        CREATE TABLE roleplay_info_categories (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            guild_id INTEGER NOT NULL,
                            title VARCHAR(100) NOT NULL,
                            description TEXT,
                            emoji VARCHAR(50),
                            order_index INTEGER DEFAULT 0,
                            is_active INTEGER DEFAULT 1,
                            created_by INTEGER NOT NULL,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    """))
                    await session.execute(text("""
                        CREATE INDEX IF NOT EXISTS ix_roleplay_info_categories_guild_id
                        ON roleplay_info_categories(guild_id)
                    """))
                    await session.execute(text("""
                        CREATE INDEX IF NOT EXISTS ix_roleplay_info_categories_order_index
                        ON roleplay_info_categories(order_index)
                    """))
                    await session.commit()
                    print("[+] Created roleplay_info_categories table")

            # ================================================================
            # 3. Create roleplay_info_pages table
            # ================================================================
            print("[*] Checking roleplay_info_pages table...")
            if dialect == 'postgresql':
                check_table = await session.execute(text("""
                    SELECT table_name
                    FROM information_schema.tables
                    WHERE table_schema = 'public'
                    AND table_name = 'roleplay_info_pages'
                """))
                if check_table.fetchone() is None:
                    print("[*] Creating roleplay_info_pages table...")
                    await session.execute(text("""
                        CREATE TABLE roleplay_info_pages (
                            id SERIAL PRIMARY KEY,
                            category_id INTEGER NOT NULL REFERENCES roleplay_info_categories(id) ON DELETE CASCADE,
                            page_number INTEGER NOT NULL DEFAULT 1,
                            title VARCHAR(200),
                            content TEXT NOT NULL,
                            created_by BIGINT NOT NULL,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    """))
                    await session.execute(text("""
                        CREATE INDEX IF NOT EXISTS ix_roleplay_info_pages_category_id
                        ON roleplay_info_pages(category_id)
                    """))
                    await session.commit()
                    print("[+] Created roleplay_info_pages table")
                else:
                    print("[✓] roleplay_info_pages table already exists")
            else:  # SQLite
                try:
                    await session.execute(text("SELECT 1 FROM roleplay_info_pages LIMIT 1"))
                    print("[✓] roleplay_info_pages table already exists")
                except:
                    await session.rollback()
                    print("[*] Creating roleplay_info_pages table...")
                    await session.execute(text("""
                        CREATE TABLE roleplay_info_pages (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            category_id INTEGER NOT NULL,
                            page_number INTEGER NOT NULL DEFAULT 1,
                            title VARCHAR(200),
                            content TEXT NOT NULL,
                            created_by INTEGER NOT NULL,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            FOREIGN KEY (category_id) REFERENCES roleplay_info_categories(id) ON DELETE CASCADE
                        )
                    """))
                    await session.execute(text("""
                        CREATE INDEX IF NOT EXISTS ix_roleplay_info_pages_category_id
                        ON roleplay_info_pages(category_id)
                    """))
                    await session.commit()
                    print("[+] Created roleplay_info_pages table")

            # ================================================================
            # 4. Create roleplay_info_access table
            # ================================================================
            print("[*] Checking roleplay_info_access table...")
            if dialect == 'postgresql':
                check_table = await session.execute(text("""
                    SELECT table_name
                    FROM information_schema.tables
                    WHERE table_schema = 'public'
                    AND table_name = 'roleplay_info_access'
                """))
                if check_table.fetchone() is None:
                    print("[*] Creating roleplay_info_access table...")
                    await session.execute(text("""
                        CREATE TABLE roleplay_info_access (
                            id SERIAL PRIMARY KEY,
                            category_id INTEGER NOT NULL REFERENCES roleplay_info_categories(id) ON DELETE CASCADE,
                            access_type VARCHAR(20) NOT NULL,
                            restriction_type VARCHAR(20) NOT NULL,
                            restriction_value VARCHAR(200) NOT NULL,
                            comparison_operator VARCHAR(10) DEFAULT 'exact',
                            comparison_value_max VARCHAR(200),
                            created_by BIGINT NOT NULL,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    """))
                    await session.execute(text("""
                        CREATE INDEX IF NOT EXISTS ix_roleplay_info_access_category_id
                        ON roleplay_info_access(category_id)
                    """))
                    await session.commit()
                    print("[+] Created roleplay_info_access table")
                else:
                    print("[✓] roleplay_info_access table already exists")
            else:  # SQLite
                try:
                    await session.execute(text("SELECT 1 FROM roleplay_info_access LIMIT 1"))
                    print("[✓] roleplay_info_access table already exists")
                except:
                    await session.rollback()
                    print("[*] Creating roleplay_info_access table...")
                    await session.execute(text("""
                        CREATE TABLE roleplay_info_access (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            category_id INTEGER NOT NULL,
                            access_type VARCHAR(20) NOT NULL,
                            restriction_type VARCHAR(20) NOT NULL,
                            restriction_value VARCHAR(200) NOT NULL,
                            comparison_operator VARCHAR(10) DEFAULT 'exact',
                            comparison_value_max VARCHAR(200),
                            created_by INTEGER NOT NULL,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            FOREIGN KEY (category_id) REFERENCES roleplay_info_categories(id) ON DELETE CASCADE
                        )
                    """))
                    await session.execute(text("""
                        CREATE INDEX IF NOT EXISTS ix_roleplay_info_access_category_id
                        ON roleplay_info_access(category_id)
                    """))
                    await session.commit()
                    print("[+] Created roleplay_info_access table")

            print("[+] All schema fixes completed successfully!")

        except Exception as e:
            print(f"[-] Migration failed: {e}")
            await session.rollback()
            raise


if __name__ == "__main__":
    import asyncio
    asyncio.run(migrate_fix_missing_schema())
