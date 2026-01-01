"""
Server configuration models for initialization and setup
"""
from sqlalchemy import BigInteger, Boolean, Column, DateTime, Integer, String, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
from database.base import Base


class ServerConfig(Base):
    """Store server-wide configuration set during initialization"""
    __tablename__ = "server_config"

    guild_id = Column(BigInteger, primary_key=True)

    # Initialization status
    is_initialized = Column(Boolean, default=False, index=True)
    initialized_at = Column(DateTime, nullable=True)
    initialized_by = Column(BigInteger, nullable=True)  # User ID who ran initialization

    # Character progression system
    # Options: "levels", "power_rating", "both", "none"
    character_system = Column(String, default=None, index=True)

    # System-specific configurations
    # For "levels" system
    max_character_level = Column(Integer, default=None)  # Max level characters can reach
    level_scaling = Column(String, default="linear")  # "linear", "exponential", etc.

    # For "power_rating" system
    min_power_rating = Column(Integer, default=None)
    max_power_rating = Column(Integer, default=None)
    rating_scaling = Column(String, default="linear")

    # For "both" system
    both_level_max = Column(Integer, default=None)
    both_rating_min = Column(Integer, default=None)
    both_rating_max = Column(Integer, default=None)

    # Class System Configuration
    classes_enabled = Column(Boolean, default=True)
    max_classes_per_player = Column(Integer, nullable=True)  # null = unlimited
    class_types_enabled = Column(Boolean, default=False)
    max_classes_per_type = Column(Integer, nullable=True)  # max of one type per player

    # Race System Configuration
    race_system_enabled = Column(Boolean, default=True)

    # Leveling Configuration
    # "character", "class", or "both"
    leveling_target = Column(String, default=None, nullable=True)

    # Attribute keys for character leveling (references AttributeDefinition.key)
    character_level_attribute_key = Column(String, nullable=True)  # Attribute used for character level (e.g., "level")
    character_exp_attribute_key = Column(String, nullable=True)  # Attribute used for character EXP (e.g., "experience")

    # Per-level reward overrides enabled
    use_per_level_rewards = Column(Boolean, default=False)

    # Resource system for class leveling (if classes enabled and leveling_target is "both" or "class")
    # "exp", "class_points", "stat_points", or None
    class_resource_type = Column(String, default=None, nullable=True)

    # Character leveling reward types (1-4) - DEPRECATED, use fields below instead
    # 1: Skill Points + Attribute Points
    # 2: Attribute Points only
    # 3: Skill Points only
    # 4: Attributes + Skills + Class-based Skill Points (if classes enabled)
    character_leveling_rewards = Column(Integer, default=None, nullable=True)

    # Character leveling reward configuration (new system)
    attribute_points_per_level = Column(Integer, default=0, nullable=True)  # How many attribute points per level
    skill_points_per_level = Column(Integer, default=0, nullable=True)  # How many skill points per level

    # Class leveling reward types (1-7, only if classes enabled)
    # 1: Attribute Points
    # 2: Class Skills
    # 3: Skill Points
    # 4: Attributes + Class Skills
    # 5: Attributes + Skill Points
    # 6: Class Skills + Skill Points
    # 7: All 3 (Attributes + Class Skills + Skill Points)
    class_leveling_rewards = Column(Integer, default=None, nullable=True)

    # Note: max_character_level is defined above at line 30
    # Use -1 to represent "infinite" (no level cap)
    # Examples: 50, 100, 999, 12345 (custom), -1 (infinite)
    class_max_level = Column(BigInteger, default=None, nullable=True)

    # Player Submission Permissions
    allow_class_submissions = Column(Boolean, default=False)
    allow_skill_submissions = Column(Boolean, default=False)
    allow_technique_submissions = Column(Boolean, default=False)

    # General settings
    require_backstory = Column(Boolean, default=False)
    auto_level_on_join = Column(Boolean, default=False)

    # Item System Settings
    item_weight_enabled = Column(Boolean, default=False)

    # ===== CROSS-SERVER LINKING FIELDS =====
    is_linked = Column(Boolean, default=False)
    link_type = Column(String, nullable=True)  # "settings_copy" or "database_link"
    source_guild_id = Column(BigInteger, nullable=True)  # Source server if this is a linked server
    link_code_id = Column(UUID(as_uuid=True), ForeignKey('link_codes.id'), nullable=True)
    shared_database_id = Column(UUID(as_uuid=True), ForeignKey('shared_databases.id'), nullable=True)
    last_link_sync = Column(DateTime, nullable=True)

    # ===== LEVEL PROGRESSION CONFIGURATION =====
    # How EXP requirements are calculated
    # Options: "formula" (use math formula) or "manual" (custom per level)
    level_progression_type = Column(String, default="formula", nullable=True)

    # Formula-based progression (when level_progression_type = "formula")
    # Options: "linear", "exponential", "logarithmic", "polynomial", "custom"
    level_formula_type = Column(String, default="exponential", nullable=True)

    # Formula parameters (JSON object with formula-specific values)
    # Example for exponential: {"base": 100, "multiplier": 1.5, "offset": 0}
    # Example for linear: {"base": 100, "increment": 50}
    # Example for polynomial: {"base": 100, "power": 2, "coefficient": 1.2}
    level_formula_params = Column(JSON, nullable=True)

    # Manual EXP thresholds (when level_progression_type = "manual")
    # JSON array: [100, 250, 450, 700, ...] for levels 1, 2, 3, 4, ...
    level_exp_thresholds = Column(JSON, nullable=True)

    # ===== CLASS LEVELING PROGRESSION CONFIGURATION =====
    # How class leveling requirements are calculated
    # Options: "formula" (use math formula) or "manual" (custom per level)
    class_level_progression_type = Column(String, default="formula", nullable=True)

    # Formula-based progression for classes (when class_level_progression_type = "formula")
    # Options: "linear", "exponential", "logarithmic", "polynomial", "custom"
    class_level_formula_type = Column(String, default="exponential", nullable=True)

    # Formula parameters for class leveling (JSON object with formula-specific values)
    # Example for exponential: {"base": 100, "multiplier": 1.5, "offset": 0}
    # Example for linear: {"base": 100, "increment": 50}
    # Example for polynomial: {"base": 100, "power": 2, "coefficient": 1.2}
    class_level_formula_params = Column(JSON, nullable=True)

    # Manual resource thresholds for classes (when class_level_progression_type = "manual")
    # JSON array: [100, 250, 450, 700, ...] for levels 1, 2, 3, 4, ...
    # Used for EXP, Skill Points, or Stat Points depending on class_resource_type
    class_level_thresholds = Column(JSON, nullable=True)

    # ===== GAME SETTINGS (consolidated from GuildSettings) =====
    # Game difficulty affects exp costs, roll chances, etc.
    difficulty_level = Column(Integer, default=1)  # 1-10

    # Character slots per player
    max_character_slots = Column(Integer, default=3)  # 1-6

    # Starting money for new characters
    starting_money = Column(Integer, default=2000)

    # Game channel category - where multiplayer game channels are created
    games_category_id = Column(BigInteger, nullable=True)  # Discord category ID

    # ===== ITEM SYSTEM FIELDS =====
    items_enabled = Column(Boolean, default=False)
    combat_system_enabled = Column(Boolean, default=False)
    item_types = Column(JSON, nullable=True)  # Custom item type definitions
    item_leveling_enabled = Column(Boolean, default=False)
    item_max_level = Column(BigInteger, nullable=True)
    item_ranking_enabled = Column(Boolean, default=False)
    item_stat_integration = Column(JSON, nullable=True)

    # ===== PROGRESSION SYSTEMS =====
    skills_techniques_leveling_enabled = Column(Boolean, default=False)  # Allow skills and techniques to level up

    # ===== MISC SYSTEM FIELDS (WIP) =====
    map_system_enabled = Column(Boolean, default=False)
    farm_system_enabled = Column(Boolean, default=False)
    fish_system_enabled = Column(Boolean, default=False)
    full_econ_enabled = Column(Boolean, default=False)
    mine_system_enabled = Column(Boolean, default=False)

    # ===== STATS & DICE ROLLING CONFIGURATION =====
    # How stats are used in rolls/combat
    # Options: "dice_vs_dice" (pure dice rolls), "dice_vs_stats" (dice vs stat values), "stats_vs_stats" (stat values vs stat values)
    stats_rolling_method = Column(String, default="dice_vs_dice", nullable=True)

    # How stats are displayed
    # Options: "letter_rank" (S, A, B, C, D, E, F ranks), "numeric_level" (1-100 numeric values)
    stats_display_format = Column(String, default="numeric_level", nullable=True)

    # ===== PROFILE DISPLAY CONFIGURATION =====
    # Profile template style
    profile_template = Column(String, default="card", nullable=True)  # card, compact, detailed, rpg_sheet
    profile_image_position = Column(String, default="right", nullable=True)  # left, right, top, bottom, none
    profile_image_size = Column(String, default="medium", nullable=True)  # small, medium, large
    profile_show_separators = Column(Boolean, default=True)  # Show separator lines between sections
    profile_footer_text = Column(String(200), nullable=True)  # Custom footer text
    profile_show_character_id = Column(Boolean, default=True)  # Show character ID in footer

    # Basic info field configuration (JSON array of field keys in order)
    # Default: ["name", "age", "class", "level"]
    # Available: name, age, class, level, race, guild, rank, + any custom stat key
    profile_basic_info_fields = Column(JSON, nullable=True)

    # ===== CLASS SYSTEM DEFAULT ATTRIBUTES =====
    # Default attributes for all classes (can be overridden per-class)
    default_class_exp_attribute_key = Column(String(100), nullable=True)  # Default exp attribute for all classes (e.g., "class_exp")
    default_class_level_attribute_key = Column(String(100), nullable=True)  # Default level attribute for all classes (e.g., "class_level")

    # Class subtype restrictions
    allow_multiple_subtypes = Column(Boolean, default=False)  # Can players have multiple classes of the same subtype?

    # Last updated
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class RolePermissionLevel(Base):
    """Store permission levels for roles and users (Level 0-10 hierarchy)"""
    __tablename__ = "role_permission_levels"

    id = Column(Integer, primary_key=True, autoincrement=True)
    guild_id = Column(BigInteger, index=True, nullable=False)
    role_id = Column(BigInteger, nullable=True, index=True)
    user_id = Column(BigInteger, nullable=True, index=True)

    # Permission levels:
    # Level 0: Regular Player (no admin access, default)
    # Level 1-8: Custom roles (user-defined hierarchy)
    # Level 9: Co-owner (full permissions management)
    # Level 10: Server Owner (auto-assigned, full control)
    permission_level = Column(Integer, nullable=False)  # 0-10

    set_at = Column(DateTime, default=datetime.utcnow)
    set_by = Column(BigInteger, nullable=True)  # User who set this permission


