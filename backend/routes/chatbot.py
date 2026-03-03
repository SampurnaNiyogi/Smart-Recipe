from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from models.users import User
from routes.authentication import get_current_user
from services.substitutes import get_substitutes
from services.recommendations import get_seasonal_suggestions
from models.recipe import Recipe
from google import genai
import os
import json
import re

# Initialize the new Client
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

class ChatQuery(BaseModel):
    query: str

class ChatResponse(BaseModel):
    response: str

chatbot_router = APIRouter()

async def analyze_intent(query: str) -> dict:
    """Uses Gemini to classify the user's intent and extract keywords."""
    prompt = f"""
    You are the brain of a Smart Recipe App chatbot. Analyze the user's message: "{query}"
    
    Categorize it into exactly one of these intents:
    - "find_recipe": User wants to cook something, looking for a recipe, or has specific ingredients.
    - "get_substitute": User needs an alternative for a specific ingredient.
    - "get_seasonal": User is asking for seasonal food suggestions.
    - "general_chat": Greetings, thank yous, or general cooking questions not requiring a database search.

    Extract the main subject as the "keyword".
    
    Respond STRICTLY with valid JSON. Do not include markdown formatting like ```json.
    Format: {{"intent": "intent_name", "keyword": "extracted_subject"}}
    """
    try:
        # NEW SDK SYNTAX
        response = await client.aio.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )
        clean_json = response.text.replace('```json', '').replace('```', '').strip()
        return json.loads(clean_json)
    except Exception as e:
        print(f"Intent parsing error: {e}")
        return {"intent": "general_chat", "keyword": query}

@chatbot_router.post(
    "/chatbot/query",
    response_model=ChatResponse,
    summary="Process a chatbot query with Gemini"
)
async def handle_chat_query(
    request: ChatQuery,
    current_user: User = Depends(get_current_user)
):
    query = request.query
    
    # Step 1: Understand the intent
    analysis = await analyze_intent(query)
    intent = analysis.get("intent")
    keyword = analysis.get("keyword", "")
    
    print(f"DEBUG - Intent: {intent} | Keyword: {keyword}") # Helpful for terminal debugging
    
    context_data = ""

    # Step 2: Fetch data based on the intent
    if intent == "find_recipe":
        regex_pattern = re.compile(keyword, re.IGNORECASE)
        recipes = await Recipe.find({"name": regex_pattern}).limit(3).to_list()
        if recipes:
            context_data = "Found these recipes in the database: " + ", ".join([r.name for r in recipes])
        else:
            context_data = f"No recipes found in the database for '{keyword}'."
            
    elif intent == "get_substitute":
        substitutes = get_substitutes(keyword)
        if substitutes:
            context_data = f"Database substitutes for {keyword}: {', '.join(substitutes)}."
        else:
            context_data = f"No substitutes found in the database for {keyword}."
            
    elif intent == "get_seasonal":
        suggestions = await get_seasonal_suggestions(limit=3)
        if suggestions:
            context_data = "Seasonal suggestions from database: " + ", ".join([r.name for r in suggestions])
        else:
            context_data = "No seasonal recipes found right now."

    # Step 3: Generate a friendly response
    response_prompt = f"""
    You are a friendly, helpful culinary assistant for a Smart Recipe App. 
    
    User details: Name is {current_user.user_name}.
    User message: "{query}"
    System Intent detected: {intent}
    Data retrieved from our app's database: "{context_data}"
    
    Instructions:
    1. Always start your response with a natural, complete greeting that includes the user's name (e.g., "Hi {current_user.user_name}!" or "Hello {current_user.user_name},").
    2. Write a conversational, helpful, and concise response. 
    3. If the database provided data, present it naturally. 
    4. If the database had no data, politely inform them and offer general cooking advice.
    """
    
    try:
        # NEW SDK SYNTAX
        final_response = await client.aio.models.generate_content(
            model='gemini-2.5-flash',
            contents=response_prompt
        )
        return ChatResponse(response=final_response.text.strip())
    except Exception as e:
        print(f"Chat generation error: {e}")
        return ChatResponse(response="I'm having a little trouble thinking right now. Please try again!")