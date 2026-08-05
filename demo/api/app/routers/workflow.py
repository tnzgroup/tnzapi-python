from typing import Optional

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app.responses import respond_with_result
from app.routers.auth import resolve_auth_token
from tnzapi import TNZAPI

router = APIRouter(prefix="/api/workflow")


class SendWorkflowRequest(BaseModel):
    WorkflowTemplateId: str
    ToNumber: Optional[str] = None
    MainPhone: Optional[str] = None
    EmailAddress: Optional[str] = None
    ContactIds: Optional[str] = None
    GroupIds: Optional[str] = None
    Reference: Optional[str] = None
    NotificationType: Optional[str] = None
    WebhookCallbackUrl: Optional[str] = None
    WebhookCallbackFormat: Optional[str] = None
    SubAccount: Optional[str] = None
    Department: Optional[str] = None
    ChargeCode: Optional[str] = None
    SendTime: Optional[str] = None
    Timezone: Optional[str] = None
    SendMode: Optional[str] = None


def _split_ids(value: Optional[str]) -> list[str]:
    if not value:
        return []
    return [part.strip() for part in value.split(",") if part.strip()]


@router.post("/send")
def send(request: Request, body: SendWorkflowRequest):
    if body.SendMode is not None:
        # tnzapi-python's WorkflowRequest has no Mode field at all - Workflow has no
        # equivalent no-cost send switch, unlike every other channel. Silently ignoring
        # SendMode here would let a caller believe SendMode="Test" protected them from a real
        # send when it does nothing at all, so this is rejected outright instead.
        return JSONResponse(
            status_code=400,
            content={
                "Result": "Failed",
                "ErrorMessage": [
                    "SendMode has no effect for Workflow - tnzapi-python's WorkflowRequest "
                    "has no Mode field, unlike every other channel. Remove this field from the "
                    "request; there is no cost-safe way to send a Workflow message."
                ],
            },
        )

    client = TNZAPI(AuthToken=resolve_auth_token(request))

    # Omni-channel: ToNumber/MainPhone/EmailAddress can all be set together on the SAME
    # recipient (the Workflow Template decides which channel(s) actually get used) - EmailAddress
    # has no top-level WorkflowRequest field, but Destinations content is never validated,
    # so it passes through on the destination dict, matching tnzapi-dotnet's own design.
    destinations = []
    single_destination = {}
    if body.ToNumber:
        single_destination["ToNumber"] = body.ToNumber
    if body.MainPhone:
        single_destination["MainPhone"] = body.MainPhone
    if body.EmailAddress:
        single_destination["EmailAddress"] = body.EmailAddress
    if single_destination:
        destinations.append(single_destination)

    destinations += [{"ContactID": cid} for cid in _split_ids(body.ContactIds)]
    destinations += [{"GroupID": gid} for gid in _split_ids(body.GroupIds)]

    if not destinations:
        # WorkflowRequest doesn't validate Destinations itself - an empty list would
        # otherwise pass straight through to the live API instead of failing locally with a
        # clear reason.
        return JSONResponse(
            status_code=400,
            content={
                "Result": "Failed",
                "ErrorMessage": [
                    "At least one of ToNumber, MainPhone, EmailAddress, ContactIds, or "
                    "GroupIds is required."
                ],
            },
        )

    # ChargeCode is intentionally dropped - no equivalent field exists in tnzapi-python's
    # v3.00 WorkflowRequest.
    result = client.Messaging.Workflow.SendMessage(
        WorkflowTemplateID=body.WorkflowTemplateId,
        Destinations=destinations,
        Reference=body.Reference,
        NotificationType=body.NotificationType,
        WebhookCallbackURL=body.WebhookCallbackUrl,
        WebhookCallbackFormat=body.WebhookCallbackFormat,
        SubAccount=body.SubAccount,
        Department=body.Department,
        SendTime=body.SendTime,
        Timezone=body.Timezone,
    )
    return respond_with_result(result)
