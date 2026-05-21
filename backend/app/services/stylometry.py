from __future__ import annotations

import math
import re
from collections import Counter

try:
    import spacy
except Exception:  # pragma: no cover - 运行环境缺依赖时走轻量兜底
    spacy = None


FUNCTION_WORDS = {
    "the",
    "a",
    "an",
    "and",
    "or",
    "but",
    "if",
    "while",
    "of",
    "to",
    "in",
    "for",
    "on",
    "with",
    "by",
    "as",
    "that",
    "which",
    "this",
    "these",
    "those",
    "we",
    "they",
    "it",
    "is",
    "are",
    "was",
    "were",
}
CONNECTIVES = {
    "therefore",
    "however",
    "moreover",
    "furthermore",
    "nevertheless",
    "consequently",
    "whereas",
    "although",
    "because",
    "since",
    "unless",
    "despite",
    "hence",
    "thus",
}
PUNCTUATION = [",", ".", ";", ":", "?", "!", "-", "(", ")", '"', "'"]

_NLP = None
_NLP_ATTEMPTED = False


def _get_nlp():
    """spaCy 模型缺失时不阻塞服务，降级到正则分词。"""
    global _NLP, _NLP_ATTEMPTED
    if _NLP_ATTEMPTED:
        return _NLP
    _NLP_ATTEMPTED = True
    if spacy is None:
        return None
    try:
        _NLP = spacy.load("en_core_web_sm")
    except Exception:
        _NLP = None
    return _NLP


def _fallback_sentences(text: str) -> list[str]:
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]


def _fallback_tokens(text: str) -> list[str]:
    return re.findall(r"[A-Za-z']+", text.lower())


def _fallback_pos_distribution(tokens: list[str]) -> dict[str, float]:
    counts = Counter()
    for token in tokens:
        if token.endswith(("ing", "ed")):
            counts["VERB"] += 1
        elif token.endswith(("ly",)):
            counts["ADV"] += 1
        elif token.endswith(("ive", "al", "ous", "ic")):
            counts["ADJ"] += 1
        else:
            counts["NOUN"] += 1
    total = max(sum(counts.values()), 1)
    return {key: value / total for key, value in counts.items()}


def _passive_ratio_fallback(sentences: list[str]) -> float:
    passive_hits = 0
    pattern = re.compile(r"\b(is|are|was|were|be|been|being)\s+\w+ed\b", re.IGNORECASE)
    for sentence in sentences:
        if pattern.search(sentence):
            passive_hits += 1
    return passive_hits / max(len(sentences), 1)


def extract_stylometry(text: str) -> dict:
    """提取稳定 JSON 特征，供画像、z-score 和图表复用。"""
    cleaned = " ".join(text.split())
    nlp = _get_nlp()
    if nlp:
        doc = nlp(cleaned)
        sentences = [sent.text.strip() for sent in doc.sents if sent.text.strip()]
        tokens = [token.text.lower() for token in doc if token.is_alpha]
        pos_counts = Counter(token.pos_ for token in doc if token.is_alpha)
        passive_hits = sum(1 for token in doc if token.dep_ in {"nsubjpass", "auxpass"})
        passive_ratio = passive_hits / max(len(sentences), 1)
        pos_distribution = {key: value / max(sum(pos_counts.values()), 1) for key, value in pos_counts.items()}
    else:
        sentences = _fallback_sentences(cleaned)
        tokens = _fallback_tokens(cleaned)
        passive_ratio = _passive_ratio_fallback(sentences)
        pos_distribution = _fallback_pos_distribution(tokens)

    sentence_lengths = [len(_fallback_tokens(sentence)) for sentence in sentences] or [0]
    token_count = max(len(tokens), 1)
    word_counts = Counter(tokens)
    punctuation_counts = {mark: cleaned.count(mark) for mark in PUNCTUATION}

    function_word_freq = {word: word_counts[word] / token_count for word in sorted(FUNCTION_WORDS)}
    connective_freq = {word: word_counts[word] / token_count for word in sorted(CONNECTIVES)}
    punctuation_style = {mark: count / token_count for mark, count in punctuation_counts.items()}

    return {
        "average_sentence_length": float(sum(sentence_lengths) / max(len(sentence_lengths), 1)),
        "long_sentence_ratio": float(sum(1 for length in sentence_lengths if length >= 30) / max(len(sentence_lengths), 1)),
        "function_word_frequency": function_word_freq,
        "punctuation_style": punctuation_style,
        "passive_voice_ratio": float(passive_ratio),
        "connective_frequency": connective_freq,
        "pos_distribution": pos_distribution,
        "lexical_diversity": float(len(set(tokens)) / token_count),
        "perplexity": None,
        "token_count": len(tokens),
        "sentence_count": len(sentences),
        "readability_proxy": float(math.log1p(token_count) / max(sum(sentence_lengths) / max(len(sentence_lengths), 1), 1)),
    }


def flatten_features(features: dict) -> dict[str, float]:
    """把嵌套特征压平成数值向量，方便统计和前端展示。"""
    flat: dict[str, float] = {}
    for key, value in features.items():
        if isinstance(value, dict):
            for child_key, child_value in value.items():
                if isinstance(child_value, (int, float)) and child_value is not None:
                    safe_key = child_key.replace(".", "_").replace(" ", "_")
                    flat[f"{key}.{safe_key}"] = float(child_value)
        elif isinstance(value, (int, float)) and value is not None and not isinstance(value, bool):
            flat[key] = float(value)
    return flat
