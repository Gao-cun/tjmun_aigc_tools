from __future__ import annotations

import numpy as np


def cosine_distance(vector: np.ndarray, centroid: np.ndarray) -> float:
    denom = (np.linalg.norm(vector) * np.linalg.norm(centroid)) or 1.0
    return float(1.0 - np.dot(vector, centroid) / denom)


def mahalanobis_distance(vector: np.ndarray, matrix: np.ndarray) -> float:
    if matrix.shape[0] < 2:
        return 0.0
    centroid = matrix.mean(axis=0)
    covariance = np.cov(matrix, rowvar=False)
    # 协方差矩阵容易奇异，使用 pinv 并加微小岭项保证稳定。
    covariance = covariance + np.eye(covariance.shape[0]) * 1e-6
    inverse = np.linalg.pinv(covariance)
    diff = vector - centroid
    return float(np.sqrt(max(diff.T @ inverse @ diff, 0.0)))


def build_embedding_stats(embeddings: list[list[float]], labels: list[str] | None = None) -> dict:
    matrix = np.asarray(embeddings, dtype=float)
    if matrix.size == 0:
        raise ValueError("No embeddings available for this delegate.")
    centroid = matrix.mean(axis=0)
    distances = [cosine_distance(row, centroid) for row in matrix]
    labels = labels or [f"History {index + 1}" for index in range(len(embeddings))]
    return {
        "document_count": int(matrix.shape[0]),
        "centroid": centroid.tolist(),
        "normal_range": {
            "cosine_mean": float(np.mean(distances)),
            "cosine_std": float(np.std(distances)),
            "cosine_upper": float(np.mean(distances) + 2 * np.std(distances)),
        },
        "cluster_points": [
            {
                "label": label,
                "x": float(row[0]) if row.size else 0.0,
                "y": float(row[1]) if row.size > 1 else 0.0,
                "kind": "history",
            }
            for label, row in zip(labels, matrix, strict=False)
        ],
    }

