import copy
from urllib.parse import quote, urlencode

from tnzapi.core.auth import TNZApiUser
from tnzapi.core.http_client import HttpClient
from tnzapi.core.response_parser import parse_response
from tnzapi.core.model_proxy import ModelRequestMixin, filter_model_fields, project_model, require_id, resolve_id
from tnzapi.core.legacy_kwargs import accept_legacy_kwargs
from tnzapi.api.v300.optout.models.requests.optout_request import OptOutRequest
from tnzapi.api.v300.optout.models.responses.optout_response import OptOutResponse
from tnzapi.api.v300.optout.models.responses.optout_list_response import OptOutListResponse
from tnzapi.api.v300.optout.models.requests.optout_batch_request import OptOutBatchRequest

VALID_DEST_TYPES = {"fax", "text", "sms", "email", "speech", "voice"}
DEST_TYPE_ERROR_MESSAGE = "Unsupported DestType - Supported DestType: Fax / Text / SMS / Email / Speech / Voice."


def _validate_dest_type_string(dest_type: str):
    if not dest_type:
        return "Missing required field: DestType"

    for part in dest_type.split(","):
        if part.strip().lower() not in VALID_DEST_TYPES:
            return DEST_TYPE_ERROR_MESSAGE

    return None


def _normalize_dest_type_string(dest_type: str) -> str:
    # Validation tolerates whitespace around each comma-separated part (e.g.
    # "SMS, Voice"), but the value actually sent to the API must not carry that
    # whitespace through - normalize once validation has already passed.
    return ",".join(part.strip() for part in dest_type.split(","))


