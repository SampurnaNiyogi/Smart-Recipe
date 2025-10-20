from pydantic import BaseModel, Field, BeforeValidator
from typing import List, Optional
from bson import ObjectId
from typing_extensions import Annotated
from beanie import Document, Link, PydanticObjectId  # Import Link & PydanticObjectId

# This is no longer needed for the Recipe document, 
# but you can keep it if other Pydantic models use it.
PyObjectId = Annotated[str, BeforeValidator(str)]

# --- NEW Pydantic Model for CREATING recipes ---
# We use this for POST requests
class RecipeIn(BaseModel):
    name: str
    cuisine_id: PydanticObjectId   # Use Beanie's ID type for input
    instructions: str
    category_id: PydanticObjectId
    diet_id: PydanticObjectId
    ingredients: str
    description: Optional[str] = None
    image_url: Optional[str] = None


class Cuisine(Document):
    
    name: str

    class Settings:
        name = "cuisines"

class Category(Document):
    name: str

    class Settings:
        name = "categories"

class Diet(Document):
    name: str

    class Settings:
        name = "diets"

# --- UPDATED Recipe Document Model ---
class Recipe(Document):
    # 'id' is handled automatically by Beanie
    name: str
    cuisine: Link[Cuisine]         # Changed from cuisine_id
    instructions: str
    category: Link[Category]     # Changed from category_id
    diet: Link[Diet]             # Changed from diet_id
    ingredients: str
    description: Optional[str] = None
    image_url: Optional[str] = None
    
    # We remove the old Pydantic 'model_config'
    
    class Settings:
        name = "recipes" # This is your collection name