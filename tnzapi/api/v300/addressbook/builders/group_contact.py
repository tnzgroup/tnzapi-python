from urllib.parse import quote, urlencode

from tnzapi.core.auth import TNZApiUser
from tnzapi.core.http_client import HttpClient
from tnzapi.core.response_parser import parse_response
from tnzapi.core.legacy_kwargs import accept_legacy_kwargs
from tnzapi.core.model_proxy import require_id
from tnzapi.api.v300.addressbook.models.responses.group_contact_response import GroupContactResponse
from tnzapi.api.v300.addressbook.models.responses.group_contact_list_response import GroupContactListResponse


class GroupContact:

    def __init__(self, user: TNZApiUser):
        self.user = user
        self.http = HttpClient(user)

    @accept_legacy_kwargs({"group_id": "GroupID", "contact_id": "ContactID"})
    def Create(self, GroupID: str, ContactID: str):
        # No distinct group-side wire endpoint exists in the v3.00 spec for adding a
        # contact to a group - this wraps the same contact-side PATCH endpoint that
        # ContactGroup.Create calls, matching tnzapi-ts's shipped GroupContactCreateApi.
        GroupID = require_id(GroupID, "GroupID")
        ContactID = require_id(ContactID, "ContactID")
        response = self.http.patch(
            f"/addressbook/contact/{quote(str(ContactID), safe='')}/group",
            {"GroupID": GroupID},
        )
        return parse_response(response, GroupContactResponse)

    @accept_legacy_kwargs({"group_id": "GroupID", "contact_id": "ContactID"})
    def Delete(self, GroupID: str, ContactID: str):
        GroupID = require_id(GroupID, "GroupID")
        ContactID = require_id(ContactID, "ContactID")
        response = self.http.delete(
            f"/addressbook/contact/{quote(str(ContactID), safe='')}/group/{quote(str(GroupID), safe='')}"
        )
        return parse_response(response, GroupContactResponse)

    @accept_legacy_kwargs({"group_id": "GroupID", "records_per_page": "RecordsPerPage", "page": "Page"})
    def List(self, GroupID: str, RecordsPerPage: int = 20, Page: int = 1):
        GroupID = require_id(GroupID, "GroupID")
        query = {"recordsPerPage": RecordsPerPage, "page": Page}
        response = self.http.get(
            f"/addressbook/group/{quote(str(GroupID), safe='')}/contact/list?{urlencode(query)}"
        )
        return parse_response(response, GroupContactListResponse)

    @accept_legacy_kwargs({
        "group_id": "GroupID", "contact_id": "ContactID",
        "records_per_page": "RecordsPerPage", "page": "Page",
    })
    def Detail(self, GroupID: str, ContactID: str, RecordsPerPage: int = 100, Page: int = 1):
        # Same "no dedicated wire endpoint" situation as ContactGroup.Detail -
        # synthesized client-side via a single List() page + filter. Deliberately
        # does NOT walk every page on the caller's behalf (unbounded HTTP calls
        # for a group with many contacts) - callers who suspect more pages exist
        # should inspect List()'s PageCount and pass a larger RecordsPerPage
        # or a specific page themselves.
        ContactID = require_id(ContactID, "ContactID")
        list_result = self.List(GroupID, RecordsPerPage=RecordsPerPage, Page=Page)

        if list_result.Result != "Success":
            return GroupContactResponse(Result=list_result.Result, ErrorMessage=list_result.ErrorMessage)

        for contact in list_result.Contacts:
            if contact.get("ContactID") == ContactID:
                return GroupContactResponse(Result="Success", Group=list_result.Group, Contact=contact)

        return GroupContactResponse(
            Result="RecordNotFound",
            ErrorMessage=[f"Contact {ContactID} not found for group {GroupID} on page {Page}"],
        )