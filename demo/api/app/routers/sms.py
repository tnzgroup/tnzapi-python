from typing import Optional

from fastapi import APIRouter, Query, Request
from pydantic import BaseModel, field_validator

from app.attachments import validate_attachment_count, validate_file_content
from app.responses import respond_with_result, validate_pagination
from app.routers.auth import resolve_auth_token
from app.routers.common import RescheduleRequest
from tnzapi import TNZAPI
from tnzapi.core.file_attachment import FileAttachment

router = APIRouter(prefix="/api/sms")


class MessageAttachment(BaseModel):
    FileName: str
    FileContent: str

    _validate_file_content = field_validator("FileContent")(validate_file_content)


class SendSmsRequest(BaseModel):
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


# Plain `def`, not `async def` - tnzapi's SDK makes synchronous (requests-based) HTTP calls,
# so an async route here would block the whole uvicorn event loop for each round-trip to TNZ's
# API. A plain def route runs in FastAPI's threadpool instead. Follow this same pattern for
# every future channel router.
@router.post("/send")
def send(request: Request, body: SendSmsRequest):
    client = TNZAPI(AuthToken=resolve_auth_token(request))

    # ChargeCode is intentionally dropped here - no equivalent field exists in
    # tnzapi-python's v3.00 SMSRequest (removed in the v2.04 -> v3.00 API change).
    # FallbackMode: the SDK now joins a list into TNZ's real comma-separated wire
    # format itself (see tnzapi.core.fallback_mode.normalize_fallback_mode) - the
    # frontend's raw list is passed straight through, no local validation needed.
    result = client.Messaging.SMS.SendMessage(
        Message=body.Message,
        Destinations=[{"ToNumber": body.ToNumber}],
        Reference=body.Reference,
        TemplateID=body.TemplateId,
        NotificationType=body.NotificationType,
        WebhookCallbackURL=body.WebhookCallbackUrl,
        WebhookCallbackFormat=body.WebhookCallbackFormat,
        ReportTo=body.ReportTo,
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
    result = client.Messaging.SMS.Status(MessageID=message_id)
    return respond_with_result(result)


# PATCH /api/sms/{message_id}/abort|reschedule - matches the real TNZ REST API's own wire shape
# (PATCH /sms/{MessageID}/abort etc.) rather than the shared frontend's POST /api/actions/{action}
# convention, per explicit direction to replace that cross-channel dispatcher entirely.
@router.patch("/{message_id}/abort")
def abort(request: Request, message_id: str):
    client = TNZAPI(AuthToken=resolve_auth_token(request))
    result = client.Messaging.SMS.Abort(MessageID=message_id)
    return respond_with_result(result)


@router.patch("/{message_id}/reschedule")
def reschedule(request: Request, message_id: str, body: RescheduleRequest):
    client = TNZAPI(AuthToken=resolve_auth_token(request))
    result = client.Messaging.SMS.Reschedule(MessageID=message_id, SendTime=body.SendTime.isoformat())
    return respond_with_result(result)


@router.get("/reply/{message_id}")
def reply(
    request: Request,
    message_id: str,
    records_per_page: int = Query(default=20, alias="recordsPerPage"),
    page: int = Query(default=1),
):
    error = validate_pagination(page, records_per_page)
    if error:
        return error

    client = TNZAPI(AuthToken=resolve_auth_token(request))
    result = client.Reports.SMSReply.Poll(MessageID=message_id, RecordsPerPage=records_per_page, Page=page)
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
    result = client.Messaging.SMS.Received(
        TimePeriod=time_period, DateFrom=date_from, DateTo=date_to,
        RecordsPerPage=records_per_page, Page=page,
    )
    return respond_with_result(result)
