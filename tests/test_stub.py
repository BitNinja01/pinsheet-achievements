"""Stub tests for the achievments plugin."""
from __future__ import annotations


def test_plugin_imports() -> None:
    from achievments.plugin import AchievmentsPlugin
    assert AchievmentsPlugin.name == "achievments"
    assert AchievmentsPlugin.version == "0.1.0"


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
