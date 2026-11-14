import time

from services.recipes.embeddings import embed
from services.recipes.generator import generate_detail, generate_options
from services.recipes.images import search_photo
from services.recipes.models import RecipeDetail, RecipeOption
from services.recipes.repository import find_similar_recipe, save_recipe
from shared.errors import RecipeGenerationError
from shared.merkadapp_client import get_recent_ingredients


def get_options() -> list[RecipeOption]:
    try:
        ingredients = get_recent_ingredients()
    except Exception as e:
        raise RecipeGenerationError(
            f"Falló la llamada a productos: {e}") from e

    if not ingredients:
        raise RecipeGenerationError(
            "No hay productos comprados recientemente para sugerir recetas")

    ingredient_names = ", ".join(i["product_name"] for i in ingredients)
    llm_options = generate_options(ingredient_names)
    # Sequential on purpose: Brave's free plan is rate-limited (~1 req/s).
    options = []
    for i, llm_option in enumerate(llm_options):
        if i > 0:
            time.sleep(1)
        options.append(
            RecipeOption(
                **llm_option.model_dump(exclude={"photo_query"}),
                photo=search_photo(llm_option.photo_query),
            )
        )
    return options


def get_recipe_detail(option: RecipeOption) -> RecipeDetail:
    query_text = option.identity_text()

    cached = find_similar_recipe(query_text)
    if cached is not None:
        return cached

    detail = generate_detail(option)
    save_recipe(detail, embed(detail.identity_text()))
    return detail
