from pymongo import MongoClient, UpdateOne
from bson import ObjectId, DBRef

# --- CONFIGURE THIS ---
MONGO_URL = "mongodb+srv://root:mongodb@chatbot.n4hmnkd.mongodb.net/" 
DB_NAME = "SmartRecipe"
# --------------------

client = MongoClient(MONGO_URL)
db = client[DB_NAME]
recipes_collection = db.recipes

bulk_updates = []
for recipe in recipes_collection.find():
    recipe_id = recipe["_id"]
    updates = {}
    
    # Check and build updates for each field
    if "cuisine_id" in recipe and isinstance(recipe["cuisine_id"], ObjectId):
        updates["cuisine"] = DBRef("cuisines", recipe["cuisine_id"])
        updates["$unset"] = {"cuisine_id": ""}
        
    if "category_id" in recipe and isinstance(recipe["category_id"], ObjectId):
        updates["category"] = DBRef("categories", recipe["category_id"])
        if "$unset" in updates:
            updates["$unset"]["category_id"] = ""
        else:
            updates["$unset"] = {"category_id": ""}

    if "diet_id" in recipe and isinstance(recipe["diet_id"], ObjectId):
        updates["diet"] = DBRef("diets", recipe["diet_id"])
        if "$unset" in updates:
            updates["$unset"]["diet_id"] = ""
        else:
            updates["$unset"] = {"diet_id": ""}

    # If there are updates to be made, add them to the bulk list
    if updates:
        if "$unset" in updates:
            bulk_updates.append(UpdateOne(
                {"_id": recipe_id},
                {"$set": updates, "$unset": updates.pop("$unset")}
            ))
        else:
            bulk_updates.append(UpdateOne(
                {"_id": recipe_id},
                {"$set": updates}
            ))

# Execute the bulk update
if bulk_updates:
    print(f"Found {len(bulk_updates)} documents to migrate...")
    result = recipes_collection.bulk_write(bulk_updates)
    print(f"Migration complete. {result.modified_count} documents updated.")
else:
    print("No documents found needing migration.")

client.close()