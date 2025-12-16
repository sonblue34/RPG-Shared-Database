"""
Data Usage Tracking Models

Tracks database operations, API calls, storage, and compute resources
for billing purposes when hosting on private server.
"""
from sqlalchemy import BigInteger, Column, Integer, String, DateTime, Float, Index, Text, Boolean
from sqlalchemy.sql import func
from datetime import datetime
from database.base import Base


class ServerUsageMetrics(Base):
    """
    Real-time usage metrics for each server
    Updated continuously as operations occur
    """
    __tablename__ = "server_usage_metrics"

    guild_id = Column(BigInteger, primary_key=True)

    # Database Operations (counts)
    db_reads_count = Column(BigInteger, default=0)  # SELECT queries
    db_writes_count = Column(BigInteger, default=0)  # INSERT/UPDATE/DELETE queries
    db_rows_read = Column(BigInteger, default=0)  # Total rows returned from queries
    db_rows_written = Column(BigInteger, default=0)  # Total rows modified

    # Storage Usage (bytes)
    storage_characters = Column(BigInteger, default=0)  # Character data size
    storage_items = Column(BigInteger, default=0)  # Item data size
    storage_stats = Column(BigInteger, default=0)  # Stats data size
    storage_story = Column(BigInteger, default=0)  # Story chapters/info pages size
    storage_images = Column(BigInteger, default=0)  # Uploaded images size
    storage_total = Column(BigInteger, default=0)  # Total storage used

    # API/Command Calls (counts)
    commands_executed = Column(BigInteger, default=0)  # Total commands run
    dashboard_views = Column(BigInteger, default=0)  # Dashboard interactions
    api_calls_external = Column(BigInteger, default=0)  # External API calls (if any)

    # Compute Resources (milliseconds)
    compute_time_commands = Column(BigInteger, default=0)  # Time spent processing commands
    compute_time_background = Column(BigInteger, default=0)  # Background tasks

    # Current Period Tracking
    current_period_start = Column(DateTime, default=datetime.utcnow)
    current_period_end = Column(DateTime)  # End of billing period

    # Metadata
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index('idx_usage_metrics_period', 'current_period_start', 'current_period_end'),
    )


class UsageEventLog(Base):
    """
    Detailed log of individual usage events
    Allows for audit trails and detailed analysis
    """
    __tablename__ = "usage_event_log"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    guild_id = Column(BigInteger, nullable=False, index=True)

    # Event Classification
    event_type = Column(String(50), nullable=False, index=True)  # "db_read", "db_write", "command", "storage"
    event_category = Column(String(50), nullable=False)  # "character", "item", "stats", "story", etc.
    event_action = Column(String(100), nullable=False)  # Specific action taken

    # Usage Metrics for This Event
    db_rows_affected = Column(Integer, default=0)  # Rows read/written
    storage_bytes = Column(BigInteger, default=0)  # Storage change
    compute_ms = Column(Integer, default=0)  # Processing time

    # Context
    user_id = Column(BigInteger, nullable=True)  # User who triggered event
    command_name = Column(String(100), nullable=True)  # Command executed
    character_id = Column(BigInteger, nullable=True)  # Related character

    # Metadata
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    additional_data = Column(Text, nullable=True)  # JSON string for extra info

    __table_args__ = (
        Index('idx_event_log_guild_time', 'guild_id', 'timestamp'),
        Index('idx_event_log_type_time', 'event_type', 'timestamp'),
    )


class UsageBillingPeriod(Base):
    """
    Historical usage data for completed billing periods
    Archived after each billing cycle for invoicing
    """
    __tablename__ = "usage_billing_periods"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    guild_id = Column(BigInteger, nullable=False, index=True)

    # Period Info
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)
    period_days = Column(Integer, nullable=False)  # Length of billing period

    # Usage Totals (copied from ServerUsageMetrics at period end)
    total_db_reads = Column(BigInteger, default=0)
    total_db_writes = Column(BigInteger, default=0)
    total_db_rows_read = Column(BigInteger, default=0)
    total_db_rows_written = Column(BigInteger, default=0)

    total_storage_bytes = Column(BigInteger, default=0)
    avg_storage_bytes = Column(BigInteger, default=0)  # Average storage during period
    peak_storage_bytes = Column(BigInteger, default=0)  # Peak storage usage

    total_commands = Column(BigInteger, default=0)
    total_dashboard_views = Column(BigInteger, default=0)
    total_api_calls = Column(BigInteger, default=0)

    total_compute_ms = Column(BigInteger, default=0)

    # Billing Info
    billing_tier = Column(String(50), nullable=True)  # "free", "basic", "premium", "enterprise"
    base_cost = Column(Float, default=0.0)  # Base subscription cost
    usage_cost = Column(Float, default=0.0)  # Variable usage cost
    total_cost = Column(Float, default=0.0)  # Total for this period

    invoice_generated = Column(Boolean, default=False)
    invoice_id = Column(String(100), nullable=True)  # External invoice system ID
    paid = Column(Boolean, default=False)
    paid_at = Column(DateTime, nullable=True)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index('idx_billing_period_guild_dates', 'guild_id', 'period_start', 'period_end'),
    )


