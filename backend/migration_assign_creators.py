import asyncio
import os
import random
from dotenv import load_dotenv

import motor.motor_asyncio
from beanie import init_beanie

# Import models
from models.users import User
from models.recipe import Recipe, Category, Cuisine, Diet
from models.history import UserViewHistory

load_dotenv()

async def assign_random_creators():
    print("Starting migration process...")

    # 1. Initialize MongoDB connection
    mongo_uri = os.getenv("MONGO_URI")
    if not mongo_uri:
         print("Error: MONGO_URI not found in environment variables.")
         return
         
    client = motor.motor_asyncio.AsyncIOMotorClient(mongo_uri)
    database = client.SmartRecipe

    # 2. Initialize Beanie
    print("Initializing Beanie models...")
    await init_beanie(
        database=database,
        document_models=[
            User,
            Category,
            Cuisine,
            Diet,
            Recipe,
            UserViewHistory
        ]
    )

    # 3. Fetch all existing users
    print("Fetching users...")
    all_users = await User.find_all().to_list()
    if not all_users:
        print("CRITICAL: No users found in the database.")
        return

    # 4. Fetch recipes via RAW motor connection
    # We bypass Beanie's to_list() to avoid Pydantic validation errors on existing data
    print("Fetching recipes via raw motor collection...")
    recipe_collection = Recipe.get_motor_collection()
    all_raw_recipes = await recipe_collection.find({}).to_list(length=None)
    
    if not all_raw_recipes:
        print("No recipes found to migrate.")
        return

    print(f"Found {len(all_users)} users and {len(all_raw_recipes)} recipes. Starting random assignment...")

    # 5. Loop through and assign
    updated_count = 0
    for raw_recipe in all_raw_recipes:
        # Check if the recipe already has a creator
        if "creator" not in raw_recipe:
            random_user = random.choice(all_users)
            
            # The exact format Beanie expects for a Link Reference
            creator_link = {
                "id": random_user.id,
                "collection": "Users" # Make sure this matches User.Settings.name if set, otherwise "User"
            }
            
            # Update the specific document in the database
            await recipe_collection.update_one(
                {"_id": raw_recipe["_id"]},
                {"$set": {"creator": creator_link}}
            )
            updated_count += 1
            print(f"✅ Assigned recipe: '{raw_recipe.get('name', 'Unknown')}' ---> Creator: '{random_user.user_name}'")
        else:
             print(f"⏩ Skipped recipe '{raw_recipe.get('name', 'Unknown')}' (already has a creator)")

    print(f"Migration complete! Successfully updated {updated_count} recipes.")

# Run the async script
if __name__ == "__main__":
    asyncio.run(assign_random_creators())