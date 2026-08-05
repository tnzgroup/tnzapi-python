from fastapi import APIRouter, Request
from pydantic import BaseModel

from app.responses import respond_with_result
from app.routers.auth import resolve_auth_token
from tnzapi import TNZAPI

router = APIRouter(prefix="/api/addressbook/group-contacts")


class GroupContactRequest(BaseModel):
    GroupID: str
    ContactID: str


@router.post("")
def add(request: Request, body: GroupContactRequest):
    client = TNZAPI(AuthToken=resolve_auth_token(request))
    result = client.Addressbook.GroupContact.Create(GroupID=body.GroupID, ContactID=body.ContactID)
    return respond_with_result(result)


@router.get("")
def list_for_group(request: Request, groupID: str):
    client = TNZAPI(AuthToken=resolve_auth_token(request))
    result = client.Addressbook.GroupContact.List(GroupID=groupID)
    return respond_with_result(result)


@router.delete("/{group_id}/{contact_id}")
def remove(request: Request, group_id: str, contact_id: str):
    client = TNZAPI(AuthToken=resolve_auth_token(request))
    result = client.Addressbook.GroupContact.Delete(GroupID=group_id, ContactID=contact_id)
    return respond_with_result(result)
