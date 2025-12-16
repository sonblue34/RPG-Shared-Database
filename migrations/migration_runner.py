"""
Migration Runner System

Automatically discovers and runs pending database migrations.
Tracks completed migrations in a database table.
"""
import os
import importlib.util
import asyncio
from pathlib import Path
from sqlalchemy import text
from typing import List, Tuple


class MigrationRunner:
    """Handles discovery and execution of database migrations"""

    def __init__(self, db_manager, database_url: str):
        self.db_manager = db_manager
        self.database_url = database_url
        self.migrations_dir = Path(__file__).parent

    async def ensure_migrations_table(self, session):
        """Create migrations tracking table if it doesn't exist"""
        dialect = session.bind.dialect.name

        if dialect == 'postgresql':
            await session.execute(text("""
                CREATE TABLE IF NOT EXISTS schema_migrations (
                    id SERIAL PRIMARY KEY,
                    migration_name VARCHAR(255) NOT NULL UNIQUE,
                    applied_at TIMESTAMP DEFAULT NOW()
                )
            """))
        else:  # SQLite
            await session.execute(text("""
                CREATE TABLE IF NOT EXISTS schema_migrations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    migration_name VARCHAR(255) NOT NULL UNIQUE,
                    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))

        await session.commit()

    async def get_completed_migrations(self, session) -> List[str]:
        """Get list of already-applied migrations"""
        result = await session.execute(text("""
            SELECT migration_name FROM schema_migrations ORDER BY id
        """))
        return [row[0] for row in result.fetchall()]

    async def mark_migration_complete(self, session, migration_name: str):
        """Mark a migration as completed"""
        await session.execute(text("""
            INSERT INTO schema_migrations (migration_name) VALUES (:name)
        """), {"name": migration_name})
        await session.commit()

    def discover_migrations(self) -> List[Tuple[str, str]]:
        """
        Discover all migration files in the migrations directory.
        Returns list of (filename, filepath) tuples, sorted alphabetically.
        """
        migrations = []

        for file in self.migrations_dir.glob("*.py"):
            # Skip __init__.py, migration_runner.py, and any test files
            if file.name in ['__init__.py', 'migration_runner.py'] or file.name.startswith('test_'):
                continue

            migrations.append((file.stem, str(file)))

        # Sort alphabetically for consistent ordering
        migrations.sort(key=lambda x: x[0])
        return migrations

    async def run_migration_file(self, migration_name: str, filepath: str) -> bool:
        """
        Run a single migration file.
        Returns True if successful, False otherwise.
        """
        try:
            print(f"[*] Running migration: {migration_name}")

            # Dynamically import the migration module
            spec = importlib.util.spec_from_file_location(migration_name, filepath)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # Find the main migration function (usually starts with 'migrate_')
            migrate_func = None
            for attr_name in dir(module):
                if attr_name.startswith('migrate_') and callable(getattr(module, attr_name)):
                    migrate_func = getattr(module, attr_name)
                    break

            if not migrate_func:
                print(f"[!] No migration function found in {migration_name}")
                return False

            # Run the migration function
            if asyncio.iscoroutinefunction(migrate_func):
                await migrate_func()
            else:
                migrate_func()

            print(f"[+] Migration {migration_name} completed successfully")
            return True

        except Exception as e:
            print(f"[-] Migration {migration_name} failed: {e}")
            return False

    async def run_migrations(self) -> Tuple[int, int, List[str]]:
        """
        Run all pending migrations.
        Returns (total_migrations, pending_count, failed_migrations)
        """
        # Initialize database
        await self.db_manager.initialize(self.database_url)

        async with self.db_manager.get_session() as session:
            # Ensure tracking table exists
            await self.ensure_migrations_table(session)

            # Get completed migrations
            completed = await self.get_completed_migrations(session)
            print(f"[*] Found {len(completed)} completed migrations")

            # Discover all migrations
            all_migrations = self.discover_migrations()
            print(f"[*] Found {len(all_migrations)} total migration files")

            # Filter to pending migrations
            pending = [(name, path) for name, path in all_migrations if name not in completed]

            if not pending:
                print("[*] No pending migrations to run")
                return len(all_migrations), 0, []

            print(f"[*] Running {len(pending)} pending migrations...")

            failed = []
            for migration_name, filepath in pending:
                success = await self.run_migration_file(migration_name, filepath)

                if success:
                    # Mark as complete
                    await self.mark_migration_complete(session, migration_name)
                else:
                    failed.append(migration_name)
                    # Stop on first failure
                    break

            if failed:
                print(f"\n[-] {len(failed)} migration(s) failed")
            else:
                print(f"\n[+] All {len(pending)} pending migrations completed successfully!")

            return len(all_migrations), len(pending), failed


async def run_migrations(db_manager, database_url: str) -> Tuple[int, int, List[str]]:
    """
    Convenience function to run all pending migrations.
    Returns (total_migrations, pending_count, failed_migrations)
    """
    runner = MigrationRunner(db_manager, database_url)
    return await runner.run_migrations()
