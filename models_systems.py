"""
System models: Race, Class, Stats, Welcome, and related system tables
"""
from sqlalchemy import BigInteger, Boolean, Column, Float, ForeignKey, Integer, String, DateTime, Text, UniqueConstraint, Index, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from database.base import Base


# ============================================================================
# RACE SYSTEM
# ============================================================================

class Race(Base):
    """Race configuration"""
    __tablename__ = "races"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    guild_id = Column(BigInteger, ForeignKey("server_config.guild_id"), nullable=False, index=True)
    race_name = Column(String(100), nullable=False)
    display_name = Column(String(200))
    description = Column(Text)

    # Flexible stat effects - supports any custom stat
    stat_effects = Column(JSON, nullable=True)  # {"strength": 10, "hp": 50, "mana_regen": 2.5}

    icon_emoji = Column(String(50))
    color_hex = Column(String(7), default='#808080')

    is_starter_race = Column(Boolean, default=False, index=True)
    is_evolution = Column(Boolean, default=False)
    is_enabled = Column(Boolean, default=True)

    can_evolve = Column(Boolean, default=False)
    evolution_level = Column(Integer)
    parent_race = Column(String(100))  # Parent race name for evolutions
    roll_chance_percentage = Column(Float, default=0.0)  # Chance to roll this race

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint('guild_id', 'race_name', name='uq_guild_race'),
    )


class RaceRequirement(Base):
    """Race unlock requirements"""
    __tablename__ = "race_requirements"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    guild_id = Column(BigInteger, nullable=False, index=True)
    race_name = Column(String(100), nullable=False)

    requirement_type = Column(String(50), nullable=False)
    requirement_target = Column(String(200), nullable=False)
    requirement_value = Column(Integer)
    requirement_operator = Column(String(10))

    display_text = Column(Text)


class RaceBonus(Base):
    """Race bonuses (skills, techniques, class unlocks, stat bonuses)"""
    __tablename__ = "race_bonuses"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    guild_id = Column(BigInteger, nullable=False, index=True)
    race_name = Column(String(100), nullable=False)

    # Flexible stat effects (for multiple stat bonuses)
    stat_effects = Column(JSON, nullable=True)  # {"strength": 10, "fire_resist": 25}

    # Stat value requirements (unlock bonus when stat reaches value)
    requirement_stat = Column(String(100), nullable=True)  # Stat key to check
    requirement_value = Column(Float, nullable=True)  # Value required to unlock bonus
    requirement_operator = Column(String(10), default=">=")  # >=, >, ==, <, <=

    # Legacy bonus system (for skills, techniques, class unlocks, passives)
    bonus_type = Column(String(50), nullable=True)  # "skill", "technique", "class_unlock", "passive", "class_bonus"
    bonus_target = Column(String(200), nullable=True)  # Name of skill/technique/class/passive
    bonus_value = Column(Integer, nullable=True)  # Numeric bonus value (for class_bonus type)
    unlock_level = Column(Integer, default=1)  # Character level when this bonus unlocks

    display_text = Column(Text)


class RaceEvolution(Base):
    """Race evolution paths"""
    __tablename__ = "race_evolutions"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    guild_id = Column(BigInteger, nullable=False, index=True)
    source_race = Column(String(100), nullable=False)  # Base race
    source_race_level = Column(Integer, nullable=True)  # Required race level (if races can level)
    result_race = Column(String(100), nullable=False)  # Evolved race

    display_name = Column(String(200), nullable=True)  # Display name for evolution
    description = Column(Text, nullable=True)  # Description/lore

    # Requirements (JSON): {"character_level": 50, "stats": {"strength": 100}, "items": ["Dragon Scale"], "titles": ["Dragon Slayer"]}
    requirements = Column(JSON, default={})

    is_enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint('guild_id', 'source_race', 'result_race', name='uq_race_evolution'),
    )


