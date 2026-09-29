from fastapi import FastAPI, HTTPException

from services.recipes.generator import generate_options
from services.recipes.models import RecipeOption, SuggestRequest
from services.recipes.service import get_recipe_detail
from shared.errors import RecipeGenerationError

app = FastAPI()


@app.post("/recipes/options")
def options(request: SuggestRequest) -> list[RecipeOption]:
    try:
        return generate_options(request.recent_products)
    except RecipeGenerationError as e:
        raise HTTPException(status_code=502, detail=str(e)) from e


@app.post("/recipes/detail")
def detail(option: RecipeOption):
    try:
        return get_recipe_detail(option)
    except RecipeGenerationError as e:
        raise HTTPException(status_code=502, detail=str(e)) from e
