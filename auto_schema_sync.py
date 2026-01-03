"""
Automatic Schema Sync System

Creates missing database tables based on model definitions.
For schema changes to existing tables, use migrations instead.
"""
import asyncio
from sqlalchemy import text, inspect
from database.db_manager import DatabaseManager
from database.base import Base

# Import ALL model files to register them with Base.metadata
# This ensures Base.metadata.tables contains ALL tables when syncing
from database import models
from database import models_attributes
from database import models_core
from database import models_economy
from database import models_equipment
from database import models_gacha
from database import models_lifetime_tiers
from database import models_payment_pool
from database import models_roleplay_info
from database import models_server_config
from database import models_systems
from database import models_usage_tracking
from database import models_verification


async def sync_schema():
    """
    Sync database schema with model definitions.
    - Creates new tables that don't exist
    - Reports schema mismatches (requires manual migration)
    - Does NOT drop or recreate existing tables
    """
    print("\n🔄 Checking database schema...")

    await DatabaseManager.initialize()

    async with DatabaseManager.engine.begin() as conn:
        # Get database dialect
        dialect = DatabaseManager.engine.dialect.name
        print(f"   Database: {dialect}")

        # Get all tables from models
        model_tables = Base.metadata.tables

        # Get existing tables from database
        def get_existing_tables(connection):
            inspector = inspect(connection)
            return set(inspector.get_table_names())

        existing_tables = await conn.run_sync(get_existing_tables)

        tables_to_create = []
        tables_with_mismatches = []

        # Check each model table
        for table_name, table in model_tables.items():
            if table_name not in existing_tables:
                # Table missing - will be created
                tables_to_create.append(table_name)
            else:
                # Table exists - check if columns match
                mismatches = await check_table_schema(conn, table_name, table, dialect)
                if mismatches:
                    tables_with_mismatches.append((table_name, mismatches))

        # Report findings
        if tables_to_create:
            print(f"\n   📝 New tables to create: {len(tables_to_create)}")
            for table in tables_to_create[:5]:
                print(f"      - {table}")
            if len(tables_to_create) > 5:
                print(f"      ... and {len(tables_to_create) - 5} more")

        if tables_with_mismatches:
            print(f"\n   ⚠️  Tables with schema mismatches: {len(tables_with_mismatches)}")
            print(f"   Run migrations to update these tables:")
            for table_name, mismatch_info in tables_with_mismatches:
                print(f"      - {table_name}")
                if mismatch_info.get('missing'):
                    print(f"        Missing columns: {mismatch_info['missing']}")
                if mismatch_info.get('extra'):
                    print(f"        Extra columns: {mismatch_info['extra']}")

        # Execute changes
        changes_made = False

        # Create missing tables
        if tables_to_create:
            print(f"\n   Creating {len(tables_to_create)} new tables...")
            # Create only missing tables
            await conn.run_sync(Base.metadata.create_all)
            changes_made = True
            print(f"   ✅ Created {len(tables_to_create)} new tables")

        if changes_made:
            print("\n✅ New tables created successfully!")
        elif not tables_with_mismatches:
            print("\n✅ Schema is up to date - no changes needed")
        else:
            print("\n⚠️  Schema mismatches detected - run migrations to update")


async def check_table_schema(conn, table_name: str, model_table, dialect: str) -> dict:
    """
    Check if a table's schema matches the model definition.
    Returns dict with mismatch info, or None if schema matches.
    """
    try:
        # Get actual columns from database
        def get_columns(connection):
            inspector = inspect(connection)
            return {col['name']: col for col in inspector.get_columns(table_name)}

        actual_columns = await conn.run_sync(get_columns)

        # Get expected columns from model
        model_columns = {col.name: col for col in model_table.columns}

        # Check if column sets match
        actual_col_names = set(actual_columns.keys())
        model_col_names = set(model_columns.keys())

        # If different columns, return mismatch info
        if actual_col_names != model_col_names:
            missing = model_col_names - actual_col_names
            extra = actual_col_names - model_col_names
            return {
                'missing': missing if missing else None,
                'extra': extra if extra else None
            }

        return None

    except Exception as e:
        print(f"      → Error checking {table_name}: {e}")
        return {'error': str(e)}


# Run sync on import (when bot starts)
if __name__ == "__main__":
    asyncio.run(sync_schema())
