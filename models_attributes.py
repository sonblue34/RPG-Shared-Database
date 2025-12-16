"""
Unified Attribute System Models (ECS Architecture)
Version 2.0.0 - Complete restructure where everything is an attribute

This replaces the fragmented systems (stats, items, classes, races) with a unified approach.
"""
from sqlalchemy import BigInteger, Boolean, Column, Float, ForeignKey, Integer, String, DateTime, Text, UniqueConstraint, Index, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from database.base import Base


class AttributeDefinition(Base):
    """
    Universal attribute template - defines ALL character data types

    This single model replaces:
    - StatDefinition (stats)
    - Item (items)
    - Race/Class definitions (affiliations)
    - Currency definitions
    - Identity fields
    - Buff/debuff definitions

    Everything is an attribute with a type.
    """
    __tablename__ = "attribute_definitions"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    guild_id = Column(BigInteger, nullable=False, index=True)

    # ===== IDENTITY =====
    attribute_key = Column(String(100), nullable=False, index=True)
    # Examples: "strength", "iron_sword", "warrior_class", "gold", "character_name"

    attribute_name = Column(String(200), nullable=False)
    # Display name shown to users

    description = Column(Text)
    # Detailed description of what this attribute does

    # ===== TYPE SYSTEM (THE CORE INNOVATION) =====
    attribute_type = Column(String(50), nullable=False, index=True)
    # PRIMARY TYPES:
    # - identity: Basic character info (name, age, appearance, backstory)
    # - stat: Traditional stats (strength, hp, mana, dexterity)
    # - progression: Leveling systems (level, exp, class_level, skill_level)
    # - currency: Money and points (gold, gems, skill_points, attribute_points)
    # - affiliation: Memberships (race, class, clan, faction, guild)
    # - item: Inventory items (weapons, armor, consumables, materials)
    # - equipment: Active gear slots (weapon_slot, armor_slot, accessory_slot)
    # - status: Temporary effects (buffs, debuffs, conditions, states)

    attribute_subtype = Column(String(50), index=True)
    # SUBTYPES for further organization:
    # identity: basic, visual, personality, history
    # stat: combat, social, physical, mental, special, resource
    # progression: character, class, skill, crafting
    # currency: money, points, tokens, premium
    # affiliation: race, class, clan, faction, guild
    # item: weapon, armor, consumable, material, quest, misc, key, reward, socket
    # equipment: weapon_slot, armor_slot, accessory_slot, tool_slot
    # status: buff, debuff, condition, state, curse, blessing

    # ===== VALUE CONFIGURATION =====
    # For numeric attributes (stats, currency, progression, quantities)
    default_value = Column(Float, default=0)
    min_value = Column(Float)
    max_value = Column(Float)

    # Value type determines how to store/display
    value_type = Column(String(20), default='number')
    # Options: number, text, boolean, json, reference

    # For calculated/formula attributes
    value_formula = Column(Text)
    # Formula syntax: "strength * 2 + level", "hp / max_hp * 100"

    grade_mappings = Column(JSON)
    # Text grade to number mappings: {"S+": 100, "S": 90, "A": 80, ...}

    # ===== STAT-SPECIFIC (when attribute_type = "stat") =====
    stat_type = Column(String(20))
    # Options: basic, gauge, calculated
    # - basic: Simple numeric value (strength, dexterity)
    # - gauge: Has current/max (hp, mana, stamina)
    # - calculated: Auto-computed from formula (total_power, attack_rating)

    gauge_display_mode = Column(String(20))
    # Options: percentage, raw
    # percentage: "80/100 (80%)"
    # raw: "80/100"

    # ===== DISPLAY SETTINGS =====
    icon_emoji = Column(String(50))
    # Visual emoji for display

    color = Column(String(7))
    # Hex color code for rarity/type indication

    display_order = Column(Integer, default=0)
    # Sort order in lists

    # Display formatting
    display_format = Column(String(50), default='icon_name_value')
    # Options: icon_name_value, name_value_bracket, icon_value, custom

    value_prefix = Column(String(20))
    # Text before value: "$", "+", "Lv.", "×"

    value_suffix = Column(String(20))
    # Text after value: "%", "HP", "pts", "kg"

    decimal_places = Column(Integer, default=0)
    # Number of decimal places for numeric values (0-3)

    # Progress bar display (for gauge stats)
    show_as_progress_bar = Column(Boolean, default=False)
    progress_bar_length = Column(Integer, default=10)
    progress_bar_filled_char = Column(String(5), default='█')
    progress_bar_empty_char = Column(String(5), default='░')
    show_percentage = Column(Boolean, default=True)

    # Visibility and editing
    is_visible = Column(Boolean, default=True)
    # Show to players?

    is_editable = Column(Boolean, default=True)
    # Can admins edit values directly?

    # Organization
    category_name = Column(String(100))
    # Category for grouping (Combat, Social, Resources, etc.)

    profile_section = Column(String(50))
    # Which profile section to display in

    # ===== ITEM-SPECIFIC (when attribute_type = "item") =====
    is_stackable = Column(Boolean, default=False)
    # Can multiple copies stack in one inventory slot?

    max_stack_size = Column(Integer, default=1)
    # Maximum stack size (99, 999, etc.)

    is_tradeable = Column(Boolean, default=True)
    # Can be traded between players?

    is_sellable = Column(Boolean, default=True)
    # Can be sold to NPCs/shops?

    is_consumable = Column(Boolean, default=False)
    # Is used up when used?

    is_equippable = Column(Boolean, default=False)
    # Can be equipped?

    equipment_slot = Column(String(50))
    # Which slot: weapon, head, chest, legs, hands, feet, accessory, ring

    is_quest_item = Column(Boolean, default=False)
    # Quest item (usually not tradeable/sellable)

    item_rarity = Column(String(50))
    # Common, Uncommon, Rare, Epic, Legendary, Mythic, etc.

    item_weight = Column(Float, default=0.0)
    # Weight of the item (for encumbrance/weight limit systems)

    item_tags = Column(JSON)
    # Array of tags: ["sword", "metal", "one-handed", "melee"]

    # ===== VISIBILITY & PERMISSIONS =====
    visibility = Column(String(50), default='everyone')
    # Options: "everyone", "admin_only", "role_restricted", "class_restricted", "hidden"

    allowed_roles = Column(JSON)
    # Array of role IDs that can see/use this item (if visibility = role_restricted)

    allowed_classes = Column(JSON)
    # Array of class names that can see/use this item (if visibility = class_restricted)

    # ===== REQUIREMENTS TO USE/EQUIP =====
    requirements = Column(JSON)
    # {
    #   "level": 10,
    #   "class": ["warrior", "paladin"],
    #   "attributes": {"strength": 15, "intelligence": 10},
    #   "items": ["iron_sword"],  # Must own these items
    #   "skills": {"swordsmanship": 5}
    # }

    # Economy (for items and services)
    base_value = Column(Integer, default=0)
    # Base gold/currency value

    sell_value = Column(Integer)
    # Sell price (null = base_value * 0.5)

    # Usage effects (for consumables)
    on_use_effects = Column(JSON)
    # {"heal_hp": 50, "restore_mana": 30, "grant_buff": "haste"}

    use_cooldown = Column(Integer, default=0)
    # Cooldown in turns/rounds

    # ===== AMMO SYSTEM (for ranged weapons and ammo items) =====
    requires_ammo = Column(Boolean, default=False)
    # Does this item need ammo to function?

    required_ammo_type = Column(String(50))
    # "arrow", "bolt", "bullet", "magic_charge", "throwing_knife"

    ammo_consumption_rate = Column(Integer, default=1)
    # How much ammo consumed per use (1 arrow, 5 bullets for burst fire)

    # For ammo items
    is_ammo = Column(Boolean, default=False)
    ammo_type = Column(String(50))
    # What type of ammo is this? "arrow", "bolt", "bullet"

    ammo_stack_size = Column(Integer, default=99)
    # Default stack size for ammo

    # ===== SLOT OCCUPANCY =====
    occupies_slots = Column(JSON)
    # ["main_hand", "off_hand"] for two-handed weapons
    # ["ring_1", "ring_2"] for set items that take multiple ring slots

    blocks_slots = Column(JSON)
    # ["off_hand"] - shield blocks off_hand weapon use

    # ===== SOCKET/MODIFICATION SYSTEM =====
    has_sockets = Column(Boolean, default=False)
    # Does this item have modification/socket slots?

    socket_count = Column(Integer, default=0)
    # Number of socket slots available (0-10 typical range)

    socket_types = Column(JSON)
    # Types of sockets available, and how many of each
    # Flexible format supports:
    # Generic: {"generic": 3} - 3 slots for any socket item
    # Typed: {"red": 1, "blue": 2, "yellow": 1} - specific socket colors/types
    # Mixed: {"generic": 2, "elemental": 1} - combination of generic and specific

    allowed_socket_items = Column(JSON)
    # What types of items can be socketed (by item_key or attribute_subtype)
    # ["gem", "rune", "enchant"] - by subtype
    # ["ruby_gem", "sapphire_gem"] - by specific item keys
    # null = any socket-type item allowed

    socket_stat_multiplier = Column(Float, default=1.0)
    # Multiplier for socketed item effects (1.0 = 100%, 1.5 = 150%, 0.5 = 50%)
    # Allows items to amplify or diminish socket effects

    # For socket items themselves (gems, runes, enchants)
    is_socket_item = Column(Boolean, default=False)
    # Can this item be placed into a socket?

    socket_item_type = Column(String(50))
    # Type of socket this item fits into
    # "generic" - fits any socket
    # "red", "blue", "yellow" - specific socket types
    # "elemental", "defensive", "offensive" - category-based

    socket_effects = Column(JSON)
    # Effects granted when socketed
    # {"strength": 10, "critical_chance": 5, "fire_damage": 20}
    # Follows same format as stat_effects

    socket_requirements = Column(JSON)
    # Requirements for the item to be socketed (not the base item)
    # {"item_level": 10, "character_level": 20}

    # ===== ITEM LEVELING SYSTEM =====
    is_levelable = Column(Boolean, default=False)
    # Can this item gain levels through use/experience?

    max_item_level = Column(Integer, default=1)
    # Maximum level this item can reach (1 = no leveling)

    exp_per_level = Column(Integer, default=100)
    # Base experience needed per level

    level_exp_formula = Column(Text)
    # Formula for exp requirements: "100 * (level ^ 1.5)"

    stat_scaling_per_level = Column(JSON)
    # How stats increase per level
    # {"strength": 2, "attack_power": 5} - adds this much per level

    # Leveling requirement type
    item_level_requirement_type = Column(String(50), default='exp')
    # Options: "exp", "materials", "attributes", "hybrid"
    # - exp: Traditional experience points
    # - materials: Consume materials to level up
    # - attributes: Require character attributes (stats, level, etc.)
    # - hybrid: Combination of multiple requirements

    # Material requirements for leveling (when type includes materials)
    level_material_requirements = Column(JSON)
    # Materials needed per level or formula-based
    # Per-level: {"1": {"iron_ore": 5}, "2": {"iron_ore": 10, "steel": 2}, ...}
    # Formula-based: {"iron_ore": "level * 5", "steel": "level * 2"}
    # Flat: {"iron_ore": 10, "steel": 5} - same for all levels

    # Attribute requirements for leveling (when type includes attributes)
    level_attribute_requirements = Column(JSON)
    # Character attribute requirements per level or formula-based
    # Per-level: {"1": {"strength": 10}, "2": {"strength": 15, "level": 5}, ...}
    # Formula-based: {"strength": "item_level * 5 + 10", "level": "item_level * 2"}
    # Threshold: {"strength": 50} - must have at least this much

    # Hybrid requirements configuration
    level_hybrid_mode = Column(String(20), default='all')
    # Options: "all", "any", "weighted"
    # - all: Must meet ALL requirement types
    # - any: Must meet ANY ONE requirement type
    # - weighted: Requirements contribute proportionally (for partial leveling)

    # ===== ITEM EVOLUTION SYSTEM =====
    can_evolve = Column(Boolean, default=False)
    # Can this item evolve into another item?

    evolution_level_requirement = Column(Integer)
    # Minimum item level required to evolve

    evolution_material_requirements = Column(JSON)
    # {"iron_ore": 10, "magic_crystal": 5} - materials needed

    evolution_stat_requirements = Column(JSON)
    # {"strength": 50, "level": 30} - character stat requirements

    evolution_options = Column(JSON)
    # [
    #   {
    #     "target_item_key": "legendary_sword",
    #     "target_item_name": "Legendary Blade",
    #     "requirements": {"item_level": 10, "materials": {...}},
    #     "description": "Evolves into a legendary weapon"
    #   }
    # ]

    evolves_from = Column(String(100))
    # Item key this evolved from (for tracking lineage)

    evolution_tree_tier = Column(Integer, default=1)
    # Tier in evolution tree (1 = base, 2 = first evolution, etc.)

    # ===== CRAFTING SYSTEM =====
    is_craftable = Column(Boolean, default=False)
    # Can this item be crafted by players?

    crafting_recipe = Column(JSON)
    # Materials needed to craft
    # {"iron_ore": 10, "wood": 5, "magic_crystal": 1}

    crafting_time = Column(Integer, default=0)
    # Time to craft in seconds (0 = instant)

    crafting_skill_requirements = Column(JSON)
    # {"blacksmithing": 50, "enchanting": 20} - skill levels needed

    crafting_level_requirements = Column(JSON)
    # {"character_level": 30, "class_level": 15} - level requirements

    crafting_stat_requirements = Column(JSON)
    # {"strength": 50, "intelligence": 30} - stat requirements

    crafting_class_requirements = Column(JSON)
    # ["Blacksmith", "Warrior", "Craftsman"] - allowed classes

    crafting_location_requirements = Column(JSON)
    # ["forge", "anvil", "enchanting_table"] - required locations/stations

    # ===== ECONOMY & PRICING =====
    # Note: base_value already exists above, this is for economy system
    price_calculation_method = Column(String(50), default='fixed')
    # Options: "fixed", "material_based", "supply_demand", "dynamic"

    material_price_multiplier = Column(Float, default=1.5)
    # When using material_based: price = sum(materials) * multiplier

    enable_supply_demand = Column(Boolean, default=False)
    # Enable dynamic pricing based on supply/demand

    supply_demand_sensitivity = Column(Float, default=1.0)
    # How much supply/demand affects price (0.0-2.0)

    # ===== EFFECTS SYSTEM =====
    # What bonuses/effects this attribute grants
    stat_effects = Column(JSON)
    # Examples:
    # Item: {"strength": 10, "hp": 50, "critical_chance": 5}
    # Race: {"agility": 5, "speed": 10}
    # Class: {"intelligence": 15, "mana": 100}
    # Buff: {"attack_power": 20, "speed": 15}

    # Requirements to use/equip/access
    requirements = Column(JSON)
    # {"level": 10, "strength": 15, "class": ["warrior", "knight"], "race": ["human"]}

    # ===== INVESTMENT SYSTEM (for progression/currency attributes) =====
    is_investable = Column(Boolean, default=False)
    # Can players spend points to increase this?

    is_investment_resource = Column(Boolean, default=False)
    # Is this attribute used as currency for investing? (skill_points, attribute_points)

    investment_resource = Column(String(100))
    # What resource is required to invest in this attribute

    cost_formula = Column(Text)
    # Formula for investment cost: "10 * (points_invested + 1)"

    # Investment targets (what can this resource invest in?)
    can_invest_in_stats = Column(Boolean, default=True)
    can_invest_in_techniques = Column(Boolean, default=False)
    can_invest_in_skills = Column(Boolean, default=False)
    can_invest_in_classes = Column(Boolean, default=False)

    # ===== STATUS-SPECIFIC (when attribute_type = "status") =====
    is_temporary = Column(Boolean, default=False)
    # Expires after time/turns?

    default_duration = Column(Integer)
    # Default duration in turns/rounds

    is_removable = Column(Boolean, default=True)
    # Can be manually removed/dispelled?

    # ===== PROTECTION & SAFETY =====
    is_system_attribute = Column(Boolean, default=False)
    # System-critical attributes (name, level, HP, etc.) - CANNOT be deleted

    is_protected = Column(Boolean, default=False)
    # Protected from deletion (shows warning, requires confirmation)

    can_be_deleted = Column(Boolean, default=True)
    # Can this attribute be deleted at all?

    deletion_warning = Column(Text)
    # Custom warning message shown when attempting to delete

    is_required = Column(Boolean, default=False)
    # Required attribute - all characters must have this

    # ===== METADATA =====
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(BigInteger)
    # Admin who created this attribute definition

    __table_args__ = (
        UniqueConstraint('guild_id', 'attribute_key', name='uq_guild_attribute'),
        Index('idx_attr_guild_type', 'guild_id', 'attribute_type'),
        Index('idx_attr_guild_subtype', 'guild_id', 'attribute_subtype'),
        Index('idx_attr_type_subtype', 'attribute_type', 'attribute_subtype'),
    )


