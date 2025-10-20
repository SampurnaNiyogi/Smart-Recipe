from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

from models.recipe import Recipe, Cuisine
from services.recommendations import get_similar_recipes, get_seasonal_suggestions
from routes.authentication import get_current_user 
from models.users import User 

# Create a new router
recommendation_router = APIRouter()

@recommendation_router.get(
    "/recommendations/similar/{recipe_id}",
    response_model=List[Recipe],
    summary="Get recipes similar to the given one"
)
async def get_similar_recipe_recommendations(
    recipe_id: str,
    current_user: User = Depends(get_current_user) # Secure the endpoint
):
    """
    Returns a list of recipes that are similar to the specified recipe,
    based on ingredient and description similarity.
    """
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
        
    similar_recipes = await get_similar_recipes(recipe_id, top_n=4)
    return similar_recipes


@recommendation_router.get(
    "/recommendations/seasonal",
    response_model=List[Recipe],
    summary="Get seasonal recipe suggestions"
)
async def get_seasonal_recipe_recommendations(
    current_user: User = Depends(get_current_user) # Secure the endpoint
):
    """
    Returns a list of recipes suggested for the current season in India.
    """
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
        
    seasonal_recipes = await get_seasonal_suggestions(limit=4)
    return seasonal_recipes

