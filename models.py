"""
Database models - Consolidated imports from split model files
"""
# Import base and core models from split files
from database.base import Base
from database.models_core import User, Character, Basic, Clan
from database.models_verification import VerificationSystem, UserVerification, PendingVerification
from database.models_server_config import (
    ServerConfig, RolePermissionLevel, CommandPermissionOverride,
    LinkCode, ServerLink, SharedDatabase
)
from database.models_systems import (
    Race, RaceRequirement, RaceBonus, RaceEvolution, RaceLevelBonus, RaceFusion, RaceAutoStat,
    Class, ClassRequirement, ClassBonus, ClassLevelConfig, ClassLevelRequirement, ClassLevelReward,
    ClassEvolution, ClassFusion, ClassAutoStat,
    StatPool, StatCategory, StatDefinition, CharacterStat, TemporaryStat, StatHistory, StatCondition, StatValueRule,
    WelcomeSystem, AlertSystem, ProfileSection
)
# Import unified attribute system models (v2.0.0)
from database.models_attributes import (
    AttributeDefinition, CharacterAttribute, AttributeHistory
)
# Import equipment system models
from database.models_equipment import (
    EquipmentSlotDefinition, ItemSlotInteraction
)
# Import refactored gacha system models
from database.models_gacha import (
    GachaCoin, GachaMachine, GachaRank, GachaReward,
    GachaCoinBalance, GachaRegistration, GachaPityCounter, GachaCombo, GachaRollHistory
)
# Import economy system models
from database.models_economy import (
    IncomeBracket, ClanIncomeBonus, GuildCooldowns, CharacterCooldowns,
    IncomeTransaction, MoneyTransaction
)
# Import lifetime tier models
from database.models_lifetime_tiers import (
    LifetimeTierGrant, BetaSupporterMilestone, UserLifetimeBenefit,
    ServerLifetimeBenefits, TierUpgradeDiscount, BetaDonationProgress
)
# Import payment pool models
from database.models_payment_pool import (
    ServerPaymentPool, PoolContribution, PoolPayment,
    PoolContributor, PoolTransaction, PoolNotification
)
# Import usage tracking models
from database.models_usage_tracking import (
    ServerUsageMetrics, UsageEventLog, UsageBillingPeriod,
    UsagePricingTier, ServerBillingConfig, UsageSnapshot
)
# Import roleplay info models (if exists)
try:
    from database.models_roleplay_info import *
except ImportError:
    pass
# Import reaction role models
from database.reaction_role_models import (
    ReactionRolePanel as ReactionRolePanelModel,
    ReactionRole, ReactionRoleLog
)

# Standard imports for remaining models
from sqlalchemy import BigInteger, Boolean, Column, Float, ForeignKey, Integer, String, DateTime, UniqueConstraint, Index, JSON, Text
from sqlalchemy.orm import relationship
from datetime import datetime

# Session factory for compatibility with older code
def SessionLocal():
    """Get a database session - compatibility function for older cogs"""
    from database.db_manager import DatabaseManager
    return DatabaseManager.get_session()

# ============================================================================
# COMMAND LOGGING
# ============================================================================

class CommandLog(Base):
    """
    Tracks all command executions for audit and monitoring purposes
    Used by both player and admin bots
    """
    __tablename__ = "command_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    guild_id = Column(BigInteger, nullable=False, index=True)
    user_id = Column(BigInteger, nullable=False, index=True)
    username = Column(String(100), nullable=False)
    command_name = Column(String(100), nullable=False, index=True)
    channel_id = Column(BigInteger, nullable=True)
    channel_name = Column(String(100), nullable=True)
    changes = Column(String(500), nullable=True)  # What changed (brief description)
    target_id = Column(BigInteger, nullable=True)  # Target user/entity ID
    target_name = Column(String(100), nullable=True)  # Target user/entity name
    highest_role = Column(String(100), nullable=True)  # User's highest role at time of command
    bot_type = Column(String(20), nullable=False)  # "player" or "admin"
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    def __repr__(self):
        return f"<CommandLog(id={self.id}, command={self.command_name}, user={self.username}, bot={self.bot_type})>"

# ============================================================================
# STAT EFFECTS & MODIFIERS
# ============================================================================