class RaceLevelBonus(Base):
    """Per-level bonuses for races (if races can level independently)"""
    __tablename__ = "race_level_bonuses"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    guild_id = Column(BigInteger, nullable=False, index=True)
    race_name = Column(String(100), nullable=False)

    # Can trigger on character level OR race level OR stat value
    trigger_type = Column(String(20), nullable=False, default="character_level")  # "character_level", "race_level", "stat_value"
    trigger_level = Column(Integer, nullable=True)  # What level triggers this bonus (for level types)

    # Stat value requirements (for stat_value trigger type)
    requirement_stat = Column(String(100), nullable=True)  # Stat key to check (e.g., "strength")
    requirement_value = Column(Float, nullable=True)  # Value required to unlock bonus (e.g., 100)
    requirement_operator = Column(String(10), default=">=")  # >=, >, ==, <, <=

    # Flexible stat effects (multiple stats per level bonus)
    stat_effects = Column(JSON, nullable=True)  # {"strength": 5, "hp": 20, "fire_resist": 10}

    # Legacy bonus system (for skills, techniques, passives)
    bonus_type = Column(String(50), nullable=True)  # "skill", "technique", "passive", "attribute_points"
    bonus_target = Column(String(200), nullable=True)  # Skill name, technique name, etc.
    bonus_value = Column(Integer, nullable=True)  # Amount of bonus

    display_text = Column(Text, nullable=True)  # Display text for players

    __table_args__ = (
        Index('idx_race_level_bonus', 'guild_id', 'race_name', 'trigger_level'),
    )


class RaceFusion(Base):
    """Race fusion paths (e.g., Elf + Mage Class = Druid Race)"""
    __tablename__ = "race_fusions"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    guild_id = Column(BigInteger, nullable=False, index=True)

    # Source components
    source_race = Column(String(100), nullable=False)  # Primary race
    source_class = Column(String(100), nullable=True)  # Required class (optional)
    source_race_2 = Column(String(100), nullable=True)  # Secondary race for race+race fusions

    # Result
    result_race = Column(String(100), nullable=False)  # Resulting fused race

    # Requirements
    min_character_level = Column(Integer, nullable=True)  # Minimum character level
    min_race_level = Column(Integer, nullable=True)  # Minimum race level
    min_class_level = Column(Integer, nullable=True)  # Minimum class level
    requirements = Column(JSON, default={})  # Additional requirements (stats, items, titles)

    # Display
    display_name = Column(String(200), nullable=True)  # Name of fusion
    description = Column(Text, nullable=True)  # Description/lore

    is_enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint('guild_id', 'source_race', 'source_class', 'source_race_2', 'result_race', name='uq_race_fusion'),
    )


class RaceAutoStat(Base):
    """Automatic stats created/granted when a character gets a race"""
    __tablename__ = "race_auto_stats"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    guild_id = Column(BigInteger, nullable=False, index=True)
    race_name = Column(String(100), nullable=False)

    stat_key = Column(String(100), nullable=False)  # Stat key from StatDefinition
    initial_value = Column(Float, default=0)  # Starting value for this stat

    # If this stat should be created in database when character gets this race
    auto_create = Column(Boolean, default=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint('guild_id', 'race_name', 'stat_key', name='uq_race_auto_stat'),
    )


# ============================================================================
# CLASS SYSTEM
# ============================================================================

class ClassType(Base):
    """Class types/categories for organization (similar to StatCategory)"""
    __tablename__ = "class_types"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    guild_id = Column(BigInteger, nullable=False, index=True)
    type_name = Column(String(100), nullable=False)  # Internal identifier
    display_name = Column(String(200))
    description = Column(Text)

    icon_emoji = Column(String(50))
    color = Column(String(7), default='#99AAB5')  # Hex color code
    display_order = Column(Integer, default=0)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint('guild_id', 'type_name', name='uq_guild_class_type'),
    )


class ClassClassType(Base):
    """Many-to-many relationship between Classes and ClassTypes"""
    __tablename__ = "class_class_types"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    guild_id = Column(BigInteger, nullable=False, index=True)
    class_name = Column(String(100), nullable=False)  # References Class.class_name
    type_name = Column(String(100), nullable=False)  # References ClassType.type_name

    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint('guild_id', 'class_name', 'type_name', name='uq_class_type_assignment'),
    )


