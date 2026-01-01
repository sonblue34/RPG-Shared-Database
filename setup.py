"""
RPG Shared Database Package Setup
Allows both RPG-BOT and RPG-BOT-ADMIN to import shared database models
"""
from setuptools import setup, find_packages

setup(
    name="rpg-shared-database",
    version="1.0.0",
    description="Shared database models for RPG Bot system",
    author="Your Name",
    packages=find_packages(),
    install_requires=[
        "sqlalchemy>=2.0.0",
        "asyncpg>=0.29.0",
        "aiosqlite>=0.19.0",
    ],
    python_requires=">=3.11",
)
