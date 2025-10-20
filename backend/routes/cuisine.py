from fastapi import APIRouter, HTTPException
# from config.db import db  <- Removed
from models.recipe import Cuisine
from typing import List
# from bson import ObjectId <- Removed

cuisine = APIRouter()

#Fetch all cuisines
@cuisine.get("/cuisines", response_model=List[Cuisine])
async def get_cuisines():  # Renamed function
    cuisines = await Cuisine.find_all().to_list()  # Use Beanie query
    if not cuisines:
        raise HTTPException(status_code=404, detail="No cuisine")

    # The for loop for converting _id is no longer needed
    
    return cuisines