class UsagePricingTier(Base):
    """
    Pricing configuration for storage-based billing
    IMPORTANT: We ONLY charge for storage (characters, items, images, stats, story).
    Other metrics (reads, writes, commands) are tracked for analytics but NOT billed.
    """
    __tablename__ = "usage_pricing_tiers"

    id = Column(BigInteger, primary_key=True, autoincrement=True)

    # Tier Info
    tier_name = Column(String(50), nullable=False, unique=True)  # "free", "basic", "premium", "enterprise"
    tier_display_name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)

    # Base Pricing (per month)
    base_price_monthly = Column(Float, default=0.0)

    # STORAGE - THE ONLY BILLABLE METRIC
    included_storage_gb = Column(Float, default=0.0)  # Included storage in GB
    price_per_gb_storage = Column(Float, default=0.0)  # Price per GB per month (overage)

    # Analytics-only fields (kept for tracking but NOT used for billing)
    included_db_reads = Column(BigInteger, default=0)  # Analytics only
    included_db_writes = Column(BigInteger, default=0)  # Analytics only
    included_commands = Column(BigInteger, default=0)  # Analytics only
    included_compute_hours = Column(Float, default=0.0)  # Analytics only
    price_per_1k_reads = Column(Float, default=0.0)  # NOT USED - analytics only
    price_per_1k_writes = Column(Float, default=0.0)  # NOT USED - analytics only
    price_per_1k_commands = Column(Float, default=0.0)  # NOT USED - analytics only
    price_per_compute_hour = Column(Float, default=0.0)  # NOT USED - analytics only

    # Tier Status
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ServerBillingConfig(Base):
    """
    Billing configuration for each server
    Links servers to pricing tiers and tracks billing status
    """
    __tablename__ = "server_billing_config"

    guild_id = Column(BigInteger, primary_key=True)

    # Tier Assignment
    pricing_tier = Column(String(50), nullable=False, default="free")  # References UsagePricingTier.tier_name

    # Billing Contact
    billing_user_id = Column(BigInteger, nullable=True)  # Discord user responsible for billing
    billing_email = Column(String(255), nullable=True)

    # Billing Cycle
    billing_day_of_month = Column(Integer, default=1)  # Day of month to bill (1-28)
    next_billing_date = Column(DateTime, nullable=True)

    # Payment Info
    payment_method = Column(String(50), nullable=True)  # "stripe", "paypal", "manual", etc.
    payment_customer_id = Column(String(255), nullable=True)  # External payment system customer ID

    # Status
    billing_enabled = Column(Boolean, default=False)
    payment_status = Column(String(50), default="none")  # "none", "active", "overdue", "suspended"
    last_payment_date = Column(DateTime, nullable=True)
    last_payment_amount = Column(Float, nullable=True)

    # Limits & Warnings
    usage_warning_threshold = Column(Float, default=0.8)  # Warn at 80% of included usage
    hard_limit_enabled = Column(Boolean, default=False)  # Stop service if limits exceeded

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class UsageSnapshot(Base):
    """
    Daily snapshots of usage metrics
    Used for generating reports and tracking trends
    """
    __tablename__ = "usage_snapshots"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    guild_id = Column(BigInteger, nullable=False, index=True)

    # Snapshot Date
    snapshot_date = Column(DateTime, nullable=False, index=True)  # Start of day

    # 24-Hour Usage Totals
    db_reads = Column(BigInteger, default=0)
    db_writes = Column(BigInteger, default=0)
    storage_bytes = Column(BigInteger, default=0)
    commands_executed = Column(BigInteger, default=0)
    compute_ms = Column(BigInteger, default=0)

    # Active Users
    active_users = Column(Integer, default=0)  # Unique users who used commands
    active_characters = Column(Integer, default=0)  # Unique characters used

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index('idx_snapshot_guild_date', 'guild_id', 'snapshot_date'),
    )
