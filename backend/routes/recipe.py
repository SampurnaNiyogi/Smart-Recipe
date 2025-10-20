from fastapi import APIRouter, HTTPException, Query, status
from models.recipe import Recipe, Cuisine, Category, Diet, RecipeIn # Import RecipeIn
from typing import List, Optional
from beanie import PydanticObjectId 
from models.users import User
from routes.authentication import get_current_user
from models.history import UserViewHistory 
from fastapi import Depends 
from typing import Optional
import datetime
from pydantic import ValidationError
from services.substitutes import get_substitutes

recipe = APIRouter()
@recipe.get(
    "/recipe/substitutes/{ingredient_name}", 
    response_model=List[str],
    summary="Get substitutes for an ingredient"
)
async def get_ingredient_substitutes(
    ingredient_name: str,
    current_user: User = Depends(get_current_user) # Secure the endpoint
):
    """
    Provides a list of potential substitutes for a given ingredient.
    """
    substitutes = get_substitutes(ingredient_name)
    return substitutes
#Fetch details of each recipe
@recipe.get("/recipe", response_model=List[Recipe])
async def get_all_recipes(
    cuisine_id: Optional[PydanticObjectId] = Query(None),
    category_id: Optional[PydanticObjectId] = Query(None),
    diet_id: Optional[PydanticObjectId] = Query(None),
    search_query: Optional[str] = Query(None)
):
    
    filter_conditions = {}

    # 1. Add text search if provided
    if search_query:
        # Use MongoDB's $text operator
        filter_conditions["$text"] = {"$search": search_query}

    # 2. Add Link filters (using raw Mongo query syntax for Links)
    if cuisine_id:
        filter_conditions["cuisine.$id"] = cuisine_id
    
    if category_id:
        filter_conditions["category.$id"] = category_id
    
    if diet_id:
        filter_conditions["diet.$id"] = diet_id
        
    # 3. Execute the combined query
    # We use .find(filter_conditions) which accepts a raw Mongo query dict
    recipes = await Recipe.find(filter_conditions, fetch_links=True).to_list()
    
    # ... (the 'if not recipes' check you removed is still good to keep removed) ...
    
    return recipes

#Fetch details about a recipe
@recipe.get("/recipe/{recipe_id}", response_model=Recipe)
async def get_recipe(recipe_id: str, current_user: Optional[User] = Depends(get_current_user)):
    
    try:
        recipe_obj_id = PydanticObjectId(recipe_id)
    except ValidationError:
        raise HTTPException(status_code=400, detail="Invalid recipe ID format")

    recipe = await Recipe.get(recipe_obj_id, fetch_links=True)
    
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    
    if current_user:
        # To avoid spamming the DB, only log if it hasn't been logged in the last hour
        one_hour_ago = datetime.datetime.utcnow() - datetime.timedelta(hours=1)
        existing_view = await UserViewHistory.find_one(
            UserViewHistory.user == current_user,
            UserViewHistory.recipe.id == recipe_obj_id,
            UserViewHistory.viewed_at > one_hour_ago
        )
        
        if not existing_view:
            try:
                # Create and save the view history record
                view_log = UserViewHistory(user=current_user, recipe=recipe)
                await view_log.insert()
                print(f"User {current_user.user_name} viewed recipe {recipe.name}")
            except Exception as e:
                # Fail silently, logging the view is not critical
                print(f"Error logging view history: {e}")
    

    return recipe
    


@recipe.post("/create_recipe", status_code=status.HTTP_201_CREATED)
async def create_recipe(recipe_in: RecipeIn): # Use the RecipeIn model
    # Check for duplicate name
    if await Recipe.find_one(Recipe.name == recipe_in.name):
        raise HTTPException(status_code=400, detail="Recipe already exists")
    
    # --- Verify the Links ---
    # Find the documents to link
    cuisine = await Cuisine.get(recipe_in.cuisine_id)
    if not cuisine:
        raise HTTPException(status_code=404, detail="Cuisine not found")
        
    category = await Category.get(recipe_in.category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
        
    diet = await Diet.get(recipe_in.diet_id)
    if not diet:
        raise HTTPException(status_code=404, detail="Diet not found")

    # Create the new Recipe document using the linked objects
    new_recipe = Recipe(
        name=recipe_in.name,
        cuisine=cuisine,
        instructions=recipe_in.instructions,
        category=category,
        diet=diet,
        ingredients=recipe_in.ingredients,
        description=recipe_in.description,
        image_url=recipe_in.image_url
    )
    
    # Insert the new document
    await new_recipe.insert()
    
    return {"message": "Recipe created successfully", "recipe_id": str(new_recipe.id)}