"""
Add class_types and class_class_types tables for custom class type management
Supports both SQLite and PostgreSQL
"""
import asyncio
from sqlalchemy import text
from database.db_manager import DatabaseManager


async def migrate_add_class_types_tables():
    """Add class_types and class_class_types tables"""
    print("\n[MIGRATION] Adding Class Types Tables...")

    await DatabaseManager.initialize()

    async with DatabaseManager.engine.begin() as conn:
        dialect = DatabaseManager.engine.dialect.name
        print(f"   Database: {dialect}")

        try:
            # ===== CREATE CLASS_TYPES TABLE =====
            print("\n   Creating class_types table...")

            # Check if table exists
            if dialect == 'postgresql':
                check_query = text("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables
                        WHERE table_name = 'class_types'
                    )
                """)
            else:  # sqlite
                check_query = text("""
                    SELECT name FROM sqlite_master
                    WHERE type='table' AND name='class_types'
                """)

            result = await conn.execute(check_query)
            table_exists = result.first() is not None

            if not table_exists:
                print("      Creating class_types table...")
                if dialect == 'postgresql':
                    await conn.execute(text("""
                        CREATE TABLE class_types (
                            id BIGSERIAL PRIMARY KEY,
                            guild_id BIGINT NOT NULL,
                            type_name VARCHAR(100) NOT NULL,
                            display_name VARCHAR(200),
                            description TEXT,
                            icon_emoji VARCHAR(50),
                            color VARCHAR(7) DEFAULT '#99AAB5',
                            display_order INTEGER DEFAULT 0,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            CONSTRAINT uq_guild_class_type UNIQUE (guild_id, type_name)
                        )
                    """))
                    await conn.execute(text("""
                        CREATE INDEX ix_class_types_guild_id ON class_types(guild_id)
                    """))
                else:  # sqlite
                    await conn.execute(text("""
                        CREATE TABLE class_types (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            guild_id INTEGER NOT NULL,
                            type_name TEXT NOT NULL,
                            display_name TEXT,
                            description TEXT,
                            icon_emoji TEXT,
                            color TEXT DEFAULT '#99AAB5',
                            display_order INTEGER DEFAULT 0,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            CONSTRAINT uq_guild_class_type UNIQUE (guild_id, type_name)
                        )
                    """))
                    await conn.execute(text("""
                        CREATE INDEX ix_class_types_guild_id ON class_types(guild_id)
                    """))
                print("      [OK] Created class_types table")
            else:
                print("      [OK] class_types table already exists")

            # ===== CREATE CLASS_CLASS_TYPES TABLE =====
            print("\n   Creating class_class_types table...")

            # Check if table exists
            if dialect == 'postgresql':
                check_query = text("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables
                        WHERE table_name = 'class_class_types'
                    )
                """)
            else:  # sqlite
                check_query = text("""
                    SELECT name FROM sqlite_master
                    WHERE type='table' AND name='class_class_types'
                """)

            result = await conn.execute(check_query)
            table_exists = result.first() is not None

            if not table_exists:
                print("      Creating class_class_types table...")
                if dialect == 'postgresql':
                    await conn.execute(text("""
                        CREATE TABLE class_class_types (
                            id BIGSERIAL PRIMARY KEY,
                            guild_id BIGINT NOT NULL,
                            class_name VARCHAR(100) NOT NULL,
                            type_name VARCHAR(100) NOT NULL,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            CONSTRAINT uq_class_type_assignment UNIQUE (guild_id, class_name, type_name)
                        )
                    """))
                    await conn.execute(text("""
                        CREATE INDEX ix_class_class_types_guild_id ON class_class_types(guild_id)
                    """))
                else:  # sqlite
                    await conn.execute(text("""
                        CREATE TABLE class_class_types (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            guild_id INTEGER NOT NULL,
                            class_name TEXT NOT NULL,
                            type_name TEXT NOT NULL,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            CONSTRAINT uq_class_type_assignment UNIQUE (guild_id, class_name, type_name)
                        )
                    """))
                    await conn.execute(text("""
                        CREATE INDEX ix_class_class_types_guild_id ON class_class_types(guild_id)
                    """))
                print("      [OK] Created class_class_types table")
            else:
                print("      [OK] class_class_types table already exists")

            print("\n[SUCCESS] Class types tables migration completed!")

        except Exception as e:
            print(f"\n[ERROR] Migration failed: {e}")
            raise


if __name__ == "__main__":
    asyncio.run(migrate_add_class_types_tables())
