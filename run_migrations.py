#!/usr/bin/env python3
"""
Standalone Migration Runner

Run this script to apply pending database migrations without needing bot configuration.
Usage: python run_migrations.py [database_url]

If database_url is not provided, will check environment variables:
- DATABASE_URL
- Or fallback to sqlite:///rpg_data.db
"""
import asyncio
import sys
import os
from pathlib import Path

# Add parent directory to path so we can import database modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from migrations.migration_runner import MigrationRunner


class SimpleDatabaseManager:
    """Simplified database manager for running migrations"""

    def __init__(self):
        self.engine = None
        self.session_factory = None

    async def initialize(self, database_url: str):
        """Initialize database connection"""
        # Convert postgres:// to postgresql+asyncpg://
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql+asyncpg://', 1)
        elif database_url.startswith('postgresql://'):
            database_url = database_url.replace('postgresql://', 'postgresql+asyncpg://', 1)
        elif database_url.startswith('sqlite:///'):
            # Convert to async sqlite
            if not database_url.startswith('sqlite+aiosqlite:///'):
                database_url = database_url.replace('sqlite:///', 'sqlite+aiosqlite:///', 1)

        print(f"[*] Connecting to database...")
        self.engine = create_async_engine(database_url, echo=False)
        self.session_factory = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
        print(f"[+] Connected successfully")

    def get_session(self):
        """Get a database session"""
        return self.session_factory()


async def main():
    """Main entry point"""
    print("=" * 60)
    print("Database Migration Runner")
    print("=" * 60)

    # Get database URL from command line or environment
    if len(sys.argv) > 1:
        database_url = sys.argv[1]
        print(f"[*] Using database URL from command line")
    else:
        database_url = os.getenv('DATABASE_URL')
        if not database_url:
            database_url = 'sqlite+aiosqlite:///rpg_data.db'
            print(f"[!] No DATABASE_URL found, using default: {database_url}")
        else:
            print(f"[*] Using DATABASE_URL from environment")

    # Create database manager
    db_manager = SimpleDatabaseManager()

    # Run migrations
    try:
        runner = MigrationRunner(db_manager, database_url)
        total, pending, failed = await runner.run_migrations()

        print("\n" + "=" * 60)
        if failed:
            print(f"❌ Migration failed!")
            print(f"   Total migrations: {total}")
            print(f"   Failed: {', '.join(failed)}")
            return 1
        else:
            print(f"✅ Migration completed successfully!")
            print(f"   Total migrations: {total}")
            print(f"   Pending (now applied): {pending}")
            return 0

    except Exception as e:
        print(f"\n❌ Error running migrations: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        if db_manager.engine:
            await db_manager.engine.dispose()


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
