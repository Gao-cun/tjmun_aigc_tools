from app.services.stylometry import extract_stylometry, flatten_features


def test_stylometry_outputs_stable_numeric_features():
    text = "We strongly support this draft resolution. However, the committee must consider implementation."
    features = extract_stylometry(text)
    flat = flatten_features(features)

    assert features["sentence_count"] >= 1
    assert features["average_sentence_length"] > 0
    assert "lexical_diversity" in flat
    assert "connective_frequency.however" in flat


def test_stylometry_detects_punctuation_style():
    features = extract_stylometry("Delegates, colleagues, and observers: we must act; we must coordinate.")

    assert features["punctuation_style"][","] > 0
    assert features["punctuation_style"][";"] > 0

