"""
Privacy System models - Player control over profile visibility

Allows players to hide specific pages/fields from other players, with admin
controls over what can/can't be hidden (e.g., names must always be visible).
"""
from sqlalchemy import BigInteger, Boolean, Column, ForeignKey, Integer, String, DateTime, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from database.base import Base


# ============================================================================
# PRIVACY SYSTEM
# ============================================================================

class ProfilePrivacySettings(Base):
    """
    Guild-level privacy configuration - What players can/can't hide
    Admins control privacy rules to prevent abuse
    """
    __tablename__ = "profile_privacy_settings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    guild_id = Column(BigInteger, nullable=False, unique=True, index=True)

    # What players are allowed to hide
    allow_hide_backstory_long = Column(Boolean, default=True)
    allow_hide_backstory_short = Column(Boolean, default=True)
    allow_hide_custom_pages = Column(Boolean, default=True)  # Allow hiding entire pages
    allow_hide_custom_fields = Column(Boolean, default=True)  # Allow hiding {answer N} fields
    allow_hide_stats = Column(Boolean, default=False)  # Usually false to prevent stat hiding abuse

    # Fields that MUST always be visible (JSON array of field keys)
    # Example: ["name", "age"]
    required_visible_fields = Column(JSON, default=[])

    # Pages that MUST always be visible (JSON array of page numbers, 0-indexed)
    # Example: [0] means first page must always be visible
    required_visible_pages = Column(JSON, default=[])

    # Metadata
    updated_by = Column(BigInteger)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<ProfilePrivacySettings(guild_id={self.guild_id})>"


class CharacterProfilePrivacy(Base):
    """
    Player-specific privacy settings for their character profile
    Controls what pages/fields are hidden from other players
    """
    __tablename__ = "character_profile_privacy"

    id = Column(Integer, primary_key=True, autoincrement=True)
    character_profile_id = Column(Integer, ForeignKey("character_profiles.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)

    # Hidden pages (JSON array of page numbers, 0-indexed)
    # Example: [1, 2] means hide pages 2 and 3
    hidden_pages = Column(JSON, default=[])

    # Hidden fields (JSON array of field keys)
    # Example: ["answer 1", "answer 3"]
    hidden_fields = Column(JSON, default=[])

    # Backstory display mode
    backstory_mode = Column(String(20), default='full')  # full, short, hidden

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    profile = relationship("CharacterProfile", back_populates="privacy_settings")

    def __repr__(self):
        return f"<CharacterProfilePrivacy(profile_id={self.character_profile_id}, backstory={self.backstory_mode})>"
