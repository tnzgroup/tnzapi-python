import copy

from tnzapi.core.auth import TNZApiUser
from tnzapi.core.http_client import HttpClient
from tnzapi.core.response_parser import parse_response
from tnzapi.core.model_proxy import ModelRequestMixin
from tnzapi.core.legacy_kwargs import accept_legacy_kwargs
from tnzapi.core.destination import normalize_destination
from tnzapi.api.v300.messaging.models.requests.workflow_request import WorkflowRequest
from tnzapi.api.v300.messaging.models.responses.workflow_response import WorkflowResponse


class Workflow(ModelRequestMixin):

    _request_model_cls = WorkflowRequest

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

    def SendMessage(self, model=None, **kwargs):

        if model is not None:
            if isinstance(model, WorkflowRequest):
                self._data = copy.deepcopy(model)
            elif isinstance(model, dict):
                invalid = self._first_invalid_field(model)
                if invalid:
                    self._reset()
                    return WorkflowResponse(Result="Failed", ErrorMessage=[f"Unknown argument: {invalid}"])
                self._reset()
                self._apply_fields(model)
            else:
                self._reset()
                return WorkflowResponse(Result="Failed", ErrorMessage=[f"Invalid model type: {type(model).__name__}"])

        invalid = self._first_invalid_field(kwargs)
        if invalid:
            self._reset()
            return WorkflowResponse(Result="Failed", ErrorMessage=[f"Unknown argument: {invalid}"])

        self._apply_fields(kwargs)

        # Unlike every other channel, ContactID/GroupID/MainPhone alone do NOT
        # satisfy this check for Workflow - only Destinations/Destination/ToNumber
        # do (route ContactID/GroupID through Destinations or AddDestination(...)
        # instead). This is deliberately narrower than ModelRequestMixin's
        # _missing_destination_error(), which the other 7 channels use.
        if not (self._data.Destinations or self._data.Destination or self._data.ToNumber):
            self._reset()
            return WorkflowResponse(
                Result="Failed",
                ErrorMessage=["Missing required field: Destinations, Destination, or ToNumber"],
            )

        if not self._data.WorkflowTemplateID:
            self._reset()
            return WorkflowResponse(Result="Failed", ErrorMessage=["Missing required field: WorkflowTemplateID"])

        try:
            response = self.http.post("/workflow", self._build_request_body())
            result = parse_response(response, WorkflowResponse)
        finally:
            self._reset()

        return result