class Class(Base):
    """Class configuration"""
    __tablename__ = "classes"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    guild_id = Column(BigInteger, ForeignKey("server_config.guild_id"), nullable=False, index=True)
    class_name = Column(String(100), nullable=False)
    display_name = Column(String(200))
    description = Column(Text)

    # Flexible stat effects - supports any custom stat
    stat_effects = Column(JSON, nullable=True)  # {"intelligence": 10, "mana": 100, "spell_power": 15}

    icon_emoji = Column(String(50))
    color_hex = Column(String(7), default='#808080')

    class_type = Column(String(50))

    is_starter_class = Column(Boolean, default=False, index=True)
    is_enabled = Column(Boolean, default=True)

    # Class-specific progression attributes
    class_exp_attribute_key = Column(String(100), nullable=True)  # Custom exp attribute for this class (overrides server default)
    class_level_attribute_key = Column(String(100), nullable=True)  # Custom level attribute for this class (overrides server default)

    # Class subtype categorization
    class_subtype = Column(String(100), nullable=True)  # e.g., "elemental", "physical", "support", "healer"

    # Gain type - how this class gains experience
    # Options: "character_level" (gains when character levels up) or "class_level" (independent class leveling)
    gain_type = Column(String(50), default="character_level")

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint('guild_id', 'class_name', name='uq_guild_class'),
    )


class ClassRequirement(Base):
    """Class unlock requirements"""
    __tablename__ = "class_requirements"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    guild_id = Column(BigInteger, nullable=False, index=True)
    class_name = Column(String(100), nullable=False)

    requirement_type = Column(String(50), nullable=False)
    requirement_target = Column(String(200), nullable=False)
    requirement_value = Column(Integer)
    requirement_operator = Column(String(10))

    display_text = Column(Text)


class ClassBonus(Base):
    """Class bonuses (skills, techniques, passives, stat bonuses)"""
    __tablename__ = "class_bonuses"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    guild_id = Column(BigInteger, nullable=False, index=True)
    class_name = Column(String(100), nullable=False)

    # Flexible stat effects (for multiple stat bonuses)
    stat_effects = Column(JSON, nullable=True)  # {"spell_damage": 20, "mana_regen": 5}

    # Stat value requirements (unlock bonus when stat reaches value)
    requirement_stat = Column(String(100), nullable=True)  # Stat key to check
    requirement_value = Column(Float, nullable=True)  # Value required to unlock bonus
    requirement_operator = Column(String(10), default=">=")  # >=, >, ==, <, <=

    # Legacy bonus system (for skills, techniques, passives)
    bonus_type = Column(String(50), nullable=True)
    bonus_target = Column(String(200), nullable=True)
    bonus_value = Column(String(500))

    display_text = Column(Text)


class ClassLevelConfig(Base):
    """Per-class, per-level configuration"""
    __tablename__ = "class_level_config"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    guild_id = Column(BigInteger, nullable=False, index=True)
    class_name = Column(String(100), nullable=False)
    level = Column(Integer, nullable=True)  # Nullable for stat_value trigger type

    # Trigger type (level or stat value)
    trigger_type = Column(String(20), nullable=False, default="class_level")  # "class_level" or "stat_value"

    # Stat value requirements (for stat_value trigger type)
    requirement_stat = Column(String(100), nullable=True)  # Stat key to check
    requirement_value = Column(Float, nullable=True)  # Value required to unlock
    requirement_operator = Column(String(10), default=">=")  # >=, >, ==, <, <=

    # Requirements for this level
    resource_requirement = Column(Integer, default=0)  # EXP or other resource needed
    uses_formula = Column(Boolean, default=True)  # Use formula or custom value
    requirements = Column(JSON)  # JSON object with additional requirement details

    # Flexible stat effects (stat bonuses gained per level)
    stat_effects = Column(JSON, nullable=True)  # {"intelligence": 5, "mana": 50, "spell_crit": 2}

    # Rewards for reaching this level
    attribute_points = Column(Integer, default=2)  # Attribute points granted
    class_skills = Column(Integer, default=0)  # Class-specific skill points
    skill_points = Column(Integer, default=0)  # General skill points
    rewards = Column(JSON)  # JSON object with additional reward details

    __table_args__ = (
        UniqueConstraint('guild_id', 'class_name', 'level', name='uq_class_level'),
    )


