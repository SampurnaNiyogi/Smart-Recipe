from fastapi import FastAPI
from routes.recipe import recipe
from routes.cuisine import cuisine
from routes.category import category
from routes.diet import diet
from routes.authentication import auth_router
from fastapi.middleware.cors import CORSMiddleware
from beanie import init_beanie
import motor.motor_asyncio
import os 
from dotenv import load_dotenv 
from models.users import User
from models.recipe import Recipe, Category, Cuisine, Diet

load_dotenv()
app = FastAPI()

@app.on_event("startup")
async def on_startup():
    """
    Initialize Beanie and the async database client.
    """
    # Create the AsyncIOMotorClient
    client = motor.motor_asyncio.AsyncIOMotorClient(
        os.getenv("MONGO_URI")
    )
    
    # Get the database name (you called it 'SmartRecipe' in config/db.py)
    database = client.SmartRecipe

    # Initialize Beanie with all your Document models
    await init_beanie(
        database=database,
        document_models=[
            User,
            Category,
            Cuisine,
            Diet,
            Recipe
        ]
    )

app.include_router(recipe)
app.include_router(cuisine)
app.include_router(category)
app.include_router(diet)
app.include_router(auth_router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.get("/")
async def root():
    return {"message": "API is running"}