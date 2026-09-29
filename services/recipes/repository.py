import psycopg
from pgvector.psycopg import register_vector

from shared.config import SUPABASE_URL
from services.recipes.models import Ingredient, Nutrition, RecipeDetail
from services.recipes.embeddings import embed


def save_recipe(detail: RecipeDetail, embedding: list[float]) -> str:
    with psycopg.connect(SUPABASE_URL) as conn:
        register_vector(conn)
        with conn.cursor() as cur:
            cur.execute(
                """
                insert into recipes (identity_text, embedding, detail)
                values (%s, %s, %s)
                returning id
                """,
                (detail.identity_text(),
                 embedding,
                 detail.model_dump_json()),
            )
            row = cur.fetchone()
            if row is None:
                raise RuntimeError("El INSERT no devolvió ninguna fila")
    return str(row[0])


def find_similar_recipe(query_text: str, threshold: float = 0.80) -> RecipeDetail | None:
    query_embedding = embed(query_text)
    with psycopg.connect(SUPABASE_URL) as conn:
        register_vector(conn)
        with conn.cursor() as cur:
            cur.execute(
                """
                select detail, 1 - (embedding <=> %s::vector) as similarity
                from recipes
                order by similarity desc
                limit 1
                """,
                (query_embedding,),
            )
            row = cur.fetchone()

    if row is None:
        return None
    detail_json, similarity = row
    if similarity < threshold:
        return None
    return RecipeDetail.model_validate(detail_json)
