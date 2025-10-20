# A simple dictionary for substitutions.
# In a real app, this could be a separate database collection.
SUBSTITUTE_DB = {
    "butter": ["margarine", "olive oil (for sauteing)", "shortening (for baking)"],
    "paneer": ["tofu (firm)", "halloumi"],
    "egg": ["flax egg (1 tbsp flax + 3 tbsp water, for baking)", "tofu (for scrambles)", "apple sauce (for baking)"],
    "all-purpose flour": ["bread flour (for yeast bread)", "cake flour (for cakes)", "gluten-free 1-to-1 blend"],
    "milk": ["soy milk", "almond milk", "oat milk", "coconut milk"],
    "sugar": ["honey", "maple syrup", "stevia", "agave nectar"],
    "heavy cream": ["coconut cream", "half-and-half (for some sauces)"],
    "yogurt": ["sour cream", "coconut yogurt"],
    "curd": ["sour cream", "coconut yogurt"],
    "onion": ["shallots", "onion powder"],
    "garlic": ["garlic powder", "asafoetida (hing)"],
    "chicken": ["tofu", "seitan", "turkey"],
    "beef": ["mushrooms", "lentils", "ground turkey"]
}

def get_substitutes(ingredient_name: str) -> list[str]:
    """
    Finds potential substitutes for a given ingredient name.
    """
    clean_name = ingredient_name.lower().strip()
    
    # Try direct lookup
    if clean_name in SUBSTITUTE_DB:
        return SUBSTITUTE_DB[clean_name]
    
    # Try partial lookup
    for key, substitutes in SUBSTITUTE_DB.items():
        if key in clean_name:
            return substitutes
            
    return [] # No substitutes found