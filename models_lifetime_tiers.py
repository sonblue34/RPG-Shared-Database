"""
Lifetime Tier System

Rewards for beta supporters who reach specific donation milestones.
Grants permanent tier access with discounts on upgrades.
"""
from sqlalchemy import BigInteger, Column, Integer, String, DateTime, Float, Text, Boolean
from datetime import datetime
from database.base import Base


class LifetimeTierGrant(Base):
    """
    Lifetime tier grants for early supporters
    These are permanent and cannot be revoked
    """
    __tablename__ = "lifetime_tier_grants"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, nullable=False, unique=True, index=True)

    # Tier Info
    granted_tier = Column(String(50), nullable=False)  # "basic", "premium", "enterprise"
    tier_value = Column(Integer, nullable=False)  # Tier hierarchy: 1=basic, 2=premium, 3=enterprise, etc.

    # Grant Reason
    grant_type = Column(String(50), nullable=False)  # "beta_supporter", "donation_milestone", "special_grant"
    donation_total = Column(Float, default=0.0)  # Total donations that earned this tier
    milestone_reached = Column(String(100), nullable=True)  # E.g., "$500 Beta Supporter"

    # Upgrade Discount
    upgrade_discount_percent = Column(Float, default=0.0)  # Discount on future tier upgrades (0-100)
    stackable_with_promos = Column(Boolean, default=True)  # Can combine with promotional discounts

    # Proof/Documentation
    granted_by_admin_id = Column(BigInteger, nullable=True)  # Admin who granted this
    grant_notes = Column(Text, nullable=True)  # Internal notes about the grant
    proof_url = Column(String(500), nullable=True)  # Link to donation proof/receipt

    # Status
    is_active = Column(Boolean, default=True)
    revoked = Column(Boolean, default=False)  # Should never be true, but just in case
    revoked_at = Column(DateTime, nullable=True)
    revoke_reason = Column(Text, nullable=True)

    # Metadata
    granted_at = Column(DateTime, default=datetime.utcnow, index=True)