class ClassLevelRequirement(Base):
    """Complex requirements for specific class levels"""
    __tablename__ = "class_level_requirements"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    guild_id = Column(BigInteger, nullable=False, index=True)
    class_name = Column(String(100), nullable=False)
    level = Column(Integer, nullable=False)

    requirement_type = Column(String(50), nullable=False)  # "item", "stat", "character_level", "title", "quest"
    requirement_target = Column(String(200), nullable=False)  # Item name, stat name, title name, etc.
    requirement_value = Column(Integer, nullable=True)  # Value for comparisons
    requirement_operator = Column(String(10), nullable=True)  # ">=", "==", ">" etc.

    display_text = Column(Text, nullable=True)  # Human-readable requirement text

    __table_args__ = (
        Index('idx_class_level_req', 'guild_id', 'class_name', 'level'),
    )


class ClassLevelReward(Base):
    """Complex rewards for specific class levels"""
    __tablename__ = "class_level_rewards"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    guild_id = Column(BigInteger, nullable=False, index=True)
    class_name = Column(String(100), nullable=False)
    level = Column(Integer, nullable=False)

    reward_type = Column(String(50), nullable=False)  # "item", "stat_boost", "title", "skill", "technique"
    reward_target = Column(String(200), nullable=False)  # Item name, stat name, skill name, etc.
    reward_value = Column(Integer, nullable=True)  # Amount of reward

    display_text = Column(Text, nullable=True)  # Human-readable reward text

    __table_args__ = (
        Index('idx_class_level_reward', 'guild_id', 'class_name', 'level'),
    )


class ClassEvolution(Base):
    """Class evolution paths (e.g., Warrior → Knight → Paladin)"""
    __tablename__ = "class_evolutions"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    guild_id = Column(BigInteger, nullable=False, index=True)

    source_class = Column(String(100), nullable=False)  # Base class
    source_class_level = Column(Integer, nullable=True)  # Required class level
    result_class = Column(String(100), nullable=False)  # Evolved class

    display_name = Column(String(200), nullable=True)  # Display name for evolution
    description = Column(Text, nullable=True)  # Description/lore

    # Requirements (JSON): {"character_level": 50, "stats": {"strength": 100}, "items": ["Holy Symbol"], "titles": ["Holy Knight"]}
    requirements = Column(JSON, default={})

    is_enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint('guild_id', 'source_class', 'result_class', name='uq_class_evolution'),
    )


class ClassFusion(Base):
    """Class fusion paths (e.g., Warrior + Mage = Spellblade)"""
    __tablename__ = "class_fusions"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    guild_id = Column(BigInteger, nullable=False, index=True)

    # Source components
    source_class = Column(String(100), nullable=False)  # Primary class
    source_class_2 = Column(String(100), nullable=False)  # Secondary class
    source_race = Column(String(100), nullable=True)  # Required race (optional)

    # Result
    result_class = Column(String(100), nullable=False)  # Resulting fused class

    # Requirements
    min_character_level = Column(Integer, nullable=True)  # Minimum character level
    min_class_level = Column(Integer, nullable=True)  # Minimum level for source_class
    min_class_2_level = Column(Integer, nullable=True)  # Minimum level for source_class_2
    requirements = Column(JSON, default={})  # Additional requirements (stats, items, titles)

    # Display
    display_name = Column(String(200), nullable=True)  # Name of fusion
    description = Column(Text, nullable=True)  # Description/lore

    is_enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint('guild_id', 'source_class', 'source_class_2', 'result_class', name='uq_class_fusion'),
    )


