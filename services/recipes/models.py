from pydantic import BaseModel, Field, ValidationError


class RecipeOption(BaseModel):
    name: str
    description: str
    key_ingredients: list[str] = Field(min_length=2, max_length=5)
    cook_time_minutes: int
    calories_approx: int

    def identity_text(self) -> str:
        """Texto que identifica esta opción, para generar su embedding más adelante."""
        ingredients = ", ".join(self.key_ingredients)
        return f"{self.name}. {self.description}. Ingredientes: {ingredients}"
