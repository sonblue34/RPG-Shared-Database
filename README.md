# RPG Shared Database

This is the shared database package used by both:
- RPG-BOT (Main/Player Bot)
- RPG-BOT-ADMIN (Admin Bot)

## Structure

\`\`\`
RPG-Shared-Database/
├── __init__.py
├── setup.py
├── base.py                    # SQLAlchemy Base
├── db_manager.py              # Database manager
├── auto_schema_sync.py        # Schema synchronization
├── auto_migrations.py         # Auto migration system
├── permissions.py             # Permission helpers
├── models.py                  # Main models import
├── models_core.py             # Core models (User, Character, etc.)
├── models_systems.py          # Game systems (Race, Class, Stats, etc.)
├── models_server_config.py    # Server configuration
├── models_verification.py     # Verification system
├── models_attributes.py       # Attribute system
├── models_equipment.py        # Equipment system
├── models_gacha.py            # Gacha system
├── models_economy.py          # Economy system
├── models_lifetime_tiers.py   # Lifetime tiers
├── models_payment_pool.py     # Payment pools
├── models_usage_tracking.py   # Usage tracking
├── models_roleplay_info.py    # Roleplay information
├── reaction_role_models.py    # Reaction roles
├── default_income_brackets.py # Default income data
└── migrations/                # Database migrations
    ├── __init__.py
    └── *.py
\`\`\`

## Usage

### Installation

\`\`\`bash
# In development mode (editable)
pip install -e /path/to/RPG-Shared-Database
\`\`\`

### Importing in Bots

\`\`\`python
# Import database manager
from database.db_manager import DatabaseManager

# Import models
from database.models import User, Character, Race, Class

# Import base
from database.base import Base
\`\`\`

## Development

When adding new models or migrations:

1. Edit files in this directory
2. Both bots will automatically use the updated models
3. Commit changes to this repository
4. Both bot repositories reference this as a shared dependency

## Docker Setup

Both bots mount this directory as a volume:

\`\`\`yaml
volumes:
  - ../RPG-Shared-Database:/app/database
\`\`\`

## Version

- **Version**: 1.0.0
- **Last Updated**: 2026-01-01
- **Compatible with**: Bot v1.11.6-beta+
