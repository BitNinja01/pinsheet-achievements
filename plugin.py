"""AchievementsPlugin — PinSheet plugin adapter for achievement/badge tracking."""
from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from textual.screen import Screen

_plugins_parent = str(Path(__file__).parent.parent)
if _plugins_parent not in sys.path:
    sys.path.insert(0, _plugins_parent)

from plugin import PinSheetPlugin

_log = logging.getLogger("achievements")


class AchievementsPlugin(PinSheetPlugin):
    """Tracks and surfaces achievements and personal milestones from round data."""

    name = "achievements"
    version = "0.2.0"

    def screens(self) -> list[type["Screen"]]:
        return []

    def bindings(self) -> list[tuple[str, str, str, str]]:
        return [
            ("DashboardScreen", "b", "app.push_screen('AchievementsScreen')", "Achievements"),
        ]

    def settings_schema(self) -> dict:
        return {
            "achievements.enabled": True,
            "achievements.notify_on_new": True,
        }

    def on_round_saved(self, round_data: dict) -> None:
        _log.info("achievements: round saved, checking achievements")

    def acknowledgment_screen(self, round_data: dict, has_details: bool) -> "Screen | None":
        from .ack_screen import RoundAcknowledgmentScreen
        _log.info("achievements: providing acknowledgment screen")
        return RoundAcknowledgmentScreen(round_data, has_details)
