from google import genai
from google.genai import types

from services.recipes.models import RecipeDetail, RecipeOption
from shared.errors import RecipeGenerationError

from shared.config import GEMINI_API_KEY, MODEL_NAME

_client = genai.Client(api_key=GEMINI_API_KEY)


def generate_options(recent_ingredients: str) -> list[RecipeOption]:
    prompt = (
        "Basado en estos productos que la persona compró recientemente: "
        f"{recent_ingredients}. "
        "Sugiere 3 opciones de receta distintas entre sí. Cada una debe tener "
        "2 a 5 ingredientes clave que la hagan inconfundible frente a las otras dos."
    )

    try:
        response = _client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=list[RecipeOption],
            ),
        )
    except Exception as e:
        raise RecipeGenerationError(f"Falló la llamada a Gemini: {e}") from e

    if response.parsed is None:
        reason = response.candidates[0].finish_reason if response.candidates else "unknown"
        raise RecipeGenerationError(
            f"Gemini no devolvió opciones válidas (finish_reason={reason})"
        )
    if not isinstance(response.parsed, list):
        raise RecipeGenerationError("Gemini no devolvió una lista de opciones")
    return response.parsed


def generate_detail(option: RecipeOption) -> RecipeDetail:
    prompt = (
        "Genera una receta para preparar el siguiente plato:"
        f"{option.name}: {option.description}"
        "Asegurate que la preparacion incluya el uso de los siguientes(pero no se limite a otros) ingredientes clave."
        f"{', '.join(option.key_ingredients)}"
        "Indica el tiempo de coccion y la informacion nutricional del plato preparado"
    )

    try:
        response = _client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=RecipeDetail,
            ),
        )
    except Exception as e:
        raise RecipeGenerationError(f"Falló la llamada a Gemini: {e}") from e

    if response.parsed is None:
        reason = response.candidates[0].finish_reason if response.candidates else "unknown"
        raise RecipeGenerationError(
            f"Gemini no devolvió opciones válidas (finish_reason={reason})"
        )
    if not isinstance(response.parsed, RecipeDetail):
        raise RecipeGenerationError("Gemini no devolvió una receta válida")
    return response.parsed
