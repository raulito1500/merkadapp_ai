from pydantic import BaseModel, Field


class RecipeOption(BaseModel):
    name: str
    description: str
    key_ingredients: list[str] = Field(min_length=2, max_length=5)
    cook_time_minutes: int
    calories_approx: int

    def identity_text(self) -> str:
        ingredients = ", ".join(self.key_ingredients)
        return f"{self.name}. {self.description}. Ingredientes: {ingredients}"


class Ingredient(BaseModel):
    name: str
    amount: float
    unit: str


class Nutrition(BaseModel):
    calories: float
    protein_g: float
    carbs_g: float
    fat_g: float


class RecipeDetail(BaseModel):
    name: str
    description: str
    ingredients: list[Ingredient]
    steps: list[str]
    cook_time_minutes: int
    nutrition: Nutrition

    def identity_text(self) -> str:
        ingredients = ", ".join(map(lambda i: i.name, self.ingredients))
        return f"{self.name}. {self.description}. Ingredientes: {ingredients}"
