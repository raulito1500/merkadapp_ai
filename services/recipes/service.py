from services.recipes.embeddings import embed
from services.recipes.generator import generate_detail, generate_options
from services.recipes.models import RecipeDetail, RecipeOption
from services.recipes.repository import find_similar_recipe, save_recipe
from shared.errors import RecipeGenerationError


def get_recipe_detail(option: RecipeOption) -> RecipeDetail:
    query_text = option.identity_text()

    cached = find_similar_recipe(query_text)
    if cached is not None:
        return cached

    detail = generate_detail(option)
    save_recipe(detail, embed(detail.identity_text()))
    return detail