class CommandPermissionOverride(Base):
    """Store command-specific permission overrides for fine-grained control"""
    __tablename__ = "command_permission_overrides"

    id = Column(Integer, primary_key=True, autoincrement=True)
    guild_id = Column(BigInteger, index=True, nullable=False)
    command_name = Column(String, nullable=False, index=True)  # e.g., "grant_exp", "settings_dashboard"

    # Minimum permission level required to use this command
    # Overrides the default permission level for the command
    required_level = Column(Integer, nullable=False)  # 0-10

    set_at = Column(DateTime, default=datetime.utcnow)
    set_by = Column(BigInteger, nullable=True)  # User who set this override


# ===== CROSS-SERVER LINKING MODELS =====

class LinkCode(Base):
    """
    Stores link codes for cross-server configuration sharing

    Code Types:
    - settings_copy: One-time use, expires in 7 days, copies settings snapshot
    - database_link: Unlimited uses, never expires, creates real-time database sync
    """
    __tablename__ = 'link_codes'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code = Column(String(14), unique=True, nullable=False, index=True)  # Format: XXXX-XXXX-XXXX
    source_guild_id = Column(BigInteger, nullable=False, index=True)

    # Code types: "settings_copy" or "database_link"
    code_type = Column(String(20), nullable=False)

    # Metadata
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    created_by = Column(BigInteger, nullable=False)  # Discord User ID
    expires_at = Column(DateTime, nullable=True)  # NULL for database_link (never expires)

    # Usage tracking
    usage_count = Column(Integer, default=0)
    max_uses = Column(Integer, nullable=True)  # NULL = unlimited
    is_active = Column(Boolean, default=True)
    revoked_at = Column(DateTime, nullable=True)
    revoked_by = Column(BigInteger, nullable=True)

    # Snapshot of configuration at time of code generation (for settings_copy)
    config_snapshot = Column(JSON, nullable=True)


