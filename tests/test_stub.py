"""Stub tests for the achievments plugin."""
from __future__ import annotations


def test_plugin_imports() -> None:
    from achievments.plugin import AchievmentsPlugin
    assert AchievmentsPlugin.name == "achievments"
    assert AchievmentsPlugin.version == "0.2.0"


def test_plugin_instantiation() -> None:
    from achievments.plugin import AchievmentsPlugin
    plugin = AchievmentsPlugin()
    assert plugin is not None
    assert plugin.name == "achievments"


def test_settings_schema() -> None:
    from achievments.plugin import AchievmentsPlugin
    plugin = AchievmentsPlugin()
    schema = plugin.settings_schema()
    assert "achievments.enabled" in schema
    assert "achievments.notify_on_new" in schema
    assert schema["achievments.enabled"] is True


def test_acknowledgment_screen_returns_screen() -> None:
    """acknowledgment_screen() returns a Screen instance for valid data."""
    from achievments.plugin import AchievmentsPlugin
    plugin = AchievmentsPlugin()
    result = plugin.acknowledgment_screen({"differential": "12.5", "date": "2026-01-01", "index": 1}, has_details=False)
    from textual.screen import Screen
    assert isinstance(result, Screen)


def test_acknowledgment_screen_with_details() -> None:
    """acknowledgment_screen() returns a Screen with details flag."""
    from achievments.plugin import AchievmentsPlugin
    plugin = AchievmentsPlugin()
    round_data = {
        "differential": "12.5",
        "date": "2026-01-01",
        "index": 1,
        "holes": {"1": {"gross": "4", "fairway": "H", "gir": "H", "putts": "2", "penalties": "0"}},
    }
    result = plugin.acknowledgment_screen(round_data, has_details=True)
    from textual.screen import Screen
    assert isinstance(result, Screen)
