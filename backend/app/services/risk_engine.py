from __future__ import annotations

import numpy as np

from app.services.embedding_stats import cosine_distance, mahalanobis_distance
from app.services.stylometry import flatten_features


RADAR_FEATURES = {
    "Sentence Length": "average_sentence_length",
    "Long Sentences": "long_sentence_ratio",
    "Passive Voice": "passive_voice_ratio",
    "Lexical Diversity": "lexical_diversity",
    "Connectives": "connective_frequency.however",
    "Punctuation": "punctuation_style.;",
}


def _feature_matrix(history_features: list[dict]) -> tuple[list[str], np.ndarray]:
    flattened = [flatten_features(item) for item in history_features]
    keys = sorted({key for item in flattened for key in item})
    matrix = np.asarray([[item.get(key, 0.0) for key in keys] for item in flattened], dtype=float)
    return keys, matrix


def _z_scores(history_features: list[dict], new_features: dict) -> dict[str, float]:
    keys, matrix = _feature_matrix(history_features)
    new_flat = flatten_features(new_features)
    if matrix.size == 0:
        return {}
    means = matrix.mean(axis=0)
    stds = matrix.std(axis=0)
    stds = np.where(stds < 1e-6, 1.0, stds)
    values = np.asarray([new_flat.get(key, 0.0) for key in keys], dtype=float)
    return {key: float(abs(score)) for key, score in zip(keys, (values - means) / stds, strict=False)}


def _radar(history_features: list[dict], new_features: dict) -> list[dict]:
    keys, matrix = _feature_matrix(history_features)
    index = {key: idx for idx, key in enumerate(keys)}
    new_flat = flatten_features(new_features)
    rows = []
    for label, feature_key in RADAR_FEATURES.items():
        if feature_key not in index:
            baseline = 0.0
            current = new_flat.get(feature_key, 0.0)
        else:
            baseline = float(matrix[:, index[feature_key]].mean())
            current = float(new_flat.get(feature_key, 0.0))
        scale = max(abs(baseline), abs(current), 1e-6)
        rows.append({"feature": label, "baseline": baseline / scale, "current": current / scale, "rawBaseline": baseline, "rawCurrent": current})
    return rows


def analyze_consistency(history_features: list[dict], history_embeddings: list[list[float]], new_features: dict, new_embedding: list[float]) -> dict:
    if len(history_features) < 2 or len(history_embeddings) < 2:
        raise ValueError("At least two processed history documents are required to establish a style baseline.")

    history_matrix = np.asarray(history_embeddings, dtype=float)
    new_vector = np.asarray(new_embedding, dtype=float)
    centroid = history_matrix.mean(axis=0)
    cosine = cosine_distance(new_vector, centroid)
    mahalanobis = mahalanobis_distance(new_vector, history_matrix)
    z_scores = _z_scores(history_features, new_features)
    significant = sorted(z_scores.items(), key=lambda item: item[1], reverse=True)[:8]
    stylometric_shift = float(np.mean([score for _, score in significant[:5]]) if significant else 0.0)

    semantic_score = min(cosine / 0.45, 2.0)
    style_score = min(stylometric_shift / 3.0, 2.0)
    distance_score = min(mahalanobis / 6.0, 2.0)
    composite = 0.45 * semantic_score + 0.4 * style_score + 0.15 * distance_score

    if composite >= 1.15:
        risk_level = "High Consistency Risk"
    elif composite >= 0.65:
        risk_level = "Medium Consistency Risk"
    else:
        risk_level = "Low Consistency Risk"

    return {
        "riskLevel": risk_level,
        "historicalDeviation": round(composite, 4),
        "stylometricShift": round(stylometric_shift, 4),
        "semanticDrift": round(cosine, 4),
        "embeddingDistance": {"cosine": round(cosine, 4), "mahalanobis": round(mahalanobis, 4)},
        "significantFeatures": [{"feature": key, "zScore": round(score, 3)} for key, score in significant],
        "radar": _radar(history_features, new_features),
        "featureDrift": [{"feature": key, "zScore": round(score, 3)} for key, score in significant],
        "interpretation": "This result describes writing consistency deviation against the delegate's historical baseline.",
    }

