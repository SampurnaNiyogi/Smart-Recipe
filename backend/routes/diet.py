from fastapi import APIRouter, HTTPException
from config.db import db
from models.recipe import Diet
from typing import List
from bson import ObjectId
diet = APIRouter()

#Fetch all cuisines
@diet.get("/diets", response_model=List[Diet])
async def get_diets():
    diets = list(db.diets.find({}))
    if not diets:
        raise HTTPException(status_code=404, detail="No diet")

    for diet in diets:
        diet["_id"] = str(diet["_id"])   
    
    return diets