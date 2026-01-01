"""
Gacha System Models - Refactored for cleaner coin management
"""
from sqlalchemy import BigInteger, Boolean, Column, Float, ForeignKey, Integer, String, DateTime, Text, UniqueConstraint, Index
from sqlalchemy.orm import relationship
from datetime import datetime
from database.base import Base


class GachaCoin(Base):
    """
    Coin types used across gacha machines
    Multiple machines can use the same coin type
    """
    __tablename__ = "gacha_coins"

    id = Column(Integer, primary_key=True, autoincrement=True)
    guild_id = Column(BigInteger, nullable=False, index=True)

    # Coin details
    coin_name = Column(String(100), nullable=False)  # e.g., "Premium Coins", "Event Tokens"
    coin_icon = Column(String(50), default="🪙")  # Emoji for the coin
    coin_color = Column(String(10))  # Hex color for embeds

    # Default rewards
    welcome_amount = Column(Integer, default=0)  # Coins given when user first registers
    daily_amount = Column(Integer, default=0)  # Daily free coins (0 = disabled)

    # Metadata
    created_by = Column(BigInteger, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    machines = relationship("GachaMachine", back_populates="coin")
    balances = relationship("GachaCoinBalance", back_populates="coin", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint('guild_id', 'coin_name', name='uq_gacha_coin_name'),
    )


class GachaMachine(Base):
    """
    Gacha machine configuration
    Now references a shared coin type instead of storing coin details
    """
    __tablename__ = "gacha_machines"

    id = Column(Integer, primary_key=True, autoincrement=True)
    guild_id = Column(BigInteger, nullable=False, index=True)

    # Machine details
    name = Column(String(100), nullable=False)
    description = Column(String(500))

    # Currency settings (now references GachaCoin)
    coin_id = Column(Integer, ForeignKey("gacha_coins.id"), nullable=False, index=True)
    cost_per_roll = Column(Integer, default=1)  # How many coins per roll

    # Roll settings
    rolls_per_pull = Column(Integer, default=1)  # How many items per pull
    daily_limit = Column(Integer, nullable=True)  # NULL = unlimited

    # Combo settings
    combo_enabled = Column(Boolean, default=False)  # Enable/disable combo system

    # Pity system settings (REFACTORED)
    pity_enabled = Column(Boolean, default=False)  # Enable/disable pity
    pity_guaranteed_rolls = Column(Integer, default=50)  # After X rolls, guarantee a rank
    pity_guaranteed_rank = Column(String(50), nullable=True)  # Which rank to guarantee (e.g., "Legendary")
    # Note: Pity counter tracks per user per machine

    # Display settings
    icon_emoji = Column(String(50), default="🎰")
    color = Column(String(10))  # Hex color for embeds

    # Status
    enabled = Column(Boolean, default=True)

    # Metadata
    created_by = Column(BigInteger, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    coin = relationship("GachaCoin", back_populates="machines")
    ranks = relationship("GachaRank", back_populates="machine", cascade="all, delete-orphan", order_by="GachaRank.rank_order")
    rewards = relationship("GachaReward", back_populates="machine", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint('guild_id', 'name', name='uq_gacha_machine_name'),
    )


class GachaRank(Base):
    """
    Rarity ranks for gacha rewards (e.g., Common, Rare, Legendary)
    Stars (⭐) indicate rarity - more stars = higher rarity
    """
    __tablename__ = "gacha_ranks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    machine_id = Column(Integer, ForeignKey("gacha_machines.id"), nullable=False, index=True)
    guild_id = Column(BigInteger, nullable=False, index=True)

    # Rank details
    rank_name = Column(String(50), nullable=False)  # e.g., "Common", "Rare", "SSR"
    rank_order = Column(Integer, default=0)  # Display order (LOWER = HIGHER rarity, 0 = top tier)
    star_count = Column(Integer, default=1)  # Number of stars (1-5+) for visual display

    # Drop rate (as percentage)
    drop_rate = Column(Float, nullable=False)  # e.g., 50.0 for 50%

    # Display settings
    rank_emoji = Column(String(50), default="⭐")  # Default star emoji
    rank_color = Column(String(10))  # Hex color

    # Special rewards (optional)
    bonus_coins = Column(Integer, default=0)  # Extra coins awarded on this rank

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    machine = relationship("GachaMachine", back_populates="ranks")
    rewards = relationship("GachaReward", back_populates="rank", cascade="all, delete-orphan")

    __table_args__ = (
        Index('idx_gacha_rank_order', 'machine_id', 'rank_order'),
    )


class GachaReward(Base):
    """
    Individual rewards (items) that can be obtained from gacha
    Links to items from the unified attribute system (item panel)
    """
    __tablename__ = "gacha_rewards"

    id = Column(Integer, primary_key=True, autoincrement=True)
    machine_id = Column(Integer, ForeignKey("gacha_machines.id"), nullable=False, index=True)
    rank_id = Column(Integer, ForeignKey("gacha_ranks.id"), nullable=False, index=True)
    guild_id = Column(BigInteger, nullable=False, index=True)

    # Link to item from item panel
    item_id = Column(BigInteger, ForeignKey("attribute_definitions.id"), nullable=True, index=True)
    # If item_id is set, item details are pulled from AttributeDefinition
    # If null, falls back to reward_name/description for legacy rewards

    # Legacy fields (for backward compatibility)
    reward_name = Column(String(200), nullable=True)  # Item name (legacy or override)
    reward_description = Column(String(500))  # Description (legacy or override)

    # Quantity management
    quantity_limit = Column(Integer, nullable=True)  # NULL = unlimited
    quantity_remaining = Column(Integer, nullable=True)  # Current stock, NULL = unlimited

    # Display
    reward_emoji = Column(String(50))  # Override emoji from item

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    machine = relationship("GachaMachine", back_populates="rewards")
    rank = relationship("GachaRank", back_populates="rewards")


class GachaCoinBalance(Base):
    """
    Tracks user coin balances per coin type
    """
    __tablename__ = "gacha_coin_balances"

    id = Column(Integer, primary_key=True, autoincrement=True)
    guild_id = Column(BigInteger, nullable=False, index=True)
    user_id = Column(BigInteger, nullable=False, index=True)
    coin_id = Column(Integer, ForeignKey("gacha_coins.id"), nullable=False, index=True)

    # Balance
    balance = Column(Integer, default=0)

    # Daily tracking
    last_daily_claim = Column(DateTime, nullable=True)  # When user last claimed daily coins

    # Statistics
    total_earned = Column(Integer, default=0)  # Total coins ever earned
    total_spent = Column(Integer, default=0)  # Total coins ever spent

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    coin = relationship("GachaCoin", back_populates="balances")

    __table_args__ = (
        UniqueConstraint('guild_id', 'user_id', 'coin_id', name='uq_gacha_coin_balance'),
    )


class GachaRegistration(Base):
    """
    Tracks which users have registered for gacha system
    """
    __tablename__ = "gacha_registrations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    guild_id = Column(BigInteger, nullable=False, index=True)
    user_id = Column(BigInteger, nullable=False, index=True)
    username = Column(String(100), nullable=False)

    # Metadata
    registered_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint('guild_id', 'user_id', name='uq_gacha_registration'),
    )


class GachaPityCounter(Base):
    """
    Tracks pity counter for each user per machine
    Increments with each roll, resets when guaranteed rank is obtained
    """
    __tablename__ = "gacha_pity_counters"

    id = Column(Integer, primary_key=True, autoincrement=True)
    guild_id = Column(BigInteger, nullable=False, index=True)
    user_id = Column(BigInteger, nullable=False, index=True)
    machine_id = Column(Integer, ForeignKey("gacha_machines.id"), nullable=False)

    # Counter
    rolls_since_pity = Column(Integer, default=0)  # Number of rolls since last pity activation
    total_rolls = Column(Integer, default=0)  # Total rolls on this machine

    # Metadata
    last_roll_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint('guild_id', 'user_id', 'machine_id', name='uq_gacha_pity_counter'),
    )


