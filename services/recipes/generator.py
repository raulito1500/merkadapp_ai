from google.genai import types

from services.recipes.models import RecipeDetail, RecipeOption, RecipeOptionLLMSchema
from shared.errors import RecipeGenerationError

from shared.config import MODEL_NAME
from shared.llm import client


def generate_options(recent_ingredients: str) -> list[RecipeOptionLLMSchema]:
    meal_type = "desayuno, almuerzo, snack"
    goal = "Mantenimiento del peso"
    dietary_preferences = "bajo en calorias, carbohidratos para perdida de peso, alto en proteina. Cero picante"
    culinary_style = "Latinoamericana Thai, Italiana y meditarranea."
    prompt = f"""
        Actúa como un chef profesional y un nutricionista experto. 
        A partir de los siguientes datos del usuario:

        - **Ingredientes disponibles:** {recent_ingredients}
        - **Tipo de comida:** {meal_type}  
        - **Objetivo nutricional:** {goal} 
        - **Preferencias o restricciones dietéticas:** {dietary_preferences}  # Ej: Sin restricciones, vegetariano, alergia al maní, no me gusta el cilantro, etc.
        - **Estilo culinario preferido (opcional):** {culinary_style}  # Ej: Comida colombiana, italiana, rápida, casera, etc.

        Genera 3 opciones de recetas distintas entre sí que cumplan estrictamente con las siguientes reglas:
        1. **Alineación nutricional y de estilo:** Deben ajustarse al objetivo, al tipo de comida y respetar las preferencias o restricciones indicadas.
        2. **Variedad:** Las 3 opciones deben ser diferentes entre sí (evita repetir el mismo tipo de preparación).
        3. **Ingredientes clave:** Cada receta debe destacar de 2 a 5 ingredientes clave (priorizando los ingredientes disponibles del usuario).
        4. **Imagen:** En `photo_query` incluye una frase corta de búsqueda EN INGLÉS que nombre el platillo específico (por ejemplo "grilled chicken quinoa bowl"). No incluyas URLs.

        Cada opción debe ajustarse exactamente al esquema de datos requerido.
        """

    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=list[RecipeOptionLLMSchema],
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
        response = client.models.generate_content(
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