class StatEffect(Base):
    """
    Defines how stats and techniques affect each other

    Supported relationships:
    - Stat → Stat: Defense → HP, Fire Affinity → Fire Damage
    - Stat → Technique: Strength → Melee Damage, Intelligence → Spell Power
    - Technique → Stat: Using Fire Blast → Fire Affinity (temporary)
    - Technique → Technique: Mastery Level → Cooldown Reduction

    Examples:
    - Defense → Max HP (+10 HP per Defense point)
    - Strength → Physical Technique Damage (+5% per point)
    - Intelligence → Mana Cost Reduction (-2% per point)
    - Agility → Technique Cooldown (-0.5s per point)
    """
    __tablename__ = "stat_effects"

    id = Column(Integer, primary_key=True, autoincrement=True)
    guild_id = Column(BigInteger, nullable=False, index=True)
    effect_name = Column(String(100), nullable=False)  # Display name for admins
    description = Column(String(500), nullable=True)  # What this effect does

    # Effect scope (what type of relationship this is)
    effect_scope = Column(String(50), nullable=False, default="stat_to_stat")
    # Options: "stat_to_stat", "stat_to_technique", "technique_to_stat", "technique_to_technique"

    # Source (what provides the effect)
    source_stat_key = Column(String(50), nullable=True)  # e.g., "physical_defense" (for stat sources)
    source_stat_name = Column(String(100), nullable=True)  # Display name
    source_technique_key = Column(String(50), nullable=True)  # e.g., "fire_blast" (for technique sources)
    source_technique_name = Column(String(100), nullable=True)  # Display name

    # Target (what gets affected)
    target_stat_key = Column(String(50), nullable=True)  # e.g., "max_hp" (for stat targets)
    target_stat_name = Column(String(100), nullable=True)  # Display name
    target_technique_key = Column(String(50), nullable=True)  # e.g., "all_melee" or specific technique key
    target_technique_name = Column(String(100), nullable=True)  # Display name

    # Application context (for technique-related effects)
    application_context = Column(String(100), nullable=True)
    # Options: "damage", "healing", "cost", "cooldown", "range", "duration", "effectiveness"
    # Examples:
    # - Strength → Melee Techniques (context: "damage")
    # - Intelligence → Spell Cost (context: "cost")
    # - Agility → Movement Techniques (context: "cooldown")

    # Effect configuration
    effect_type = Column(String(50), nullable=False)
    # Options: "per_point", "multiplier", "flat_bonus", "resistance", "percentage", "custom_formula"
    effect_value = Column(Float, nullable=True)  # For simple effects (e.g., 10 for "+10 per point")
    effect_formula = Column(String(500), nullable=True)  # For complex calculations (JSON formula structure)

    # Conditions (optional)
    condition_type = Column(String(50), nullable=True)  # "always", "if_greater", "if_less", "if_equal", "if_has_tag", "custom"
    condition_value = Column(Float, nullable=True)  # Threshold value for conditions
    condition_tags = Column(String(200), nullable=True)  # Comma-separated tags for tag-based conditions

    # Display settings
    show_in_tooltip = Column(Boolean, default=True)  # Show effect in stat/technique tooltips
    tooltip_format = Column(String(200), nullable=True)  # How to display (e.g., "+{value} HP per Defense")

    # Meta
    is_active = Column(Boolean, default=True)
    display_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_by = Column(BigInteger, nullable=False)

    __table_args__ = (
        Index('idx_stat_effects_guild_scope', 'guild_id', 'effect_scope'),
        Index('idx_stat_effects_guild_source_stat', 'guild_id', 'source_stat_key'),
        Index('idx_stat_effects_guild_target_stat', 'guild_id', 'target_stat_key'),
        Index('idx_stat_effects_guild_source_tech', 'guild_id', 'source_technique_key'),
        Index('idx_stat_effects_guild_target_tech', 'guild_id', 'target_technique_key'),
    )

    def __repr__(self):
        source = self.source_stat_key or self.source_technique_key or "unknown"
        target = self.target_stat_key or self.target_technique_key or "unknown"
        return f"<StatEffect(id={self.id}, name={self.effect_name}, {source}→{target})>"


class StatEffectPreset(Base):
    """
    Preset configurations for common stat effect setups
    Helps admins quickly configure standard systems (HP, damage, resistance)
    """
    __tablename__ = "stat_effect_presets"

    id = Column(Integer, primary_key=True, autoincrement=True)
    preset_name = Column(String(100), nullable=False)  # e.g., "Physical Combat System"
    preset_category = Column(String(50), nullable=False)  # "combat", "defense", "magic", "custom"
    description = Column(String(500), nullable=False)

    # Preset configuration (JSON)
    # Contains array of effect definitions that will be created
    preset_config = Column(String(5000), nullable=False)

    # Requirements
    required_stats = Column(String(500), nullable=True)  # Comma-separated list of stat keys needed

    # Meta
    is_builtin = Column(Boolean, default=False)  # True for system presets, False for user-created
    usage_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<StatEffectPreset(id={self.id}, name={self.preset_name}, category={self.preset_category})>"

# ============================================================================
# ITEMS & INVENTORY
# ============================================================================

