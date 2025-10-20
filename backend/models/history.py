from beanie import Document, Link, PydanticObjectId
from models.users import User
from models.recipe import Recipe
from datetime import datetime
import pydantic

class UserViewHistory(Document):
    user: Link[User]
    recipe: Link[Recipe]
    viewed_at: datetime = pydantic.Field(default_factory=datetime.utcnow)

    class Settings:
        name = "user_view_history"
        indexes = [
            "user",
            "recipe",
            [("user", 1), ("recipe", 1)] # Index for faster lookups
        ]