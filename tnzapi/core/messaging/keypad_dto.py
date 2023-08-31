import json
from dataclasses import dataclass, field

from tnzapi.helpers.custom_json_encoder import CustomJSONEncoder
from tnzapi.helpers.functions import Functions


@dataclass
class KeypadDTO:
    
    Tone: str = None
    Play: str = None
    PlayFile: str = None
    RouteNumber: str = None
    PlaySection: str = None

    def __iter__(self):
        yield from {
            "Tone": self.Tone,
            "Play": self.Play,
            "PlayFile": self.PlayFile,
            "RouteNumber": self.RouteNumber,
            "PlaySection": self.PlaySection,
        }.items()

    def __repr__(self):
        return Functions.__pretty_class__(self, self)
    
    def __str__(self):
        return json.dumps(dict(self), cls=CustomJSONEncoder, ensure_ascii=False)