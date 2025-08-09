from fastapi import APIRouter, HTTPException
from config.db import db
from models.recipe import Category
from typing import List
from bson import ObjectId
category = APIRouter()

#Fetch all cuisines
@category.get("/categories", response_model=List[Category])
async def get_ingredients():
    categories = list(db.categories.find({}))
    if not categories:
        raise HTTPException(status_code=404, detail="No cuisine")

    for category in categories:
        category["_id"] = str(category["_id"])   
    
    return categories