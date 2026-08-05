import copy
from urllib.parse import quote, urlencode

from tnzapi.core.auth import TNZApiUser
from tnzapi.core.http_client import HttpClient
from tnzapi.core.response_parser import parse_response
from tnzapi.core.model_proxy import ModelRequestMixin, require_id
from tnzapi.core.legacy_kwargs import accept_legacy_kwargs
from tnzapi.core.destination import normalize_destination
from tnzapi.core.file_attachment import FileAttachment, normalize_attachment
from tnzapi.api.v300.messaging.models.requests.email_request import EmailRequest
from tnzapi.api.v300.messaging.models.responses.email_response import EmailResponse
from tnzapi.api.v300.messaging.models.responses.email_status import EmailStatus
from tnzapi.api.v300.messaging.models.responses.email_action_result import EmailActionResult


class Email(ModelRequestMixin):

    _request_model_cls = EmailRequest
    _destination_primary_key = "EmailAddress"

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

    @accept_legacy_kwargs({"name": "Name", "data": "Data"})
    def AddAttachment(self, Name=None, Data=None):

        if isinstance(Name, (FileAttachment, dict)):
            item = normalize_attachment(Name)
        elif Data is None and isinstance(Name, str):
            # Single-argument shorthand - Name doubles as a file path, mirroring
            # Files=["path"]'s bare-string support. Only reachable this way
            # because Data now defaults to None (previously both arguments were
            # required, so a 1-arg call was a TypeError before this change -
            # purely additive, not a behavior change for any previously-legal
            # call).
            item = normalize_attachment(Name)
        else:
            item = normalize_attachment({"Name": Name, "Data": Data})

        if item is not None:
            self._data.Files.append(item)
        return self

    def AddAttachments(self, Items):
        if not isinstance(Items, (list, tuple)):
            raise TypeError("AddAttachments() expects a list or tuple of attachments.")
        for item in Items:
            self.AddAttachment(item)
        return self

    def SendMessage(self, model=None, **kwargs):

        if model is not None:
            if isinstance(model, EmailRequest):
                self._data = copy.deepcopy(model)
            elif isinstance(model, dict):
                invalid = self._first_invalid_field(model)
                if invalid:
                    self._reset()
                    return EmailResponse(Result="Failed", ErrorMessage=[f"Unknown argument: {invalid}"])
                self._reset()
                self._apply_fields(model)
            else:
                self._reset()
                return EmailResponse(Result="Failed", ErrorMessage=[f"Invalid model type: {type(model).__name__}"])

        invalid = self._first_invalid_field(kwargs)
        if invalid:
            self._reset()
            return EmailResponse(Result="Failed", ErrorMessage=[f"Unknown argument: {invalid}"])

        self._apply_fields(kwargs)

        missing_destination = self._missing_destination_error(EmailResponse)
        if missing_destination:
            self._reset()
            return missing_destination

        if not (self._data.MessagePlain or self._data.MessageHTML or self._data.TemplateID):
            self._reset()
            return EmailResponse(Result="Failed", ErrorMessage=["Missing required field: MessagePlain, MessageHTML, or TemplateID"])

        try:
            response = self.http.post("/email", self._build_request_body())
            result = parse_response(response, EmailResponse)
        finally:
            self._reset()

        return result

    @accept_legacy_kwargs({"message_id": "MessageID", "records_per_page": "RecordsPerPage", "page": "Page"})
    def Status(self, MessageID: str, RecordsPerPage: int = 20, Page: int = 1):

        MessageID = require_id(MessageID, "MessageID")
        query = {"recordsPerPage": RecordsPerPage, "page": Page}
        path = f"/email/{quote(str(MessageID), safe='')}?{urlencode(query)}"
        response = self.http.get(path)
        return parse_response(response, EmailStatus)

    @accept_legacy_kwargs({"message_id": "MessageID", "send_time": "SendTime"})
    def Reschedule(self, MessageID: str, SendTime: str):

        MessageID = require_id(MessageID, "MessageID")
        response = self.http.patch(f"/email/{quote(str(MessageID), safe='')}/reschedule", {"SendTime": SendTime})
        return parse_response(response, EmailActionResult)

    @accept_legacy_kwargs({"message_id": "MessageID"})
    def Abort(self, MessageID: str):

        MessageID = require_id(MessageID, "MessageID")
        response = self.http.patch(f"/email/{quote(str(MessageID), safe='')}/abort", {})
        return parse_response(response, EmailActionResult)

    @accept_legacy_kwargs({"message_id": "MessageID", "send_time": "SendTime"})
    def Resubmit(self, MessageID: str, SendTime: str):

        MessageID = require_id(MessageID, "MessageID")
        response = self.http.patch(f"/email/{quote(str(MessageID), safe='')}/resubmit", {"SendTime": SendTime})
        return parse_response(response, EmailActionResult)