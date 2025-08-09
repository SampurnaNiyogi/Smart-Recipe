from fastapi import FastAPI
from routes.recipe import recipe
from routes.cuisine import cuisine
from routes.category import category
from routes.diet import diet
from fastapi.middleware.cors import CORSMiddleware
app = FastAPI()

app.include_router(recipe)
app.include_router(cuisine)
app.include_router(category)
app.include_router(diet)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.get("/")
async def root():
    return {"message": "API is running"}