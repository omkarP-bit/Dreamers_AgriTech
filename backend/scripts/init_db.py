"""
Database Initialization Script - MongoDB Version

Creates collections and optionally seeds initial data
"""

import sys
import os
import asyncio
from datetime import datetime, date, timedelta

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.database import Database


async def init_database():
    """
    Initialize database collections and indexes
    """
    print("🗄️  Initializing MongoDB database...")
    
    try:
        await Database.connect_db()
        db = Database.db
        
        # Get list of existing collections
        collections = await db.list_collection_names()
        
        print(f"📊 Existing collections: {len(collections)}")
        if collections:
            for collection in collections:
                print(f"   - {collection}")
        
        print("✅ MongoDB connected and ready!")
        
        await Database.close_db()
        
    except Exception as e:
        print(f"❌ Error initializing database: {e}")


async def seed_test_data():
    """
    Seed database with test data for development
    """
    print("\n🌱 Seeding test data...")
    
    try:
        await Database.connect_db()
        db = Database.db
        
        # Check if data already exists
        existing_farmers = await db.farmers.count_documents({})
        
        if existing_farmers > 0:
            print(f"⚠️  Database already has {existing_farmers} farmers. Skipping seed.")
            await Database.close_db()
            return
        
        # Create test farmers
        farmers = [
            {
                "name": "Ramesh Kumar",
                "phone": "+91-9876543210",
                "location": "Punjab, Ludhiana",
                "created_at": datetime.utcnow()
            },
            {
                "name": "Suresh Patel",
                "phone": "+91-9876543211",
                "location": "Gujarat, Ahmedabad",
                "created_at": datetime.utcnow()
            },
            {
                "name": "Kavita Sharma",
                "phone": "+91-9876543212",
                "location": "Maharashtra, Pune",
                "created_at": datetime.utcnow()
            },
        ]
        
        result = await db.farmers.insert_many(farmers)
        farmer_ids = result.inserted_ids
        
        print(f"✅ Created {len(farmers)} test farmers")
        
        # Create test crop season for first farmer
        season = {
            "farmer_id": str(farmer_ids[0]),
            "crop_type": None,
            "variety": None,
            "start_date": datetime.utcnow(),
            "expected_harvest_date": None,
            "current_phase": "pre_sowing",
            "farmer_type": "traditional",
            "soil_type": "loam",
            "previous_crop": "wheat",
            "initial_weather_data": {"note": "Weather data will be fetched when conversation starts"},
            "crop_plan": None,
            "yield_prediction": None,
            "actual_yield": None,
            "status": "active",
            "created_at": datetime.utcnow()
        }
        
        season_result = await db.crop_seasons.insert_one(season)
        
        print(f"✅ Created 1 active crop season (ID: {season_result.inserted_id})")
        
        print("\n👤 Test Farmer Accounts:")
        for i, farmer in enumerate(farmers):
            print(f"   Name: {farmer['name']}")
            print(f"   Phone: {farmer['phone']}")
            print(f"   Location: {farmer['location']}")
            print(f"   ID: {str(farmer_ids[i])}")
            print()
        
        await Database.close_db()
        
    except Exception as e:
        print(f"❌ Error seeding data: {e}")
        await Database.close_db()


async def drop_all_collections():
    """
    Drop all collections (CAUTION: This deletes all data!)
    """
    print("\n⚠️  WARNING: This will delete ALL data!")
    confirm = input("Are you sure? Type 'yes' to confirm: ")
    
    if confirm.lower() == "yes":
        try:
            await Database.connect_db()
            db = Database.db
            
            print("🗑️  Dropping all collections...")
            collections = await db.list_collection_names()
            
            for collection in collections:
                await db[collection].drop()
                print(f"   Dropped: {collection}")
            
            print("✅ All collections dropped")
            await Database.close_db()
            
        except Exception as e:
            print(f"❌ Error dropping collections: {e}")
            await Database.close_db()
    else:
        print("❌ Operation cancelled")


async def reset_database():
    """
    Drop all collections and recreate them
    """
    print("\n🔄 Resetting database...")
    await drop_all_collections()
    await init_database()
    await seed_test_data()


async def show_stats():
    """
    Show database statistics
    """
    try:
        await Database.connect_db()
        db = Database.db
        
        farmer_count = await db.farmers.count_documents({})
        season_count = await db.crop_seasons.count_documents({})
        active_seasons = await db.crop_seasons.count_documents({"status": "active"})
        task_count = await db.tasks.count_documents({})
        conversation_count = await db.agent_conversations.count_documents({})
        
        print("\n📊 Database Statistics:")
        print(f"   Farmers: {farmer_count}")
        print(f"   Total Seasons: {season_count}")
        print(f"   Active Seasons: {active_seasons}")
        print(f"   Tasks: {task_count}")
        print(f"   Conversations: {conversation_count}")
        
        await Database.close_db()
        
    except Exception as e:
        print(f"❌ Error getting stats: {e}")
        await Database.close_db()


async def interactive_menu():
    """
    Interactive menu for database management
    """
    print("""
    ╔══════════════════════════════════════════════════════════════════╗
    ║                                                                  ║
    ║           🌾 FARM AI - MongoDB Initialization 🌾                 ║
    ║                                                                  ║
    ╚══════════════════════════════════════════════════════════════════╝
    """)
    
    while True:
        print("\n💡 Options:")
        print("   1. Initialize database (create indexes)")
        print("   2. Seed test data")
        print("   3. Show statistics")
        print("   4. Reset database (drop + init + seed)")
        print("   5. Drop all collections")
        print("   6. Exit")
        
        choice = input("\nEnter choice (1-6): ").strip()
        
        if choice == "1":
            await init_database()
        elif choice == "2":
            await seed_test_data()
        elif choice == "3":
            await show_stats()
        elif choice == "4":
            await reset_database()
        elif choice == "5":
            await drop_all_collections()
        elif choice == "6":
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please enter 1-6.")


async def main():
    """
    Main function - parse command line arguments
    """
    import argparse
    
    parser = argparse.ArgumentParser(description="MongoDB database initialization script")
    parser.add_argument(
        "command",
        nargs="?",
        choices=["init", "seed", "reset", "drop", "stats"],
        help="Command to execute"
    )
    
    args = parser.parse_args()
    
    if args.command == "init":
        await init_database()
    elif args.command == "seed":
        await seed_test_data()
    elif args.command == "reset":
        await reset_database()
    elif args.command == "drop":
        await drop_all_collections()
    elif args.command == "stats":
        await show_stats()
    else:
        # No command - show interactive menu
        await interactive_menu()
    
    print("\n" + "="*70)
    print("💡 Usage examples:")
    print("   python scripts/init_db.py init    # Initialize indexes")
    print("   python scripts/init_db.py seed    # Seed test data")
    print("   python scripts/init_db.py reset   # Reset database")
    print("   python scripts/init_db.py stats   # Show statistics")
    print("   python scripts/init_db.py drop    # Drop all collections")
    print("="*70)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 Interrupted by user. Goodbye!")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()