class ClassAutoStat(Base):
    """Automatic stats created/granted when a character gets a class"""
    __tablename__ = "class_auto_stats"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    guild_id = Column(BigInteger, nullable=False, index=True)
    class_name = Column(String(100), nullable=False)

    stat_key = Column(String(100), nullable=False)  # Stat key from StatDefinition
    initial_value = Column(Float, default=0)  # Starting value for this stat

    # If this stat should be created in database when character gets this class
    auto_create = Column(Boolean, default=True)

    # Level-based stat creation (e.g., create "exp_swordsman" only when class levels exist)
    create_at_level = Column(Integer, default=1)  # At what class level to create this stat

    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint('guild_id', 'class_name', 'stat_key', name='uq_class_auto_stat'),
    )


# ============================================================================
# STAT SYSTEM
# ============================================================================

class StatPool(Base):
    """Shared point pools for stats"""
    __tablename__ = "stat_pools"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    guild_id = Column(BigInteger, nullable=False, index=True)
    pool_name = Column(String(100), nullable=False)
    display_name = Column(String(200))
    description = Column(Text)

    is_shared = Column(Boolean, default=True)
    max_points = Column(Integer)

    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint('guild_id', 'pool_name', name='uq_guild_pool'),
    )


class StatCategory(Base):
    """Stat categories for organization"""
    __tablename__ = "stat_categories"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    guild_id = Column(BigInteger, nullable=False, index=True)
    category_name = Column(String(100), nullable=False)
    display_name = Column(String(200))
    description = Column(Text)

    icon_emoji = Column(String(50))
    color = Column(String(7), default='#99AAB5')  # Hex color code
    display_order = Column(Integer, default=0)
    show_in_profile = Column(Boolean, default=True)  # Show category in character profile
    requirements = Column(Text, default='{}')  # JSON string of requirements

    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint('guild_id', 'category_name', name='uq_guild_category'),
    )


class StatDefinition(Base):
    """Stat definitions and properties"""
    __tablename__ = "stat_definitions"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    guild_id = Column(BigInteger, nullable=False, index=True)
    stat_key = Column(String(100), nullable=False)  # Unique identifier for code/functions
    stat_name = Column(String(100), nullable=False)  # Display name
    display_name = Column(String(200))  # Alternative display name
    description = Column(Text)

    category_name = Column(String(100))
    profile_section = Column(String(50))  # section_key from ProfileSection table

    stat_type = Column(String(50))  # 'basic', 'gauge', 'calculated', etc. (legacy - use has_gauge and uses_formula instead)

    # Stat behavior flags (independent, can be combined)
    has_gauge = Column(Boolean, default=False)  # Has current/max values (HP, Mana, etc.)
    uses_formula = Column(Boolean, default=False)  # Value calculated from formula

    # Investment system
    is_investable = Column(Boolean, default=False)  # Can players spend points to increase this stat?
    is_investment_resource = Column(Boolean, default=False)  # Is this stat used as currency for investing? (EXP, Skill Points, etc.)
    investment_resource = Column(String(100))  # What resource type is required to invest in this stat (if is_investable=True)
    investment_resources = Column(JSON)  # Multiple resources required: ["stat_points", "skill_points"] - allows combined costs
    cost_formula = Column(Text)  # Formula for point cost when investing

    # Investment targets (what can this resource be invested in?)
    can_invest_in_stats = Column(Boolean, default=True)  # Can invest in character stats (Strength, etc.)
    can_invest_in_techniques = Column(Boolean, default=False)  # Can invest in techniques/abilities
    can_invest_in_skills = Column(Boolean, default=False)  # Can invest in skills
    can_invest_in_classes = Column(Boolean, default=False)  # Can invest in class progression

    # EXP type system
    exp_type = Column(String(100))  # Type of EXP this stat represents (general, combat, social, crafting, etc.)

    # Gauge stat settings
    gauge_display_mode = Column(String(20))  # 'percentage' or 'raw' - how to display gauge stats

    # Value settings
    default_value = Column(Float, default=0)
    min_value = Column(Float)
    max_value = Column(Float)  # For gauges: maximum possible value; For investable: max investment limit

    # Calculated stats
    value_formula = Column(Text)  # Formula for calculated stats
    grade_mappings = Column(JSON)  # Map text grades to numbers {"S+": 100, "A": 50, etc.}

    # Display settings
    is_visible = Column(Boolean, default=True)  # Show to players?
    is_editable = Column(Boolean, default=True)  # Can admins edit character values directly?

    icon_emoji = Column(String(50))
    display_order = Column(Integer, default=0)

    # Advanced display formatting
    display_format = Column(String(50), default='icon_name_value')  # icon_name_value, name_value_bracket, icon_value, custom
    value_prefix = Column(String(20))  # Text before value (e.g., "$", "+")
    value_suffix = Column(String(20))  # Text after value (e.g., "%", "HP")
    decimal_places = Column(Integer, default=0)  # Number of decimal places (0-3)
    show_as_progress_bar = Column(Boolean, default=False)  # Show gauge stats as progress bar
    progress_bar_length = Column(Integer, default=10)  # Length of progress bar (5-20)
    progress_bar_filled_char = Column(String(5), default='█')  # Character for filled portion
    progress_bar_empty_char = Column(String(5), default='░')  # Character for empty portion
    show_percentage = Column(Boolean, default=True)  # Show percentage for gauge stats

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint('guild_id', 'stat_key', name='uq_guild_stat'),
    )