class Inventory(Base):
    __tablename__ = "inventory"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    character_id = Column(BigInteger, ForeignKey("characters.id"))
    item_name = Column(String)
    item_rank = Column(String)  # E, D, C, B, A, S
    item_exp = Column(Integer)
    is_consumed = Column(Boolean, default=False)
    received_at = Column(DateTime, default=datetime.utcnow)

    character = relationship("Character", back_populates="inventory")


class Item(Base):
    """
    Flexible Item System

    Supports any custom stats via stat_effects JSON field.
    Items can grant bonuses, be equipped, consumed, traded, etc.
    """
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    guild_id = Column(BigInteger, nullable=False, index=True, default=0)  # 0 = global/default items
    item_key = Column(String(100), nullable=False, index=True)  # Unique identifier (e.g., "iron_sword")
    item_name = Column(String(200), nullable=False)  # Display name
    description = Column(String(1000), nullable=True)  # Item description
    icon_emoji = Column(String(50), nullable=True)  # Display emoji

    # Categorization
    item_type = Column(String(100), nullable=True)  # Weapon, Armor, Consumable, Material, Quest, etc.
    item_rarity = Column(String(50), nullable=True)  # Common, Uncommon, Rare, Epic, Legendary, etc.
    item_tags = Column(JSON, nullable=True)  # Array of tags: ["sword", "one-handed", "metal"]

    # Stat Effects (Flexible system)
    # JSON format: {"stat_key": bonus_value, ...}
    # Example: {"strength": 10, "hp": 50, "critical_chance": 5.5}
    stat_effects = Column(JSON, nullable=True)

    # Requirements (who can use this item)
    # JSON format: {"stat_requirements": {"level": 10, "strength": 15}, "class_requirements": ["warrior", "knight"]}
    requirements = Column(JSON, nullable=True)

    # Item Properties
    is_equippable = Column(Boolean, default=False)
    equipment_slot = Column(String(50), nullable=True)  # weapon, head, chest, legs, accessory, etc.
    is_consumable = Column(Boolean, default=False)
    is_stackable = Column(Boolean, default=True)
    max_stack_size = Column(Integer, default=99)
    is_tradeable = Column(Boolean, default=True)
    is_sellable = Column(Boolean, default=True)
    is_quest_item = Column(Boolean, default=False)

    # Economy
    base_value = Column(Integer, default=0)  # Base gold/currency value
    sell_value = Column(Integer, nullable=True)  # Sell price (null = base_value * 0.5)

    # Usage effects (for consumables)
    # JSON format: {"heal_hp": 50, "restore_mana": 30, "grant_buffs": ["buff_id_1", "buff_id_2"]}
    on_use_effects = Column(JSON, nullable=True)
    use_cooldown = Column(Integer, default=0)  # Cooldown in turns (not seconds)

    # Visual & Display
    display_order = Column(Integer, default=0)
    color = Column(String(7), nullable=True)  # Hex color for rarity

    # Metadata
    created_by = Column(BigInteger, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index('idx_items_guild_key', 'guild_id', 'item_key', unique=True),
        Index('idx_items_guild_type', 'guild_id', 'item_type'),
    )


class StatBonus(Base):
    """Track active stat bonuses on characters from various sources"""
    __tablename__ = "stat_bonuses"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    character_id = Column(BigInteger, ForeignKey("characters.id"), nullable=False, index=True)
    stat_key = Column(String(100), nullable=False, index=True)  # Which stat is affected
    bonus_value = Column(Float, nullable=False)  # Amount of bonus (can be negative)

    # Source tracking
    source_type = Column(String(50), nullable=False, index=True)  # 'item', 'buff', 'ability', 'race', 'class', 'technique'
    source_id = Column(BigInteger, nullable=True)  # ID of item, ability, etc.
    source_name = Column(String(200), nullable=True)  # Human-readable source name

    # Duration tracking (for temporary bonuses)
    is_temporary = Column(Boolean, default=False)
    duration_turns = Column(Integer, nullable=True)  # Duration in turns (null = permanent)
    turns_remaining = Column(Integer, nullable=True)  # How many turns left (decrements each turn)

    # Stacking rules
    stacks = Column(Boolean, default=True)  # Whether this bonus stacks with others from same source
    stack_count = Column(Integer, default=1)  # How many times this bonus is applied

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index('idx_stat_bonuses_char_stat', 'character_id', 'stat_key'),
        Index('idx_stat_bonuses_source', 'source_type', 'source_id'),
    )


class ShopInventory(Base):
    """Track items available in the shop"""
    __tablename__ = "shop_inventory"

    id = Column(Integer, primary_key=True, autoincrement=True)
    guild_id = Column(BigInteger, nullable=False, index=True)
    item_id = Column(Integer, ForeignKey("items.id"), nullable=False)

    stock = Column(Integer, default=1)  # -1 for unlimited
    price = Column(Integer, nullable=False)
    is_available = Column(Boolean, default=True)

    # Refresh mechanics
    restocks = Column(Boolean, default=False)
    last_restock = Column(DateTime, nullable=True)

    # Relationships
    item = relationship("Item")

