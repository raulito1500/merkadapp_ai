from sentence_transformers import SentenceTransformer, util

MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"
_model = SentenceTransformer(MODEL_NAME)


def embed(text: str) -> list[float]:
    encoded = _model.encode(text)
    return encoded.tolist()


if __name__ == "__main__":
    frases = [
        {"texto": "arroz con pollo", "embebido": 0},
        {"texto": "algo con ave y arroz", "embebido": 0},
        {"texto": "pollo con arroz", "embebido": 0},
        {"texto": "brownies de chocolate", "embebido": 0},
        {"texto": "chicken and rice", "embebido": 0},
        {"texto": "Rice with chicken", "embebido": 0},
        {"texto": "arroz con pollo y verduras", "embebido": 0},
        {"texto": "arroz con leche", "embebido": 0},
        {"texto": "pollo al horno con papas", "embebido": 0},
        {"texto": "sopa de pollo", "embebido": 0},
    ]
    referencia = embed(frases[0]["texto"])
    for frase in frases:
        vector = embed(frase["texto"])
        frase["embebido"] = float(util.cos_sim(referencia, vector).item())

    frases.sort(key=lambda frase: frase["embebido"], reverse=True)
    for frase in frases:
        print(f"{frase['texto']}\n{frase['embebido']}\n")
