"""
Profile Template System models - Template-based character profile creation

This replaces the old ProfileSection system with a template-based approach where
admins type formatted templates in channel using placeholders and Discord markdown.
"""
from sqlalchemy import BigInteger, Boolean, Column, Float, ForeignKey, Integer, String, DateTime, Text, UniqueConstraint, Index, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from database.base import Base


# ============================================================================
# PROFILE TEMPLATE SYSTEM
# ============================================================================

class ProfileTemplate(Base):
    """
    Profile template with 3 slots per guild
    Admins create templates using placeholders like {name}, {age}, {str:value}, {answer 1}
    """
    __tablename__ = "profile_templates"

    id = Column(Integer, primary_key=True, autoincrement=True)
    guild_id = Column(BigInteger, nullable=False, index=True)
    slot_number = Column(Integer, nullable=False)  # 1, 2, or 3
    template_name = Column(String(100))

    # Raw template content with placeholders and [page]/[blank] tags
    raw_template = Column(Text, nullable=False)

    # Stat mappings: {stat_key: stat_def_id} for validated stat references
    stat_mappings = Column(JSON, default={})

    # Template status
    is_active = Column(Boolean, default=False)  # Which template players use
    is_published_to_marketplace = Column(Boolean, default=False)

    # Metadata
    created_by = Column(BigInteger)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    questions = relationship("ProfileTemplateQuestion", back_populates="template", cascade="all, delete-orphan")
    character_profiles = relationship("CharacterProfile", back_populates="template")

    __table_args__ = (
        UniqueConstraint('guild_id', 'slot_number', name='uq_guild_slot'),
    )

    def __repr__(self):
        return f"<ProfileTemplate(id={self.id}, guild={self.guild_id}, slot={self.slot_number}, active={self.is_active})>"


class ProfileTemplateQuestion(Base):
    """
    Questions defined for {answer N} placeholders in templates
    Each question is defined separately after template submission
    """
    __tablename__ = "profile_template_questions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    template_id = Column(Integer, ForeignKey("profile_templates.id", ondelete="CASCADE"), nullable=False)

    # Question configuration
    question_key = Column(String(50), nullable=False)  # "answer 1", "answer 2", etc.
    question_text = Column(Text, nullable=False)  # "What is your character's favorite color?"
    field_type = Column(String(20), default='text')  # text, select, button
    options = Column(JSON)  # For select/button types: ["Option 1", "Option 2", ...]
    required = Column(Boolean, default=True)
    display_order = Column(Integer)

    # Relationships
    template = relationship("ProfileTemplate", back_populates="questions")

    __table_args__ = (
        UniqueConstraint('template_id', 'question_key', name='uq_template_question_key'),
        Index('idx_template_questions', 'template_id', 'display_order'),
    )

    def __repr__(self):
        return f"<ProfileTemplateQuestion(id={self.id}, key={self.question_key}, type={self.field_type})>"


class CharacterProfile(Base):
    """
    Player-created character profiles using active template
    Stores both raw field values and rendered page content
    """
    __tablename__ = "character_profiles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    character_id = Column(Integer, ForeignKey("characters.id", ondelete="CASCADE"), nullable=False, index=True)
    template_id = Column(Integer, ForeignKey("profile_templates.id"), nullable=True)

    # Field values: All placeholder values
    # {
    #   "name": "John Doe",
    #   "age": "25",
    #   "answer 1": "Blue",
    #   "answer 2": "I am a brave warrior...",
    #   "str:value": "150"  # Cached stat values
    # }
    field_values = Column(JSON, default={})

    # Rendered pages: Pre-rendered page content for quick display
    # [
    #   {"content": "**Name:** John Doe\n**Age:** 25...", "is_blank": false},
    #   {"content": "**Backstory**\nI am a brave...", "is_blank": false},
    #   {"content": "", "is_blank": true}
    # ]
    rendered_pages = Column(JSON, default=[])

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    template = relationship("ProfileTemplate", back_populates="character_profiles")
    privacy_settings = relationship("CharacterProfilePrivacy", back_populates="profile", uselist=False, cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint('character_id', name='uq_character_profile'),
        Index('idx_character_template', 'character_id', 'template_id'),
    )

    def __repr__(self):
        return f"<CharacterProfile(id={self.id}, character_id={self.character_id}, template_id={self.template_id})>"
