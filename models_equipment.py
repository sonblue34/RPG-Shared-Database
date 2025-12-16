"""
Equipment Slot System Models

Defines equipment slots and their interactions for the flexible equipment system.
"""

from sqlalchemy import Column, BigInteger, Integer, String, Boolean, Text, JSON, DateTime, ForeignKey
from datetime import datetime
from database.base import Base


class EquipmentSlotDefinition(Base):
    """Defines equipment slots available in the game"""
    __tablename__ = "equipment_slot_definitions"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    guild_id = Column(BigInteger, nullable=False, index=True)

    # Identity
    slot_key = Column(String(50), nullable=False, index=True)
    # "main_hand", "off_hand", "ring", "head", "ammo_slot"

    slot_name = Column(String(100), nullable=False)
    # "Main Hand", "Off Hand", "Ring Slot", "Head Slot"

    description = Column(Text)
    # "Primary weapon slot for right-handed weapons"

    # Display
    icon_emoji = Column(String(50))
    display_order = Column(Integer, default=0)

    # ===== SLOT CONFIGURATION =====
    default_slot_count = Column(Integer, default=1)
    # How many of this slot by default? (1 for weapon, 2 for rings, etc.)

    is_enabled = Column(Boolean, default=True)
    # Can this slot be used at all?

    # ===== CLASS-BASED VARIATIONS =====
    class_slot_counts = Column(JSON)
    # {"Warrior": 1, "Rogue": 2, "Mage": 0}
    # Class-specific slot counts (for dual-wield, multiple rings, etc.)

    # ===== LEVEL REQUIREMENTS =====
    unlock_level = Column(Integer, default=1)
    # Character level required to use this slot

    # ===== SLOT RESTRICTIONS =====
    allowed_item_types = Column(JSON)
    # ["weapon", "shield"] - what can go in this slot

    allowed_item_subtypes = Column(JSON)
    # ["sword", "axe", "mace"] - more specific restrictions

    blocked_item_tags = Column(JSON)
    # ["two-handed"] - items with these tags can't use this slot

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<EquipmentSlotDefinition(guild_id={self.guild_id}, slot_key='{self.slot_key}', slot_name='{self.slot_name}')>"


class ItemSlotInteraction(Base):
    """Defines slot interactions for items (two-handed, ammo requirements, etc.)"""
    __tablename__ = "item_slot_interactions"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    guild_id = Column(BigInteger, nullable=False, index=True)

    # The item this applies to
    attribute_def_id = Column(BigInteger, ForeignKey("attribute_definitions.id"), nullable=False)
    item_name = Column(String(200))

    # ===== SLOT OCCUPANCY =====
    primary_slot = Column(String(50), nullable=False)
    # "main_hand" - the main slot this item uses

    occupies_slots = Column(JSON)
    # ["main_hand", "off_hand"] - all slots this item takes up
    # Two-handed sword: ["main_hand", "off_hand"]
    # Shield: ["off_hand"]
    # Ring: ["ring"]

    # ===== SLOT REQUIREMENTS =====
    requires_empty_slots = Column(JSON)
    # ["off_hand"] - these slots must be empty to equip

    requires_item_in_slot = Column(JSON)
    # {"off_hand": {"item_type": "ammo", "ammo_type": "arrow"}}
    # Bow requires arrows in off_hand/ammo_slot

    blocks_slots = Column(JSON)
    # ["off_hand"] - prevents using these slots while equipped
    # Shield blocks off_hand weapon use

    # ===== AMMO SYSTEM =====
    requires_ammo = Column(Boolean, default=False)
    required_ammo_type = Column(String(50))
    # "arrow", "bolt", "bullet", "magic_charge"

    ammo_consumption_rate = Column(Integer, default=1)
    # How much ammo consumed per use/attack

    ammo_capacity = Column(Integer)
    # For items that hold ammo (quiver holds 30 arrows)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<ItemSlotInteraction(guild_id={self.guild_id}, item_name='{self.item_name}', primary_slot='{self.primary_slot}')>"