# ============================================================================
# GUILD & SYSTEM SETTINGS
# ============================================================================

class GuildSettings(Base):
    """Store guild-specific settings"""
    __tablename__ = "guild_settings"

    guild_id = Column(BigInteger, primary_key=True)
    difficulty_level = Column(Integer, default=1)  # Game difficulty
    max_character_slots = Column(Integer, default=3)  # Max character slots per player (1-6)
    starting_money = Column(Integer, default=2000)  # Starting money for new characters
    command_log_channel_id = Column(BigInteger, nullable=True)  # Channel for player bot command logs (general-log)
    admin_log_channel_id = Column(BigInteger, nullable=True)  # Channel for admin bot command logs (admin-log)
    transaction_log_channel_id = Column(BigInteger, nullable=True)  # Channel for economy transaction logs (both bots)
    server_rules = Column(String, nullable=True)  # Server rules visible to all users (including unverified)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    used_build_id = Column(Integer, nullable=True)  # Track which build was used


class ClanDefinition(Base):
    """Define custom clans per guild"""
    __tablename__ = "clan_definitions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    guild_id = Column(BigInteger, nullable=False, index=True)
    clan_name = Column(String, nullable=False)
    description = Column(String, default="")

    # Access control
    is_rollable = Column(Boolean, default=True)  # Can be rolled during character creation
    roll_chance = Column(Float, default=0.05)  # 5% default
    requires_admin_approval = Column(Boolean, default=False)

    # Metadata
    created_by = Column(BigInteger, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint('guild_id', 'clan_name', name='unique_guild_clan'),
    )


class GuildPermissions(Base):
    """Store user permissions per guild"""
    __tablename__ = "guild_permissions"

    discord_id = Column(BigInteger, primary_key=True)
    guild_id = Column(BigInteger, primary_key=True)
    permission_level = Column(Integer, default=0)  # 0=Player, 1=Helper, 2=Mod, 3=Admin


class AdminLog(Base):
    """Log admin actions"""
    __tablename__ = "admin_logs"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    guild_id = Column(BigInteger, nullable=False, index=True)
    admin_id = Column(BigInteger, nullable=False, index=True)
    action = Column(String, nullable=False)
    target_user_id = Column(BigInteger, nullable=True, index=True)
    details = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)


class ErrorLog(Base):
    """Log errors for debugging"""
    __tablename__ = "error_logs"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    guild_id = Column(BigInteger, nullable=True, index=True)
    user_id = Column(BigInteger, nullable=True, index=True)
    command_name = Column(String, nullable=True, index=True)
    error_type = Column(String, nullable=False)
    error_message = Column(String, nullable=False)
    stack_trace = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

    # Extra context
    context_data = Column(String, nullable=True)  # JSON string of additional context

# ============================================================================
# SUBMISSIONS & CONTENT
# ============================================================================

class Submission(Base):
    """Track backstory and hatsu submissions"""
    __tablename__ = "submissions"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    guild_id = Column(BigInteger, nullable=False, index=True)
    user_id = Column(BigInteger, nullable=False, index=True)
    character_id = Column(BigInteger, ForeignKey("characters.id"), nullable=False)
    submission_type = Column(String, nullable=False, index=True)  # "backstory", "hatsu", "technique"

    # Content
    title = Column(String)
    content = Column(String, nullable=False)  # Can be text or link to doc
    additional_notes = Column(String)

    # Status
    status = Column(String, default="pending", index=True)  # pending, approved, rejected, revision_requested
    priority = Column(Integer, default=0, index=True)  # Higher = review first

    # Timestamps
    submitted_at = Column(DateTime, default=datetime.utcnow, index=True)
    reviewed_at = Column(DateTime, nullable=True)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    reviews = relationship("SubmissionReview", back_populates="submission", cascade="all, delete-orphan")


class SubmissionReview(Base):
    """Track reviews on submissions"""
    __tablename__ = "submission_reviews"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    submission_id = Column(BigInteger, ForeignKey("submissions.id"), nullable=False)
    reviewer_id = Column(BigInteger, nullable=False, index=True)

    # Review content
    decision = Column(String, nullable=False)  # approved, rejected, revision_requested
    feedback = Column(String)
    private_notes = Column(String)  # Notes only admins can see

    # Metadata
    reviewed_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    submission = relationship("Submission", back_populates="reviews")


