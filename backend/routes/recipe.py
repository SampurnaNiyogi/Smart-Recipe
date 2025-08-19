from fastapi import APIRouter, HTTPException, Query
from config.db import db
from models.recipe import Recipe, Cuisine, Category
from typing import List
from bson import ObjectId
recipe = APIRouter()

#Fetch details of each recipe
@recipe.get("/recipe", response_model=List[Recipe])
async def get_all_recipes(cuisine_id: str | None = Query(None), category_id: str | None = Query(None), diet_id: str | None = Query(None)):
    query = {}
    if cuisine_id:
        query["cuisine_id"] = ObjectId(cuisine_id)
    if category_id:
        query["category_id"] = ObjectId(category_id)
    if diet_id:
        query["diet_id"] = ObjectId(diet_id)
        
    recipes = list(db.recipes.find(query))
    if not recipes:
        raise HTTPException(status_code=404, detail="Recipe not found")
    
    for recipe in recipes:
        recipe["_id"] = str(recipe["_id"])
        cuisine = db.cuisines.find_one({"_id": recipe["cuisine_id"]})
        recipe["cuisine_id"] = cuisine["name"] if cuisine else None
        category = db.categories.find_one({"_id": recipe["category_id"]})
        recipe["category_id"] = category["name"] if category else None
        diet = db.diets.find_one({"_id": recipe["diet_id"]})
        recipe["diet_id"] = diet["name"] if diet else None
        
    return recipes

#Fetch details about a recipe
@recipe.get("/recipe/{recipe_id}", response_model=Recipe)
async def get_recipe(recipe_id: str):
    recipe_data = db.recipes.find_one({"_id": ObjectId(recipe_id)})
    if not recipe_data:
        raise HTTPException(status_code=404, detail="Recipe not found")
    
    recipe_data["_id"] = str(recipe_data["_id"])
    
    cuisine = db.cuisines.find_one({"_id": recipe_data["cuisine_id"]})
    recipe_data["cuisine_id"] = cuisine["name"] if cuisine else None
    
    category = db.categories.find_one({"_id": recipe_data["category_id"]})
    recipe_data["category_id"] = category["name"] if category else None
    
    diet = db.diets.find_one({"_id": recipe_data["diet_id"]})
    recipe_data["diet_id"] = diet["name"] if diet else None

    return recipe_data


@recipe.post("/create_recipe")
async def create_recipe(recipe: Recipe):
    existing_recipe = db.recipes.find_one({"name": recipe.name})
    if existing_recipe:
        raise HTTPException(status_code=404, detail = "Recipe already exists")
    
    db.recipes.insert_one(recipe.dict(exclude={"_id"}))    
    return {"message": "Recipe created successfully"}  