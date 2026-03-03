from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from models.recipe import Recipe
from routes.authentication import get_current_user
from models.users import User
from services.recommendations import get_similar_recipes
import urllib.request
import json
import re
import asyncio

recommendation_router = APIRouter()

@recommendation_router.get("/recommendations/similar/{recipe_id}", response_model=List[Recipe])
async def get_similar_recipe_recommendations(
    recipe_id: str,
    current_user: User = Depends(get_current_user)
):
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
        
    similar_recipes = await get_similar_recipes(recipe_id, top_n=4)
    return similar_recipes

def fetch_weather_sync(lat: float, lon: float):
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,precipitation"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as response:
        return json.loads(response.read().decode())

@recommendation_router.get("/recommendations/seasonal", response_model=List[Recipe])
async def get_seasonal_recipe_recommendations(
    lat: Optional[float] = Query(None),
    lon: Optional[float] = Query(None),
    current_user: User = Depends(get_current_user)
):
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
        
    search_terms = ["salad", "cooler", "mango", "cold", "ice cream", "refreshing", "summer"]
    
    if lat is not None and lon is not None:
        try:
            weather_data = await asyncio.to_thread(fetch_weather_sync, lat, lon)
            current = weather_data.get("current", {})
            temp = current.get("temperature_2m", 25)
            precip = current.get("precipitation", 0)
            
            if precip > 0.5:
                search_terms = ["fry", "pakora", "tea", "spicy", "soup", "warm", "monsoon"]
            elif temp < 20:
                search_terms = ["soup", "stew", "bake", "hot", "roast", "winter"]
            elif temp > 30:
                search_terms = ["salad", "cooler", "mango", "cold", "refreshing", "summer"]
            else:
                search_terms = ["fresh", "light", "green", "berry", "fruit", "spring"]
        except Exception:
            pass
            
    regex_pattern = re.compile("|".join(search_terms), re.IGNORECASE)
    
    recipes = await Recipe.find(
        {"$or": [
            {"name": regex_pattern},
            {"description": regex_pattern},
            {"ingredients": regex_pattern}
        ]},
        fetch_links=True
    ).limit(4).to_list()
    
    if not recipes:
        recipes = await Recipe.find_all(fetch_links=True).limit(4).to_list()
        
    return recipes