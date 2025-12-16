# RPG Shared Database Models

Shared database models and utilities for the RP.env bot system.

## Purpose

This repository contains SQLAlchemy database models and related utilities that are shared between:
- **RPG-BOT** (Player-facing bot)
- **RPG-BOT-ADMIN** (Administration bot)

## Structure

- `models_*.py` - SQLAlchemy ORM models for different systems
- `db_manager.py` - Database connection management
- `base.py` - SQLAlchemy Base class
- `migrations/` - Database migration scripts
- `auto_migrations.py` - Automatic migration detection
- `permissions.py` - Permission level definitions

## Usage as Git Submodule

Both bot repositories include this as a git submodule at `/database/`.

### Updating Submodule in Bot Repos

```bash
# Pull latest changes
git submodule update --remote database

# Commit the submodule update
git add database
git commit -m "Update shared database models"
```

### Making Changes to Database Models

1. Make changes directly in this repository
2. Commit and push changes here
3. Update submodule in both bot repos
4. Deploy both bots to apply changes

## Important Notes

- Both bots **must** use the same database schema
- Any model changes must be tested in both bots
- Database migrations should be run after model updates
- Keep this repo in sync between both bot deployments

## Version

Synced with:
- Admin Bot: v1.7.106-beta
- Player Bot: Latest
