from typing import Optional

from fastapi import APIRouter, Query, Request
from pydantic import BaseModel

from app.responses import respond_with_result, validate_pagination
from app.routers.auth import resolve_auth_token
from tnzapi import TNZAPI

router = APIRouter(prefix="/api/addressbook/contacts")

# Field names match tnzapi-python's ContactRequest exactly - no translation needed.


class ContactRequest(BaseModel):
    FirstName: Optional[str] = None
    LastName: Optional[str] = None
    Company: Optional[str] = None
    MobilePhone: Optional[str] = None
    EmailAddress: Optional[str] = None
    FaxNumber: Optional[str] = None
    Title: Optional[str] = None
    Position: Optional[str] = None
    Attention: Optional[str] = None
    RecipDepartment: Optional[str] = None
    StreetAddress: Optional[str] = None
    Suburb: Optional[str] = None
    City: Optional[str] = None
    State: Optional[str] = None
    Country: Optional[str] = None
    Postcode: Optional[str] = None
    MainPhone: Optional[str] = None
    WebAddress: Optional[str] = None
    Custom1: Optional[str] = None
    Custom2: Optional[str] = None
    Custom3: Optional[str] = None
    Custom4: Optional[str] = None
    Notes: Optional[str] = None


@router.get("")
def list_contacts(request: Request, records_per_page: int = Query(default=50, alias="recordsPerPage"), page: int = 1):
    error = validate_pagination(page, records_per_page)
    if error:
        return error

    client = TNZAPI(AuthToken=resolve_auth_token(request))
    result = client.Addressbook.Contact.List(RecordsPerPage=records_per_page, Page=page)
    return respond_with_result(result)


@router.post("")
def create_contact(request: Request, body: ContactRequest):
    client = TNZAPI(AuthToken=resolve_auth_token(request))
    result = client.Addressbook.Contact.Create(
        FirstName=body.FirstName,
        LastName=body.LastName,
        Company=body.Company,
        MobilePhone=body.MobilePhone,
        EmailAddress=body.EmailAddress,
        FaxNumber=body.FaxNumber,
        Title=body.Title,
        Position=body.Position,
        Attention=body.Attention,
        RecipDepartment=body.RecipDepartment,
        StreetAddress=body.StreetAddress,
        Suburb=body.Suburb,
        City=body.City,
        State=body.State,
        Country=body.Country,
        Postcode=body.Postcode,
        MainPhone=body.MainPhone,
        WebAddress=body.WebAddress,
        Custom1=body.Custom1,
        Custom2=body.Custom2,
        Custom3=body.Custom3,
        Custom4=body.Custom4,
        Notes=body.Notes,
    )
    return respond_with_result(result)


@router.get("/{contact_id}")
def get_contact(request: Request, contact_id: str):
    client = TNZAPI(AuthToken=resolve_auth_token(request))
    result = client.Addressbook.Contact.Detail(ContactID=contact_id)
    return respond_with_result(result)


@router.put("/{contact_id}")
def update_contact(request: Request, contact_id: str, body: ContactRequest):
    client = TNZAPI(AuthToken=resolve_auth_token(request))
    result = client.Addressbook.Contact.Update(
        ContactID=contact_id,
        FirstName=body.FirstName,
        LastName=body.LastName,
        Company=body.Company,
        MobilePhone=body.MobilePhone,
        EmailAddress=body.EmailAddress,
        FaxNumber=body.FaxNumber,
        Title=body.Title,
        Position=body.Position,
        Attention=body.Attention,
        RecipDepartment=body.RecipDepartment,
        StreetAddress=body.StreetAddress,
        Suburb=body.Suburb,
        City=body.City,
        State=body.State,
        Country=body.Country,
        Postcode=body.Postcode,
        MainPhone=body.MainPhone,
        WebAddress=body.WebAddress,
        Custom1=body.Custom1,
        Custom2=body.Custom2,
        Custom3=body.Custom3,
        Custom4=body.Custom4,
        Notes=body.Notes,
    )
    return respond_with_result(result)


@router.delete("/{contact_id}")
def delete_contact(request: Request, contact_id: str):
    client = TNZAPI(AuthToken=resolve_auth_token(request))
    result = client.Addressbook.Contact.Delete(ContactID=contact_id)
    return respond_with_result(result)
