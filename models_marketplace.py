"""
Template Marketplace models - Community sharing system for profile templates

Allows users to publish templates to a marketplace where others can request
permission to use them. No monetary sales, purely sharing-based.
"""
from sqlalchemy import BigInteger, Boolean, Column, Float, ForeignKey, Integer, String, DateTime, Text, UniqueConstraint, Index, JSON, Numeric
from sqlalchemy.orm import relationship
from datetime import datetime
from database.base import Base


# ============================================================================
# MARKETPLACE SYSTEM
# ============================================================================

class MarketplaceTemplate(Base):
    """
    Published templates in the community marketplace
    Snapshots template at publish time to prevent retroactive changes
    """
    __tablename__ = "marketplace_templates"

    id = Column(Integer, primary_key=True, autoincrement=True)
    original_template_id = Column(Integer, ForeignKey("profile_templates.id", ondelete="CASCADE"), nullable=False)

    # Creator information (cached for display)
    creator_id = Column(BigInteger, nullable=False, index=True)
    creator_username = Column(String(100))

    # Template metadata
    template_name = Column(String(100), nullable=False)
    description = Column(Text)
    category = Column(String(50), index=True)  # combat, roleplay, simple, complex, etc.
    tags = Column(JSON, default=[])  # ["fantasy", "stats-heavy", "multi-page"]

    # Snapshot of template at publish time (prevents retroactive changes)
    raw_template_snapshot = Column(Text, nullable=False)
    questions_snapshot = Column(JSON, default=[])  # Snapshot of all questions

    # Metadata
    published_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    download_count = Column(Integer, default=0)

    # Future features
    rating_avg = Column(Numeric(3, 2), default=0)  # Average rating 0.00-5.00
    rating_count = Column(Integer, default=0)
    is_featured = Column(Boolean, default=False, index=True)

    # Relationships
    permissions = relationship("MarketplacePermission", back_populates="template", cascade="all, delete-orphan")

    __table_args__ = (
        Index('idx_marketplace_creator', 'creator_id'),
        Index('idx_marketplace_category', 'category', 'is_featured'),
        Index('idx_marketplace_published', 'published_at'),
    )

    def __repr__(self):
        return f"<MarketplaceTemplate(id={self.id}, name={self.template_name}, creator={self.creator_id})>"


class MarketplacePermission(Base):
    """
    Permission requests and approvals for marketplace templates
    Users request permission, creator approves/denies
    """
    __tablename__ = "marketplace_permissions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    marketplace_template_id = Column(Integer, ForeignKey("marketplace_templates.id", ondelete="CASCADE"), nullable=False, index=True)

    # Requester information
    requester_id = Column(BigInteger, nullable=False, index=True)
    requester_username = Column(String(100))
    requester_guild_id = Column(BigInteger, nullable=False)  # Which guild wants to use it

    # Permission status
    status = Column(String(20), default='pending', nullable=False, index=True)  # pending, approved, denied
    requested_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    responded_at = Column(DateTime)
    response_note = Column(Text)  # Optional message from creator

    # Relationships
    template = relationship("MarketplaceTemplate", back_populates="permissions")

    __table_args__ = (
        UniqueConstraint('marketplace_template_id', 'requester_id', 'requester_guild_id', name='uq_marketplace_permission'),
        Index('idx_permission_status', 'marketplace_template_id', 'status'),
        Index('idx_permission_requester', 'requester_id', 'status'),
    )

    def __repr__(self):
        return f"<MarketplacePermission(id={self.id}, template={self.marketplace_template_id}, requester={self.requester_id}, status={self.status})>"
