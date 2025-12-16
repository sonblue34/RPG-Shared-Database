"""
Core character models: User, Character, Basic, Clan, and related access models
"""
from sqlalchemy import BigInteger, Boolean, Column, Float, ForeignKey, Integer, String, DateTime, UniqueConstraint, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from database.base import Base


class User(Base):
    """User table to track Discord users and their active character"""
    __tablename__ = "users"

    discord_id = Column(BigInteger, primary_key=True)
    active_character_slot = Column(Integer, default=1)  # 1, 2, or 3
    bonus_character_slots = Column(Integer, default=0)  # Additional character slots beyond base 3
    created_at = Column(DateTime, default=datetime.utcnow)

    characters = relationship("Character", back_populates="user", cascade="all, delete-orphan")


class Character(Base):
    """Character table - supports both player characters and NPCs"""
    __tablename__ = "characters"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    discord_id = Column(BigInteger, ForeignKey("users.discord_id"), nullable=True)  # NULL for NPCs
    guild_id = Column(BigInteger, nullable=False, index=True)  # Guild where character was created
    character_slot = Column(Integer, nullable=True)  # 1, 2, or 3 for players; NULL for NPCs

    # NPC-specific fields
    is_npc = Column(Boolean, default=False, index=True, nullable=False)  # True if this is an NPC
    npc_slot = Column(Integer, nullable=True)  # NPC slot number within guild (1, 2, 3, etc.)
    created_by = Column(BigInteger, nullable=True)  # Discord ID of admin who created this NPC

    # Admin control for NPCs
    is_public = Column(Boolean, default=True)  # Whether players can see this NPC
    admin_notes = Column(String, nullable=True)  # Private notes about NPC (only admins see)
    allowed_admin_ids = Column(String, nullable=True)  # JSON array of admin discord IDs who can edit this NPC

    # Fake stats system for NPCs
    show_fake_stats = Column(Boolean, default=False)  # Whether to show fake stats to non-admin players
    fake_stats_json = Column(JSON, default={})  # JSON object: {"stat_key": fake_value, "strength": 50, "total_exp": 1000}

    user = relationship("User", back_populates="characters")
    basic = relationship("Basic", back_populates="character", uselist=False, cascade="all, delete-orphan")
    clan = relationship("Clan", back_populates="character", uselist=False, cascade="all, delete-orphan")
    inventory = relationship("Inventory", back_populates="character", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint('discord_id', 'guild_id', 'character_slot', name='unique_user_guild_slot'),
    )


class Basic(Base):
    __tablename__ = "basic"

    character_id = Column(BigInteger, ForeignKey("characters.id"), primary_key=True)
    character_name = Column(String, index=True)
    character_age = Column(Integer)
    character_image = Column(String, default=None)
    race_name = Column(String, default=None, index=True)  # Selected race during character creation
    backstory = Column(String, default=None)  # Approved backstory text or link
    backstory_approved = Column(Boolean, default=False, index=True)  # Character approved for play
    unspent_exp = Column(Integer, default=0)
    spent_exp = Column(Integer, default=0)
    total_exp = Column(Integer, default=0)

    # Money system - split into cash and bank
    cash = Column(Integer, default=0)  # Money on hand (can be stolen/lost in RP)
    bank = Column(Integer, default=0)  # Money in bank (safe storage)

    # Income system
    income_bracket_id = Column(Integer, nullable=True)  # Which income bracket they're in
    last_income_claim = Column(DateTime, default=None)  # Last time income was claimed

    last_session_participation = Column(DateTime, default=None)  # Last time in an RP session
    in_combat = Column(Boolean, default=False)  # True if currently in combat
    combat_id = Column(Integer, nullable=True)  # ID of active combat session
    overall_rank = Column(String, index=True, default="E-")  # Overall character rank based on top 10 stats

    # Perk reroll system
    perk_rerolls_remaining = Column(Integer, default=3)  # Total rerolls allowed per character
    perk_rerolls_used = Column(Integer, default=0)  # Track how many rerolls used

    # Class system
    class_name = Column(String, default=None, index=True)  # Current active class name
    class_level = Column(Integer, default=0)  # Current class level
    class_exp = Column(Integer, default=0)  # EXP earned in current class

    character = relationship("Character", back_populates="basic")


class Clan(Base):
    __tablename__ = "clan"

    character_id = Column(BigInteger, ForeignKey("characters.id"), primary_key=True)
    clan_name = Column(String, default="Undefined")
    is_in_clan = Column(Boolean, index=True, default=False)

    character = relationship("Character", back_populates="clan")
