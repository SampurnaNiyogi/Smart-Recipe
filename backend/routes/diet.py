from fastapi import APIRouter, HTTPException
# from config.db import db  <- Removed
from models.recipe import Diet
from typing import List
# from bson import ObjectId <- Removed

diet = APIRouter()

#Fetch all diets
@diet.get("/diets", response_model=List[Diet])
async def get_diets():
    diets = await Diet.find_all().to_list()  # Use Beanie query
    if not diets:
        raise HTTPException(status_code=404, detail="No diet")

    # The for loop for converting _id is no longer needed
    
    return diets