class BetaSupporterMilestone(Base):
    """
    Configuration for beta supporter milestone rewards
    Defines what donation amounts unlock which lifetime tiers
    """
    __tablename__ = "beta_supporter_milestones"

    id = Column(BigInteger, primary_key=True, autoincrement=True)

    # Milestone Info
    milestone_name = Column(String(100), nullable=False, unique=True)
    display_name = Column(String(200), nullable=False)  # Public-facing name
    description = Column(Text, nullable=True)

    # Requirements
    required_donation = Column(Float, nullable=False)  # Minimum donation to unlock
    beta_only = Column(Boolean, default=True)  # Only available during beta

    # Rewards
    granted_tier = Column(String(50), nullable=False)  # Tier granted
    upgrade_discount = Column(Float, default=0.0)  # Discount on future upgrades (%)

    # Bonus Perks (optional)
    bonus_storage_gb = Column(Float, default=0.0)  # Extra storage beyond tier
    bonus_commands_monthly = Column(Integer, default=0)  # Extra commands beyond tier
    special_badge = Column(String(100), nullable=True)  # Discord badge/role name
    special_badge_emoji = Column(String(50), nullable=True)  # Emoji for the badge

    # Display Settings
    display_order = Column(Integer, default=0)  # Order to show milestones
    show_in_public_list = Column(Boolean, default=True)  # Show on supporter page
    highlight_color = Column(String(7), default="#FFD700")  # Hex color for display

    # Availability
    is_active = Column(Boolean, default=True)
    available_from = Column(DateTime, nullable=True)  # When milestone becomes available
    available_until = Column(DateTime, nullable=True)  # When milestone expires (for beta)
    max_grants = Column(Integer, nullable=True)  # Limit on number of grants (null = unlimited)
    current_grants = Column(Integer, default=0)  # How many have been granted

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class UserLifetimeBenefit(Base):
    """
    Tracks active lifetime benefits for users
    Combines base tier grant with any bonuses/perks
    """
    __tablename__ = "user_lifetime_benefits"

    user_id = Column(BigInteger, primary_key=True)

    # Current Lifetime Tier
    lifetime_tier = Column(String(50), nullable=False)  # Base tier they have lifetime access to
    tier_value = Column(Integer, nullable=False)  # Tier hierarchy number

    # Upgrade Pricing
    upgrade_discount_percent = Column(Float, default=0.0)  # Discount on tier upgrades
    next_tier = Column(String(50), nullable=True)  # Next tier they could upgrade to
    next_tier_cost = Column(Float, nullable=True)  # Cost to upgrade (with discount applied)

    # Bonus Allocations (cumulative from all grants)
    bonus_storage_gb = Column(Float, default=0.0)  # Extra storage
    bonus_commands_monthly = Column(Integer, default=0)  # Extra commands
    bonus_compute_hours = Column(Float, default=0.0)  # Extra compute

    # Badges & Recognition
    supporter_badges = Column(Text, default="[]")  # JSON array of badge names
    public_recognition = Column(Boolean, default=True)  # Show in supporter list
    supporter_rank = Column(String(50), nullable=True)  # "Bronze", "Silver", "Gold", "Platinum", "Diamond"

    # Usage Tracking
    total_donated = Column(Float, default=0.0)  # Total lifetime donations
    donation_count = Column(Integer, default=0)  # Number of donations made

    # Status
    is_active = Column(Boolean, default=True)

    # Metadata
    first_donation_at = Column(DateTime, nullable=True)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ServerLifetimeBenefits(Base):
    """
    Lifetime tier benefits applied to servers
    Tracks which servers have lifetime tier coverage and from whom
    """
    __tablename__ = "server_lifetime_benefits"

    guild_id = Column(BigInteger, primary_key=True)

    # Primary Benefactor
    primary_benefactor_user_id = Column(BigInteger, nullable=False, index=True)  # User who granted their tier
    benefactor_lifetime_tier = Column(String(50), nullable=False)  # Their lifetime tier

    # Server Benefits
    effective_tier = Column(String(50), nullable=False)  # Current tier applied to server
    tier_value = Column(Integer, nullable=False)  # Tier hierarchy

    # Bonus Allocations (if benefactor has bonuses)
    bonus_storage_gb = Column(Float, default=0.0)
    bonus_commands_monthly = Column(Integer, default=0)
    bonus_compute_hours = Column(Float, default=0.0)

    # Additional Contributors
    additional_benefactors = Column(Text, default="[]")  # JSON array of {user_id, tier, date}

    # Billing Integration
    overrides_paid_tier = Column(Boolean, default=True)  # Lifetime tier overrides paid subscription
    can_upgrade = Column(Boolean, default=True)  # Can still upgrade beyond lifetime tier

    # Status
    is_active = Column(Boolean, default=True)
    assigned_at = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class TierUpgradeDiscount(Base):
    """
    Calculates and tracks discounts for users upgrading their tiers
    Lifetime tier holders get permanent discounts
    """
    __tablename__ = "tier_upgrade_discounts"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, nullable=False, index=True)

    # Discount Source
    discount_type = Column(String(50), nullable=False)  # "lifetime_holder", "promotional", "loyalty"
    source_tier = Column(String(50), nullable=True)  # Their current/base tier

    # Discount Details
    discount_percent = Column(Float, nullable=False)  # Percentage off (0-100)
    applies_to_tiers = Column(Text, default="[]")  # JSON array of tier names this applies to
    stackable = Column(Boolean, default=True)  # Can combine with other discounts

    # Validity
    permanent = Column(Boolean, default=False)  # Never expires (for lifetime holders)
    valid_from = Column(DateTime, default=datetime.utcnow)
    valid_until = Column(DateTime, nullable=True)  # Null = no expiration

    # Usage
    times_used = Column(Integer, default=0)
    max_uses = Column(Integer, nullable=True)  # Null = unlimited

    # Status
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class BetaDonationProgress(Base):
    """
    Tracks user progress toward beta supporter milestones
    Shows how close they are to unlocking lifetime tiers
    """
    __tablename__ = "beta_donation_progress"

    user_id = Column(BigInteger, primary_key=True)

    # Current Progress
    total_donated = Column(Float, default=0.0)  # Total donated during beta
    donation_count = Column(Integer, default=0)

    # Milestones
    highest_milestone_reached = Column(String(100), nullable=True)  # Name of highest milestone
    highest_tier_unlocked = Column(String(50), nullable=True)  # Tier unlocked by milestone
    next_milestone = Column(String(100), nullable=True)  # Next milestone to work toward
    next_milestone_remaining = Column(Float, default=0.0)  # Amount needed for next milestone

    # Recognition
    public_donor = Column(Boolean, default=True)  # Show in public donor list
    donor_message = Column(Text, nullable=True)  # Custom message to display

    # Metadata
    first_donation_at = Column(DateTime, nullable=True)
    last_donation_at = Column(DateTime, nullable=True)
    milestone_checked_at = Column(DateTime, default=datetime.utcnow)  # Last time we checked milestones
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
