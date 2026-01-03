"""
Automatic migration system that runs on bot startup
Checks and applies any missing database schema changes

All base tables are created via Base.metadata.create_all() in DatabaseManager.initialize()
This file is for incremental schema changes after initial deployment
"""
import asyncio
from sqlalchemy import text
from database.db_manager import DatabaseManager


async def run_auto_migrations():
    """Run all automatic migrations on bot startup"""
    print("\n[MIGRATIONS] Checking for pending migrations...")

    async with DatabaseManager.get_session() as session:
        try:
            # Get database dialect
            dialect = session.bind.dialect.name
            print(f"   Database: {dialect}")

            migrations_run = 0

            # ============================================================================
            # MIGRATIONS START HERE
            # ============================================================================
            # All previous migrations (1-62) have been incorporated into base models
            # Schema is complete as of v1.8.0-beta
            #
            # Add new migrations below as needed:

            # Migration 63: Create stat_value_rules table for caps, conditions, and display ranges
            if await _table_missing(session, 'stat_value_rules'):
                print("   📝 Creating stat_value_rules table...")
                if dialect == 'postgresql':
                    await session.execute(text("""
                        CREATE TABLE IF NOT EXISTS stat_value_rules (
                            id BIGSERIAL PRIMARY KEY,
                            guild_id BIGINT NOT NULL,
                            stat_key VARCHAR(100) NOT NULL,
                            rule_name VARCHAR(200),
                            rule_type VARCHAR(50) NOT NULL,
                            priority INTEGER DEFAULT 0,
                            is_active BOOLEAN DEFAULT TRUE,
                            condition_type VARCHAR(50) NOT NULL DEFAULT 'always',
                            condition_data JSONB,
                            target_value DOUBLE PRECISION,
                            target_formula TEXT,
                            soft_cap_penalty_type VARCHAR(50),
                            soft_cap_penalty_value DOUBLE PRECISION,
                            soft_cap_penalty_formula TEXT,
                            display_text VARCHAR(100),
                            range_min DOUBLE PRECISION,
                            range_max DOUBLE PRECISION,
                            range_color VARCHAR(7),
                            description TEXT,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        );
                        CREATE INDEX IF NOT EXISTS idx_guild_stat_rule ON stat_value_rules(guild_id, stat_key, rule_type);
                        CREATE INDEX IF NOT EXISTS idx_stat_value_rules_guild_id ON stat_value_rules(guild_id);
                        CREATE INDEX IF NOT EXISTS idx_stat_value_rules_stat_key ON stat_value_rules(stat_key);
                    """))
                else:  # SQLite
                    await session.execute(text("""
                        CREATE TABLE IF NOT EXISTS stat_value_rules (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            guild_id INTEGER NOT NULL,
                            stat_key VARCHAR(100) NOT NULL,
                            rule_name VARCHAR(200),
                            rule_type VARCHAR(50) NOT NULL,
                            priority INTEGER DEFAULT 0,
                            is_active INTEGER DEFAULT 1,
                            condition_type VARCHAR(50) NOT NULL DEFAULT 'always',
                            condition_data TEXT,
                            target_value REAL,
                            target_formula TEXT,
                            soft_cap_penalty_type VARCHAR(50),
                            soft_cap_penalty_value REAL,
                            soft_cap_penalty_formula TEXT,
                            display_text VARCHAR(100),
                            range_min REAL,
                            range_max REAL,
                            range_color VARCHAR(7),
                            description TEXT,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        );
                        CREATE INDEX IF NOT EXISTS idx_guild_stat_rule ON stat_value_rules(guild_id, stat_key, rule_type);
                        CREATE INDEX IF NOT EXISTS idx_stat_value_rules_guild_id ON stat_value_rules(guild_id);
                        CREATE INDEX IF NOT EXISTS idx_stat_value_rules_stat_key ON stat_value_rules(stat_key);
                    """))
                migrations_run += 1

            # Migration 64: Create equipment_slot_definitions table for flexible slot system
            if await _table_missing(session, 'equipment_slot_definitions'):
                print("   📝 Creating equipment_slot_definitions table...")
                if dialect == 'postgresql':
                    await session.execute(text("""
                        CREATE TABLE IF NOT EXISTS equipment_slot_definitions (
                            id BIGSERIAL PRIMARY KEY,
                            guild_id BIGINT NOT NULL,
                            slot_key VARCHAR(50) NOT NULL,
                            slot_name VARCHAR(100) NOT NULL,
                            description TEXT,
                            icon_emoji VARCHAR(50),
                            display_order INTEGER DEFAULT 0,
                            default_slot_count INTEGER DEFAULT 1,
                            is_enabled BOOLEAN DEFAULT TRUE,
                            class_slot_counts JSONB,
                            unlock_level INTEGER DEFAULT 1,
                            allowed_item_types JSONB,
                            allowed_item_subtypes JSONB,
                            blocked_item_tags JSONB,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        );
                        CREATE INDEX IF NOT EXISTS idx_equipment_slot_guild_id ON equipment_slot_definitions(guild_id);
                        CREATE INDEX IF NOT EXISTS idx_equipment_slot_guild_key ON equipment_slot_definitions(guild_id, slot_key);
                    """))
                else:  # SQLite
                    await session.execute(text("""
                        CREATE TABLE IF NOT EXISTS equipment_slot_definitions (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            guild_id INTEGER NOT NULL,
                            slot_key VARCHAR(50) NOT NULL,
                            slot_name VARCHAR(100) NOT NULL,
                            description TEXT,
                            icon_emoji VARCHAR(50),
                            display_order INTEGER DEFAULT 0,
                            default_slot_count INTEGER DEFAULT 1,
                            is_enabled INTEGER DEFAULT 1,
                            class_slot_counts TEXT,
                            unlock_level INTEGER DEFAULT 1,
                            allowed_item_types TEXT,
                            allowed_item_subtypes TEXT,
                            blocked_item_tags TEXT,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        );
                        CREATE INDEX IF NOT EXISTS idx_equipment_slot_guild_id ON equipment_slot_definitions(guild_id);
                        CREATE INDEX IF NOT EXISTS idx_equipment_slot_guild_key ON equipment_slot_definitions(guild_id, slot_key);
                    """))
                migrations_run += 1

            # Migration 65: Create item_slot_interactions table for slot occupancy and ammo
            if await _table_missing(session, 'item_slot_interactions'):
                print("   📝 Creating item_slot_interactions table...")
                if dialect == 'postgresql':
                    await session.execute(text("""
                        CREATE TABLE IF NOT EXISTS item_slot_interactions (
                            id BIGSERIAL PRIMARY KEY,
                            guild_id BIGINT NOT NULL,
                            attribute_def_id BIGINT NOT NULL REFERENCES attribute_definitions(id),
                            item_name VARCHAR(200),
                            primary_slot VARCHAR(50) NOT NULL,
                            occupies_slots JSONB,
                            requires_empty_slots JSONB,
                            requires_item_in_slot JSONB,
                            blocks_slots JSONB,
                            requires_ammo BOOLEAN DEFAULT FALSE,
                            required_ammo_type VARCHAR(50),
                            ammo_consumption_rate INTEGER DEFAULT 1,
                            ammo_capacity INTEGER,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        );
                        CREATE INDEX IF NOT EXISTS idx_item_slot_guild_id ON item_slot_interactions(guild_id);
                        CREATE INDEX IF NOT EXISTS idx_item_slot_attr_id ON item_slot_interactions(attribute_def_id);
                    """))
                else:  # SQLite
                    await session.execute(text("""
                        CREATE TABLE IF NOT EXISTS item_slot_interactions (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            guild_id INTEGER NOT NULL,
                            attribute_def_id INTEGER NOT NULL REFERENCES attribute_definitions(id),
                            item_name VARCHAR(200),
                            primary_slot VARCHAR(50) NOT NULL,
                            occupies_slots TEXT,
                            requires_empty_slots TEXT,
                            requires_item_in_slot TEXT,
                            blocks_slots TEXT,
                            requires_ammo INTEGER DEFAULT 0,
                            required_ammo_type VARCHAR(50),
                            ammo_consumption_rate INTEGER DEFAULT 1,
                            ammo_capacity INTEGER,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        );
                        CREATE INDEX IF NOT EXISTS idx_item_slot_guild_id ON item_slot_interactions(guild_id);
                        CREATE INDEX IF NOT EXISTS idx_item_slot_attr_id ON item_slot_interactions(attribute_def_id);
                    """))
                migrations_run += 1

            # Migration 66: Add ammo fields to attribute_definitions
            if await _column_missing(session, 'attribute_definitions', 'requires_ammo'):
                print("   📝 Adding ammo fields to attribute_definitions table...")
                if dialect == 'postgresql':
                    await session.execute(text("""
                        ALTER TABLE attribute_definitions
                        ADD COLUMN IF NOT EXISTS requires_ammo BOOLEAN DEFAULT FALSE,
                        ADD COLUMN IF NOT EXISTS required_ammo_type VARCHAR(50),
                        ADD COLUMN IF NOT EXISTS ammo_consumption_rate INTEGER DEFAULT 1,
                        ADD COLUMN IF NOT EXISTS is_ammo BOOLEAN DEFAULT FALSE,
                        ADD COLUMN IF NOT EXISTS ammo_type VARCHAR(50),
                        ADD COLUMN IF NOT EXISTS ammo_stack_size INTEGER DEFAULT 99,
                        ADD COLUMN IF NOT EXISTS occupies_slots JSONB,
                        ADD COLUMN IF NOT EXISTS blocks_slots JSONB;
                    """))
                else:  # SQLite
                    # SQLite doesn't support ADD COLUMN IF NOT EXISTS, so check each column
                    columns_to_add = [
                        ('requires_ammo', 'INTEGER DEFAULT 0'),
                        ('required_ammo_type', 'VARCHAR(50)'),
                        ('ammo_consumption_rate', 'INTEGER DEFAULT 1'),
                        ('is_ammo', 'INTEGER DEFAULT 0'),
                        ('ammo_type', 'VARCHAR(50)'),
                        ('ammo_stack_size', 'INTEGER DEFAULT 99'),
                        ('occupies_slots', 'TEXT'),
                        ('blocks_slots', 'TEXT')
                    ]

                    for col_name, col_type in columns_to_add:
                        if await _column_missing(session, 'attribute_definitions', col_name):
                            await session.execute(text(f"""
                                ALTER TABLE attribute_definitions ADD COLUMN {col_name} {col_type};
                            """))
                migrations_run += 1

            # Migration 67: Add item leveling and evolution fields to attribute_definitions
            if await _column_missing(session, 'attribute_definitions', 'is_levelable'):
                print("   📝 Adding item leveling/evolution fields to attribute_definitions...")
                if dialect == 'postgresql':
                    await session.execute(text("""
                        ALTER TABLE attribute_definitions
                        ADD COLUMN IF NOT EXISTS is_levelable BOOLEAN DEFAULT FALSE,
                        ADD COLUMN IF NOT EXISTS max_item_level INTEGER DEFAULT 1,
                        ADD COLUMN IF NOT EXISTS exp_per_level INTEGER DEFAULT 100,
                        ADD COLUMN IF NOT EXISTS level_exp_formula TEXT,
                        ADD COLUMN IF NOT EXISTS stat_scaling_per_level JSONB,
                        ADD COLUMN IF NOT EXISTS can_evolve BOOLEAN DEFAULT FALSE,
                        ADD COLUMN IF NOT EXISTS evolution_level_requirement INTEGER,
                        ADD COLUMN IF NOT EXISTS evolution_material_requirements JSONB,
                        ADD COLUMN IF NOT EXISTS evolution_stat_requirements JSONB,
                        ADD COLUMN IF NOT EXISTS evolution_options JSONB,
                        ADD COLUMN IF NOT EXISTS evolves_from VARCHAR(100),
                        ADD COLUMN IF NOT EXISTS evolution_tree_tier INTEGER DEFAULT 1;
                    """))
                else:  # SQLite
                    columns_to_add = [
                        ('is_levelable', 'INTEGER DEFAULT 0'),
                        ('max_item_level', 'INTEGER DEFAULT 1'),
                        ('exp_per_level', 'INTEGER DEFAULT 100'),
                        ('level_exp_formula', 'TEXT'),
                        ('stat_scaling_per_level', 'TEXT'),
                        ('can_evolve', 'INTEGER DEFAULT 0'),
                        ('evolution_level_requirement', 'INTEGER'),
                        ('evolution_material_requirements', 'TEXT'),
                        ('evolution_stat_requirements', 'TEXT'),
                        ('evolution_options', 'TEXT'),
                        ('evolves_from', 'VARCHAR(100)'),
                        ('evolution_tree_tier', 'INTEGER DEFAULT 1')
                    ]

                    for col_name, col_type in columns_to_add:
                        if await _column_missing(session, 'attribute_definitions', col_name):
                            await session.execute(text(f"""
                                ALTER TABLE attribute_definitions ADD COLUMN {col_name} {col_type};
                            """))
                migrations_run += 1

            # Migration 68: Add item instance leveling fields to character_attributes
            if await _column_missing(session, 'character_attributes', 'item_level'):
                print("   📝 Adding item instance leveling fields to character_attributes...")
                if dialect == 'postgresql':
                    await session.execute(text("""
                        ALTER TABLE character_attributes
                        ADD COLUMN IF NOT EXISTS item_level INTEGER DEFAULT 1,
                        ADD COLUMN IF NOT EXISTS item_exp INTEGER DEFAULT 0,
                        ADD COLUMN IF NOT EXISTS item_total_exp INTEGER DEFAULT 0;
                    """))
                else:  # SQLite
                    columns_to_add = [
                        ('item_level', 'INTEGER DEFAULT 1'),
                        ('item_exp', 'INTEGER DEFAULT 0'),
                        ('item_total_exp', 'INTEGER DEFAULT 0')
                    ]

                    for col_name, col_type in columns_to_add:
                        if await _column_missing(session, 'character_attributes', col_name):
                            await session.execute(text(f"""
                                ALTER TABLE character_attributes ADD COLUMN {col_name} {col_type};
                            """))
                migrations_run += 1

            # Migration 69: Add crafting and economy fields to attribute_definitions
            if await _column_missing(session, 'attribute_definitions', 'is_craftable'):
                print("   📝 Adding crafting/economy fields to attribute_definitions...")
                if dialect == 'postgresql':
                    await session.execute(text("""
                        ALTER TABLE attribute_definitions
                        ADD COLUMN IF NOT EXISTS is_craftable BOOLEAN DEFAULT FALSE,
                        ADD COLUMN IF NOT EXISTS crafting_recipe JSONB,
                        ADD COLUMN IF NOT EXISTS crafting_time INTEGER DEFAULT 0,
                        ADD COLUMN IF NOT EXISTS crafting_skill_requirements JSONB,
                        ADD COLUMN IF NOT EXISTS crafting_level_requirements JSONB,
                        ADD COLUMN IF NOT EXISTS crafting_stat_requirements JSONB,
                        ADD COLUMN IF NOT EXISTS crafting_class_requirements JSONB,
                        ADD COLUMN IF NOT EXISTS crafting_location_requirements JSONB,
                        ADD COLUMN IF NOT EXISTS price_calculation_method VARCHAR(50) DEFAULT 'fixed',
                        ADD COLUMN IF NOT EXISTS material_price_multiplier DOUBLE PRECISION DEFAULT 1.5,
                        ADD COLUMN IF NOT EXISTS enable_supply_demand BOOLEAN DEFAULT FALSE,
                        ADD COLUMN IF NOT EXISTS supply_demand_sensitivity DOUBLE PRECISION DEFAULT 1.0;
                    """))
                else:  # SQLite
                    columns_to_add = [
                        ('is_craftable', 'INTEGER DEFAULT 0'),
                        ('crafting_recipe', 'TEXT'),
                        ('crafting_time', 'INTEGER DEFAULT 0'),
                        ('crafting_skill_requirements', 'TEXT'),
                        ('crafting_level_requirements', 'TEXT'),
                        ('crafting_stat_requirements', 'TEXT'),
                        ('crafting_class_requirements', 'TEXT'),
                        ('crafting_location_requirements', 'TEXT'),
                        ('price_calculation_method', 'VARCHAR(50) DEFAULT ''fixed'''),
                        ('material_price_multiplier', 'REAL DEFAULT 1.5'),
                        ('enable_supply_demand', 'INTEGER DEFAULT 0'),
                        ('supply_demand_sensitivity', 'REAL DEFAULT 1.0')
                    ]

                    for col_name, col_type in columns_to_add:
                        if await _column_missing(session, 'attribute_definitions', col_name):
                            await session.execute(text(f"""
                                ALTER TABLE attribute_definitions ADD COLUMN {col_name} {col_type};
                            """))
                migrations_run += 1

            # Migration 70: Add creator tracking fields to character_attributes
            if await _column_missing(session, 'character_attributes', 'is_player_crafted'):
                print("   📝 Adding creator tracking fields to character_attributes...")
                if dialect == 'postgresql':
                    await session.execute(text("""
                        ALTER TABLE character_attributes
                        ADD COLUMN IF NOT EXISTS is_player_crafted BOOLEAN DEFAULT FALSE,
                        ADD COLUMN IF NOT EXISTS crafted_by_character_id BIGINT,
                        ADD COLUMN IF NOT EXISTS crafted_by_player_id BIGINT,
                        ADD COLUMN IF NOT EXISTS crafter_name VARCHAR(200),
                        ADD COLUMN IF NOT EXISTS crafted_at TIMESTAMP;
                    """))
                else:  # SQLite
                    columns_to_add = [
                        ('is_player_crafted', 'INTEGER DEFAULT 0'),
                        ('crafted_by_character_id', 'INTEGER'),
                        ('crafted_by_player_id', 'INTEGER'),
                        ('crafter_name', 'VARCHAR(200)'),
                        ('crafted_at', 'TIMESTAMP')
                    ]

                    for col_name, col_type in columns_to_add:
                        if await _column_missing(session, 'character_attributes', col_name):
                            await session.execute(text(f"""
                                ALTER TABLE character_attributes ADD COLUMN {col_name} {col_type};
                            """))
                migrations_run += 1

            # Migration 71: Add item leveling requirement types to attribute_definitions
            if await _column_missing(session, 'attribute_definitions', 'item_level_requirement_type'):
                print("   📝 Adding item leveling requirement type fields to attribute_definitions...")
                if dialect == 'postgresql':
                    await session.execute(text("""
                        ALTER TABLE attribute_definitions
                        ADD COLUMN IF NOT EXISTS item_level_requirement_type VARCHAR(50) DEFAULT 'exp',
                        ADD COLUMN IF NOT EXISTS level_material_requirements JSON,
                        ADD COLUMN IF NOT EXISTS level_attribute_requirements JSON,
                        ADD COLUMN IF NOT EXISTS level_hybrid_mode VARCHAR(20) DEFAULT 'all';
                    """))
                else:  # SQLite
                    columns_to_add = [
                        ('item_level_requirement_type', "VARCHAR(50) DEFAULT 'exp'"),
                        ('level_material_requirements', 'TEXT'),
                        ('level_attribute_requirements', 'TEXT'),
                        ('level_hybrid_mode', "VARCHAR(20) DEFAULT 'all'")
                    ]

                    for col_name, col_type in columns_to_add:
                        if await _column_missing(session, 'attribute_definitions', col_name):
                            await session.execute(text(f"""
                                ALTER TABLE attribute_definitions ADD COLUMN {col_name} {col_type};
                            """))
                migrations_run += 1

            # Migration 72: Add socket/modification system to attribute_definitions
            if await _column_missing(session, 'attribute_definitions', 'has_sockets'):
                print("   📝 Adding socket/modification system to attribute_definitions...")
                if dialect == 'postgresql':
                    await session.execute(text("""
                        ALTER TABLE attribute_definitions
                        ADD COLUMN IF NOT EXISTS has_sockets BOOLEAN DEFAULT FALSE,
                        ADD COLUMN IF NOT EXISTS socket_count INTEGER DEFAULT 0,
                        ADD COLUMN IF NOT EXISTS socket_types JSON,
                        ADD COLUMN IF NOT EXISTS allowed_socket_items JSON,
                        ADD COLUMN IF NOT EXISTS socket_stat_multiplier FLOAT DEFAULT 1.0,
                        ADD COLUMN IF NOT EXISTS is_socket_item BOOLEAN DEFAULT FALSE,
                        ADD COLUMN IF NOT EXISTS socket_item_type VARCHAR(50),
                        ADD COLUMN IF NOT EXISTS socket_effects JSON,
                        ADD COLUMN IF NOT EXISTS socket_requirements JSON;
                    """))
                else:  # SQLite
                    columns_to_add = [
                        ('has_sockets', 'INTEGER DEFAULT 0'),
                        ('socket_count', 'INTEGER DEFAULT 0'),
                        ('socket_types', 'TEXT'),
                        ('allowed_socket_items', 'TEXT'),
                        ('socket_stat_multiplier', 'REAL DEFAULT 1.0'),
                        ('is_socket_item', 'INTEGER DEFAULT 0'),
                        ('socket_item_type', 'VARCHAR(50)'),
                        ('socket_effects', 'TEXT'),
                        ('socket_requirements', 'TEXT')
                    ]

                    for col_name, col_type in columns_to_add:
                        if await _column_missing(session, 'attribute_definitions', col_name):
                            await session.execute(text(f"""
                                ALTER TABLE attribute_definitions ADD COLUMN {col_name} {col_type};
                            """))
                migrations_run += 1

            # Migration 73: Add custom naming and socket tracking to character_attributes
            if await _column_missing(session, 'character_attributes', 'custom_name'):
                print("   📝 Adding custom naming and socket tracking to character_attributes...")
                if dialect == 'postgresql':
                    await session.execute(text("""
                        ALTER TABLE character_attributes
                        ADD COLUMN IF NOT EXISTS custom_name VARCHAR(200),
                        ADD COLUMN IF NOT EXISTS custom_name_set_at TIMESTAMP,
                        ADD COLUMN IF NOT EXISTS custom_name_set_by BIGINT,
                        ADD COLUMN IF NOT EXISTS socketed_items JSON,
                        ADD COLUMN IF NOT EXISTS socket_modifications JSON,
                        ADD COLUMN IF NOT EXISTS total_sockets_used INTEGER DEFAULT 0;
                    """))
                else:  # SQLite
                    columns_to_add = [
                        ('custom_name', 'VARCHAR(200)'),
                        ('custom_name_set_at', 'TIMESTAMP'),
                        ('custom_name_set_by', 'INTEGER'),
                        ('socketed_items', 'TEXT'),
                        ('socket_modifications', 'TEXT'),
                        ('total_sockets_used', 'INTEGER DEFAULT 0')
                    ]

                    for col_name, col_type in columns_to_add:
                        if await _column_missing(session, 'character_attributes', col_name):
                            await session.execute(text(f"""
                                ALTER TABLE character_attributes ADD COLUMN {col_name} {col_type};
                            """))
                migrations_run += 1

            # Migration 74: Add item weight system fields
            if await _column_missing(session, 'server_config', 'item_weight_enabled'):
                print("  → Running migration 74: Adding item weight system...")
                await session.execute(text("""
                    ALTER TABLE server_config ADD COLUMN item_weight_enabled BOOLEAN DEFAULT FALSE;
                """))
                migrations_run += 1

            if await _column_missing(session, 'attribute_definitions', 'item_weight'):
                print("  → Running migration 74b: Adding item_weight column...")
                await session.execute(text("""
                    ALTER TABLE attribute_definitions ADD COLUMN item_weight FLOAT DEFAULT 0.0;
                """))
                migrations_run += 1

            # Migration 75: Add visibility and requirements fields to items
            if await _column_missing(session, 'attribute_definitions', 'visibility'):
                print("  → Running migration 75: Adding visibility and requirements fields...")
                await session.execute(text("""
                    ALTER TABLE attribute_definitions ADD COLUMN visibility VARCHAR(50) DEFAULT 'everyone';
                """))
                migrations_run += 1

            if await _column_missing(session, 'attribute_definitions', 'allowed_roles'):
                print("  → Running migration 75b: Adding allowed_roles column...")
                await session.execute(text("""
                    ALTER TABLE attribute_definitions ADD COLUMN allowed_roles JSON;
                """))
                migrations_run += 1

            if await _column_missing(session, 'attribute_definitions', 'allowed_classes'):
                print("  → Running migration 75c: Adding allowed_classes column...")
                await session.execute(text("""
                    ALTER TABLE attribute_definitions ADD COLUMN allowed_classes JSON;
                """))
                migrations_run += 1

            if await _column_missing(session, 'attribute_definitions', 'requirements'):
                print("  → Running migration 75d: Adding requirements column...")
                await session.execute(text("""
                    ALTER TABLE attribute_definitions ADD COLUMN requirements JSON;
                """))
                migrations_run += 1

            # Migration 76: Add permissions_applied field to verification_system
            if await _column_missing(session, 'verification_system', 'permissions_applied'):
                print("  → Running migration 76: Adding permissions_applied to verification_system...")
                await session.execute(text("""
                    ALTER TABLE verification_system ADD COLUMN permissions_applied BOOLEAN DEFAULT FALSE;
                """))
                migrations_run += 1

            # Migration 77: Add approved character fields for RP channels
            if await _column_missing(session, 'verification_system', 'rp_channels_require_approved'):
                print("  → Running migration 77: Adding approved character fields...")
                await session.execute(text("""
                    ALTER TABLE verification_system ADD COLUMN rp_channels_require_approved BOOLEAN DEFAULT FALSE;
                """))
                migrations_run += 1

            if await _column_missing(session, 'verification_system', 'approved_character_role_id'):
                print("  → Running migration 77b: Adding approved_character_role_id column...")
                await session.execute(text("""
                    ALTER TABLE verification_system ADD COLUMN approved_character_role_id BIGINT;
                """))
                migrations_run += 1

            # Migration 78: Add multi-page support to welcome_system
            if await _column_missing(session, 'welcome_system', 'welcome_pages'):
                print("  → Running migration 78: Adding multi-page support to welcome_system...")
                await session.execute(text("""
                    ALTER TABLE welcome_system ADD COLUMN welcome_pages JSON DEFAULT '[]';
                """))
                migrations_run += 1

            if await _column_missing(session, 'welcome_system', 'setup_by'):
                print("  → Running migration 78b: Adding setup_by to welcome_system...")
                await session.execute(text("""
                    ALTER TABLE welcome_system ADD COLUMN setup_by BIGINT;
                """))
                migrations_run += 1

            # Migration 79: Add games_category_id to server_config for game channel organization
            if await _column_missing(session, 'server_config', 'games_category_id'):
                print("  → Running migration 79: Adding games_category_id to server_config...")
                await session.execute(text("""
                    ALTER TABLE server_config ADD COLUMN games_category_id BIGINT;
                """))
                migrations_run += 1

            # ============================================================================
            # END MIGRATIONS
            # ============================================================================

            await session.commit()

            if migrations_run > 0:
                print(f"[OK] Applied {migrations_run} migration(s)")
            else:
                print("✅ Database schema is up to date")

        except Exception as e:
            await session.rollback()
            print(f"❌ Migration error: {e}")
            print("   You can run manual migrations using: python scripts/run_migrations_simple.py")
            # Don't raise - allow bot to continue even if migrations fail


async def _column_missing(session, table_name: str, column_name: str) -> bool:
    """Check if a column is missing from a table using information_schema"""
    dialect = session.bind.dialect.name

    if dialect == 'postgresql':
        # Use PostgreSQL information_schema
        result = await session.execute(text("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = :table_name
            AND column_name = :column_name
        """), {"table_name": table_name, "column_name": column_name})
        return result.fetchone() is None
    else:
        # SQLite: try to select the column
        try:
            await session.execute(text(f"SELECT {column_name} FROM {table_name} LIMIT 1"))
            return False
        except Exception:
            # Roll back the failed query to avoid transaction abort
            await session.rollback()
            return True


async def _table_missing(session, table_name: str) -> bool:
    """Check if a table is missing from the database"""
    dialect = session.bind.dialect.name

    if dialect == 'postgresql':
        # Use PostgreSQL information_schema
        result = await session.execute(text("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            AND table_name = :table_name
        """), {"table_name": table_name})
        return result.fetchone() is None
    else:
        # SQLite: check sqlite_master
        result = await session.execute(text("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name = :table_name
        """), {"table_name": table_name})
        return result.fetchone() is None
