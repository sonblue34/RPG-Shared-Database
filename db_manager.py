from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import select
from database.base import Base
from database.models import User, Character, Basic, Clan, Inventory
from database.models_server_config import ServerConfig, RolePermissionLevel
from config import DATABASE_URL, MAX_CHARACTERS_PER_USER
from typing import Optional

class DatabaseManager:
    engine = None
    session_maker = None
    
    @classmethod
    async def initialize(cls, database_url=None):
        """Initialize database engine and create tables"""
        url = database_url or DATABASE_URL
        cls.engine = create_async_engine(url, echo=False)
        cls.session_maker = async_sessionmaker(
            cls.engine,
            expire_on_commit=False,
            class_=AsyncSession
        )

        async with cls.engine.begin() as conn:
            # Create all tables from single shared Base instance
            await conn.run_sync(Base.metadata.create_all)
    
    @classmethod
    def get_session(cls):
        """Get a new database session"""
        return cls.session_maker()
    
    @classmethod
    async def get_or_create_user(cls, discord_id: int) -> User:
        """Get or create a user"""
        async with cls.get_session() as session:
            result = await session.execute(
                select(User).where(User.discord_id == discord_id)
            )
            user = result.scalar_one_or_none()
            
            if not user:
                user = User(discord_id=discord_id, active_character_slot=1)
                session.add(user)
                await session.commit()
                await session.refresh(user)
            
            return user
    
    @classmethod
    async def create_character(cls, discord_id: int, character_name: str, character_age: int, guild_id: int, slot: int = None) -> Optional[Character]:
        """Create a new character for a user in a specific guild"""
        async with cls.get_session() as session:
            # Get user
            user = await cls.get_or_create_user(discord_id)

            # Check character count for this guild
            result = await session.execute(
                select(Character).where(
                    Character.discord_id == discord_id,
                    Character.guild_id == guild_id
                )
            )
            existing_chars = result.scalars().all()

            if len(existing_chars) >= MAX_CHARACTERS_PER_USER:
                return None

            # Determine slot
            if slot is None:
                used_slots = [char.character_slot for char in existing_chars]
                slot = next(i for i in range(1, MAX_CHARACTERS_PER_USER + 1) if i not in used_slots)

            # Create character
            character = Character(discord_id=discord_id, guild_id=guild_id, character_slot=slot)
            session.add(character)
            await session.flush()
            
            # Create all related tables
            basic = Basic(character_id=character.id, character_name=character_name, character_age=character_age)
            clan = Clan(character_id=character.id)

            session.add_all([basic, clan])
            
            await session.commit()
            await session.refresh(character)
            
            return character
    
    @classmethod
    async def get_active_character(cls, discord_id: int) -> Optional[Character]:
        """Get user's active character with all relationships"""
        async with cls.get_session() as session:
            user_result = await session.execute(
                select(User).where(User.discord_id == discord_id)
            )
            user = user_result.scalar_one_or_none()
            
            if not user:
                return None
            
            result = await session.execute(
                select(Character)
                .where(Character.discord_id == discord_id)
                .where(Character.character_slot == user.active_character_slot)
            )
            character = result.scalar_one_or_none()
            
            if character:
                # Eager load all relationships
                await session.refresh(character, ['basic', 'clan'])
            
            return character
    
    @classmethod
    async def get_all_user_characters(cls, discord_id: int):
        """Get all characters for a user"""
        async with cls.get_session() as session:
            result = await session.execute(
                select(Character).where(Character.discord_id == discord_id)
            )
            characters = result.scalars().all()
            
            for char in characters:
                await session.refresh(char, ['basic'])
            
            return characters
    
    @classmethod
    async def switch_character(cls, discord_id: int, slot: int) -> bool:
        """Switch active character"""
        async with cls.get_session() as session:
            user_result = await session.execute(
                select(User).where(User.discord_id == discord_id)
            )
            user = user_result.scalar_one_or_none()
            
            if not user:
                return False
            
            # Check if character exists in that slot
            char_result = await session.execute(
                select(Character)
                .where(Character.discord_id == discord_id)
                .where(Character.character_slot == slot)
            )
            character = char_result.scalar_one_or_none()
            
            if not character:
                return False
            
            user.active_character_slot = slot
            await session.commit()
            return True
    
    @classmethod
    async def delete_character(cls, discord_id: int, slot: int) -> bool:
        """Delete a character"""
        async with cls.get_session() as session:
            result = await session.execute(
                select(Character)
                .where(Character.discord_id == discord_id)
                .where(Character.character_slot == slot)
            )
            character = result.scalar_one_or_none()
            
            if not character:
                return False
            
            await session.delete(character)
            await session.commit()
            return True
    
    @classmethod
    async def add_exp(cls, character_id: int, exp: int):
        """Add EXP to a character"""
        async with cls.get_session() as session:
            result = await session.execute(
                select(Basic).where(Basic.character_id == character_id)
            )
            basic = result.scalar_one_or_none()
            
            if basic:
                basic.unspent_exp += exp
                basic.total_exp += exp
                await session.commit()
    
    @classmethod
    async def add_item(cls, character_id: int, item_name: str, item_rank: str, item_exp: int):
        """Add an item to character inventory"""
        async with cls.get_session() as session:
            item = Inventory(
                character_id=character_id,
                item_name=item_name,
                item_rank=item_rank,
                item_exp=item_exp
            )
            session.add(item)
            await session.commit()
    
    @classmethod
    async def consume_item(cls, item_id: int) -> Optional[int]:
        """Consume an item and return its EXP value"""
        async with cls.get_session() as session:
            result = await session.execute(
                select(Inventory).where(Inventory.id == item_id)
            )
            item = result.scalar_one_or_none()
            
            if not item or item.is_consumed:
                return None
            
            exp_value = item.item_exp
            item.is_consumed = True
            await session.commit()
            return exp_value
    
    @classmethod
    async def get_inventory(cls, character_id: int):
        """Get character inventory"""
        async with cls.get_session() as session:
            result = await session.execute(
                select(Inventory)
                .where(Inventory.character_id == character_id)
                .where(Inventory.is_consumed == False)
            )
            return result.scalars().all()