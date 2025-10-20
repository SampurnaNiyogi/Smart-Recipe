from fastapi import APIRouter, HTTPException, Query, status
# from config.db import db  <- No longer need to import db directly
from models.recipe import Recipe, Cuisine, Category, Diet, RecipeIn # Import RecipeIn
from typing import List, Optional
# from bson import ObjectId <- No longer needed
from beanie import PydanticObjectId # Import for ID validation

recipe = APIRouter()

#Fetch details of each recipe
@recipe.get("/recipe", response_model=List[Recipe])
async def get_all_recipes(
    cuisine_id: Optional[PydanticObjectId] = Query(None),
    category_id: Optional[PydanticObjectId] = Query(None),
    diet_id: Optional[PydanticObjectId] = Query(None)
):
    
    # Build a list of search queries
    find_queries = []
    if cuisine_id:
        # Query on the linked document's ID
        find_queries.append(Recipe.cuisine.id == cuisine_id)
    if category_id:
        find_queries.append(Recipe.category.id == category_id)
    if diet_id:
        find_queries.append(Recipe.diet.id == diet_id)
        
    # Run the query. fetch_links=True automatically populates
    # recipe.cuisine, recipe.category, and recipe.diet
    recipes = await Recipe.find(*find_queries, fetch_links=True).to_list()
    
    if not recipes:
        raise HTTPException(status_code=404, detail="Recipe not found")
    
    # No more manual for-loops to replace IDs!
    
    return recipes

#Fetch details about a recipe
@recipe.get("/recipe/{recipe_id}", response_model=Recipe)
async def get_recipe(recipe_id: PydanticObjectId):
    # .get() with fetch_links=True is all you need
    recipe = await Recipe.get(recipe_id, fetch_links=True)
    
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    
    # No more manual lookups!
    
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