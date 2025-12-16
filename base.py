"""
Shared declarative base for all database models.

All model files should import Base from this module to ensure
foreign key relationships can be properly resolved across models.
"""
from sqlalchemy.ext.declarative import declarative_base

# Single shared Base instance for all models
Base = declarative_base()
