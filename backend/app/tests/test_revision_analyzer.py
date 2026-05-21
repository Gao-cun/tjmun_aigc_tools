from app.services.revision_analyzer import analyze_revision_events


def test_revision_analyzer_detects_paste_and_large_insertions():
    result = analyze_revision_events(
        [
            {"timestamp": 0, "type": "insert", "text": "Opening sentence."},
            {"timestamp": 240, "type": "paste", "text": "x" * 320},
            {"timestamp": 260, "type": "delete", "chars": 80},
        ]
    )

    assert result["pasteBursts"] == 1
    assert result["largeInsertions"] == 1
    assert result["longPauseCount"] == 1
    assert result["deleteRewriteRatio"] > 0

