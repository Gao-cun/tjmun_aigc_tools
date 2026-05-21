from app.services.risk_engine import analyze_consistency


def _features(avg: float, lexical: float, passive: float = 0.1):
    return {
        "average_sentence_length": avg,
        "long_sentence_ratio": 0.1,
        "passive_voice_ratio": passive,
        "lexical_diversity": lexical,
        "connective_frequency": {"however": 0.01},
        "punctuation_style": {";": 0.01},
    }


def test_risk_engine_returns_low_for_near_baseline():
    result = analyze_consistency(
        [_features(18, 0.48), _features(19, 0.5), _features(17, 0.47)],
        [[1, 0, 0], [0.98, 0.02, 0], [0.99, 0.01, 0]],
        _features(18.5, 0.49),
        [0.99, 0.01, 0],
    )

    assert result["riskLevel"] == "Low Consistency Risk"
    assert "semanticDrift" in result


def test_risk_engine_flags_large_deviation():
    result = analyze_consistency(
        [_features(18, 0.48), _features(19, 0.5), _features(17, 0.47)],
        [[1, 0, 0], [0.98, 0.02, 0], [0.99, 0.01, 0]],
        _features(45, 0.9, 0.7),
        [0, 1, 0],
    )

    assert result["riskLevel"] in {"Medium Consistency Risk", "High Consistency Risk"}
    assert result["significantFeatures"]

