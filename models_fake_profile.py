"""
Fake Profile System models - Deceptive profiles for roleplay scenarios

Allows players to create fake profiles that show different information than
their real profile. Requires admin approval and permission-based viewing.
"""
from sqlalchemy import BigInteger, Boolean, Column, ForeignKey, Integer, String, DateTime, Text, UniqueConstraint, Index, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from database.base import Base


# ============================================================================
# FAKE PROFILE SYSTEM
# ============================================================================

class FakeProfileConfig(Base):
    """
    Guild-level configuration for fake profiles
    Admins control if fake profiles are enabled and limits
    """
    __tablename__ = "fake_profile_config"

    id = Column(Integer, primary_key=True, autoincrement=True)
    guild_id = Column(BigInteger, nullable=False, unique=True, index=True)

    # Configuration
    fake_profiles_enabled = Column(Boolean, default=False)
    max_fakes_per_player = Column(Integer, default=5)
    require_approval = Column(Boolean, default=True)

    # Auto-approve roles (JSON array of role IDs that can auto-approve their own fakes)
    # Example: [123456789, 987654321]
    auto_approve_roles = Column(JSON, default=[])

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<FakeProfileConfig(guild_id={self.guild_id}, enabled={self.fake_profiles_enabled}, max={self.max_fakes_per_player})>"


class FakeProfile(Base):
    """
    Fake/deceptive character profiles
    Uses same template as real profile but with different field values
    Requires admin approval before activation
    """
    __tablename__ = "fake_profiles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    character_id = Column(Integer, ForeignKey("characters.id", ondelete="CASCADE"), nullable=False, index=True)
    template_id = Column(Integer, ForeignKey("profile_templates.id"), nullable=True)

    # Fake profile identification
    fake_profile_name = Column(String(100), nullable=False)  # "Undercover Merchant", "Noble Persona", etc.

    # Field values: All placeholder values for the fake profile
    # Same structure as CharacterProfile.field_values
    # {
    #   "name": "Marcus the Trader",  # Fake name
    #   "age": "45",  # Fake age
    #   "answer 1": "Gold",  # Fake answers
    #   "answer 2": "I am a simple merchant..."
    # }
    field_values = Column(JSON, default={})

    # Rendered pages: Pre-rendered fake profile content
    # Same structure as CharacterProfile.rendered_pages
    rendered_pages = Column(JSON, default=[])

    # Approval status
    status = Column(String(20), default='pending', nullable=False, index=True)  # pending, approved, rejected
    reviewed_by = Column(BigInteger)  # Admin who reviewed
    reviewed_at = Column(DateTime)
    review_note = Column(Text)  # Admin's note about why approved/rejected

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    permissions = relationship("FakeProfilePermission", back_populates="fake_profile", cascade="all, delete-orphan")

    __table_args__ = (
        Index('idx_fake_profile_character', 'character_id', 'status'),
    )

    def __repr__(self):
        return f"<FakeProfile(id={self.id}, character={self.character_id}, name={self.fake_profile_name}, status={self.status})>"


class FakeProfilePermission(Base):
    """
    Permission system for fake profiles - Who can see which fake
    Supports: per person, party, guild, role, or everyone
    """
    __tablename__ = "fake_profile_permissions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    fake_profile_id = Column(Integer, ForeignKey("fake_profiles.id", ondelete="CASCADE"), nullable=False, index=True)

    # Permission type and target
    permission_type = Column(String(20), nullable=False, index=True)  # person, party, guild, role, everyone
    target_id = Column(BigInteger)  # user_id, party_id, guild_id, role_id (null for everyone)

    # Metadata
    granted_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    fake_profile = relationship("FakeProfile", back_populates="permissions")

    __table_args__ = (
        UniqueConstraint('fake_profile_id', 'permission_type', 'target_id', name='uq_fake_permission'),
        Index('idx_fake_permission_type', 'permission_type', 'target_id'),
    )

    def __repr__(self):
        return f"<FakeProfilePermission(id={self.id}, fake={self.fake_profile_id}, type={self.permission_type}, target={self.target_id})>"