class GachaCombo(Base):
    """
    Combo rewards for getting specific combinations of items
    """
    __tablename__ = "gacha_combos"

    id = Column(Integer, primary_key=True, autoincrement=True)
    machine_id = Column(Integer, ForeignKey("gacha_machines.id"), nullable=False, index=True)
    guild_id = Column(BigInteger, nullable=False, index=True)

    # Combo details
    combo_name = Column(String(100), nullable=False)
    required_items = Column(Text, nullable=False)  # JSON array of reward IDs

    # Bonus reward
    bonus_type = Column(String(50), nullable=False)  # "coins", "item", "stat"
    bonus_value = Column(String(200), nullable=False)  # Amount or item name

    # Display
    combo_emoji = Column(String(50))

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index('idx_gacha_combo_machine', 'machine_id'),
    )


class GachaRollHistory(Base):
    """
    Tracks individual roll history for analytics and daily limits
    Each roll in a multi-pull shares the same pull_id
    """
    __tablename__ = "gacha_roll_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    guild_id = Column(BigInteger, nullable=False, index=True)
    user_id = Column(BigInteger, nullable=False, index=True)
    machine_id = Column(Integer, ForeignKey("gacha_machines.id"), nullable=False, index=True)

    # Pull grouping
    pull_id = Column(String(36), nullable=False, index=True)  # UUID to group rolls from same pull

    # Roll details
    reward_id = Column(Integer, ForeignKey("gacha_rewards.id"), nullable=False)
    rank_id = Column(Integer, ForeignKey("gacha_ranks.id"), nullable=False)

    # Timestamp
    rolled_at = Column(DateTime, default=datetime.utcnow, index=True)

    __table_args__ = (
        Index('idx_gacha_roll_user_machine_date', 'guild_id', 'user_id', 'machine_id', 'rolled_at'),
    )
