from __future__ import annotations

import hashlib
from abc import ABC, abstractmethod

import numpy as np

from app.core.config import Settings, get_settings


class EmbeddingProvider(ABC):
    @abstractmethod
    def embed_texts(self, texts: list[str]) -> np.ndarray:
        raise NotImplementedError


class HashEmbeddingProvider(EmbeddingProvider):
    """离线兜底向量，保证 demo/test 在无模型环境仍可运行。"""

    def __init__(self, dimensions: int = 384):
        self.dimensions = dimensions

    def embed_texts(self, texts: list[str]) -> np.ndarray:
        vectors = []
        for text in texts:
            vector = np.zeros(self.dimensions, dtype=float)
            for token in text.lower().split():
                digest = hashlib.sha256(token.encode("utf-8")).digest()
                index = int.from_bytes(digest[:4], "big") % self.dimensions
                vector[index] += 1.0
            norm = np.linalg.norm(vector) or 1.0
            vectors.append(vector / norm)
        return np.vstack(vectors)


class SentenceTransformerProvider(EmbeddingProvider):
    def __init__(self, model_name: str):
        try:
            from sentence_transformers import SentenceTransformer

            self.model = SentenceTransformer(model_name)
        except Exception:
            self.model = None
            self.fallback = HashEmbeddingProvider()

    def embed_texts(self, texts: list[str]) -> np.ndarray:
        if self.model is None:
            return self.fallback.embed_texts(texts)
        return np.asarray(self.model.encode(texts, normalize_embeddings=True), dtype=float)


class OpenAIEmbeddingProvider(EmbeddingProvider):
    def __init__(self, settings: Settings):
        if not settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY is required when EMBEDDING_PROVIDER=openai")
        from openai import OpenAI

        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_embedding_model

    def embed_texts(self, texts: list[str]) -> np.ndarray:
        response = self.client.embeddings.create(model=self.model, input=texts)
        return np.asarray([item.embedding for item in response.data], dtype=float)


def get_embedding_provider(settings: Settings | None = None) -> EmbeddingProvider:
    settings = settings or get_settings()
    if settings.embedding_provider.lower() == "openai":
        return OpenAIEmbeddingProvider(settings)
    return SentenceTransformerProvider(settings.local_embedding_model)

