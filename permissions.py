import discord
from discord import app_commands
from typing import Optional
from sqlalchemy import select
from database.db_manager import DatabaseManager

# Special user ID with full permissions
DEVELOPER_ID = 413644682158014466

class PermissionLevel:
    """Permission level constants"""
    PLAYER = 0
    LEVEL_1 = 1
    LEVEL_2 = 2
    LEVEL_3 = 3
    LEVEL_4 = 4
    LEVEL_5 = 5  # Server owner / Developer

class PermissionManager:
    """Manages role-based permissions for the bot"""
    
    @staticmethod
    async def get_guild_permissions(guild_id: int):
        """Get all permission settings for a guild"""
        from database.models import GuildPermissions
        
        async with DatabaseManager.get_session() as session:
            result = await session.execute(
                select(GuildPermissions).where(GuildPermissions.guild_id == guild_id)
            )
            return result.scalars().all()
    
    @staticmethod
    async def set_role_permission(guild_id: int, role_id: int, level: int):
        """Set permission level for a role"""
        from database.models import GuildPermissions
        
        async with DatabaseManager.get_session() as session:
            # Check if permission already exists
            result = await session.execute(
                select(GuildPermissions)
                .where(GuildPermissions.guild_id == guild_id)
                .where(GuildPermissions.role_id == role_id)
            )
            perm = result.scalar_one_or_none()
            
            if perm:
                perm.permission_level = level
            else:
                perm = GuildPermissions(
                    guild_id=guild_id,
                    role_id=role_id,
                    permission_level=level
                )
                session.add(perm)
            
            await session.commit()
    
    @staticmethod
    async def remove_role_permission(guild_id: int, role_id: int):
        """Remove permission for a role"""
        from database.models import GuildPermissions
        
        async with DatabaseManager.get_session() as session:
            result = await session.execute(
                select(GuildPermissions)
                .where(GuildPermissions.guild_id == guild_id)
                .where(GuildPermissions.role_id == role_id)
            )
            perm = result.scalar_one_or_none()
            
            if perm:
                await session.delete(perm)
                await session.commit()
                return True
            return False
    
    @staticmethod
    async def get_user_permission_level(interaction: discord.Interaction) -> int:
        """Get the highest permission level for a user"""
        # Developer has max permissions
        if interaction.user.id == DEVELOPER_ID:
            return PermissionLevel.LEVEL_5
        
        # Server owner has level 5
        if interaction.guild and interaction.guild.owner_id == interaction.user.id:
            return PermissionLevel.LEVEL_5
        
        # Check role permissions
        if interaction.guild:
            permissions = await PermissionManager.get_guild_permissions(interaction.guild.id)
            
            max_level = PermissionLevel.PLAYER
            for perm in permissions:
                role = interaction.guild.get_role(perm.role_id)
                if role and role in interaction.user.roles:
                    max_level = max(max_level, perm.permission_level)
            
            return max_level
        
        return PermissionLevel.PLAYER

def require_permission(level: int):
    """Decorator to require a minimum permission level"""
    async def predicate(interaction: discord.Interaction) -> bool:
        user_level = await PermissionManager.get_user_permission_level(interaction)
        return user_level >= level
    return app_commands.check(predicate)

async def check_permission(interaction: discord.Interaction, required_level: int) -> bool:
    """Check if user has required permission level"""
    user_level = await PermissionManager.get_user_permission_level(interaction)
    return user_level >= required_level