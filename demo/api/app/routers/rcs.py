from typing import Optional

from fastapi import APIRouter, Query, Request
from pydantic import BaseModel, field_validator

from app.attachments import validate_attachment_count, validate_file_content
from app.responses import respond_with_result, validate_pagination
from app.routers.auth import resolve_auth_token
from app.routers.common import RescheduleRequest
from tnzapi import TNZAPI
from tnzapi.core.file_attachment import FileAttachment

router = APIRouter(prefix="/api/rcs")


class MessageAttachment(BaseModel):
    FileName: str
    FileContent: str

    _validate_file_content = field_validator("FileContent")(validate_file_content)


class SendRcsRequest(BaseModel):
    ToNumber: str
    Message: str
    Reference: Optional[str] = None
    TemplateId: Optional[str] = None
    NotificationType: Optional[str] = None
    WebhookCallbackUrl: Optional[str] = None
    WebhookCallbackFormat: Optional[str] = None
    ReportTo: Optional[str] = None
    SendTime: Optional[str] = None
    Timezone: Optional[str] = None
    SubAccount: Optional[str] = None
    Department: Optional[str] = None
    ChargeCode: Optional[str] = None
    FromNumber: Optional[str] = None
    SmsEmailReply: Optional[str] = None
    CharacterConversion: Optional[bool] = None
    FallbackMode: Optional[list[str]] = None
    SendMode: Optional[str] = None
    Attachments: Optional[list[MessageAttachment]] = None

    _validate_attachment_count = field_validator("Attachments")(validate_attachment_count)


@router.post("/send")
def send(request: Request, body: SendRcsRequest):
    client = TNZAPI(AuthToken=resolve_auth_token(request))

    # ReportTo/ChargeCode are intentionally dropped - neither has an equivalent field in
    # tnzapi-python's v3.00 RCSRequest (unlike SMS, which does have ReportTo).
    # FallbackMode: the SDK now joins a list into TNZ's real comma-separated wire
    # format itself (see tnzapi.core.fallback_mode.normalize_fallback_mode) - the
    # frontend's raw list is passed straight through, no local validation needed.
    result = client.Messaging.RCS.SendMessage(
        Message=body.Message,
        Destinations=[{"ToNumber": body.ToNumber}],
        Reference=body.Reference,
        TemplateID=body.TemplateId,
        NotificationType=body.NotificationType,
        WebhookCallbackURL=body.WebhookCallbackUrl,
        WebhookCallbackFormat=body.WebhookCallbackFormat,
        SendTime=body.SendTime,
        Timezone=body.Timezone,
        SubAccount=body.SubAccount,
        Department=body.Department,
        FromNumber=body.FromNumber,
        SMSEmailReply=body.SmsEmailReply,
        CharacterConversion=body.CharacterConversion,
        FallbackMode=body.FallbackMode,
        Mode=body.SendMode,
        Files=[FileAttachment(Name=a.FileName, Data=a.FileContent) for a in body.Attachments] if body.Attachments else None,
    )
    return respond_with_result(result)


@router.get("/status/{message_id}")
def status(request: Request, message_id: str):
    client = TNZAPI(AuthToken=resolve_auth_token(request))
    result = client.Messaging.RCS.Status(MessageID=message_id)
    return respond_with_result(result)


@router.patch("/{message_id}/abort")
def abort(request: Request, message_id: str):
    client = TNZAPI(AuthToken=resolve_auth_token(request))
    result = client.Messaging.RCS.Abort(MessageID=message_id)
    return respond_with_result(result)


@router.patch("/{message_id}/reschedule")
def reschedule(request: Request, message_id: str, body: RescheduleRequest):
    client = TNZAPI(AuthToken=resolve_auth_token(request))
    result = client.Messaging.RCS.Reschedule(MessageID=message_id, SendTime=body.SendTime.isoformat())
    return respond_with_result(result)


@router.get("/received")
def received(
    request: Request,
    time_period: Optional[int] = Query(default=None, alias="timePeriod"),
    date_from: Optional[str] = Query(default=None, alias="dateFrom"),
    date_to: Optional[str] = Query(default=None, alias="dateTo"),
    records_per_page: int = Query(default=100, alias="recordsPerPage"),
    page: int = Query(default=1),
):
    error = validate_pagination(page, records_per_page)
    if error:
        return error

    client = TNZAPI(AuthToken=resolve_auth_token(request))
    result = client.Messaging.RCS.Received(
        TimePeriod=time_period, DateFrom=date_from, DateTo=date_to,
        RecordsPerPage=records_per_page, Page=page,
    )
    return respond_with_result(result)
