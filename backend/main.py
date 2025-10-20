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
from routes.recommendations import recommendation_router
from services.recommendations import build_recommendation_model
from contextlib import asynccontextmanager
from models.history import UserViewHistory
load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Code to run on startup
    print("Application startup...")
    
    # --- START FIX ---
    # Initialize the database client and Beanie here
    print("Initializing database connection and Beanie...")
    client = motor.motor_asyncio.AsyncIOMotorClient(
        os.getenv("MONGO_URI")
    )
    database = client.SmartRecipe # Get the database name

    # Initialize Beanie with all your Document models
    await init_beanie(
        database=database,
        document_models=[
            User,
            Category,
            Cuisine,
            Diet,
            Recipe,
            UserViewHistory
        ]
    )
    print("Beanie initialized.")
    # --- END FIX ---

    # Now it's safe to call the recommendation model build
    await build_recommendation_model()
    
    yield
    
    # Code to run on shutdown (if any)
    print("Application shutdown.")

app = FastAPI(lifespan=lifespan)

# Remove the old @app.on_event("startup") function
# It is now handled by the lifespan context manager

app.include_router(recipe)
app.include_router(cuisine)
app.include_router(category)
app.include_router(diet)
app.include_router(auth_router)
app.include_router(recommendation_router)

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