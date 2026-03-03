from pydantic import BaseModel, ConfigDict, Field, BeforeValidator
from typing import List, Optional, ClassVar
from bson import ObjectId
from typing_extensions import Annotated
from beanie import Document, Link, PydanticObjectId
from pymongo import IndexModel, TEXT
from models.users import User

PyObjectId = Annotated[str, BeforeValidator(str)]

class RecipeIn(BaseModel):
    name: str
    cuisine_id: PydanticObjectId
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

class Recipe(Document):
    creator: Link[User]
    name: str
    cuisine: Link[Cuisine]
    instructions: str
    category: Link[Category]
    diet: Link[Diet]
    ingredients: str
    description: Optional[str] = None
    image_url: Optional[str] = None

    class Settings:
        name = "recipes"
        indexes: ClassVar = [
            IndexModel(
                [("name", TEXT), ("description", TEXT), ("ingredients", TEXT)],
                name="recipe_text_search_index"
            )
        ]