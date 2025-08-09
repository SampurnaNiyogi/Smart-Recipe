from pydantic import BaseModel, Field, BeforeValidator, ConfigDict
from typing import List, Optional
from bson import ObjectId
from typing_extensions import Annotated

PyObjectId = Annotated[str, BeforeValidator(str)]
class Recipe(BaseModel):
    id: Optional[PyObjectId] = Field(alias = "_id", default = None)
    name: str
    cuisine_id: PyObjectId
    instructions: str
    category_id: PyObjectId
    diet_id: PyObjectId
    ingredients: str
    description: Optional[str] = None
    image_url: Optional[str] = None

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str, PyObjectId: str}
    )

class Cuisine(BaseModel):
    id: Optional[PyObjectId] = Field(alias = "_id", default = None)
    name: str

class Category(BaseModel):
    id: Optional[PyObjectId] = Field(alias = "_id", default = None)
    name: str

class Diet(BaseModel):
    id: Optional[PyObjectId] = Field(alias = "_id", default = None)
    name: str