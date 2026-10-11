"""Exception hierarchy. Everything user-facing derives from TrailbirdError."""
from __future__ import annotations


class TrailbirdError(Exception):
    """Base class: the message is always safe and useful to show to an end user."""


class AudioError(TrailbirdError, ValueError):
    """Missing, unsupported, unreadable, empty or too-long audio."""


class ModelError(TrailbirdError, RuntimeError):
    """Model missing, failed to load, or failed during inference."""


class NetworkBlockedError(TrailbirdError, RuntimeError):
    """Raised when code tries to reach a non-loopback host while offline mode is enforced."""