class Technique(Base):
    """Combat techniques"""
    __tablename__ = "techniques"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    guild_id = Column(BigInteger, nullable=False, index=True)
    creator_id = Column(BigInteger, nullable=False, index=True)

    # Technique details
    technique_name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    technique_type = Column(String, nullable=False)  # "offensive", "defensive", "support", "movement"

    # Requirements
    required_stats = Column(String)  # JSON: {"offense": 10, "dexterity": 5}
    exp_cost_to_learn = Column(Integer, default=100)

    # Effects
    power = Column(Integer, default=0)
    accuracy = Column(Integer, default=0)
    special_effects = Column(String)  # JSON string

    # Access control
    is_public = Column(Boolean, default=False)
    is_approved = Column(Boolean, default=False)
    requires_permission = Column(Boolean, default=False)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    approved_by = Column(BigInteger, nullable=True)
    approved_at = Column(DateTime, nullable=True)


class TechniquePermission(Base):
    """Track who can use which techniques"""
    __tablename__ = "technique_permissions"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    technique_id = Column(BigInteger, ForeignKey("techniques.id"), nullable=False)
    character_id = Column(BigInteger, ForeignKey("characters.id"), nullable=False)
    granted_by = Column(BigInteger, nullable=False)
    granted_at = Column(DateTime, default=datetime.utcnow)


# ============================================================================
# USER SETTINGS & ACCESS
# ============================================================================

class UserSettings(Base):
    """User preferences"""
    __tablename__ = "user_settings"

    user_id = Column(BigInteger, primary_key=True)
    guild_id = Column(BigInteger, primary_key=True)

    # Privacy settings
    profile_visibility = Column(String, default="public")  # public, private, friends
    allow_dms = Column(Boolean, default=True)

    # UI preferences
    ephemeral_responses = Column(Boolean, default=True)  # Legacy field (kept for compatibility)
    ephemeral_commands = Column(Boolean, default=False)  # Player commands (default: public during beta)
    ephemeral_admin_commands = Column(Boolean, default=False)  # Admin commands (default: public during beta)
    compact_mode = Column(Boolean, default=False)

    # Notification preferences
    notify_on_review = Column(Boolean, default=True)
    notify_on_mention = Column(Boolean, default=True)

    # Updated
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ProfileAccess(Base):
    """Track who can view whose profiles"""
    __tablename__ = "profile_access"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    owner_id = Column(BigInteger, nullable=False, index=True)
    viewer_id = Column(BigInteger, nullable=False, index=True)
    guild_id = Column(BigInteger, nullable=False, index=True)

    # Access level
    can_view_stats = Column(Boolean, default=False)
    can_view_inventory = Column(Boolean, default=False)
    can_view_techniques = Column(Boolean, default=False)
    can_view_backstory = Column(Boolean, default=False)

    # Metadata
    granted_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint('owner_id', 'viewer_id', 'guild_id', name='unique_profile_access'),
    )


class TechniqueAccess(Base):
    """Track who can view whose techniques"""
    __tablename__ = "technique_access"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    owner_id = Column(BigInteger, nullable=False, index=True)
    viewer_id = Column(BigInteger, nullable=False, index=True)
    guild_id = Column(BigInteger, nullable=False, index=True)

    # Access permissions
    can_view = Column(Boolean, default=False)
    can_copy = Column(Boolean, default=False)

    # Metadata
    granted_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint('owner_id', 'viewer_id', 'guild_id', name='unique_technique_access'),
    )

# ============================================================================
# RP & STORY
# ============================================================================

class RPLocation(Base):
    """RP locations"""
    __tablename__ = "rp_locations"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    guild_id = Column(BigInteger, nullable=False, index=True)

    # Location details
    location_name = Column(String, nullable=False)
    description = Column(String)
    location_type = Column(String)  # city, dungeon, wilderness, etc.

    # Access control
    is_public = Column(Boolean, default=True)
    required_rank = Column(String, nullable=True)

    # Metadata
    created_by = Column(BigInteger, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class RPSession(Base):
    """RP sessions"""
    __tablename__ = "rp_sessions"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    guild_id = Column(BigInteger, nullable=False, index=True)
    location_id = Column(BigInteger, ForeignKey("rp_locations.id"), nullable=True)

    # Session details
    session_name = Column(String, nullable=False)
    description = Column(String)
    session_status = Column(String, default="active", index=True)  # active, paused, completed

    # Rewards
    exp_reward = Column(Integer, default=0)
    money_reward = Column(Integer, default=0)

    # Timing
    started_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime, nullable=True)

    # DM info
    dm_id = Column(BigInteger, nullable=False, index=True)

    # Relationships
    participants = relationship("RPSessionParticipant", back_populates="session", cascade="all, delete-orphan")


