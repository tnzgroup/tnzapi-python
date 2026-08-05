from urllib.parse import quote, urlencode

from tnzapi.core.auth import TNZApiUser
from tnzapi.core.http_client import HttpClient
from tnzapi.core.response_parser import parse_response
from tnzapi.core.legacy_kwargs import accept_legacy_kwargs
from tnzapi.core.model_proxy import require_id
from tnzapi.api.v300.addressbook.models.responses.contact_group_response import ContactGroupResponse
from tnzapi.api.v300.addressbook.models.responses.contact_group_list_response import ContactGroupListResponse


class ContactGroup:

    def __init__(self, user: TNZApiUser):
        self.user = user
        self.http = HttpClient(user)

    @accept_legacy_kwargs({"contact_id": "ContactID", "group_id": "GroupID"})
    def Create(self, ContactID: str, GroupID: str):
        ContactID = require_id(ContactID, "ContactID")
        GroupID = require_id(GroupID, "GroupID")
        response = self.http.patch(
            f"/addressbook/contact/{quote(str(ContactID), safe='')}/group",
            {"GroupID": GroupID},
        )
        return parse_response(response, ContactGroupResponse)

    @accept_legacy_kwargs({"contact_id": "ContactID", "group_id": "GroupID"})
    def Delete(self, ContactID: str, GroupID: str):
        ContactID = require_id(ContactID, "ContactID")
        GroupID = require_id(GroupID, "GroupID")
        response = self.http.delete(
            f"/addressbook/contact/{quote(str(ContactID), safe='')}/group/{quote(str(GroupID), safe='')}"
        )
        return parse_response(response, ContactGroupResponse)

    @accept_legacy_kwargs({"contact_id": "ContactID", "records_per_page": "RecordsPerPage", "page": "Page"})
    def List(self, ContactID: str, RecordsPerPage: int = 20, Page: int = 1):
        ContactID = require_id(ContactID, "ContactID")
        query = {"recordsPerPage": RecordsPerPage, "page": Page}
        response = self.http.get(
            f"/addressbook/contact/{quote(str(ContactID), safe='')}/group/list?{urlencode(query)}"
        )
        return parse_response(response, ContactGroupListResponse)

    @accept_legacy_kwargs({
        "contact_id": "ContactID", "group_id": "GroupID",
        "records_per_page": "RecordsPerPage", "page": "Page",
    })
    def Detail(self, ContactID: str, GroupID: str, RecordsPerPage: int = 100, Page: int = 1):
        # No dedicated v3.00 wire endpoint exists for a single Contact<->Group
        # association detail (confirmed absent from the OpenAPI spec) - synthesized
        # client-side via a single List() page + filter, rather than silently
        # dropping the method. Only scans the requested page - deliberately does
        # NOT walk every page on the caller's behalf (that could mean an unbounded
        # number of HTTP calls for a contact with many group memberships). Callers
        # who suspect more pages exist should inspect List()'s PageCount and pass
        # a larger RecordsPerPage or a specific page themselves.
        GroupID = require_id(GroupID, "GroupID")
        list_result = self.List(ContactID, RecordsPerPage=RecordsPerPage, Page=Page)

        if list_result.Result != "Success":
            return ContactGroupResponse(Result=list_result.Result, ErrorMessage=list_result.ErrorMessage)

        for group in list_result.Groups:
            if group.get("GroupID") == GroupID:
                return ContactGroupResponse(Result="Success", Contact=list_result.Contact, Group=group)

        return ContactGroupResponse(
            Result="RecordNotFound",
            ErrorMessage=[f"Group {GroupID} not found for contact {ContactID} on page {Page}"],
        )