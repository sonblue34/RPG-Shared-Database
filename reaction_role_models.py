"""
Reaction Role Models

These models can be easily copied to a standalone utility bot if needed.
They are self-contained and don't depend on RPG-specific models.
"""

from sqlalchemy import BigInteger, Boolean, Column, Float, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from database.base import Base


class ReactionRolePanel(Base):
    """Reaction role panels - messages with reactions that grant roles"""
    __tablename__ = "reaction_role_panels"

    id = Column(Integer, primary_key=True, autoincrement=True)
    guild_id = Column(BigInteger, nullable=False, index=True)
    channel_id = Column(BigInteger, nullable=False)
    message_id = Column(BigInteger, nullable=False, unique=True, index=True)

    # Panel settings
    panel_name = Column(String, nullable=False)  # Internal name for reference
    mode = Column(String, default="normal")  # normal, permanent, unique, limit, reversed

    # Mode-specific settings
    role_limit = Column(Integer, nullable=True)  # For "limit" mode - max roles user can have from this panel

    # Embed content
    embed_title = Column(String, nullable=False)
    embed_description = Column(String, default="")
    embed_color = Column(Integer, default=5814783)  # Default blue (0x58B9FF in decimal)
    embed_footer = Column(String, default="")
    embed_image_url = Column(String, default="")
    embed_thumbnail_url = Column(String, default="")

    # Metadata
    created_by = Column(BigInteger, nullable=False)  # Discord ID of creator
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    reactions = relationship("ReactionRole", back_populates="panel", cascade="all, delete-orphan", order_by="ReactionRole.display_order")


class ReactionRole(Base):
    """Individual reaction-role mappings within a panel"""
    __tablename__ = "reaction_roles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    panel_id = Column(Integer, ForeignKey("reaction_role_panels.id", ondelete="CASCADE"), nullable=False)

    # Reaction details
    emoji = Column(String, nullable=False)  # Can be unicode emoji or custom emoji ID
    emoji_name = Column(String, default="")  # For custom emojis, store the name too
    is_custom_emoji = Column(Boolean, default=False)

    # Role to grant
    role_id = Column(BigInteger, nullable=False, index=True)
    role_name = Column(String, nullable=False)  # Store name for reference (in case role is deleted)

    # Display
    description = Column(String, default="")  # Description shown in embed
    display_order = Column(Integer, default=0)  # Order in which reactions appear

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    panel = relationship("ReactionRolePanel", back_populates="reactions")


class ReactionRoleLog(Base):
    """Log of reaction role grants/removals for analytics"""
    __tablename__ = "reaction_role_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    guild_id = Column(BigInteger, nullable=False, index=True)
    panel_id = Column(Integer, nullable=True)  # Null if panel was deleted
    user_id = Column(BigInteger, nullable=False, index=True)
    role_id = Column(BigInteger, nullable=False)

    # Action
    action = Column(String, nullable=False)  # "granted", "removed"
    mode = Column(String, default="normal")  # Panel mode at time of action

    # Timestamp
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