class RPSessionParticipant(Base):
    """Track participants in RP sessions"""
    __tablename__ = "rp_session_participants"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    session_id = Column(BigInteger, ForeignKey("rp_sessions.id"), nullable=False)
    character_id = Column(BigInteger, ForeignKey("characters.id"), nullable=False)

    # Participation
    joined_at = Column(DateTime, default=datetime.utcnow)
    left_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)

    # Individual rewards (can differ from session rewards)
    exp_earned = Column(Integer, default=0)
    money_earned = Column(Integer, default=0)

    # Relationships
    session = relationship("RPSession", back_populates="participants")

    __table_args__ = (
        Index('idx_session_character', 'session_id', 'character_id'),
    )


class StoryChapter(Base):
    """Story chapters"""
    __tablename__ = "story_chapters"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    guild_id = Column(BigInteger, nullable=False, index=True)

    # Chapter details
    chapter_number = Column(Integer, nullable=False)
    title = Column(String, nullable=False)
    description = Column(String)

    # Visibility
    is_published = Column(Boolean, default=False, index=True)

    # Metadata
    created_by = Column(BigInteger, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    pages = relationship("StoryPage", back_populates="chapter", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint('guild_id', 'chapter_number', name='unique_guild_chapter'),
    )


class StoryPage(Base):
    """Story pages within chapters"""
    __tablename__ = "story_pages"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    guild_id = Column(BigInteger, nullable=True, index=True)
    chapter_id = Column(BigInteger, ForeignKey("story_chapters.id"), nullable=False)

    # Page details
    page_number = Column(Integer, nullable=False)
    content = Column(String, nullable=False)

    # Metadata
    created_by = Column(BigInteger, nullable=False)  # Who created this page
    created_at = Column(DateTime, default=datetime.utcnow)
    editors = Column(String, default="")  # Comma-separated list of user IDs who edited

    # Relationships
    chapter = relationship("StoryChapter", back_populates="pages")


class UserStoryProgress(Base):
    """Track user's progress through the story"""
    __tablename__ = "user_story_progress"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, nullable=False, index=True)
    guild_id = Column(BigInteger, nullable=False, index=True)
    current_chapter_id = Column(Integer, ForeignKey("story_chapters.id"), nullable=True)
    last_read_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    current_chapter = relationship("StoryChapter")

    __table_args__ = (
        UniqueConstraint('user_id', 'guild_id', name='unique_user_guild_progress'),
    )


class InformationTopic(Base):
    """Information topics for server wiki/knowledge base"""
    __tablename__ = "information_topics"

    id = Column(Integer, primary_key=True, autoincrement=True)
    guild_id = Column(BigInteger, nullable=False, index=True)
    title = Column(String, nullable=False)  # Topic title
    content = Column(String, nullable=False)  # Topic content (up to 2000 chars per page)
    parent_id = Column(Integer, ForeignKey("information_topics.id"), nullable=True)  # For subtopics
    order_index = Column(Integer, default=0)  # For custom ordering within same parent
    is_published = Column(Boolean, default=False)  # Visible to players

    # Category and organization
    category = Column(String, nullable=True)  # Category name for grouping topics

    # View requirements stored as JSON
    # Format: {"roles": [role_id1, role_id2], "min_level": 10, "hidden": false}
    # hidden: true = never shows in list, false = shows if requirements met
    view_requirements = Column(String, default="{}")  # JSON string of requirements

    # Links stored as JSON
    # Format: {"story_chapters": [1, 2, 3], "topics": [5, 6, 7]}
    links = Column(String, default="{}")  # JSON string of links

    # Metadata
    created_by = Column(BigInteger, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    editors = Column(String, default="")  # Comma-separated list of user IDs who edited

    # Relationships
    pages = relationship("InformationPage", back_populates="topic", cascade="all, delete-orphan")


class InformationPage(Base):
    """Information pages within topics"""
    __tablename__ = "information_pages"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    guild_id = Column(BigInteger, nullable=True, index=True)
    topic_id = Column(Integer, ForeignKey("information_topics.id"), nullable=False)

    # Page details
    page_number = Column(Integer, nullable=False)
    content = Column(String, nullable=False)
    image_url = Column(String, nullable=True)  # Optional image URL for the page

    # Metadata
    created_by = Column(BigInteger, nullable=False)  # Who created this page
    created_at = Column(DateTime, default=datetime.utcnow)
    editors = Column(String, default="")  # Comma-separated list of user IDs who edited

    # Relationships
    topic = relationship("InformationTopic", back_populates="pages")


class BackstoryPage(Base):
    """Backstory pages for approved backstories"""
    __tablename__ = "backstory_pages"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    character_id = Column(BigInteger, ForeignKey("characters.id"), nullable=False)

    # Page details
    page_number = Column(Integer, nullable=False)
    content = Column(String, nullable=False)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)


