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
    def __init__(self, api_key: str | None, model: str):
        if not api_key:
            raise ValueError("OPENAI_API_KEY is required when EMBEDDING_PROVIDER=openai")
        from openai import OpenAI

        self.client = OpenAI(api_key=api_key)
        self.model = model

    def embed_texts(self, texts: list[str]) -> np.ndarray:
        try:
            response = self.client.embeddings.create(model=self.model, input=texts)
        except Exception as exc:
            message = str(exc)
            if "insufficient_quota" in message or "exceeded your current quota" in message:
                raise ValueError("OpenAI Embedding 调用失败：当前 API key 额度不足或账单不可用。请更换可用 key，或在前端切换为 Hash 本地快速模式 / HuggingFace 本地模型。") from exc
            if "invalid_api_key" in message or "Incorrect API key" in message:
                raise ValueError("OpenAI Embedding 调用失败：API key 无效。请检查前端填写的 key。") from exc
            raise ValueError(f"OpenAI Embedding 调用失败：{message}") from exc
        return np.asarray([item.embedding for item in response.data], dtype=float)


def get_embedding_provider(settings: Settings | None = None, overrides: dict | None = None) -> EmbeddingProvider:
    """按环境变量或本次请求参数选择 embedding provider。

    overrides 只用于本次调用，不写入数据库或配置文件，避免前端传入的 API key 落盘。
    """
    settings = settings or get_settings()
    overrides = overrides or {}
    provider_name = str(overrides.get("embedding_provider") or settings.embedding_provider).lower()
    local_model = str(overrides.get("local_embedding_model") or settings.local_embedding_model)
    openai_model = str(overrides.get("openai_embedding_model") or settings.openai_embedding_model)
    openai_api_key = overrides.get("openai_api_key") or settings.openai_api_key

    if provider_name == "hash":
        return HashEmbeddingProvider()
    if provider_name == "openai":
        return OpenAIEmbeddingProvider(openai_api_key, openai_model)
    return SentenceTransformerProvider(local_model)
