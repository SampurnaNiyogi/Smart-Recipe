from fastapi import APIRouter, HTTPException
from config.db import db
from models.recipe import Cuisine
from typing import List
from bson import ObjectId
cuisine = APIRouter()

#Fetch all cuisines
@cuisine.get("/cuisines", response_model=List[Cuisine])
async def get_ingredients():
    cuisines = list(db.cuisines.find({}))
    if not cuisines:
        raise HTTPException(status_code=404, detail="No cuisine")

    for cuisine in cuisines:
        cuisine["_id"] = str(cuisine["_id"])   
    
    return cuisines