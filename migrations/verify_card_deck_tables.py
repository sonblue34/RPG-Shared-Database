"""
Verify and create card_decks and deck_cards tables if they don't exist
"""
import asyncio
from sqlalchemy import text
from database.db_manager import DatabaseManager

async def verify_tables():
    """Verify card deck tables exist"""
    await DatabaseManager.initialize()
    async with DatabaseManager.get_session() as session:
        try:
            # Check if card_decks table exists
            result = await session.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='card_decks'"))
            card_decks_exists = result.fetchone() is not None

            # Check if deck_cards table exists
            result = await session.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='deck_cards'"))
            deck_cards_exists = result.fetchone() is not None

            print(f"card_decks table exists: {card_decks_exists}")
            print(f"deck_cards table exists: {deck_cards_exists}")

            if not card_decks_exists or not deck_cards_exists:
                print("\nCreating missing tables...")
                from database.models import Base

                # Create all tables (will skip existing ones)
                async with DatabaseManager.engine.begin() as conn:
                    await conn.run_sync(Base.metadata.create_all)

                print("Tables created successfully!")
            else:
                print("\nAll card deck tables exist!")

        except Exception as e:
            print(f"Error verifying tables: {e}")
            await session.rollback()

if __name__ == "__main__":
    print("Verifying card deck tables...")
    asyncio.run(verify_tables())
