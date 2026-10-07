class MerkadappAIError(Exception):
    """Error propio del proyecto, en vez de una excepción cruda de una librería externa."""


class RecipeGenerationError(MerkadappAIError):
    """Gemini no pudo generar opciones de receta usables."""

class InvoiceProcessingError(MerkadappAIError):
    """Gemini no pudo decidir sobre una factura, o la llamada falló."""

