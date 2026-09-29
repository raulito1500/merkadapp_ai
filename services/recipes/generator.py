import os

from dotenv import load_dotenv
from google import genai
from google.genai import types

from services.recipes.models import RecipeOption
from shared.errors import RecipeGenerationError

load_dotenv()

_client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
MODEL_NAME = "gemini-2.5-flash"


def generate_options(recent_products: list[str]) -> list[RecipeOption]:
    prompt = (
        "Basado en estos productos que la persona compró recientemente: "
        f"{', '.join(recent_products)}. "
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
                max_output_tokens=20,
            ),
        )
    except Exception as e:
        raise RecipeGenerationError(f"Falló la llamada a Gemini: {e}") from e

    if response.parsed is None:
        reason = response.candidates[0].finish_reason if response.candidates else "unknown"
        raise RecipeGenerationError(
            f"Gemini no devolvió opciones válidas (finish_reason={reason})"
        )
    return response.parsed


if __name__ == "__main__":
    productos = ["pechuga de pollo", "arroz", "cebolla", "tomate", "leche"]
    try:
        opciones = generate_options(productos)
        for o in opciones:
            print(o)
            print("---")
    except RecipeGenerationError as e:
        print(f"Un error se presentó durante la obtención: {e}")