class OptOut(ModelRequestMixin):

    _request_model_cls = OptOutRequest

    def __init__(self, user: TNZApiUser):
        self.user = user
        self.http = HttpClient(user)
        self._reset()

    def Create(self, model=None, **kwargs):

        if model is not None:
            if isinstance(model, OptOutRequest):
                self._data = copy.deepcopy(model)
            elif isinstance(model, OptOutResponse):
                self._data = project_model(model, OptOutRequest)
            elif isinstance(model, dict):
                invalid = self._first_invalid_field(model)
                if invalid:
                    self._reset()
                    return OptOutResponse(Result="Failed", ErrorMessage=[f"Unknown argument: {invalid}"])
                self._reset()
                self._apply_fields(model)
            else:
                self._reset()
                return OptOutResponse(Result="Failed", ErrorMessage=[f"Invalid model type: {type(model).__name__}"])

        invalid = self._first_invalid_field(kwargs)
        if invalid:
            self._reset()
            return OptOutResponse(Result="Failed", ErrorMessage=[f"Unknown argument: {invalid}"])

        self._apply_fields(kwargs)

        dest_type_error = _validate_dest_type_string(self._data.DestType)
        if dest_type_error:
            self._reset()
            return OptOutResponse(Result="Failed", ErrorMessage=[dest_type_error])

        self._data.DestType = _normalize_dest_type_string(self._data.DestType)

        if not self._data.Destination and not self._data.ContactID:
            self._reset()
            return OptOutResponse(Result="Failed", ErrorMessage=["Missing required field: Destination or ContactID"])

        try:
            response = self.http.post("/optout", self._build_request_body())
            result = parse_response(response, OptOutResponse)
        finally:
            self._reset()

        return result

    @accept_legacy_kwargs({"opt_out_id": "OptOutID"})
    def Update(self, OptOutID, model=None, **kwargs):

        OptOutID = resolve_id(OptOutID, OptOutResponse, "ID")

        if model is not None:
            if isinstance(model, OptOutRequest):
                self._data = copy.deepcopy(model)
            elif isinstance(model, OptOutResponse):
                self._data = project_model(model, OptOutRequest)
            elif isinstance(model, dict):
                invalid = self._first_invalid_field(model)
                if invalid:
                    self._reset()
                    return OptOutResponse(Result="Failed", ErrorMessage=[f"Unknown argument: {invalid}"])
                self._reset()
                self._apply_fields(model)
            else:
                self._reset()
                return OptOutResponse(Result="Failed", ErrorMessage=[f"Invalid model type: {type(model).__name__}"])

        invalid = self._first_invalid_field(kwargs)
        if invalid:
            self._reset()
            return OptOutResponse(Result="Failed", ErrorMessage=[f"Unknown argument: {invalid}"])

        self._apply_fields(kwargs)

        # Update is a partial PATCH - unlike Create, it does not require
        # Destination/ContactID, and only validates DestType if one was actually
        # supplied in this call (a caller might only be touching Notes).
        if self._data.DestType:
            dest_type_error = _validate_dest_type_string(self._data.DestType)
            if dest_type_error:
                self._reset()
                return OptOutResponse(Result="Failed", ErrorMessage=[dest_type_error])

            self._data.DestType = _normalize_dest_type_string(self._data.DestType)

        try:
            response = self.http.patch(f"/optout/{quote(str(OptOutID), safe='')}", self._build_request_body())
            result = parse_response(response, OptOutResponse)
        finally:
            self._reset()

        return result

    @accept_legacy_kwargs({"opt_out_id": "OptOutID"})
    def Details(self, OptOutID: str):
        OptOutID = require_id(OptOutID, "OptOutID")
        response = self.http.get(f"/optout/{quote(str(OptOutID), safe='')}")
        return parse_response(response, OptOutResponse)

    @accept_legacy_kwargs({"opt_out_id": "OptOutID"})
    def Delete(self, OptOutID):
        OptOutID = resolve_id(OptOutID, OptOutResponse, "ID")
        response = self.http.delete(f"/optout/{quote(str(OptOutID), safe='')}")
        return parse_response(response, OptOutResponse)

    @accept_legacy_kwargs({
        "time_period": "TimePeriod", "dest_type": "DestType", "contact_id": "ContactID",
        "page": "Page", "records_per_page": "RecordsPerPage",
    })
    def List(self, TimePeriod=None, DestType=None, ContactID=None, Page: int = 1, RecordsPerPage: int = 100):

        query = {}
        if TimePeriod is not None:
            query["timePeriod"] = TimePeriod
        if DestType is not None:
            query["destType"] = DestType
        if ContactID is not None:
            query["contactID"] = ContactID
        query["recordsPerPage"] = RecordsPerPage
        query["page"] = Page

        response = self.http.get(f"/optout/list?{urlencode(query)}")
        return parse_response(response, OptOutListResponse)

    @accept_legacy_kwargs({
        "dest_type": "DestType", "destination": "Destination", "destinations": "Destinations",
        "contact_id": "ContactID", "contact_ids": "ContactIDs",
        "sub_account": "SubAccount", "department": "Department",
    })
    def CreateBatch(self, DestType: str, Destination=None, Destinations=None,
                     ContactID=None, ContactIDs=None, SubAccount=None, Department=None):

        dest_type_error = _validate_dest_type_string(DestType)
        if dest_type_error:
            return OptOutResponse(Result="Failed", ErrorMessage=[dest_type_error])

        DestType = _normalize_dest_type_string(DestType)

        has_destination = bool(Destination) or bool(Destinations)
        has_contact = bool(ContactID) or bool(ContactIDs)

        if not has_destination and not has_contact:
            return OptOutResponse(
                Result="Failed",
                ErrorMessage=["Missing required field: Destination, Destinations, ContactID, or ContactIDs"],
            )

        batch = OptOutBatchRequest(
            DestType=DestType,
            Destination=Destination,
            Destinations=Destinations or [],
            ContactID=ContactID,
            ContactIDs=ContactIDs or [],
            SubAccount=SubAccount,
            Department=Department,
        )
        body = filter_model_fields(batch)

        response = self.http.post("/optout/batch", body)
        return parse_response(response, OptOutResponse)