class AIViolation(Base):
    """Track AI-generated content violations"""
    __tablename__ = "ai_violations"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    guild_id = Column(BigInteger, nullable=False, index=True)
    user_id = Column(BigInteger, nullable=False, index=True)

    # Violation details
    violation_type = Column(String, nullable=False)  # backstory, hatsu, technique, etc.
    content = Column(String, nullable=False)
    ai_confidence = Column(Float, default=0.0)  # 0.0-1.0

    # Action taken
    action_taken = Column(String)  # warning, rejection, ban, etc.
    reviewed_by = Column(BigInteger, nullable=True)

    # Metadata
    detected_at = Column(DateTime, default=datetime.utcnow, index=True)
    reviewed_at = Column(DateTime, nullable=True)

# ============================================================================
# COMBAT
# ============================================================================

class CombatSession(Base):
    """Combat sessions"""
    __tablename__ = "combat_sessions"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    guild_id = Column(BigInteger, nullable=False, index=True)

    # Combat details
    combat_type = Column(String, nullable=False)  # pvp, pve, training
    status = Column(String, default="active", index=True)  # active, completed, fled

    # Timing
    started_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime, nullable=True)

    # Relationships
    participants = relationship("CombatParticipant", back_populates="combat", cascade="all, delete-orphan")


class CombatParticipant(Base):
    """Participants in combat"""
    __tablename__ = "combat_participants"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    combat_id = Column(BigInteger, ForeignKey("combat_sessions.id"), nullable=False)
    character_id = Column(BigInteger, ForeignKey("characters.id"), nullable=False)

    # Combat stats
    current_hp = Column(Integer, nullable=False)

    # Status
    is_defeated = Column(Boolean, default=False)
    fled = Column(Boolean, default=False)

    # Relationships
    combat = relationship("CombatSession", back_populates="participants")
    status_effects = relationship("StatusEffect", back_populates="participant", cascade="all, delete-orphan")


class StatusEffect(Base):
    """Status effects on combat participants"""
    __tablename__ = "status_effects"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    participant_id = Column(BigInteger, ForeignKey("combat_participants.id"), nullable=False)

    # Effect details
    effect_name = Column(String, nullable=False)
    effect_type = Column(String, nullable=False)  # buff, debuff, dot, hot
    duration_turns = Column(Integer, nullable=False)
    remaining_turns = Column(Integer, nullable=False)

    # Effect values
    power = Column(Integer, default=0)
    stacks = Column(Integer, default=1)

    # Metadata
    applied_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    participant = relationship("CombatParticipant", back_populates="status_effects")

# ============================================================================
# TESTING SYSTEM
# ============================================================================

class CommandTest(Base):
    """Track commands that need testing"""
    __tablename__ = "command_tests"

    id = Column(Integer, primary_key=True, autoincrement=True)
    guild_id = Column(BigInteger, nullable=False, index=True)

    # Command details
    command_name = Column(String, nullable=False, unique=True)
    category = Column(String, nullable=False, index=True)
    description = Column(String)  # What the command does
    features_to_test = Column(String)  # JSON array of features to test
    stable = Column(Boolean, default=False)  # If True, don't show testing prompts
    testing_enabled = Column(Boolean, default=True)  # If False, testing is disabled
    version = Column(Integer, default=1)  # Version number - incremented when edited
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship to test results
    test_results = relationship("CommandTestResult", back_populates="command", cascade="all, delete-orphan")


class CommandTestResult(Base):
    """Test results for commands"""
    __tablename__ = "command_test_results"

    id = Column(Integer, primary_key=True, autoincrement=True)
    command_test_id = Column(Integer, ForeignKey("command_tests.id", ondelete="CASCADE"), nullable=False)
    tester_id = Column(BigInteger, nullable=False, index=True)
    guild_id = Column(BigInteger, nullable=False, index=True)

    # Test results
    passed = Column(Boolean, nullable=False)
    features_tested = Column(String)  # JSON object mapping feature names to pass/fail
    notes = Column(String)  # Tester's notes
    error_details = Column(String)  # Error message if failed
    tested_version = Column(Integer, default=1)  # Which version was tested

    # Timestamps
    tested_at = Column(DateTime)  # When the test was completed
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    command = relationship("CommandTest", back_populates="test_results")

    __table_args__ = (
        UniqueConstraint('command_test_id', 'tester_id', name='unique_command_tester'),
    )

# ============================================================================
# ECONOMY & BANKING
# ============================================================================

