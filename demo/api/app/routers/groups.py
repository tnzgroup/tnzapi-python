from typing import Optional

from fastapi import APIRouter, Query, Request
from pydantic import BaseModel

from app.responses import respond_with_result, validate_pagination
from app.routers.auth import resolve_auth_token
from tnzapi import TNZAPI

router = APIRouter(prefix="/api/addressbook/groups")


class GroupRequest(BaseModel):
    GroupName: Optional[str] = None
    SubAccount: Optional[str] = None
    Department: Optional[str] = None
    ViewEditBy: Optional[str] = None


@router.get("")
def list_groups(request: Request, records_per_page: int = Query(default=50, alias="recordsPerPage"), page: int = 1):
    error = validate_pagination(page, records_per_page)
    if error:
        return error

    client = TNZAPI(AuthToken=resolve_auth_token(request))
    result = client.Addressbook.Group.List(RecordsPerPage=records_per_page, Page=page)
    return respond_with_result(result)


@router.post("")
def create_group(request: Request, body: GroupRequest):
    client = TNZAPI(AuthToken=resolve_auth_token(request))
    result = client.Addressbook.Group.Create(
        GroupName=body.GroupName,
        SubAccount=body.SubAccount,
        Department=body.Department,
        ViewEditBy=body.ViewEditBy,
    )
    return respond_with_result(result)


@router.get("/{group_id}")
def get_group(request: Request, group_id: str):
    client = TNZAPI(AuthToken=resolve_auth_token(request))
    result = client.Addressbook.Group.Detail(GroupID=group_id)
    return respond_with_result(result)


@router.put("/{group_id}")
def update_group(request: Request, group_id: str, body: GroupRequest):
    client = TNZAPI(AuthToken=resolve_auth_token(request))
    result = client.Addressbook.Group.Update(
        GroupID=group_id,
        GroupName=body.GroupName,
        SubAccount=body.SubAccount,
        Department=body.Department,
        ViewEditBy=body.ViewEditBy,
    )
    return respond_with_result(result)


@router.delete("/{group_id}")
def delete_group(request: Request, group_id: str):
    client = TNZAPI(AuthToken=resolve_auth_token(request))
    result = client.Addressbook.Group.Delete(GroupID=group_id)
    return respond_with_result(result)