class CharacterAttribute(Base):
    """
    Character's actual attribute values/instances

    This single model replaces:
    - CharacterStat (stat values)
    - Inventory (item ownership)
    - Basic table fields (name, age, level, exp, gold, etc.)
    - Active effects/buffs

    Every piece of character data is a CharacterAttribute linked to an AttributeDefinition.
    """
    __tablename__ = "character_attributes"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    character_id = Column(BigInteger, ForeignKey("characters.id"), nullable=False, index=True)
    attribute_def_id = Column(BigInteger, ForeignKey("attribute_definitions.id"), nullable=False, index=True)

    # ===== VALUE STORAGE (FLEXIBLE) =====
    # For numeric values (stats, currency, level, quantity, etc.)
    base_value = Column(Float, default=0)
    # Base/starting value set by admin or default

    bonus_value = Column(Float, default=0)
    # Bonuses from items/buffs/effects (calculated from stat_effects)

    current_value = Column(Float)
    # For gauge stats: current resource amount (current_hp, current_mana)

    max_value = Column(Float)
    # For gauge stats: maximum resource amount

    # For text values (identity attributes like name, backstory)
    text_value = Column(String)

    # For complex data (JSON storage)
    json_value = Column(JSON)

    # ===== ITEM-SPECIFIC =====
    quantity = Column(Integer, default=1)
    # Stack size for items

    is_equipped = Column(Boolean, default=False)
    # For equippable items

    equipped_slot = Column(String(50))
    # Which equipment slot if equipped

    # Item leveling (for levelable items)
    item_level = Column(Integer, default=1)
    # Current level of this item instance

    item_exp = Column(Integer, default=0)
    # Current experience points towards next level

    item_total_exp = Column(Integer, default=0)
    # Total experience earned (for tracking)

    # Creator tracking (for crafted items)
    is_player_crafted = Column(Boolean, default=False)
    # Is this player-crafted vs loot/shop item?

    crafted_by_character_id = Column(BigInteger)
    # Character who crafted this item

    crafted_by_player_id = Column(BigInteger)
    # Player who crafted (for cross-character tracking)

    crafter_name = Column(String(200))
    # Name of crafter for display purposes

    crafted_at = Column(DateTime)
    # When this item was crafted

    # ===== CUSTOM NAMING =====
    custom_name = Column(String(200))
    # Player-given custom name for this item instance
    # Allows naming weapons like "Excalibur" or "Dragon Slayer"
    # Original item name is preserved in AttributeDefinition

    custom_name_set_at = Column(DateTime)
    # When the custom name was set

    custom_name_set_by = Column(BigInteger)
    # Character ID who set the custom name

    # ===== SOCKET/MODIFICATION TRACKING =====
    socketed_items = Column(JSON)
    # Tracks what items are in each socket
    # Format supports multiple styles:
    # Indexed: {"0": item_id, "1": item_id, "2": null} - by slot index
    # Typed: {"red_1": item_id, "blue_1": item_id, "generic_1": null} - by socket type
    # Named: {"fire_socket": item_id, "ice_socket": null} - by socket name
    # All reference character_attribute IDs of the socketed items

    socket_modifications = Column(JSON)
    # Additional modification data per socket
    # {"0": {"added_at": "2025-01-15", "modified_by": 12345}}
    # Tracks history and metadata of socket modifications

    total_sockets_used = Column(Integer, default=0)
    # Quick count of how many sockets are currently filled

    # ===== TEMPORARY/TIMED ATTRIBUTES =====
    is_temporary = Column(Boolean, default=False)
    # Will expire?

    expires_at = Column(DateTime)
    # When it expires (absolute time)

    duration_remaining = Column(Integer)
    # Turns/rounds remaining (for combat)

    # ===== SOURCE TRACKING =====
    # Know where every value comes from
    source_type = Column(String(50))
    # Options: race, class, item, equipment, buff, debuff, manual, formula, default

    source_id = Column(BigInteger)
    # ID of source attribute (if applicable)

    source_name = Column(String(200))
    # Human-readable source name ("Iron Sword", "Warrior Class", "Haste Potion")

    # ===== INVESTMENT TRACKING (for progression attributes) =====
    points_invested = Column(Integer, default=0)
    # How many times this attribute was increased through investment

    total_earned = Column(Float, default=0)
    # For investment resources: total ever earned

    total_spent = Column(Float, default=0)
    # For investment resources: total ever spent
    # Available = total_earned - total_spent

    # ===== METADATA =====
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_modified_by = Column(BigInteger)
    # Admin who last edited this value

    # Relationships
    attribute_def = relationship("AttributeDefinition", foreign_keys=[attribute_def_id])

    __table_args__ = (
        UniqueConstraint('character_id', 'attribute_def_id', name='uq_char_attribute'),
        Index('idx_char_attr_char_def', 'character_id', 'attribute_def_id'),
        Index('idx_char_attr_equipped', 'character_id', 'is_equipped'),
        Index('idx_char_attr_source', 'character_id', 'source_type'),
        Index('idx_char_attr_temporary', 'is_temporary', 'expires_at'),
    )


class AttributeHistory(Base):
    """
    Track all changes to character attributes for audit and rollback
    """
    __tablename__ = "attribute_history"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    character_id = Column(BigInteger, ForeignKey("characters.id"), nullable=False, index=True)
    attribute_def_id = Column(BigInteger, ForeignKey("attribute_definitions.id"), nullable=False)

    # What changed
    old_value = Column(Float)
    new_value = Column(Float)
    old_text_value = Column(String)
    new_text_value = Column(String)
    change_amount = Column(Float)

    # Why it changed
    change_reason = Column(String(200))
    change_type = Column(String(50))
    # manual, investment, equipment, buff, formula, level_up, reward

    # Who changed it
    changed_by = Column(BigInteger)
    # Admin or system ID

    # When
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    __table_args__ = (
        Index('idx_attr_history_char', 'character_id', 'created_at'),
        Index('idx_attr_history_def', 'attribute_def_id', 'created_at'),
    )