class BankTransaction(Base):
    """Track all money transactions for characters"""
    __tablename__ = "bank_transactions"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    character_id = Column(BigInteger, ForeignKey("characters.id"), nullable=False, index=True)
    guild_id = Column(BigInteger, nullable=False, index=True)

    # Transaction details
    transaction_type = Column(String, nullable=False, index=True)  # deposit, withdraw, transfer_send, etc.
    amount = Column(Integer, nullable=False)  # Positive for gains, negative for losses

    # Balances after transaction
    cash_before = Column(Integer, default=0)
    cash_after = Column(Integer, default=0)
    bank_before = Column(Integer, default=0)
    bank_after = Column(Integer, default=0)

    # Additional context
    description = Column(String, nullable=False)  # Human-readable description
    related_character_id = Column(BigInteger, nullable=True)  # For transfers
    related_character_name = Column(String, nullable=True)  # Character name for display
    admin_user_id = Column(BigInteger, nullable=True)  # If admin action

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationships
    character = relationship("Character", foreign_keys=[character_id])

    __table_args__ = (
        Index('idx_character_transactions', 'character_id', 'created_at'),
        Index('idx_guild_transactions', 'guild_id', 'created_at'),
    )


class MoneyRequest(Base):
    """Track money requests between players"""
    __tablename__ = "money_requests"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    from_character_id = Column(BigInteger, ForeignKey("characters.id"), nullable=False, index=True)
    to_character_id = Column(BigInteger, ForeignKey("characters.id"), nullable=False, index=True)
    from_user_id = Column(BigInteger, nullable=False)  # Discord user ID for DM
    to_user_id = Column(BigInteger, nullable=False)  # Discord user ID for DM
    guild_id = Column(BigInteger, nullable=False, index=True)

    amount = Column(Integer, nullable=False)
    reason = Column(String, nullable=False)
    message = Column(String, nullable=True)  # Optional message

    status = Column(String, default="pending", index=True)  # pending, accepted, declined, expired
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    responded_at = Column(DateTime, nullable=True)

    # Relationships
    from_character = relationship("Character", foreign_keys=[from_character_id])
    to_character = relationship("Character", foreign_keys=[to_character_id])

    __table_args__ = (
        Index('idx_pending_requests', 'to_character_id', 'status', 'created_at'),
    )


# NOTE: IncomeBracket is defined in models_economy.py to avoid duplication
# Import it here if needed for backward compatibility
try:
    from database.models_economy import IncomeBracket
except ImportError:
    pass  # models_economy might not be available in all contexts

# ============================================================================
# CONTINENTAL GAME
# ============================================================================

class ContinentalGame(Base):
    """Continental coin game sessions"""
    __tablename__ = "continental_games"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    guild_id = Column(BigInteger, nullable=False, index=True)
    message_id = Column(BigInteger, nullable=False, unique=True)
    channel_id = Column(BigInteger, nullable=False)

    # Game details
    game_status = Column(String, default="active", index=True)  # active, completed
    current_pot = Column(Integer, default=0)
    entry_fee = Column(Integer, nullable=False)

    # Timing
    started_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime, nullable=True)

    # Winner
    winner_id = Column(BigInteger, nullable=True)
    winner_character_name = Column(String, nullable=True)

    # Relationships
    players = relationship("ContinentalPlayer", back_populates="game", cascade="all, delete-orphan")


class ContinentalPlayer(Base):
    """Players in continental games"""
    __tablename__ = "continental_players"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    game_id = Column(BigInteger, ForeignKey("continental_games.id"), nullable=False)
    character_id = Column(BigInteger, ForeignKey("characters.id"), nullable=False)
    user_id = Column(BigInteger, nullable=False, index=True)

    # Player stats
    bet_amount = Column(Integer, nullable=False)
    is_active = Column(Boolean, default=True)
    placement = Column(Integer, nullable=True)  # 1st, 2nd, 3rd, etc.

    # Metadata
    joined_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    game = relationship("ContinentalGame", back_populates="players")

    __table_args__ = (
        UniqueConstraint('game_id', 'character_id', name='unique_game_player'),
    )

class BotSettings(Base):
    """Bot-wide settings for temporary admin overrides"""
    __tablename__ = "bot_settings"

    id = Column(Integer, primary_key=True, default=1)
    maintenance_mode = Column(Boolean, default=False)
    global_announcement = Column(String, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class WelcomeSettings(Base):
    """Welcome message configuration per guild"""
    __tablename__ = "welcome_settings"

    guild_id = Column(BigInteger, primary_key=True)

    # Channel settings
    channel_id = Column(BigInteger, nullable=True)  # None = auto-detect first writable channel

    # Message settings
    welcome_message = Column(String, nullable=True)  # None = default message
    is_public = Column(Boolean, default=False)  # False = ephemeral (only player sees)

    # Status
    enabled = Column(Boolean, default=True)

    # Metadata
    configured_by = Column(BigInteger, nullable=True)
    configured_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
