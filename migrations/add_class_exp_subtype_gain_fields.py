"""
Add comprehensive class system fields for exp/level tracking, subtypes, and gain types
Supports both SQLite and PostgreSQL
"""
import asyncio
from sqlalchemy import text
from database.db_manager import DatabaseManager


async def migrate_add_class_exp_subtype_gain_fields():
    """Add new fields to Class and ServerConfig tables"""
    print("\n[MIGRATION] Adding Class System Enhancement Fields...")

    await DatabaseManager.initialize()

    async with DatabaseManager.engine.begin() as conn:
        dialect = DatabaseManager.engine.dialect.name
        print(f"   Database: {dialect}")

        try:
            # ===== ADD FIELDS TO CLASS TABLE =====
            print("\n   Adding fields to Class table...")

            # Check if class_exp_attribute_key column exists
            if dialect == 'postgresql':
                check_query = text("""
                    SELECT column_name FROM information_schema.columns
                    WHERE table_name = 'classes' AND column_name = 'class_exp_attribute_key'
                """)
            else:  # sqlite
                check_query = text("""
                    SELECT name FROM pragma_table_info('classes')
                    WHERE name = 'class_exp_attribute_key'
                """)

            result = await conn.execute(check_query)
            column_exists = result.first() is not None

            if not column_exists:
                print("      Adding class_exp_attribute_key column...")
                if dialect == 'postgresql':
                    await conn.execute(text("""
                        ALTER TABLE classes
                        ADD COLUMN class_exp_attribute_key VARCHAR(100)
                    """))
                else:  # sqlite
                    await conn.execute(text("""
                        ALTER TABLE classes
                        ADD COLUMN class_exp_attribute_key TEXT
                    """))
                print("      [OK] Added class_exp_attribute_key")
            else:
                print("      [OK] class_exp_attribute_key already exists")

            # Check if class_level_attribute_key column exists
            if dialect == 'postgresql':
                check_query = text("""
                    SELECT column_name FROM information_schema.columns
                    WHERE table_name = 'classes' AND column_name = 'class_level_attribute_key'
                """)
            else:  # sqlite
                check_query = text("""
                    SELECT name FROM pragma_table_info('classes')
                    WHERE name = 'class_level_attribute_key'
                """)

            result = await conn.execute(check_query)
            column_exists = result.first() is not None

            if not column_exists:
                print("      Adding class_level_attribute_key column...")
                if dialect == 'postgresql':
                    await conn.execute(text("""
                        ALTER TABLE classes
                        ADD COLUMN class_level_attribute_key VARCHAR(100)
                    """))
                else:  # sqlite
                    await conn.execute(text("""
                        ALTER TABLE classes
                        ADD COLUMN class_level_attribute_key TEXT
                    """))
                print("      [OK] Added class_level_attribute_key")
            else:
                print("      [OK] class_level_attribute_key already exists")

            # Check if class_subtype column exists
            if dialect == 'postgresql':
                check_query = text("""
                    SELECT column_name FROM information_schema.columns
                    WHERE table_name = 'classes' AND column_name = 'class_subtype'
                """)
            else:  # sqlite
                check_query = text("""
                    SELECT name FROM pragma_table_info('classes')
                    WHERE name = 'class_subtype'
                """)

            result = await conn.execute(check_query)
            column_exists = result.first() is not None

            if not column_exists:
                print("      Adding class_subtype column...")
                if dialect == 'postgresql':
                    await conn.execute(text("""
                        ALTER TABLE classes
                        ADD COLUMN class_subtype VARCHAR(100)
                    """))
                else:  # sqlite
                    await conn.execute(text("""
                        ALTER TABLE classes
                        ADD COLUMN class_subtype TEXT
                    """))
                print("      [OK] Added class_subtype")
            else:
                print("      [OK] class_subtype already exists")

            # Check if gain_type column exists
            if dialect == 'postgresql':
                check_query = text("""
                    SELECT column_name FROM information_schema.columns
                    WHERE table_name = 'classes' AND column_name = 'gain_type'
                """)
            else:  # sqlite
                check_query = text("""
                    SELECT name FROM pragma_table_info('classes')
                    WHERE name = 'gain_type'
                """)

            result = await conn.execute(check_query)
            column_exists = result.first() is not None

            if not column_exists:
                print("      Adding gain_type column...")
                if dialect == 'postgresql':
                    await conn.execute(text("""
                        ALTER TABLE classes
                        ADD COLUMN gain_type VARCHAR(50) DEFAULT 'character_level'
                    """))
                else:  # sqlite
                    await conn.execute(text("""
                        ALTER TABLE classes
                        ADD COLUMN gain_type TEXT DEFAULT 'character_level'
                    """))
                print("      [OK] Added gain_type")
            else:
                print("      [OK] gain_type already exists")

            # ===== ADD FIELDS TO SERVER_CONFIG TABLE =====
            print("\n   Adding fields to ServerConfig table...")

            # Check if default_class_exp_attribute_key column exists
            if dialect == 'postgresql':
                check_query = text("""
                    SELECT column_name FROM information_schema.columns
                    WHERE table_name = 'server_config' AND column_name = 'default_class_exp_attribute_key'
                """)
            else:  # sqlite
                check_query = text("""
                    SELECT name FROM pragma_table_info('server_config')
                    WHERE name = 'default_class_exp_attribute_key'
                """)

            result = await conn.execute(check_query)
            column_exists = result.first() is not None

            if not column_exists:
                print("      Adding default_class_exp_attribute_key column...")
                if dialect == 'postgresql':
                    await conn.execute(text("""
                        ALTER TABLE server_config
                        ADD COLUMN default_class_exp_attribute_key VARCHAR(100)
                    """))
                else:  # sqlite
                    await conn.execute(text("""
                        ALTER TABLE server_config
                        ADD COLUMN default_class_exp_attribute_key TEXT
                    """))
                print("      [OK] Added default_class_exp_attribute_key")
            else:
                print("      [OK] default_class_exp_attribute_key already exists")

            # Check if default_class_level_attribute_key column exists
            if dialect == 'postgresql':
                check_query = text("""
                    SELECT column_name FROM information_schema.columns
                    WHERE table_name = 'server_config' AND column_name = 'default_class_level_attribute_key'
                """)
            else:  # sqlite
                check_query = text("""
                    SELECT name FROM pragma_table_info('server_config')
                    WHERE name = 'default_class_level_attribute_key'
                """)

            result = await conn.execute(check_query)
            column_exists = result.first() is not None

            if not column_exists:
                print("      Adding default_class_level_attribute_key column...")
                if dialect == 'postgresql':
                    await conn.execute(text("""
                        ALTER TABLE server_config
                        ADD COLUMN default_class_level_attribute_key VARCHAR(100)
                    """))
                else:  # sqlite
                    await conn.execute(text("""
                        ALTER TABLE server_config
                        ADD COLUMN default_class_level_attribute_key TEXT
                    """))
                print("      [OK] Added default_class_level_attribute_key")
            else:
                print("      [OK] default_class_level_attribute_key already exists")

            # Check if allow_multiple_subtypes column exists
            if dialect == 'postgresql':
                check_query = text("""
                    SELECT column_name FROM information_schema.columns
                    WHERE table_name = 'server_config' AND column_name = 'allow_multiple_subtypes'
                """)
            else:  # sqlite
                check_query = text("""
                    SELECT name FROM pragma_table_info('server_config')
                    WHERE name = 'allow_multiple_subtypes'
                """)

            result = await conn.execute(check_query)
            column_exists = result.first() is not None

            if not column_exists:
                print("      Adding allow_multiple_subtypes column...")
                if dialect == 'postgresql':
                    await conn.execute(text("""
                        ALTER TABLE server_config
                        ADD COLUMN allow_multiple_subtypes BOOLEAN DEFAULT FALSE
                    """))
                else:  # sqlite
                    await conn.execute(text("""
                        ALTER TABLE server_config
                        ADD COLUMN allow_multiple_subtypes INTEGER DEFAULT 0
                    """))
                print("      [OK] Added allow_multiple_subtypes")
            else:
                print("      [OK] allow_multiple_subtypes already exists")

            print("\n[SUCCESS] Class system enhancement migration completed!")

        except Exception as e:
            print(f"\n[ERROR] Migration failed: {e}")
            raise


if __name__ == "__main__":
    asyncio.run(migrate_add_class_exp_subtype_gain_fields())
