"""
Verification system models for server security and user verification
"""
from sqlalchemy import BigInteger, Boolean, Column, DateTime, String, Text, JSON
from datetime import datetime
from database.base import Base


class VerificationSystem(Base):
    """Verification system configuration per guild"""
    __tablename__ = "verification_system"

    guild_id = Column(BigInteger, primary_key=True)

    # System status
    is_enabled = Column(Boolean, default=False, index=True)
    setup_completed = Column(Boolean, default=False)
    permissions_applied = Column(Boolean, default=False)  # Track if server permissions have been modified

    # Setup metadata
    setup_by = Column(BigInteger, nullable=True)
    setup_at = Column(DateTime, default=datetime.utcnow)

    # Roles and channels
    verified_role_id = Column(BigInteger, nullable=True)
    verification_channel_id = Column(BigInteger, nullable=True)
    rules_channel_id = Column(BigInteger, nullable=True)  # Channel visible to all users (verified or not)
    verification_message = Column(JSON, nullable=True)  # Custom verification embed {"title": str, "description": str, "color": str}
    verification_message_id = Column(BigInteger, nullable=True)  # ID of posted verification message

    # Verification method: "password" or "questions"
    verification_method = Column(String(20), default="password")

    # Password verification
    verification_password = Column(String(100), nullable=True)

    # Security questions (JSON array of {"question": str, "answer": str, "allow_image": bool, "required": bool})
    security_questions = Column(JSON, nullable=True)
    questions_review_mode = Column(String(20), default="auto")  # "auto" or "manual" - auto checks answers, manual requires admin approval

    # Channel configuration (JSON arrays of channel IDs)
    roleplay_channels = Column(JSON, default='[]')
    information_channels = Column(JSON, default='[]')
    ooc_channels = Column(JSON, default='[]')
    admin_channels = Column(JSON, default='[]')
    test_channels = Column(JSON, default='[]')  # Channels exempt from verification requirements

    # RP Channel approved character settings
    rp_channels_require_approved = Column(Boolean, default=False)  # Lock RP channels to approved characters only
    approved_character_role_id = Column(BigInteger, nullable=True)  # Role ID for approved characters

    # Statistics
    total_verified_users = Column(BigInteger, default=0)
    last_verification = Column(DateTime, nullable=True)

    # Updated timestamp
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class UserVerification(Base):
    """Track verification status for users per guild"""
    __tablename__ = "user_verification"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    guild_id = Column(BigInteger, index=True, nullable=False)
    user_id = Column(BigInteger, index=True, nullable=False)

    # Verification status
    is_verified = Column(Boolean, default=False, index=True)
    verified_at = Column(DateTime, nullable=True)
    verification_method_used = Column(String(20), nullable=True)  # "password" or "questions"

    # Attempts tracking
    verification_attempts = Column(BigInteger, default=0)
    last_attempt = Column(DateTime, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class PendingVerification(Base):
    """Track pending verifications awaiting manual review"""
    __tablename__ = "pending_verifications"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    guild_id = Column(BigInteger, index=True, nullable=False)
    user_id = Column(BigInteger, index=True, nullable=False)

    # Verification data
    answers = Column(JSON, nullable=False)  # Array of {"question": str, "answer": str, "image_url": str or None}
    thread_id = Column(BigInteger, nullable=True)  # ID of the private thread used for questions

    # Status
    status = Column(String(20), default="pending", index=True)  # "pending", "approved", "denied"
    reviewed_by = Column(BigInteger, nullable=True)  # Admin who reviewed
    reviewed_at = Column(DateTime, nullable=True)
    review_note = Column(Text, nullable=True)  # Optional note from reviewer

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
