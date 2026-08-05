"""SendMode - typed alternative to the plain "Test"/"Live" string literal
accepted by every messaging channel's Mode field (all except Workflow,
which has no Mode field).

A str-subclass Enum: SendMode.Test == "Test" and isinstance(SendMode.Test, str)
are both True, so it serializes identically to the plain string through
dataclasses.asdict()/json.dumps() with no other code changes anywhere in
tnzapi/ - Mode="Test" and Mode=SendMode.Test are fully interchangeable.
"""

from enum import Enum


class SendMode(str, Enum):
    Test = "Test"
    Live = "Live"