class StatCondition(Base):
    """Conditional formulas for stats based on conditions (e.g., level thresholds)"""
    __tablename__ = "stat_conditions"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    stat_definition_id = Column(BigInteger, ForeignKey("stat_definitions.id"), nullable=False, index=True)
    guild_id = Column(BigInteger, nullable=False, index=True)

    # Condition details
    condition_order = Column(Integer, default=0)  # Order to evaluate conditions (lower = higher priority)
    condition_type = Column(String(50), nullable=False)  # 'level', 'stat_value', 'class', 'race', etc.
    condition_operator = Column(String(20), nullable=False)  # '<', '<=', '>', '>=', '==', '!='
    condition_value = Column(String(200), nullable=False)  # The value to compare against

    # Result when condition is met
    result_type = Column(String(50), nullable=False)  # 'value', 'formula', 'modifier'
    result_value = Column(Text, nullable=False)  # The value/formula to use when condition is true

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class StatValueRule(Base):
    """Rules for stat values: hard caps, soft caps, conditional values, and display ranges"""
    __tablename__ = "stat_value_rules"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    guild_id = Column(BigInteger, nullable=False, index=True)
    stat_key = Column(String(100), nullable=False, index=True)  # Which stat this rule applies to

    # Rule identification
    rule_name = Column(String(200))  # Optional friendly name for the rule
    rule_type = Column(String(50), nullable=False)  # 'hard_cap', 'soft_cap', 'set_value', 'display_range'
    priority = Column(Integer, default=0)  # Order of evaluation (higher = evaluated first)
    is_active = Column(Boolean, default=True)

    # Condition system (when this rule applies)
    condition_type = Column(String(50), nullable=False, default='always')  # 'always', 'simple', 'formula', 'class_race', 'compound'
    condition_data = Column(JSON)  # Stores the actual condition
    # Examples:
    # simple: {"stat_key": "level", "operator": ">=", "value": 10}
    # formula: {"expression": "(strength * 2 + level) >= 50"}
    # class_race: {"classes": ["Warrior", "Knight"], "races": ["Orc"], "match": "any"}
    # compound: {"conditions": [...], "logic": "and"}

    # Target value/behavior
    target_value = Column(Float)  # For hard_cap, soft_cap, set_value: the numeric value
    target_formula = Column(Text)  # Alternative: calculate value from formula

    # Soft cap specific (for penalties when exceeding cap)
    soft_cap_penalty_type = Column(String(50))  # 'diminishing', 'flat_reduction', 'percentage'
    soft_cap_penalty_value = Column(Float)  # Amount of penalty per point over cap
    soft_cap_penalty_formula = Column(Text)  # Formula for complex penalty calculation
    # Examples:
    # diminishing: Each point over cap only counts as (1 - penalty_value), e.g., 0.5 = 50% effectiveness
    # flat_reduction: Lose penalty_value points per point over cap (discourages going over)
    # percentage: Reduce total value by penalty_value% for each point over

    # Display range system (for text/rank values like "Beginner", "Expert", "S-Rank")
    display_text = Column(String(100))  # Text to display when value is in range
    range_min = Column(Float)  # Minimum value for this range (inclusive)
    range_max = Column(Float)  # Maximum value for this range (inclusive)
    range_color = Column(String(7))  # Optional hex color for this range
    # Example: range_min=0, range_max=10, display_text="Beginner"
    #          range_min=11, range_max=25, display_text="Novice"

    # Metadata
    description = Column(Text)  # Admin note about what this rule does
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index('idx_guild_stat_rule', 'guild_id', 'stat_key', 'rule_type'),
    )


