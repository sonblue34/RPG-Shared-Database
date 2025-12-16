"""
Roleplay Info System Models
Allows admins to create categorized information pages with access control
"""
from sqlalchemy import BigInteger, Boolean, Column, String, DateTime, Integer, Text, ForeignKey
from datetime import datetime
from database.base import Base


class RoleplayInfoCategory(Base):
    """Categories for organizing roleplay information"""
    __tablename__ = "roleplay_info_categories"

    id = Column(Integer, primary_key=True, autoincrement=True)
    guild_id = Column(BigInteger, nullable=False, index=True)

    # Category details
    title = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    emoji = Column(String(50), nullable=True)  # Unicode emoji or custom emoji ID

    # Ordering
    order_index = Column(Integer, default=0, index=True)

    # Status
    is_active = Column(Boolean, default=True)

    # Metadata
    created_by = Column(BigInteger, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class RoleplayInfoPage(Base):
    """Individual pages within a category"""
    __tablename__ = "roleplay_info_pages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    category_id = Column(Integer, ForeignKey('roleplay_info_categories.id', ondelete='CASCADE'), nullable=False, index=True)

    # Page details
    page_number = Column(Integer, nullable=False, default=1)
    title = Column(String(200), nullable=True)  # Optional page title
    content = Column(Text, nullable=False)  # Main content (supports markdown)

    # Metadata
    created_by = Column(BigInteger, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class RoleplayInfoAccess(Base):
    """Access control for categories (whitelist/blacklist)"""
    __tablename__ = "roleplay_info_access"

    id = Column(Integer, primary_key=True, autoincrement=True)
    category_id = Column(Integer, ForeignKey('roleplay_info_categories.id', ondelete='CASCADE'), nullable=False, index=True)

    # Access control
    access_type = Column(String(20), nullable=False)  # 'whitelist' or 'blacklist'
    restriction_type = Column(String(20), nullable=False)  # 'role', 'class', 'level', 'power_level', 'title', 'achievement'
    restriction_value = Column(String(200), nullable=False)  # The actual value (role ID, class name, level number, etc.)

    # Comparison operators for numeric restrictions (level, power_level)
    # 'exact', 'min', 'max', 'range'
    comparison_operator = Column(String(10), nullable=True, default='exact')
    comparison_value_max = Column(String(200), nullable=True)  # For range comparisons

    # Metadata
    created_by = Column(BigInteger, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
