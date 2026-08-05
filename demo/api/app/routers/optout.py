from typing import Optional

from fastapi import APIRouter, Query, Request
from pydantic import BaseModel

from app.responses import respond_with_result, validate_pagination
from app.routers.auth import resolve_auth_token
from tnzapi import TNZAPI

router = APIRouter(prefix="/api/optout")

# Field names match tnzapi-python's OptOutRequest exactly - no translation needed.


class OptOutRequest(BaseModel):
    Destination: Optional[str] = None
    DestType: Optional[str] = None
    Department: Optional[str] = None
    SubAccount: Optional[str] = None
    ContactID: Optional[str] = None
    StopMessage: Optional[str] = None
    Notes: Optional[str] = None


@router.get("")
def list_optouts(
    request: Request,
    records_per_page: int = Query(default=50, alias="recordsPerPage", ge=1, le=1000),
    page: int = Query(default=1, ge=1),
):
    error = validate_pagination(page, records_per_page)
    if error:
        return error

    client = TNZAPI(AuthToken=resolve_auth_token(request))
    result = client.OptOut.List(RecordsPerPage=records_per_page, Page=page)
    return respond_with_result(result)


@router.post("")
def create_optout(request: Request, body: OptOutRequest):
    client = TNZAPI(AuthToken=resolve_auth_token(request))
    result = client.OptOut.Create(
        Destination=body.Destination,
        DestType=body.DestType,
        Department=body.Department,
        SubAccount=body.SubAccount,
        ContactID=body.ContactID,
        StopMessage=body.StopMessage,
        Notes=body.Notes,
    )
    return respond_with_result(result)


@router.get("/{opt_out_id}")
def get_optout(request: Request, opt_out_id: str):
    client = TNZAPI(AuthToken=resolve_auth_token(request))
    result = client.OptOut.Details(OptOutID=opt_out_id)
    return respond_with_result(result)


@router.delete("/{opt_out_id}")
def delete_optout(request: Request, opt_out_id: str):
    client = TNZAPI(AuthToken=resolve_auth_token(request))
    result = client.OptOut.Delete(OptOutID=opt_out_id)
    return respond_with_result(result)