class CharacterStat(Base):
    """Character stat values"""
    __tablename__ = "character_stats"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    character_id = Column(BigInteger, ForeignKey("characters.id"), nullable=False, index=True)
    stat_def_id = Column(BigInteger, ForeignKey("stat_definitions.id"), nullable=True, index=True)
    stat_name = Column(String(100), nullable=False)

    # Basic stat values
    base_value = Column(Float, default=0)  # Base value (for basic stats, gauges current value)
    bonus_value = Column(Float, default=0)  # Temporary bonuses from items/buffs
    current_value = Column(Float, default=0)  # For gauge stats: current resource amount
    max_value = Column(Float)  # For gauge stats: maximum resource amount

    # Investment tracking
    points_invested = Column(Integer, default=0)  # How many times this stat has been invested in

    # Investment resource tracking (for stats that ARE investment resources like EXP/Skill Points)
    total_earned = Column(Float, default=0)  # Total amount ever earned
    total_spent = Column(Float, default=0)  # Total amount spent on investments
    # Available = total_earned - total_spent (calculated, not stored)

    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint('character_id', 'stat_name', name='uq_character_stat'),
    )


class TemporaryStat(Base):
    """Temporary stat modifiers (buffs/debuffs)"""
    __tablename__ = "temporary_stats"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    character_id = Column(BigInteger, ForeignKey("characters.id"), nullable=False, index=True)
    stat_name = Column(String(100), nullable=False)

    modifier_value = Column(Float, nullable=False)
    modifier_type = Column(String(20))  # 'flat', 'percent', 'multiply'

    source = Column(String(200))  # What caused this modifier
    expires_at = Column(DateTime)

    created_at = Column(DateTime, default=datetime.utcnow)


class StatHistory(Base):
    """Stat change history"""
    __tablename__ = "stat_history"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    character_id = Column(BigInteger, ForeignKey("characters.id"), nullable=False, index=True)
    stat_name = Column(String(100), nullable=False)

    old_value = Column(Float)
    new_value = Column(Float)
    change_amount = Column(Float)

    change_reason = Column(String(200))
    changed_by = Column(BigInteger)  # Discord user ID

    created_at = Column(DateTime, default=datetime.utcnow, index=True)


# ============================================================================
# CHARACTER LEVELING SYSTEM
# ============================================================================

class CharacterLevelRequirement(Base):
    """Manual EXP requirements for specific character levels"""
    __tablename__ = "character_level_requirements"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    guild_id = Column(BigInteger, nullable=False, index=True)
    level = Column(Integer, nullable=False)  # The level to reach (e.g., 2, 3, 4...)
    exp_required = Column(BigInteger, nullable=False)  # Total EXP needed to reach this level

    __table_args__ = (
        UniqueConstraint('guild_id', 'level', name='uq_guild_level'),
        Index('idx_character_level_req', 'guild_id', 'level'),
    )