class ServerLink(Base):
    """
    Tracks relationships between linked servers

    Link Types:
    - settings_copy: One-way copy of settings from source to target
    - database_link: Two-way database sharing with real-time sync
    """
    __tablename__ = 'server_links'

    id = Column(Integer, primary_key=True, autoincrement=True)
    source_guild_id = Column(BigInteger, nullable=False, index=True)
    target_guild_id = Column(BigInteger, nullable=False, index=True)

    # Link types: "settings_copy" or "database_link"
    link_type = Column(String(20), nullable=False)

    # Linking metadata
    linked_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    linked_by = Column(BigInteger, nullable=False)  # User who applied code
    link_code_id = Column(UUID(as_uuid=True), ForeignKey('link_codes.id'), nullable=True)

    # For database_link type only
    shared_database_id = Column(UUID(as_uuid=True), ForeignKey('shared_databases.id'), nullable=True)
    last_sync_at = Column(DateTime, nullable=True)

    # Disconnection
    is_active = Column(Boolean, default=True)
    disconnected_at = Column(DateTime, nullable=True)
    disconnected_by = Column(BigInteger, nullable=True)


class SharedDatabase(Base):
    """
    Manages multi-server database sharing for database_link type

    A shared database allows multiple servers to share the same character data,
    items, and game state in real-time for a unified multi-server world.
    """
    __tablename__ = 'shared_databases'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    primary_guild_id = Column(BigInteger, nullable=False, index=True)  # Original server that created this

    # Metadata
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    created_by = Column(BigInteger, nullable=False)

    # Configuration
    is_active = Column(Boolean, default=True)

    # Statistics (can be updated periodically)
    total_linked_servers = Column(Integer, default=1)
    total_characters = Column(Integer, default=0)
    total_items = Column(Integer, default=0)
