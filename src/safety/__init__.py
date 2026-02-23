"""Medical safety module — disclaimers, red-flag detection, escalation."""

from .disclaimers import DISCLAIMERS, get_disclaimer, get_disclaimer_text
from .red_flags import RedFlagDetector

__all__ = [
    "DISCLAIMERS",
    "get_disclaimer",
    "get_disclaimer_text",
    "RedFlagDetector",
]
