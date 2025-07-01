import numpy as np
from collections import defaultdict
from typing import List, Tuple, Callable
from aimakerspace.openai_utils.embedding import EmbeddingModel
import asyncio


def cosine_similarity(vector_a: np.array, vector_b: np.array) -> float:
    """Computes the cosine similarity between two vectors."""
    dot_product = np.dot(vector_a, vector_b)
    norm_a = np.linalg.norm(vector_a)
    norm_b = np.linalg.norm(vector_b)
    return dot_product / (norm_a * norm_b)


def euclidean_distance(vector_a: np.array, vector_b: np.array) -> float:
    """Computes the euclidean distance between two vectors."""
    return np.linalg.norm(vector_a - vector_b)


class VectorDatabase:
    def __init__(
        self,
        embedding_model: EmbeddingModel = None,
        distance_metric: str = "cosine",
    ):
        self.vectors = defaultdict(dict)
        self.embedding_model = embedding_model or EmbeddingModel()
        if distance_metric == "cosine":
            self.distance_measure = cosine_similarity
        elif distance_metric == "euclidean":
            self.distance_measure = euclidean_distance
        else:
            raise ValueError(f"Unknown distance metric: {distance_metric}")
        self.distance_metric = distance_metric

    def insert(self, key: str, vector: np.array, metadata: dict = None) -> None:
        self.vectors[key]["vector"] = vector
        self.vectors[key]["metadata"] = metadata or {}

    def search(
        self,
        query_vector: np.array,
        k: int,
        return_metadata: bool = False,
    ) -> List[Tuple]:
        scores = [
            (
                key,
                self.distance_measure(query_vector, data["vector"]),
                data.get("metadata", {}),
            )
            for key, data in self.vectors.items()
        ]
        if self.distance_metric == "cosine":
            sorted_scores = sorted(scores, key=lambda x: x[1], reverse=True)
        else:
            sorted_scores = sorted(scores, key=lambda x: x[1], reverse=False)

        top_k = sorted_scores[:k]

        if return_metadata:
            return top_k
        else:
            return [(text, score) for text, score, metadata in top_k]

    def search_by_text(
        self,
        query_text: str,
        k: int,
        return_metadata: bool = False,
    ) -> List[Tuple]:
        query_vector = self.embedding_model.get_embedding(query_text)
        results = self.search(query_vector, k, return_metadata=return_metadata)
        return results

    def retrieve_from_key(self, key: str) -> np.array:
        return self.vectors.get(key, None)

    async def abuild_from_list(
        self, list_of_docs: List
    ) -> "VectorDatabase":
        if not list_of_docs:
            return self

        if isinstance(list_of_docs[0], tuple):
            texts, metadatas = zip(*list_of_docs)
            list_of_text = list(texts)
            metadatas = list(metadatas)
        else:
            list_of_text = list_of_docs
            metadatas = [{} for _ in list_of_text]
        
        embeddings = await self.embedding_model.async_get_embeddings(list_of_text)
        for text, embedding, metadata in zip(list_of_text, embeddings, metadatas):
            self.insert(text, np.array(embedding), metadata)
        return self


if __name__ == "__main__":
    list_of_text = [
        "I like to eat broccoli and bananas.",
        "I ate a banana and spinach smoothie for breakfast.",
        "Chinchillas and kittens are cute.",
        "My sister adopted a kitten yesterday.",
        "Look at this cute hamster munching on a piece of broccoli.",
    ]

    vector_db = VectorDatabase()
    vector_db = asyncio.run(vector_db.abuild_from_list(list_of_text))
    k = 2

    searched_vector = vector_db.search_by_text("I think fruit is awesome!", k=k)
    print(f"Closest {k} vector(s):", searched_vector)

    retrieved_vector = vector_db.retrieve_from_key(
        "I like to eat broccoli and bananas."
    )
    print("Retrieved vector:", retrieved_vector)

    relevant_texts = vector_db.search_by_text(
        "I think fruit is awesome!", k=k, return_metadata=True
    )
    print(f"Closest {k} text(s):", relevant_texts)
