"""
Migration: Add InformationPage table and editors field to InformationTopic

This migration:
1. Adds 'editors' column to information_topics table
2. Creates information_pages table for multi-page topic support
3. Migrates existing topic content to first page of each topic
"""

from sqlalchemy import text
from database.db_manager import DatabaseManager
import asyncio


async def run_migration():
    """Run the migration"""
    async with DatabaseManager.get_session() as session:
        try:
            print("🔄 Starting information pages system migration...")

            # Step 1: Add editors column to information_topics if it doesn't exist
            print("  📝 Adding editors column to information_topics...")
            await session.execute(text("""
                ALTER TABLE information_topics
                ADD COLUMN IF NOT EXISTS editors VARCHAR DEFAULT '';
            """))
            print("  ✅ Editors column added")

            # Step 2: Create information_pages table if it doesn't exist
            print("  📝 Creating information_pages table...")
            await session.execute(text("""
                CREATE TABLE IF NOT EXISTS information_pages (
                    id BIGSERIAL PRIMARY KEY,
                    topic_id INTEGER NOT NULL,
                    page_number INTEGER NOT NULL,
                    content TEXT NOT NULL,
                    created_by BIGINT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    editors VARCHAR DEFAULT '',
                    FOREIGN KEY (topic_id) REFERENCES information_topics(id) ON DELETE CASCADE
                );
            """))
            print("  ✅ information_pages table created")

            # Step 3: Create index on topic_id for faster lookups
            print("  📝 Creating indexes...")
            await session.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_information_pages_topic_id
                ON information_pages(topic_id);
            """))
            print("  ✅ Indexes created")

            # Step 4: Migrate existing content to pages (if any topics exist with content)
            print("  📝 Migrating existing topic content to pages...")

            # Check if there are topics with content but no pages
            result = await session.execute(text("""
                SELECT id, content, created_by
                FROM information_topics
                WHERE content IS NOT NULL
                  AND content != ''
                  AND id NOT IN (SELECT DISTINCT topic_id FROM information_pages);
            """))
            topics_to_migrate = result.fetchall()

            if topics_to_migrate:
                print(f"  📦 Found {len(topics_to_migrate)} topics to migrate...")

                for topic_id, content, created_by in topics_to_migrate:
                    # Create first page with existing content
                    await session.execute(text("""
                        INSERT INTO information_pages (topic_id, page_number, content, created_by)
                        VALUES (:topic_id, 1, :content, :created_by);
                    """), {
                        "topic_id": topic_id,
                        "content": content[:2000],  # Limit to 2000 chars for first page
                        "created_by": created_by
                    })

                print(f"  ✅ Migrated {len(topics_to_migrate)} topics to page system")
            else:
                print("  ℹ️  No topics need migration")

            await session.commit()
            print("✅ Information pages system migration completed successfully!")
            return True

        except Exception as e:
            print(f"❌ Migration failed: {e}")
            await session.rollback()
            raise


if __name__ == "__main__":
    asyncio.run(run_migration())
