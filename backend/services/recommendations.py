import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
import pandas as pd
from models.recipe import Recipe # Import your Recipe model
from beanie import PydanticObjectId

# --- In-memory cache for the recommendation model ---
# In a production app, you might use a more robust cache like Redis
# or regenerate this periodically.
recommendation_cache = {
    "data": None,
    "indices": None,
    "cosine_sim": None,
}

async def build_recommendation_model():
    """
    Fetches all recipes and builds a TF-IDF matrix and cosine similarity matrix.
    Caches the results in memory.
    """
    print("Building recommendation model...")
    recipes = await Recipe.find_all(fetch_links=True).to_list()

    if not recipes:
        print("No recipes found to build model.")
        return

    # Create a pandas DataFrame from the recipe data
    recipe_list = [
        {
            "_id": str(r.id),
            "name": r.name,
            # Simple text cleaning: replace commas with spaces for better tokenization
            "ingredients": r.ingredients.replace(",", " "),
            "description": r.description or "",
        }
        for r in recipes
    ]
    df = pd.DataFrame(recipe_list)

    # Use TF-IDF to convert ingredients text into a matrix of feature vectors
    # analyzer='word', ngram_range=(1, 2) considers single words and pairs of words
    # min_df=0 stops it from dropping words that appear rarely
    tfidf = TfidfVectorizer(analyzer='word', ngram_range=(1, 2), min_df=1, stop_words='english')
    
    # Combine ingredients and description for a richer feature set
    df['combined_features'] = df['ingredients'] + " " + df['description']
    tfidf_matrix = tfidf.fit_transform(df['combined_features'])

    # Calculate cosine similarity between all recipes
    cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)

    # Create a mapping from recipe ID to DataFrame index
    indices = pd.Series(df.index, index=df['_id'])

    # Store the built model in the cache
    recommendation_cache["data"] = df
    recommendation_cache["indices"] = indices
    recommendation_cache["cosine_sim"] = cosine_sim
    print("Recommendation model built successfully.")


async def get_similar_recipes(recipe_id: str, top_n: int = 5):
    """
    Given a recipe ID, returns the top N most similar recipes.
    """
    # Check if the model is built, if not, build it.
    if recommendation_cache["cosine_sim"] is None:
        await build_recommendation_model()
    
    # Retrieve cached model components
    df = recommendation_cache["data"]
    indices = recommendation_cache["indices"]
    cosine_sim = recommendation_cache["cosine_sim"]

    if indices is None or recipe_id not in indices:
        return [] # Return empty list if model isn't ready or recipe not found

    # Get the index of the recipe that matches the ID
    idx = indices[recipe_id]

    # Get the pairwise similarity scores of all recipes with that recipe
    sim_scores = list(enumerate(cosine_sim[idx]))

    # Sort the recipes based on the similarity scores
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

    # Get the scores of the (top_n + 1) most similar recipes (we exclude the recipe itself)
    sim_scores = sim_scores[1:top_n+1]

    # Get the recipe indices
    recipe_indices = [i[0] for i in sim_scores]
    
    # Get the recipe IDs from the indices
    recommended_ids = df['_id'].iloc[recipe_indices].tolist()
    
    # Fetch the full recipe documents from the database
    object_ids = [PydanticObjectId(rid) for rid in recommended_ids]

    # Fetch the full recipe documents from the database using a raw query
    recommended_recipes = await Recipe.find(
        {"_id": {"$in": object_ids}},
        fetch_links=True
    ).to_list()
    
    return recommended_recipes


def get_current_season():
    """
    Determines the current season in India based on the month.
    """
    month = datetime.datetime.now().month
    if month in [12, 1, 2]:
        return "winter"
    elif month in [3, 4, 5]:
        return "summer"
    elif month in [6, 7, 8, 9]:
        return "monsoon"
    else: # 10, 11
        return "autumn"

async def get_seasonal_suggestions(limit: int = 4):
    """
    Suggests recipes based on the current season in India.
    """
    season = get_current_season()
    query = {}
    
    # Define keywords for each season
    if season == "winter":
        # Search for soups, stews, hot, spicy, baked dishes
        query = {"$or": [
            {"name": {"$regex": "soup|stew|hot|baked|spicy", "$options": "i"}},
            {"description": {"$regex": "soup|stew|hot|baked|spicy", "$options": "i"}},
        ]}
    elif season == "summer":
        # Search for salads, cool, fresh, ice cream, drinks
        query = {"$or": [
            {"name": {"$regex": "salad|cool|fresh|ice|juice|drink", "$options": "i"}},
            {"description": {"$regex": "salad|cool|fresh|ice|juice|drink", "$options": "i"}},
        ]}
    elif season == "monsoon":
        # Search for fried, warm, tea, coffee, pakora
        query = {"$or": [
            {"name": {"$regex": "fried|warm|tea|coffee|pakora|samosa", "$options": "i"}},
            {"description": {"$regex": "fried|warm|tea|coffee|pakora|samosa", "$options": "i"}},
        ]}
    else: # Autumn - can be a mix of warm and festive
        query = {"$or": [
            {"name": {"$regex": "pumpkin|sweet|festive|pie", "$options": "i"}},
            {"description": {"$regex": "pumpkin|sweet|festive|pie", "$options": "i"}},
        ]}

    # Execute the query using Beanie, limit results
    seasonal_recipes = await Recipe.find(query, fetch_links=True).limit(limit).to_list()
    
    return seasonal_recipes
