from fastapi import APIRouter, Request
from pydantic import BaseModel

from app.responses import respond_with_result
from app.routers.auth import resolve_auth_token
from tnzapi import TNZAPI

router = APIRouter(prefix="/api/addressbook/contact-groups")


class ContactGroupRequest(BaseModel):
    ContactID: str
    GroupID: str


@router.post("")
def add(request: Request, body: ContactGroupRequest):
    client = TNZAPI(AuthToken=resolve_auth_token(request))
    result = client.Addressbook.ContactGroup.Create(ContactID=body.ContactID, GroupID=body.GroupID)
    return respond_with_result(result)


@router.get("")
def list_for_contact(request: Request, contactID: str):
    client = TNZAPI(AuthToken=resolve_auth_token(request))
    result = client.Addressbook.ContactGroup.List(ContactID=contactID)
    return respond_with_result(result)


@router.delete("/{contact_id}/{group_id}")
def remove(request: Request, contact_id: str, group_id: str):
    client = TNZAPI(AuthToken=resolve_auth_token(request))
    result = client.Addressbook.ContactGroup.Delete(ContactID=contact_id, GroupID=group_id)
    return respond_with_result(result)
