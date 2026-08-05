import copy
from urllib.parse import quote, urlencode

from tnzapi.core.auth import TNZApiUser
from tnzapi.core.http_client import HttpClient
from tnzapi.core.response_parser import parse_response
from tnzapi.core.model_proxy import ModelRequestMixin, project_model, require_id, resolve_id
from tnzapi.core.legacy_kwargs import accept_legacy_kwargs
from tnzapi.api.v300.addressbook.models.requests.contact_request import ContactRequest
from tnzapi.api.v300.addressbook.models.responses.contact_response import ContactResponse
from tnzapi.api.v300.addressbook.models.responses.contact_list_response import ContactListResponse


class Contact(ModelRequestMixin):

    _request_model_cls = ContactRequest

    def __init__(self, user: TNZApiUser):
        self.user = user
        self.http = HttpClient(user)
        self._reset()

    def Create(self, model=None, **kwargs):

        if model is not None:
            if isinstance(model, ContactRequest):
                self._data = copy.deepcopy(model)
            elif isinstance(model, ContactResponse):
                self._data = project_model(model, ContactRequest)
            elif isinstance(model, dict):
                invalid = self._first_invalid_field(model)
                if invalid:
                    self._reset()
                    return ContactResponse(Result="Failed", ErrorMessage=[f"Unknown argument: {invalid}"])
                self._reset()
                self._apply_fields(model)
            else:
                self._reset()
                return ContactResponse(Result="Failed", ErrorMessage=[f"Invalid model type: {type(model).__name__}"])

        invalid = self._first_invalid_field(kwargs)
        if invalid:
            self._reset()
            return ContactResponse(Result="Failed", ErrorMessage=[f"Unknown argument: {invalid}"])

        self._apply_fields(kwargs)

        try:
            response = self.http.post("/addressbook/contact", self._build_request_body())
            result = parse_response(response, ContactResponse)
        finally:
            self._reset()

        return result

    @accept_legacy_kwargs({"contact_id": "ContactID"})
    def Update(self, ContactID, model=None, **kwargs):

        ContactID = resolve_id(ContactID, ContactResponse, "ContactID")

        if model is not None:
            if isinstance(model, ContactRequest):
                self._data = copy.deepcopy(model)
            elif isinstance(model, ContactResponse):
                self._data = project_model(model, ContactRequest)
            elif isinstance(model, dict):
                invalid = self._first_invalid_field(model)
                if invalid:
                    self._reset()
                    return ContactResponse(Result="Failed", ErrorMessage=[f"Unknown argument: {invalid}"])
                self._reset()
                self._apply_fields(model)
            else:
                self._reset()
                return ContactResponse(Result="Failed", ErrorMessage=[f"Invalid model type: {type(model).__name__}"])

        invalid = self._first_invalid_field(kwargs)
        if invalid:
            self._reset()
            return ContactResponse(Result="Failed", ErrorMessage=[f"Unknown argument: {invalid}"])

        self._apply_fields(kwargs)

        try:
            response = self.http.patch(f"/addressbook/contact/{quote(str(ContactID), safe='')}", self._build_request_body())
            result = parse_response(response, ContactResponse)
        finally:
            self._reset()

        return result

    @accept_legacy_kwargs({"contact_id": "ContactID"})
    def Detail(self, ContactID: str):
        ContactID = require_id(ContactID, "ContactID")
        response = self.http.get(f"/addressbook/contact/{quote(str(ContactID), safe='')}")
        return parse_response(response, ContactResponse)

    @accept_legacy_kwargs({"contact_id": "ContactID"})
    def Delete(self, ContactID):
        ContactID = resolve_id(ContactID, ContactResponse, "ContactID")
        response = self.http.delete(f"/addressbook/contact/{quote(str(ContactID), safe='')}")
        return parse_response(response, ContactResponse)

    @accept_legacy_kwargs({"records_per_page": "RecordsPerPage", "page": "Page"})
    def List(self, RecordsPerPage: int = 20, Page: int = 1):
        query = {"recordsPerPage": RecordsPerPage, "page": Page}
        response = self.http.get(f"/addressbook/contact/list?{urlencode(query)}")
        return parse_response(response, ContactListResponse)

    @accept_legacy_kwargs({
        "email_address": "EmailAddress", "mobile_phone": "MobilePhone", "main_phone": "MainPhone",
        "attention": "Attention", "first_name": "FirstName", "last_name": "LastName", "company": "Company",
        "records_per_page": "RecordsPerPage", "page": "Page",
    })
    def Search(self, EmailAddress=None, MobilePhone=None, MainPhone=None, Attention=None,
               FirstName=None, LastName=None, Company=None, RecordsPerPage: int = 20, Page: int = 1):

        query = {}
        if EmailAddress is not None:
            query["EmailAddress"] = EmailAddress
        if MobilePhone is not None:
            query["MobilePhone"] = MobilePhone
        if MainPhone is not None:
            query["MainPhone"] = MainPhone
        if Attention is not None:
            query["Attention"] = Attention
        if FirstName is not None:
            query["FirstName"] = FirstName
        if LastName is not None:
            query["LastName"] = LastName
        if Company is not None:
            query["Company"] = Company
        query["recordsPerPage"] = RecordsPerPage
        query["page"] = Page

        response = self.http.get(f"/addressbook/contact/search?{urlencode(query)}")
        return parse_response(response, ContactListResponse)
