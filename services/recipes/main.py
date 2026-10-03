from fastapi import FastAPI, HTTPException

from services.recipes.models import RecipeOption
from services.recipes.service import get_options, get_recipe_detail
from shared.errors import RecipeGenerationError

app = FastAPI()


@app.get("/recipes/options")
def options() -> list[RecipeOption]:
    try:
        return get_options()
    except RecipeGenerationError as e:
        raise HTTPException(status_code=502, detail=str(e)) from e


@app.post("/recipes/detail")
def detail(option: RecipeOption):
    try:
        return get_recipe_detail(option)
    except RecipeGenerationError as e:
        raise HTTPException(status_code=502, detail=str(e)) from e
