"""
Economy System Models: Income Brackets and Cooldown Management

This module contains all economy-related database models including:
- Income brackets with admin controls
- Cooldown management for income and other systems
- Clan-based income bonuses
"""

from sqlalchemy import BigInteger, Boolean, Column, Float, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from database.base import Base


class IncomeBracket(Base):
    """Define income brackets with customizable tiers"""
    __tablename__ = "income_brackets"

    id = Column(Integer, primary_key=True, autoincrement=True)
    guild_id = Column(BigInteger, index=True, nullable=False)

    # Bracket details
    bracket_name = Column(String, nullable=False)  # e.g., "Low Income", "Middle Class", "Wealthy"
    bracket_level = Column(Integer, nullable=False)  # Ranking/tier level (1=lowest, higher=better)
    emoji = Column(String, default="💰")

    # Income amounts
    base_income = Column(Integer, nullable=False)  # Base amount per claim
    bonus_income = Column(Integer, default=0)  # Additional bonus amount

    # Requirements
    rank_required = Column(String, nullable=True)  # Overall rank required (e.g., "B+")
    total_exp_required = Column(Integer, default=0)  # Minimum total EXP required

    # Cooldown (in hours)
    cooldown_hours = Column(Integer, default=24)  # How often can claim (default 24hr)

    # Special flags
    is_default = Column(Boolean, default=False)  # True = assigned to new characters
    requires_approval = Column(Boolean, default=False)  # True = admin must manually assign

    # Metadata
    description = Column(String, default="")
    created_by = Column(BigInteger, nullable=False)  # Discord ID
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    clan_bonuses = relationship("ClanIncomeBonus", back_populates="bracket", cascade="all, delete-orphan")


class ClanIncomeBonus(Base):
    """Clan-specific bonuses to income brackets"""
    __tablename__ = "clan_income_bonuses"

    id = Column(Integer, primary_key=True, autoincrement=True)
    guild_id = Column(BigInteger, index=True, nullable=False)
    bracket_id = Column(Integer, ForeignKey("income_brackets.id", ondelete="CASCADE"), nullable=False)
    clan_name = Column(String, nullable=False)

    # Bonus amounts
    flat_bonus = Column(Integer, default=0)  # Flat jenny bonus
    percent_bonus = Column(Float, default=0.0)  # Percentage bonus (e.g., 0.10 = 10% more)

    # Cooldown reduction
    cooldown_reduction_hours = Column(Integer, default=0)  # Reduce cooldown by X hours

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    bracket = relationship("IncomeBracket", back_populates="clan_bonuses")


class GuildCooldowns(Base):
    """Guild-wide cooldown settings (admin configurable)"""
    __tablename__ = "guild_cooldowns"

    guild_id = Column(BigInteger, primary_key=True)

    # Income cooldowns
    income_cooldown_hours = Column(Integer, default=24)  # Default income claim cooldown

    # Character interaction cooldowns
    meditation_cooldown_hours = Column(Integer, default=24)  # Meditation for nen unlock
    rest_cooldown_hours = Column(Integer, default=6)  # Resting to recover aura
    training_cooldown_hours = Column(Integer, default=12)  # Training activities

    # Shop cooldowns
    shop_restock_hours = Column(Integer, default=168)  # How often shop restocks (default 1 week)

    # RP session cooldowns
    rp_claim_cooldown_hours = Column(Integer, default=0)  # Cooldown between RP rewards (0 = none)

    # Combat cooldowns
    combat_initiation_cooldown_minutes = Column(Integer, default=0)  # Cooldown after combat

    # Perk reroll cooldowns
    perk_reroll_cooldown_hours = Column(Integer, default=0)  # Cooldown between perk rerolls

    # Metadata
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = Column(BigInteger, nullable=True)  # Last admin to update


class CharacterCooldowns(Base):
    """Track individual character cooldowns"""
    __tablename__ = "character_cooldowns"

    character_id = Column(BigInteger, ForeignKey("characters.id", ondelete="CASCADE"), primary_key=True)

    # Last action timestamps
    last_income_claim = Column(DateTime, nullable=True)
    last_meditation = Column(DateTime, nullable=True)
    last_rest = Column(DateTime, nullable=True)
    last_training = Column(DateTime, nullable=True)
    last_rp_reward = Column(DateTime, nullable=True)
    last_combat = Column(DateTime, nullable=True)
    last_perk_reroll = Column(DateTime, nullable=True)
    last_shop_purchase = Column(DateTime, nullable=True)

    # Counter fields (for limited uses)
    perk_rerolls_used = Column(Integer, default=0)  # Track total perk rerolls
    daily_meditation_count = Column(Integer, default=0)  # Track meditations today
    daily_meditation_reset = Column(DateTime, nullable=True)  # When to reset counter

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class IncomeTransaction(Base):
    """Log all income claims for tracking and analytics"""
    __tablename__ = "income_transactions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    character_id = Column(BigInteger, ForeignKey("characters.id", ondelete="CASCADE"), nullable=False)
    guild_id = Column(BigInteger, index=True, nullable=False)

    # Transaction details
    bracket_id = Column(Integer, ForeignKey("income_brackets.id"), nullable=True)
    amount_claimed = Column(Integer, nullable=False)
    base_amount = Column(Integer, nullable=False)
    clan_bonus = Column(Integer, default=0)
    other_bonuses = Column(Integer, default=0)

    # Deposited to
    deposited_to_cash = Column(Boolean, default=True)  # True = cash, False = bank
    amount_to_cash = Column(Integer, default=0)
    amount_to_bank = Column(Integer, default=0)

    # Metadata
    claimed_at = Column(DateTime, default=datetime.utcnow, index=True)
    notes = Column(String, default="")  # Optional notes


class MoneyTransaction(Base):
    """Log all money transfers between bank/cash and characters"""
    __tablename__ = "money_transactions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    character_id = Column(BigInteger, ForeignKey("characters.id", ondelete="CASCADE"), nullable=False)
    guild_id = Column(BigInteger, index=True, nullable=False)

    # Transaction type
    transaction_type = Column(String, nullable=False, index=True)
    # "bank_deposit", "bank_withdrawal", "transfer_to", "transfer_from",
    # "purchase", "reward", "admin_grant", "admin_remove", "stolen", "lost"

    # Amounts
    amount = Column(Integer, nullable=False)

    # Source/destination
    from_location = Column(String, nullable=True)  # "cash", "bank", "character_X", "shop", "admin"
    to_location = Column(String, nullable=True)  # "cash", "bank", "character_X", "shop", "admin"

    # Related entities
    related_character_id = Column(BigInteger, nullable=True)  # If transferring to another character
    related_item_id = Column(BigInteger, nullable=True)  # If purchasing an item

    # Balances after transaction
    cash_after = Column(Integer, default=0)
    bank_after = Column(Integer, default=0)

    # Metadata
    transaction_date = Column(DateTime, default=datetime.utcnow, index=True)
    initiated_by = Column(BigInteger, nullable=False)  # Discord ID who initiated
    notes = Column(String, default="")
    is_admin_transaction = Column(Boolean, default=False)
