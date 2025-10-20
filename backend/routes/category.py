from fastapi import APIRouter, HTTPException
# from config.db import db  <- Removed
from models.recipe import Category
from typing import List
# from bson import ObjectId <- Removed

category = APIRouter()

#Fetch all categories
@category.get("/categories", response_model=List[Category])
async def get_categories():  # Renamed function
    categories = await Category.find_all().to_list()  # Use Beanie query
    if not categories:
        raise HTTPException(status_code=404, detail="No categories found") # Updated detail

    # The for loop for converting _id is no longer needed
    
    return categories