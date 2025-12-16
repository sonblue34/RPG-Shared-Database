"""
Database migration to add race and class progression system tables

This migration adds NEW tables that are NOT created by auto_migrations.py:
1. Add race_level_bonuses table (per-level stat/skill gains)
2. Add race_fusions table (race+race or race+class fusion paths)
3. Add race_auto_stats table (automatic stat creation for races)
4. Add class_fusions table (class+class fusion paths)
5. Add class_auto_stats table (automatic stat creation for classes)

Note: The following tables are ALREADY created by auto_migrations.py:
- race_evolutions (with requirements_json field)
- race_bonuses (with unlock_level and bonus_value)
- class_level_config (with all new fields)
- class_level_requirements
- class_level_rewards
- class_evolutions

Added in v1.7.73-beta for comprehensive race and class progression systems.
"""
import asyncio
from sqlalchemy import text
from database.db_manager import DatabaseManager
from database.base import Base
from database.models import (
    RaceLevelBonus,
    RaceFusion,
    RaceAutoStat,
    ClassFusion,
    ClassAutoStat
)


async def migrate_add_race_class_progression_tables():
    """Add NEW race and class progression tables that are NOT in auto_migrations.py"""
    print("[*] Starting race/class progression system migration...")

    await DatabaseManager.initialize()

    async with DatabaseManager.get_session() as session:
        try:
            dialect = session.bind.dialect.name
            print(f"[*] Database: {dialect}")

            # Check which tables need to be created
            tables_to_create = []

            # Check for race_level_bonuses
            result = await session.execute(text("""
                SELECT table_name FROM information_schema.tables
                WHERE table_schema = 'public' AND table_name = 'race_level_bonuses'
            """) if dialect == 'postgresql' else text("""
                SELECT name FROM sqlite_master
                WHERE type='table' AND name = 'race_level_bonuses'
            """))
            if result.fetchone() is None:
                tables_to_create.append('race_level_bonuses')

            # Check for race_fusions
            result = await session.execute(text("""
                SELECT table_name FROM information_schema.tables
                WHERE table_schema = 'public' AND table_name = 'race_fusions'
            """) if dialect == 'postgresql' else text("""
                SELECT name FROM sqlite_master
                WHERE type='table' AND name = 'race_fusions'
            """))
            if result.fetchone() is None:
                tables_to_create.append('race_fusions')

            # Check for race_auto_stats
            result = await session.execute(text("""
                SELECT table_name FROM information_schema.tables
                WHERE table_schema = 'public' AND table_name = 'race_auto_stats'
            """) if dialect == 'postgresql' else text("""
                SELECT name FROM sqlite_master
                WHERE type='table' AND name = 'race_auto_stats'
            """))
            if result.fetchone() is None:
                tables_to_create.append('race_auto_stats')

            # Check for class_fusions
            result = await session.execute(text("""
                SELECT table_name FROM information_schema.tables
                WHERE table_schema = 'public' AND table_name = 'class_fusions'
            """) if dialect == 'postgresql' else text("""
                SELECT name FROM sqlite_master
                WHERE type='table' AND name = 'class_fusions'
            """))
            if result.fetchone() is None:
                tables_to_create.append('class_fusions')

            # Check for class_auto_stats
            result = await session.execute(text("""
                SELECT table_name FROM information_schema.tables
                WHERE table_schema = 'public' AND table_name = 'class_auto_stats'
            """) if dialect == 'postgresql' else text("""
                SELECT name FROM sqlite_master
                WHERE type='table' AND name = 'class_auto_stats'
            """))
            if result.fetchone() is None:
                tables_to_create.append('class_auto_stats')

            if tables_to_create:
                print(f"[*] Creating {len(tables_to_create)} new progression system tables...")

                # Use SQLAlchemy to create only the tables that don't exist
                async with session.begin():
                    await session.run_sync(Base.metadata.create_all, session.bind)

                print("[+] New tables created!")
                for table in tables_to_create:
                    print(f"  ✓ {table}")
            else:
                print("[*] All progression tables already exist")

            await session.commit()

            print("[+] Migration complete!")
            print()
            print("New tables added:")
            print("  - race_level_bonuses (per-level bonuses)")
            print("  - race_fusions (race fusion paths)")
            print("  - race_auto_stats (automatic stat creation)")
            print("  - class_fusions (class fusion paths)")
            print("  - class_auto_stats (automatic stat creation)")
            print()
            print("Note: The following were created by auto_migrations.py:")
            print("  - race_evolutions, race_bonuses, class_level_config")
            print("  - class_level_requirements, class_level_rewards, class_evolutions")

        except Exception as e:
            print(f"[-] Migration failed: {e}")
            import traceback
            traceback.print_exc()
            await session.rollback()
            raise


if __name__ == "__main__":
    asyncio.run(migrate_add_race_class_progression_tables())
