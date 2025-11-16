import json
from offset_updater.offset_analyzer import OffsetAnalyzer


def test_analyze_no_changes():
    """If parsed dump contains same offsets, no changes should be returned."""
    parsed_dump = {
        "get_PlayerHealth": "0x12345",
        "set_PlayerSpeed": "0x99999"
    }

    analyzer = OffsetAnalyzer(parsed_dump)

    existing_code_offsets = {
        "get_PlayerHealth": "0x12345",
        "set_PlayerSpeed": "0x99999"
    }

    changes = analyzer.analyze(existing_code_offsets)

    assert changes == {}  # no updates needed


def test_analyze_with_changes():
    """If some offsets changed, only changed entries are returned."""
    parsed_dump = {
        "get_PlayerHealth": "0x12345",
        "set_PlayerSpeed": "0xABCD0"
    }

    analyzer = OffsetAnalyzer(parsed_dump)

    existing_code_offsets = {
        "get_PlayerHealth": "0x11111",
        "set_PlayerSpeed": "0xABCD0"
    }

    changes = analyzer.analyze(existing_code_offsets)

    assert len(changes) == 1
    assert changes["get_PlayerHealth"] == ("0x11111", "0x12345")


def test_analyze_new_entries():
    """If dump contains new functions not present in code, they should be added."""
    parsed_dump = {
        "NewFunction": "0x88888"
    }

    analyzer = OffsetAnalyzer(parsed_dump)

    existing_code_offsets = {}

    changes = analyzer.analyze(existing_code_offsets)

    assert len(changes) == 1
    assert changes["NewFunction"] == (None, "0x88888")
