from offset_updater.reporter import Reporter


def test_report_summary_empty():
    """Reporter should generate message saying no changes when list is empty."""
    reporter = Reporter()
    summary = reporter.summary({})

    assert "No changes detected" in summary


def test_report_summary_with_changes():
    """Reporter should describe each change clearly."""
    changes = {
        "FunctionX": ("0x11111", "0x22222"),
        "FunctionY": (None, "0xAAAAA")
    }

    reporter = Reporter()
    summary = reporter.summary(changes)

    # Both functions should appear
    assert "FunctionX" in summary
    assert "0x11111 → 0x22222" in summary
    assert "FunctionY" in summary
    assert "NEW → 0xAAAAA" in summary
