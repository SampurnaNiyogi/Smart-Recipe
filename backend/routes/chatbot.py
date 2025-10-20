from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from models.users import User
from routes.authentication import get_current_user

# Import the services you've already built!
from services.substitutes import get_substitutes
from services.recommendations import get_seasonal_suggestions
from models.recipe import Recipe # We'll use this to search

# --- Pydantic Models for the Request/Response ---

class ChatQuery(BaseModel):
    """The user's message"""
    query: str

class ChatResponse(BaseModel):
    """The bot's response"""
    response: str

# --- The Chatbot Router ---

chatbot_router = APIRouter()

@chatbot_router.post(
    "/chatbot/query",
    response_model=ChatResponse,
    summary="Process a chatbot query"
)
async def handle_chat_query(
    request: ChatQuery,
    current_user: User = Depends(get_current_user)
):
    """
    This is the main "brain" of the chatbot.
    It takes a user's query and tries to match it to an intent.
    
    This is a simple rule-based example. A more advanced bot
    would use NLP libraries like spaCy or Rasa.
    """
    query = request.query.lower().strip()
    
    # --- Intent 1: Greeting ---
    if query in ["hi", "hello", "hey"]:
        return ChatResponse(response=f"Hello, {current_user.user_name}! How can I help you with recipes today?")

    # --- Intent 2: Ask for Substitutes ---
    if "substitute for" in query or "replace" in query:
        # Simple parser: find the word after "substitute for"
        try:
            ingredient = query.split("substitute for")[-1].strip()
            if not ingredient:
                ingredient = query.split("replace")[-1].strip()

            if ingredient:
                substitutes = get_substitutes(ingredient)
                if substitutes:
                    sub_list = ", ".join(substitutes)
                    return ChatResponse(response=f"Possible substitutes for {ingredient} are: {sub_list}.")
                else:
                    return ChatResponse(response=f"Sorry, I don't have any common substitutes listed for {ingredient}.")
            else:
                 return ChatResponse(response="What ingredient do you need a substitute for?")
        except Exception:
            return ChatResponse(response="I'm not sure what ingredient you're asking about. Try 'What is a substitute for butter?'.")

    # --- Intent 3: Ask for Seasonal Recipes ---
    if "seasonal" in query or "in season" in query:
        suggestions = await get_seasonal_suggestions(limit=3)
        if suggestions:
            names = [r.name for r in suggestions]
            return ChatResponse(response=f"Here are some popular seasonal recipes: {', '.join(names)}. Would you like to know more about one?")
        else:
            return ChatResponse(response="I couldn't find any seasonal recipes right now.")

    # --- Intent 4: Ask for a specific recipe ---
    if "how to make" in query or "recipe for" in query:
        search_term = query.replace("how to make", "").replace("recipe for", "").strip()
        
        # Use your existing text search capability
        recipe = await Recipe.find_one({"$text": {"$search": search_term}}, fetch_links=True)
        
        if recipe:
            # Respond with a summary and link (the frontend would need to handle this)
            # For a pure text bot, we can give instructions.
            return ChatResponse(response=f"I found a recipe for {recipe.name}! Here are the instructions: {recipe.instructions}")
        else:
            return ChatResponse(response=f"Sorry, I couldn't find a recipe matching '{search_term}'.")

    # --- Fallback Response ---
    else:
        return ChatResponse(response="I'm not sure how to help with that. You can ask me for recipe substitutes, seasonal ideas, or how to make a specific dish.")