"""
Default Income Brackets (Call of Cthulhu-Inspired System)

Tier System:
- Tier 1: Poor - Bare minimum for survival
- Tier 2: Average - Standard living with average accommodations
- Tier 3: Wealthy - First-class living
- Tier 4: Top 10% (The Rich) - Luxury living
- Tier 5: Top 5% (Royalty) - Money ceases to matter

Character Creation:
- Players choose Poor or Average to start
- Players pick 2 lucky numbers (1-10), then roll d10
- If they roll one of their numbers (~20% chance), they start Wealthy
- Rolling a 10 gives Top 10% (1% effective chance after number selection)
- Top 5% (Royalty) is admin-only assignment
"""

from database.db_manager import DatabaseManager
from database.models_economy import IncomeBracket
from sqlalchemy import select, and_


# Income bracket definitions (Call of Cthulhu style)
INCOME_BRACKETS = [
    {
        "bracket_name": "Poor",
        "bracket_level": 1,
        "emoji": "🪙",
        "base_income": 5000,  # 5,000 Jenny
        "bonus_income": 0,
        "cooldown_hours": 24,
        "description": "You are poor. You have the bare minimum needed for survival and function.",
        "is_default": True,  # Default for new characters
        "requires_approval": False,
    },
    {
        "bracket_name": "Average",
        "bracket_level": 2,
        "emoji": "💵",
        "base_income": 15000,  # 15,000 Jenny
        "bonus_income": 0,
        "cooldown_hours": 24,
        "description": "You're living an average life with average accommodations.",
        "is_default": False,
        "requires_approval": False,
    },
    {
        "bracket_name": "Wealthy",
        "bracket_level": 3,
        "emoji": "💎",
        "base_income": 50000,  # 50,000 Jenny
        "bonus_income": 10000,
        "cooldown_hours": 20,  # Slightly faster claim
        "description": "You are wealthy. Expect first class living.",
        "is_default": False,
        "requires_approval": False,  # Can be obtained through lucky roll
    },
    {
        "bracket_name": "Top 10% (The Rich)",
        "bracket_level": 4,
        "emoji": "👑",
        "base_income": 150000,  # 150,000 Jenny
        "bonus_income": 50000,
        "cooldown_hours": 18,
        "description": "You are living in luxury as one of the rich. The top 10% of society.",
        "is_default": False,
        "requires_approval": False,  # Can be obtained through rolling 10
    },
    {
        "bracket_name": "Top 5% (Royalty)",
        "bracket_level": 5,
        "emoji": "👸",
        "base_income": 500000,  # 500,000 Jenny
        "bonus_income": 250000,
        "cooldown_hours": 12,  # Much faster claims
        "description": "Money ceases to matter to you. You are royalty among the elite.",
        "is_default": False,
        "requires_approval": True,  # Admin-only assignment
    }
]


async def initialize_income_brackets(guild_id: int, admin_id: int):
    """
    Initialize default income brackets for a guild

    Args:
        guild_id: Discord guild ID
        admin_id: Discord ID of admin initializing

    Returns:
        Number of brackets created
    """
    async with DatabaseManager.get_session() as session:
        # Check if brackets already exist
        existing_result = await session.execute(
            select(IncomeBracket).where(IncomeBracket.guild_id == guild_id)
        )
        existing = existing_result.scalars().all()

        if existing:
            print(f"Income brackets already exist for guild {guild_id}")
            return 0

        # Create all brackets
        created_count = 0
        for bracket_data in INCOME_BRACKETS:
            bracket = IncomeBracket(
                guild_id=guild_id,
                bracket_name=bracket_data["bracket_name"],
                bracket_level=bracket_data["bracket_level"],
                emoji=bracket_data["emoji"],
                base_income=bracket_data["base_income"],
                bonus_income=bracket_data["bonus_income"],
                cooldown_hours=bracket_data["cooldown_hours"],
                description=bracket_data["description"],
                is_default=bracket_data["is_default"],
                requires_approval=bracket_data["requires_approval"],
                created_by=admin_id
            )
            session.add(bracket)
            created_count += 1

        await session.commit()
        print(f"✅ Created {created_count} income brackets for guild {guild_id}")
        return created_count


async def get_bracket_by_level(guild_id: int, bracket_level: int):
    """
    Get income bracket by level

    Args:
        guild_id: Discord guild ID
        bracket_level: Bracket level (1-5)

    Returns:
        IncomeBracket or None
    """
    async with DatabaseManager.get_session() as session:
        result = await session.execute(
            select(IncomeBracket).where(
                and_(
                    IncomeBracket.guild_id == guild_id,
                    IncomeBracket.bracket_level == bracket_level
                )
            )
        )
        return result.scalar_one_or_none()


async def get_bracket_by_name(guild_id: int, bracket_name: str):
    """
    Get income bracket by name

    Args:
        guild_id: Discord guild ID
        bracket_name: Name of bracket

    Returns:
        IncomeBracket or None
    """
    async with DatabaseManager.get_session() as session:
        result = await session.execute(
            select(IncomeBracket).where(
                and_(
                    IncomeBracket.guild_id == guild_id,
                    IncomeBracket.bracket_name == bracket_name
                )
            )
        )
        return result.scalar_one_or_none()


