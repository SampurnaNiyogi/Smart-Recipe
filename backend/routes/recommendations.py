from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from beanie import PydanticObjectId
from models.history import UserViewHistory
from models.recipe import Recipe, Cuisine
from services.recommendations import get_similar_recipes, get_seasonal_suggestions
from routes.authentication import get_current_user 
from models.users import User 
import asyncio
from collections import Counter
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

@recommendation_router.get(
    "/recommendations/history",
    response_model=List[Recipe],
    summary="Get recommendations based on user's view history"
)
async def get_history_recommendations(
    current_user: User = Depends(get_current_user)
):
    """
    Returns a list of recipes that are similar to the user's most
    recently viewed items.
    """
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    # 1. Get the last N unique recipes the user viewed (all history for exclusion)
    recent_views = await UserViewHistory.find(
        UserViewHistory.user == current_user,
        fetch_links=True # Fetch the linked recipe document
    ).sort("-viewed_at").to_list()

    if not recent_views:
        return []

    # Collect ALL seen recipe IDs for exclusion (to avoid recommending anything viewed before)
    all_seen_ids = {view.recipe._id for view in recent_views if view.recipe}

    # 2. Get the last 3 unique recipe IDs as basis for similarity
    unique_recipe_ids = []
    recent_seen_ids = set()
    for view in recent_views:
        if view.recipe and view.recipe._id not in recent_seen_ids:
            unique_recipe_ids.append(view.recipe._id)
            recent_seen_ids.add(view.recipe._id)
        if len(unique_recipe_ids) >= 3: # Get similar to last 3 unique items
            break
            
    if not unique_recipe_ids:
        return []

    # 3. Get similar recipes for each of those viewed recipes
    tasks = []
    for recipe_id in unique_recipe_ids:
        # Get 2 similar items for each of the 3 viewed items
        tasks.append(get_similar_recipes(str(recipe_id), top_n=2)) 
        
    results = await asyncio.gather(*tasks)
    
    # 4. Flatten the list and remove duplicates, excluding ALL previously seen
    final_recommendations = {} # Use dict to de-duplicate
    for recipe_list in results:
        for recipe in recipe_list:
            if recipe._id not in all_seen_ids:
                final_recommendations[recipe._id] = recipe
    
    return list(final_recommendations.values())[:4]

@recommendation_router.get(
    "/recommendations/preferred_cuisine",
    response_model=List[Recipe],
    summary="Get recommendations from user's preferred cuisine"
)
async def get_preferred_cuisine_recommendations(
    current_user: User = Depends(get_current_user)
):
    """
    Analyzes view history to find the user's most viewed cuisine
    and suggests other recipes from that cuisine.
    """
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )

    # 1. Get all view history for the user
    views = await UserViewHistory.find(
        UserViewHistory.user == current_user,
        fetch_links=True # This will fetch the linked Recipe
    ).to_list()

    if not views:
        return []

    # 2. Analyze fetched recipes to find the top cuisine
    cuisine_ids = []
    for view in views:
        if view.recipe and view.recipe.cuisine:
            # We need to fetch the cuisine link
            await view.recipe.fetch_link("cuisine")
            if view.recipe.cuisine:
                cuisine_ids.append(view.recipe.cuisine._id)

    if not cuisine_ids:
        return []

    # Count occurrences of each cuisine ID
    cuisine_counts = Counter(cuisine_ids)
    most_common_cuisine_id = cuisine_counts.most_common(1)[0][0]

    # 3. Get other recipes from that cuisine
    # Exclude recipes the user has already seen
    seen_recipe_ids = {view.recipe._id for view in views if view.recipe}
    
    preferred_recipes = await Recipe.find(
        Recipe.cuisine._id == most_common_cuisine_id,
        # The line that was here is now deleted
        fetch_links=True
    ).limit(4).to_list()
    
    return preferred_recipes