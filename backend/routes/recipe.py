from fastapi import APIRouter, HTTPException, Query, status, Depends
from models.recipe import Recipe, Cuisine, Category, Diet, RecipeIn
from typing import List, Optional
from beanie import PydanticObjectId 
from models.users import User
from routes.authentication import get_current_user
from models.history import UserViewHistory 
import datetime
from pydantic import ValidationError
from services.substitutes import get_substitutes
import asyncio
import re
import os
from google import genai

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

recipe = APIRouter()

@recipe.get("/recipe/substitutes/{ingredient_name}", response_model=List[str])
async def get_ingredient_substitutes(
    ingredient_name: str,
    current_user: User = Depends(get_current_user)
):
    substitutes = get_substitutes(ingredient_name)
    return substitutes

async def validate_recipe_with_gemini(recipe_data: Recipe, search_term: str) -> bool:
    prompt = f"""
    You are a culinary expert API. A user searched for the recipe/ingredient: "{search_term}".
    
    Evaluate the following recipe:
    Name: {recipe_data.name}
    Ingredients: {recipe_data.ingredients}
    Description: {recipe_data.description or 'None'}
    
    Is this genuinely a "{search_term}" recipe? 
    (For example, if the search is "chicken" and this is a fish recipe that says "as good as chicken", the answer is False).
    If the user searched for a broad category like "salad" and this is clearly a salad, the answer is True.
    
    Reply ONLY with the exact word "True" or "False". Do not add any other text.
    """
    
    try:
        response = await client.aio.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )
        result = response.text.strip().lower()
        return "true" in result
    except Exception as e:
        print(f"Gemini API Validation Error for {recipe_data.name}: {e}")
        return True 

@recipe.get("/recipe", response_model=List[Recipe])
async def get_all_recipes(
    cuisine_id: Optional[PydanticObjectId] = Query(None),
    category_id: Optional[PydanticObjectId] = Query(None),
    diet_id: Optional[PydanticObjectId] = Query(None),
    search_query: Optional[str] = Query(None)
):
    if not search_query:
        queries = []
        if cuisine_id: queries.append(Recipe.cuisine.id == cuisine_id)
        if category_id: queries.append(Recipe.category.id == category_id)
        if diet_id: queries.append(Recipe.diet.id == diet_id)
            
        if queries:
            return await Recipe.find(*queries, fetch_links=True).to_list()
        return await Recipe.find_all(fetch_links=True).to_list()

    clean_query = re.sub(r'\b(recipe|recipes|dish|how to make)\b', '', search_query, flags=re.IGNORECASE).strip().lower()
    if not clean_query:
        clean_query = search_query.lower()

    regex_pattern = re.compile(clean_query, re.IGNORECASE)
    
    query_filters = {
        "$or": [
            {"name": regex_pattern},
            {"ingredients": regex_pattern},
            {"description": regex_pattern}
        ]
    }
    
    if cuisine_id: query_filters["cuisine.$id"] = cuisine_id
    if category_id: query_filters["category.$id"] = category_id
    if diet_id: query_filters["diet.$id"] = diet_id
        
    raw_recipes = await Recipe.find(query_filters, fetch_links=True).to_list()
    
    if not raw_recipes:
        return []

    validation_tasks = [validate_recipe_with_gemini(r, clean_query) for r in raw_recipes]
    validation_results = await asyncio.gather(*validation_tasks)

    final_recipes = [
        raw_recipes[i] for i in range(len(raw_recipes)) 
        if validation_results[i] is True
    ]

    return final_recipes

@recipe.get("/my-recipes", response_model=List[Recipe])
async def get_my_recipes(current_user: User = Depends(get_current_user)):
    recipes = await Recipe.find(Recipe.creator.id == current_user.id, fetch_links=True).to_list()
    return recipes

@recipe.get("/recipe/{recipe_id}", response_model=Recipe)
async def get_recipe(recipe_id: str, current_user: Optional[User] = Depends(get_current_user)):
    try:
        recipe_obj_id = PydanticObjectId(recipe_id)
    except ValidationError:
        raise HTTPException(status_code=400, detail="Invalid recipe ID format")

    fetched_recipe = await Recipe.get(recipe_obj_id, fetch_links=True)
    
    if not fetched_recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    
    if current_user:
        one_hour_ago = datetime.datetime.utcnow() - datetime.timedelta(hours=1)
        existing_view = await UserViewHistory.find_one(
            UserViewHistory.user.id == current_user.id,
            UserViewHistory.recipe.id == recipe_obj_id,
            UserViewHistory.viewed_at > one_hour_ago
        )
        
        if not existing_view:
            try:
                view_log = UserViewHistory(user=current_user, recipe=fetched_recipe)
                await view_log.insert()
                print(f"User {current_user.user_name} viewed recipe {fetched_recipe.name}")
            except Exception as e:
                print(f"Error logging view history: {e}")
    
    return fetched_recipe
    
@recipe.post("/create_recipe", status_code=status.HTTP_201_CREATED)
async def create_recipe(recipe_in: RecipeIn, current_user: User = Depends(get_current_user)): 
    if await Recipe.find_one(Recipe.name == recipe_in.name):
        raise HTTPException(status_code=400, detail="Recipe already exists")
    
    cuisine = await Cuisine.get(recipe_in.cuisine_id)
    category = await Category.get(recipe_in.category_id)
    diet = await Diet.get(recipe_in.diet_id)
    
    if not all([cuisine, category, diet]):
         raise HTTPException(status_code=404, detail="Relational data missing")

    new_recipe = Recipe(
        creator=current_user,
        name=recipe_in.name,
        cuisine=cuisine,
        instructions=recipe_in.instructions,
        category=category,
        diet=diet,
        ingredients=recipe_in.ingredients,
        description=recipe_in.description,
        image_url=recipe_in.image_url
    )
    
    await new_recipe.insert()
    return {"message": "Recipe created successfully", "recipe_id": str(new_recipe.id)}


@recipe.put("/recipe/{recipe_id}")
async def update_recipe(
    recipe_id: str, 
    recipe_update: RecipeIn, 
    current_user: User = Depends(get_current_user)
):
    recipe_obj = await Recipe.get(PydanticObjectId(recipe_id), fetch_links=True)
    
    if not recipe_obj:
        raise HTTPException(status_code=404, detail="Recipe not found")

    if not recipe_obj.creator or recipe_obj.creator.id != current_user.id:
        raise HTTPException(
            status_code=403, 
            detail="Permission denied: You can only edit your own recipes"
        )

    recipe_obj.name = recipe_update.name
    recipe_obj.instructions = recipe_update.instructions
    recipe_obj.ingredients = recipe_update.ingredients
    recipe_obj.description = recipe_update.description
    recipe_obj.image_url = recipe_update.image_url
    
    await recipe_obj.save()
    return {"message": "Recipe updated successfully"}

@recipe.delete("/recipe/{recipe_id}")
async def delete_recipe(
    recipe_id: str, 
    current_user: User = Depends(get_current_user)
):
    recipe_obj = await Recipe.get(PydanticObjectId(recipe_id), fetch_links=True)
    
    if not recipe_obj:
        raise HTTPException(status_code=404, detail="Recipe not found")

    if not recipe_obj.creator or recipe_obj.creator.id != current_user.id:
        raise HTTPException(
            status_code=403, 
            detail="Permission denied: You can only delete your own recipes"
        )
    
    await recipe_obj.delete()
    return {"message": "Recipe deleted successfully"}