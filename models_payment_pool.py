"""
Payment Pool System

Allows multiple users to contribute to a server's hosting costs.
Creates a shared balance that bills are paid from automatically.
"""
from sqlalchemy import BigInteger, Column, Integer, String, DateTime, Float, Index, Text, Boolean
from datetime import datetime
from database.base import Base


class ServerPaymentPool(Base):
    """
    Shared payment pool for a server
    Multiple users can contribute to cover hosting costs
    """
    __tablename__ = "server_payment_pools"

    guild_id = Column(BigInteger, primary_key=True)

    # Pool Balance
    current_balance = Column(Float, default=0.0)  # Current available funds
    lifetime_contributions = Column(Float, default=0.0)  # Total ever contributed
    lifetime_spent = Column(Float, default=0.0)  # Total ever spent on bills

    # Auto-Pay Settings
    auto_pay_enabled = Column(Boolean, default=True)  # Automatically pay bills from pool
    low_balance_threshold = Column(Float, default=10.0)  # Warn when balance below this
    auto_refill_enabled = Column(Boolean, default=False)  # Auto-charge contributors
    auto_refill_amount = Column(Float, default=50.0)  # Amount to refill

    # Pool Configuration
    min_contribution = Column(Float, default=1.0)  # Minimum contribution amount
    contribution_public = Column(Boolean, default=True)  # Show contributor names/amounts
    allow_refunds = Column(Boolean, default=False)  # Allow contributors to withdraw

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    last_contribution_at = Column(DateTime, nullable=True)
    last_payment_at = Column(DateTime, nullable=True)


class PoolContribution(Base):
    """
    Individual contributions to a server's payment pool
    Tracks who contributed, how much, and when
    """
    __tablename__ = "pool_contributions"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    guild_id = Column(BigInteger, nullable=False, index=True)

    # Contributor Info
    user_id = Column(BigInteger, nullable=False, index=True)
    user_name = Column(String(255), nullable=True)  # Snapshot of username at contribution time

    # Contribution Details
    amount = Column(Float, nullable=False)  # Amount contributed
    contribution_type = Column(String(50), default="manual")  # "manual", "auto_refill", "recurring"
    payment_method = Column(String(50), nullable=True)  # "stripe", "paypal", "crypto", etc.
    payment_transaction_id = Column(String(255), nullable=True)  # External payment ID

    # Status
    status = Column(String(50), default="completed")  # "pending", "completed", "refunded", "failed"
    refunded_amount = Column(Float, default=0.0)  # If partially refunded
    refunded_at = Column(DateTime, nullable=True)

    # Notes
    contributor_note = Column(Text, nullable=True)  # Optional message from contributor
    admin_note = Column(Text, nullable=True)  # Internal notes

    # Metadata
    contributed_at = Column(DateTime, default=datetime.utcnow, index=True)

    __table_args__ = (
        Index('idx_contributions_guild_user', 'guild_id', 'user_id'),
        Index('idx_contributions_guild_date', 'guild_id', 'contributed_at'),
    )


class PoolPayment(Base):
    """
    Payments made from the pool to cover server bills
    Tracks how pool funds were spent
    """
    __tablename__ = "pool_payments"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    guild_id = Column(BigInteger, nullable=False, index=True)

    # Payment Details
    amount = Column(Float, nullable=False)  # Amount paid
    payment_type = Column(String(50), default="invoice")  # "invoice", "manual", "overage"
    billing_period_id = Column(BigInteger, nullable=True)  # Link to UsageBillingPeriod

    # What was paid for
    description = Column(Text, nullable=False)  # E.g., "Monthly hosting - March 2025"

    # Status
    status = Column(String(50), default="completed")  # "pending", "completed", "failed"

    # Metadata
    paid_at = Column(DateTime, default=datetime.utcnow, index=True)
    paid_by_user_id = Column(BigInteger, nullable=True)  # Who authorized the payment


class PoolContributor(Base):
    """
    Track active contributors to a server's pool
    Shows who has contributed and their statistics
    """
    __tablename__ = "pool_contributors"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    guild_id = Column(BigInteger, nullable=False, index=True)
    user_id = Column(BigInteger, nullable=False)

    # Contribution Stats
    total_contributed = Column(Float, default=0.0)  # Lifetime contributions
    contribution_count = Column(Integer, default=0)  # Number of contributions
    first_contribution_at = Column(DateTime, nullable=True)
    last_contribution_at = Column(DateTime, nullable=True)

    # Recurring Contributions
    recurring_enabled = Column(Boolean, default=False)  # Auto-contribute monthly
    recurring_amount = Column(Float, nullable=True)  # Amount to auto-contribute
    recurring_day = Column(Integer, default=1)  # Day of month (1-28)
    next_recurring_date = Column(DateTime, nullable=True)

    # Contributor Preferences
    public_contributor = Column(Boolean, default=True)  # Show in contributor list
    contributor_tier = Column(String(50), nullable=True)  # "bronze", "silver", "gold", "platinum"
    contributor_role_id = Column(BigInteger, nullable=True)  # Optional Discord role for contributors

    # Notifications
    notify_low_balance = Column(Boolean, default=True)  # Notify when pool is low
    notify_payment_success = Column(Boolean, default=True)  # Notify when bill is paid

    # Status
    is_active = Column(Boolean, default=True)  # Currently contributing

    __table_args__ = (
        Index('idx_contributors_guild_user', 'guild_id', 'user_id'),
    )


class PoolTransaction(Base):
    """
    Complete transaction history for the pool
    Combines contributions and payments for audit trail
    """
    __tablename__ = "pool_transactions"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    guild_id = Column(BigInteger, nullable=False, index=True)

    # Transaction Type
    transaction_type = Column(String(50), nullable=False, index=True)  # "contribution", "payment", "refund"

    # Amount
    amount = Column(Float, nullable=False)  # Positive for contributions, negative for payments
    balance_before = Column(Float, nullable=False)  # Pool balance before transaction
    balance_after = Column(Float, nullable=False)  # Pool balance after transaction

    # Context
    related_user_id = Column(BigInteger, nullable=True)  # User who triggered transaction
    related_contribution_id = Column(BigInteger, nullable=True)  # Link to PoolContribution
    related_payment_id = Column(BigInteger, nullable=True)  # Link to PoolPayment

    # Description
    description = Column(Text, nullable=False)

    # Metadata
    transaction_at = Column(DateTime, default=datetime.utcnow, index=True)

    __table_args__ = (
        Index('idx_transactions_guild_type', 'guild_id', 'transaction_type'),
        Index('idx_transactions_guild_date', 'guild_id', 'transaction_at'),
    )


class PoolNotification(Base):
    """
    Notifications sent to pool contributors and admins
    Tracks low balance alerts, payment confirmations, etc.
    """
    __tablename__ = "pool_notifications"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    guild_id = Column(BigInteger, nullable=False, index=True)

    # Notification Details
    notification_type = Column(String(50), nullable=False)  # "low_balance", "payment_success", "contribution_thanks"
    recipient_user_id = Column(BigInteger, nullable=True)  # Specific user, or null for all contributors

    # Message
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)

    # Status
    sent = Column(Boolean, default=False)
    sent_at = Column(DateTime, nullable=True)
    delivery_method = Column(String(50), default="discord_dm")  # "discord_dm", "email", "both"

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
