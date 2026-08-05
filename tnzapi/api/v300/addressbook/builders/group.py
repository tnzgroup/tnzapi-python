import copy
from urllib.parse import quote, urlencode

from tnzapi.core.auth import TNZApiUser
from tnzapi.core.http_client import HttpClient
from tnzapi.core.response_parser import parse_response
from tnzapi.core.model_proxy import ModelRequestMixin, project_model, require_id, resolve_id
from tnzapi.core.legacy_kwargs import accept_legacy_kwargs
from tnzapi.api.v300.addressbook.models.requests.group_request import GroupRequest
from tnzapi.api.v300.addressbook.models.responses.group_response import GroupResponse
from tnzapi.api.v300.addressbook.models.responses.group_list_response import GroupListResponse


class Group(ModelRequestMixin):

    _request_model_cls = GroupRequest

    def __init__(self, user: TNZApiUser):
        self.user = user
        self.http = HttpClient(user)
        self._reset()

    def Create(self, model=None, **kwargs):

        if model is not None:
            if isinstance(model, GroupRequest):
                self._data = copy.deepcopy(model)
            elif isinstance(model, GroupResponse):
                self._data = project_model(model, GroupRequest)
            elif isinstance(model, dict):
                invalid = self._first_invalid_field(model)
                if invalid:
                    self._reset()
                    return GroupResponse(Result="Failed", ErrorMessage=[f"Unknown argument: {invalid}"])
                self._reset()
                self._apply_fields(model)
            else:
                self._reset()
                return GroupResponse(Result="Failed", ErrorMessage=[f"Invalid model type: {type(model).__name__}"])

        invalid = self._first_invalid_field(kwargs)
        if invalid:
            self._reset()
            return GroupResponse(Result="Failed", ErrorMessage=[f"Unknown argument: {invalid}"])

        self._apply_fields(kwargs)

        try:
            response = self.http.post("/addressbook/group", self._build_request_body())
            result = parse_response(response, GroupResponse)
        finally:
            self._reset()

        return result

    @accept_legacy_kwargs({"group_id": "GroupID"})
    def Update(self, GroupID, model=None, **kwargs):

        GroupID = resolve_id(GroupID, GroupResponse, "GroupID")

        if model is not None:
            if isinstance(model, GroupRequest):
                self._data = copy.deepcopy(model)
            elif isinstance(model, GroupResponse):
                self._data = project_model(model, GroupRequest)
            elif isinstance(model, dict):
                invalid = self._first_invalid_field(model)
                if invalid:
                    self._reset()
                    return GroupResponse(Result="Failed", ErrorMessage=[f"Unknown argument: {invalid}"])
                self._reset()
                self._apply_fields(model)
            else:
                self._reset()
                return GroupResponse(Result="Failed", ErrorMessage=[f"Invalid model type: {type(model).__name__}"])

        invalid = self._first_invalid_field(kwargs)
        if invalid:
            self._reset()
            return GroupResponse(Result="Failed", ErrorMessage=[f"Unknown argument: {invalid}"])

        self._apply_fields(kwargs)

        try:
            response = self.http.patch(f"/addressbook/group/{quote(str(GroupID), safe='')}", self._build_request_body())
            result = parse_response(response, GroupResponse)
        finally:
            self._reset()

        return result

    @accept_legacy_kwargs({"group_id": "GroupID"})
    def Detail(self, GroupID: str):
        GroupID = require_id(GroupID, "GroupID")
        response = self.http.get(f"/addressbook/group/{quote(str(GroupID), safe='')}")
        return parse_response(response, GroupResponse)

    @accept_legacy_kwargs({"group_id": "GroupID"})
    def Delete(self, GroupID):
        GroupID = resolve_id(GroupID, GroupResponse, "GroupID")
        response = self.http.delete(f"/addressbook/group/{quote(str(GroupID), safe='')}")
        return parse_response(response, GroupResponse)

    @accept_legacy_kwargs({"records_per_page": "RecordsPerPage", "page": "Page"})
    def List(self, RecordsPerPage: int = 20, Page: int = 1):
        query = {"recordsPerPage": RecordsPerPage, "page": Page}
        response = self.http.get(f"/addressbook/group/list?{urlencode(query)}")
        return parse_response(response, GroupListResponse)
