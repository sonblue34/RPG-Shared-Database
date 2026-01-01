"""
Automatic Schema Sync System

Checks if database tables match model definitions.
If tables are different from code, drops and recreates them automatically.
Replaces traditional migrations with automatic schema synchronization.
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
    Drops and recreates tables that don't match the code.
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
        tables_to_drop = []
        tables_to_recreate = []
        
        # Check each model table
        for table_name, table in model_tables.items():
            if table_name not in existing_tables:
                # Table missing - will be created
                tables_to_create.append(table_name)
            else:
                # Table exists - check if columns match
                needs_recreate = await check_table_schema(conn, table_name, table, dialect)
                if needs_recreate:
                    tables_to_recreate.append(table_name)
        
        # Find tables in DB that aren't in models
        for table_name in existing_tables:
            if table_name not in model_tables and not table_name.startswith('alembic'):
                tables_to_drop.append(table_name)
        
        # Report findings
        if tables_to_create:
            print(f"\n   📝 New tables to create: {len(tables_to_create)}")
            for table in tables_to_create[:5]:
                print(f"      - {table}")
            if len(tables_to_create) > 5:
                print(f"      ... and {len(tables_to_create) - 5} more")
        
        if tables_to_recreate:
            print(f"\n   🔄 Tables to recreate (schema changed): {len(tables_to_recreate)}")
            for table in tables_to_recreate:
                print(f"      - {table}")
        
        if tables_to_drop:
            print(f"\n   🗑️  Orphaned tables to drop: {len(tables_to_drop)}")
            for table in tables_to_drop:
                print(f"      - {table}")
        
        # Execute changes
        changes_made = False
        
        # Drop orphaned tables
        for table_name in tables_to_drop:
            print(f"   Dropping orphaned table: {table_name}")
            await conn.execute(text(f"DROP TABLE IF EXISTS {table_name} CASCADE"))
            changes_made = True

        # Create missing tables FIRST (before recreating, in case of FK dependencies)
        if tables_to_create:
            print(f"   Creating {len(tables_to_create)} new tables...")
            # Create only missing tables
            await conn.run_sync(Base.metadata.create_all)
            changes_made = True

        # Recreate mismatched tables (after new tables exist)
        for table_name in tables_to_recreate:
            print(f"   Recreating table with new schema: {table_name}")
            table = model_tables[table_name]
            # Drop old version with CASCADE to handle foreign keys
            await conn.execute(text(f"DROP TABLE IF EXISTS {table_name} CASCADE"))
            # Create new version
            await conn.run_sync(lambda sync_conn: table.create(sync_conn))
            changes_made = True
        
        if changes_made:
            print("\n✅ Schema synchronized successfully!")
        else:
            print("\n✅ Schema is up to date - no changes needed")


async def check_table_schema(conn, table_name: str, model_table, dialect: str) -> bool:
    """
    Check if a table's schema matches the model definition.
    Returns True if table needs to be recreated.
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

        # If different columns, needs recreation
        if actual_col_names != model_col_names:
            missing = model_col_names - actual_col_names
            extra = actual_col_names - model_col_names
            if missing:
                print(f"      → Missing columns in {table_name}: {missing}")
            if extra:
                print(f"      → Extra columns in {table_name}: {extra}")
            return True

        # Could add more detailed type checking here if needed
        # For now, just checking column names is sufficient

        return False

    except Exception as e:
        # If we can't check, assume it needs recreation
        print(f"      → Error checking {table_name}: {e}")
        return True


# Run sync on import (when bot starts)
if __name__ == "__main__":
    asyncio.run(sync_schema())