async def assign_clan_bracket(character, guild_id: int) -> dict:
    """
    Check if character's clan gives them automatic income bracket

    Zoldyck and Teier clans automatically get Top 10% bracket

    Args:
        character: Character object (with clan data loaded)
        guild_id: Discord guild ID

    Returns:
        dict with bracket info if assigned, or None if no clan bonus
    """
    async with DatabaseManager.get_session() as session:
        # Check if Zoldyck or Teier
        if not (character.clan.is_zoldyck or character.clan.is_teier):
            return None

        # Get Top 10% bracket
        result = await session.execute(
            select(IncomeBracket).where(
                and_(
                    IncomeBracket.guild_id == guild_id,
                    IncomeBracket.bracket_level == 4  # Top 10%
                )
            )
        )
        bracket = result.scalar_one_or_none()

        if not bracket:
            return None

        # Assign bracket
        character.basic.income_bracket_id = bracket.id
        session.add(character.basic)
        await session.commit()

        clan_name = "Zoldyck" if character.clan.is_zoldyck else "Teier"

        return {
            'success': True,
            'bracket': bracket,
            'bracket_id': bracket.id,
            'bracket_name': bracket.bracket_name,
            'bracket_level': bracket.bracket_level,
            'emoji': bracket.emoji,
            'base_income': bracket.base_income,
            'description': bracket.description,
            'clan_bonus': True,
            'clan_name': clan_name,
            'result_message': f"🏛️ **{clan_name} Clan Bonus!**\n\nAs a member of the prestigious {clan_name} family, you automatically receive **{bracket.bracket_name}** status!\n\n{bracket.emoji} Income: **{bracket.base_income + bracket.bonus_income:,} Jenny**"
        }


async def roll_starting_bracket(guild_id: int, chosen_start: str, lucky_numbers: list[int], roll_result: int) -> dict:
    """
    Determine starting income bracket based on CoC-style roll system

    Args:
        guild_id: Discord guild ID
        chosen_start: "Poor" or "Average" - player's choice
        lucky_numbers: List of 2 numbers the player chose (1-10)
        roll_result: The d10 roll result (1-10)

    Returns:
        dict with bracket info and result message
    """
    async with DatabaseManager.get_session() as session:
        # Validate choices
        if chosen_start not in ["Poor", "Average"]:
            return {
                'success': False,
                'error': 'Starting bracket must be "Poor" or "Average"'
            }

        if len(lucky_numbers) != 2 or not all(1 <= n <= 10 for n in lucky_numbers):
            return {
                'success': False,
                'error': 'Must choose exactly 2 lucky numbers between 1-10'
            }

        if roll_result < 1 or roll_result > 10:
            return {
                'success': False,
                'error': 'Roll must be between 1-10'
            }

        # Determine outcome
        bracket_name = chosen_start
        result_message = f"You rolled **{roll_result}**"

        # Special case: Rolling 10 = Top 10% (overrides lucky numbers)
        if roll_result == 10:
            bracket_name = "Top 10% (The Rich)"
            result_message += f"\n\n🎰 **JACKPOT!** You rolled a 10! You start as one of **The Rich**!"

        # Lucky number hit = Wealthy
        elif roll_result in lucky_numbers:
            bracket_name = "Wealthy"
            result_message += f"\n\n✨ **LUCKY!** You hit one of your numbers ({', '.join(map(str, lucky_numbers))})! You start **Wealthy**!"

        # No special roll = chosen start
        else:
            result_message += f"\n\nYour lucky numbers were {', '.join(map(str, lucky_numbers))}, but you didn't hit them. You start as **{chosen_start}**."

        # Get the bracket
        result = await session.execute(
            select(IncomeBracket).where(
                and_(
                    IncomeBracket.guild_id == guild_id,
                    IncomeBracket.bracket_name == bracket_name
                )
            )
        )
        bracket = result.scalar_one_or_none()

        if not bracket:
            return {
                'success': False,
                'error': f'Bracket "{bracket_name}" not found for this guild. Contact an admin to initialize income brackets.'
            }

        return {
            'success': True,
            'bracket': bracket,
            'bracket_id': bracket.id,
            'bracket_name': bracket.bracket_name,
            'bracket_level': bracket.bracket_level,
            'emoji': bracket.emoji,
            'base_income': bracket.base_income,
            'description': bracket.description,
            'result_message': result_message
        }


# Probability explanation for reference:
"""
Probability Breakdown:
- Start Poor/Average: Player choice (0% chance upgrade)
- Start Wealthy: 2/10 chance (20%) - hit one of your 2 lucky numbers
- Start Top 10%: 1/10 chance (10%) - roll exactly 10
  - Effective chance after number selection: If you pick 9 and 10, you have 2/10 to be Wealthy OR Top 10%
  - If you don't pick 10: 1/10 chance for Top 10%
- Start Top 5%: 0% chance (admin-only)

Strategy Tips:
- Picking 9 and 10 as lucky numbers gives you the best odds of starting rich
- Picking 10 as one number gives you a shot at both Wealthy (if rolled) and Top 10% (if rolled 10)
- Not picking 10 means you can only get Wealthy from lucky numbers
"""