class CharacterLevelReward(Base):
    """Rewards granted when characters level up"""
    __tablename__ = "character_level_rewards"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    guild_id = Column(BigInteger, nullable=False, index=True)
    level = Column(Integer, nullable=False)  # 0 = all levels, specific number = that level only
    reward_type = Column(String, nullable=False)  # 'attribute', 'item', 'skill' (WIP), 'technique' (WIP)
    reward_data = Column(JSON, nullable=False)  # Stores reward details (attribute_key, amount, item_id, etc.)
    display_order = Column(Integer, default=0)  # Order to display/apply rewards

    __table_args__ = (
        Index('idx_character_level_reward', 'guild_id', 'level'),
    )


# ============================================================================
# WELCOME SYSTEM
# ============================================================================

class WelcomeSystem(Base):
    """Welcome message configuration"""
    __tablename__ = "welcome_system"

    guild_id = Column(BigInteger, primary_key=True)

    is_enabled = Column(Boolean, default=False)
    welcome_channel_id = Column(BigInteger)

    # Legacy fields (kept for backward compatibility)
    welcome_message = Column(Text)
    welcome_embed_title = Column(String(256))
    welcome_embed_description = Column(Text)
    welcome_embed_color = Column(String(7), default='#00FF00')

    # Multi-page support - JSON array of page objects
    # Each page: {"title": str, "description": str, "color": str, "image": str, "thumbnail": str, "footer": str}
    welcome_pages = Column(JSON, default='[]')

    # Auto-role system
    assign_role_id = Column(BigInteger)  # Legacy single role (kept for compatibility)
    auto_roles = Column(JSON, default='[]')  # Array of role IDs to assign on join
    restore_roles_on_rejoin = Column(Boolean, default=False)  # Restore roles when user rejoins

    setup_by = Column(BigInteger, nullable=True)  # Who configured the system

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class AlertSystem(Base):
    """Admin alert system configuration for panel/dashboard notifications"""
    __tablename__ = "alert_system"

    guild_id = Column(BigInteger, primary_key=True)

    is_enabled = Column(Boolean, default=False)

    # Alert configuration - JSON object mapping alert types to role IDs
    # Format: {"pending_submissions": [role_id1, role_id2], "verification_pending": [role_id3]}
    alert_config = Column(JSON, default='{}')

    # Global admin roles that get all alerts
    global_alert_roles = Column(JSON, default='[]')  # Array of role IDs

    # Snooze log channel - logs when admins snooze alerts
    snooze_log_channel_id = Column(BigInteger, nullable=True)

    # Snooze duration in minutes (5-60 minutes)
    snooze_duration_minutes = Column(Integer, default=60)

    setup_by = Column(BigInteger, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ProfileSection(Base):
    """Profile display sections for organizing character stats"""
    __tablename__ = "profile_sections"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    guild_id = Column(BigInteger, nullable=False, index=True)

    section_key = Column(String(50), nullable=False)  # Unique identifier for the section
    section_name = Column(String(100), nullable=False)  # Display name
    display_order = Column(Integer, default=0)  # Order in which sections appear
    layout_mode = Column(String(20), default='list')  # list, grid, bars, compact
    section_icon = Column(String(10))  # Emoji icon for the section
    section_color = Column(String(7), default='#5865F2')  # Hex color code
    show_to_player = Column(Boolean, default=True)  # Whether players can see this section
    min_permission_level = Column(Integer, default=0)  # Minimum permission level to view

    # Display customization options
    show_section_title = Column(Boolean, default=True)  # Show section name header
    show_border = Column(Boolean, default=False)  # Show decorative border around section
    separator_style = Column(String(10), default='─')  # Separator character (─, ═, •, -)
    column_count = Column(Integer, default=1)  # Number of columns for stats (1-3)
    hide_section_if_empty = Column(Boolean, default=True)  # Hide section if no stats

    # Conditional display rules (JSON)
    display_conditions = Column(JSON, nullable=True)  # {"min_level": 10, "required_class": "Mage", etc.}

    # Custom text content (for text-only sections)
    custom_text = Column(Text, nullable=True)  # Optional custom text content for text sections

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint('guild_id', 'section_key', name='uq_guild_section_key'),
    )


# NOTE: RolePermissionLevel has been moved to models_server_config.py
# It's imported in models.py from there to avoid duplicate table definition
