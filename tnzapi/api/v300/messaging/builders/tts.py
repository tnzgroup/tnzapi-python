import copy
from urllib.parse import quote, urlencode

from tnzapi.core.auth import TNZApiUser
from tnzapi.core.http_client import HttpClient
from tnzapi.core.response_parser import parse_response
from tnzapi.core.model_proxy import ModelRequestMixin, require_id
from tnzapi.core.legacy_kwargs import accept_legacy_kwargs
from tnzapi.core.destination import normalize_destination
from tnzapi.api.v300.messaging.models.requests.tts_request import TTSRequest
from tnzapi.api.v300.messaging.models.responses.tts_response import TTSResponse
from tnzapi.api.v300.messaging.models.responses.tts_status import TTSStatus
from tnzapi.api.v300.messaging.models.responses.tts_action_result import TTSActionResult


class TTS(ModelRequestMixin):

    _request_model_cls = TTSRequest

    def __init__(self, user: TNZApiUser):
        self.user = user
        self.http = HttpClient(user)
        self._reset()

    @accept_legacy_kwargs({"contact_id": "ContactID", "group_id": "GroupID"})
    def AddDestination(self, Destination=None, *, ContactID=None, GroupID=None):

        if ContactID is not None:
            self._data.Destinations.append({"ContactID": ContactID})
        elif GroupID is not None:
            self._data.Destinations.append({"GroupID": GroupID})
        elif isinstance(Destination, list):
            raise TypeError("AddDestination() does not accept a list - use AddDestinations([...]) instead.")
        else:
            normalized = normalize_destination(Destination, primary_key=self._destination_primary_key)
            if normalized is not None:
                self._data.Destinations.append(normalized)

        return self

    def AddDestinations(self, Items):
        if not isinstance(Items, (list, tuple)):
            raise TypeError("AddDestinations() expects a list or tuple of destinations.")
        for item in Items:
            self.AddDestination(item)
        return self

    @accept_legacy_kwargs({
        "tone": "Tone", "play": "Play", "route_number": "RouteNumber", "play_section": "PlaySection",
    })
    def AddKeypad(self, Tone: int, Play: str = None, RouteNumber: str = None, PlaySection: str = None):

        keypad = {"Tone": Tone}
        if Play is not None:
            keypad["Play"] = Play
        if RouteNumber is not None:
            keypad["RouteNumber"] = RouteNumber
        if PlaySection is not None:
            keypad["PlaySection"] = PlaySection

        self._data.Keypads.append(keypad)
        return self

    def AddKeypads(self, Items):
        if not isinstance(Items, (list, tuple)):
            raise TypeError("AddKeypads() expects a list or tuple of keypad dicts.")
        for item in Items:
            self.AddKeypad(**item)
        return self

    def SendMessage(self, model=None, **kwargs):

        if model is not None:
            if isinstance(model, TTSRequest):
                self._data = copy.deepcopy(model)
            elif isinstance(model, dict):
                invalid = self._first_invalid_field(model)
                if invalid:
                    self._reset()
                    return TTSResponse(Result="Failed", ErrorMessage=[f"Unknown argument: {invalid}"])
                self._reset()
                self._apply_fields(model)
            else:
                self._reset()
                return TTSResponse(Result="Failed", ErrorMessage=[f"Invalid model type: {type(model).__name__}"])

        invalid = self._first_invalid_field(kwargs)
        if invalid:
            self._reset()
            return TTSResponse(Result="Failed", ErrorMessage=[f"Unknown argument: {invalid}"])

        self._apply_fields(kwargs)

        missing_destination = self._missing_destination_error(TTSResponse)
        if missing_destination:
            self._reset()
            return missing_destination

        if not (self._data.MessageToPeople or self._data.TemplateID):
            self._reset()
            return TTSResponse(Result="Failed", ErrorMessage=["Missing required field: MessageToPeople or TemplateID"])

        try:
            response = self.http.post("/tts", self._build_request_body())
            result = parse_response(response, TTSResponse)
        finally:
            self._reset()

        return result

    @accept_legacy_kwargs({"message_id": "MessageID", "records_per_page": "RecordsPerPage", "page": "Page"})
    def Status(self, MessageID: str, RecordsPerPage: int = 20, Page: int = 1):

        MessageID = require_id(MessageID, "MessageID")
        query = {"recordsPerPage": RecordsPerPage, "page": Page}
        path = f"/tts/{quote(str(MessageID), safe='')}?{urlencode(query)}"
        response = self.http.get(path)
        return parse_response(response, TTSStatus)

    @accept_legacy_kwargs({"message_id": "MessageID", "send_time": "SendTime"})
    def Reschedule(self, MessageID: str, SendTime: str):

        MessageID = require_id(MessageID, "MessageID")
        response = self.http.patch(f"/tts/{quote(str(MessageID), safe='')}/reschedule", {"SendTime": SendTime})
        return parse_response(response, TTSActionResult)

    @accept_legacy_kwargs({"message_id": "MessageID"})
    def Abort(self, MessageID: str):

        MessageID = require_id(MessageID, "MessageID")
        response = self.http.patch(f"/tts/{quote(str(MessageID), safe='')}/abort", {})
        return parse_response(response, TTSActionResult)

    @accept_legacy_kwargs({"message_id": "MessageID", "send_time": "SendTime"})
    def Resubmit(self, MessageID: str, SendTime: str):

        MessageID = require_id(MessageID, "MessageID")
        response = self.http.patch(f"/tts/{quote(str(MessageID), safe='')}/resubmit", {"SendTime": SendTime})
        return parse_response(response, TTSActionResult)

    @accept_legacy_kwargs({"message_id": "MessageID", "number_of_operators": "NumberOfOperators"})
    def Pacing(self, MessageID: str, NumberOfOperators: int):

        MessageID = require_id(MessageID, "MessageID")
        response = self.http.patch(
            f"/tts/{quote(str(MessageID), safe='')}/pacing", {"NumberOfOperators": NumberOfOperators}
        )
        return parse_response(response, TTSActionResult)