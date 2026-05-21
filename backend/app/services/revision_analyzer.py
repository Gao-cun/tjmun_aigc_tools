from __future__ import annotations

from datetime import datetime


def _timestamp(value) -> float | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00")).timestamp()
    except ValueError:
        return None


def analyze_revision_events(events: list[dict]) -> dict:
    """分析写作过程异常指标，只输出行为信号，不做作者归因。"""
    normalized = sorted(events, key=lambda item: _timestamp(item.get("timestamp")) or 0)
    paste_bursts = 0
    large_insertions = 0
    deletes = 0
    inserted_chars = 0
    deleted_chars = 0
    pauses: list[float] = []
    previous_ts = None

    for event in normalized:
        event_type = str(event.get("type") or event.get("event") or "").lower()
        text = str(event.get("text") or event.get("value") or "")
        chars = int(event.get("chars") or len(text))
        current_ts = _timestamp(event.get("timestamp"))
        if previous_ts is not None and current_ts is not None:
            pauses.append(max(current_ts - previous_ts, 0.0))
        previous_ts = current_ts

        if "paste" in event_type or bool(event.get("pasted")):
            paste_bursts += 1
        if "insert" in event_type or "paste" in event_type:
            inserted_chars += chars
            if chars >= 240:
                large_insertions += 1
        if "delete" in event_type:
            deletes += 1
            deleted_chars += chars

    long_pauses = [pause for pause in pauses if pause >= 180]
    rewrite_ratio = deleted_chars / max(inserted_chars, 1)
    anomaly_score = min(1.0, paste_bursts * 0.18 + large_insertions * 0.22 + len(long_pauses) * 0.08 + rewrite_ratio * 0.35)

    if anomaly_score >= 0.65:
        level = "Elevated Revision Anomaly"
    elif anomaly_score >= 0.35:
        level = "Moderate Revision Anomaly"
    else:
        level = "Low Revision Anomaly"

    return {
        "level": level,
        "anomalyScore": round(anomaly_score, 4),
        "pasteBursts": paste_bursts,
        "largeInsertions": large_insertions,
        "longPauseCount": len(long_pauses),
        "medianPauseSeconds": round(sorted(pauses)[len(pauses) // 2], 2) if pauses else 0,
        "deleteRewriteRatio": round(rewrite_ratio, 4),
        "indicators": [
            {"name": "Paste behavior", "value": paste_bursts},
            {"name": "Large one-shot input", "value": large_insertions},
            {"name": "Editing pauses", "value": len(long_pauses)},
            {"name": "Delete/rewrite ratio", "value": round(rewrite_ratio, 4)},
        ],
    }

