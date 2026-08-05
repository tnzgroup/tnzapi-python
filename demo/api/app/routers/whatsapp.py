from typing import Optional

from fastapi import APIRouter, Query, Request
from pydantic import BaseModel, field_validator

from app.attachments import validate_attachment_count, validate_file_content
from app.responses import respond_with_result, validate_pagination
from app.routers.auth import resolve_auth_token
from app.routers.common import RescheduleRequest
from tnzapi import TNZAPI
from tnzapi.core.file_attachment import FileAttachment

router = APIRouter(prefix="/api/whatsapp")

_CUSTOM_FIELDS = [f"Custom{i}" for i in range(1, 10)]


class MessageAttachment(BaseModel):
    FileName: str
    FileContent: str

    _validate_file_content = field_validator("FileContent")(validate_file_content)


class SendWhatsAppRequest(BaseModel):
    ToNumber: str
    Message: str
    TemplateId: str
    FromNumber: str
    Attachments: Optional[list[MessageAttachment]] = None
    Reference: Optional[str] = None
    FallbackMode: Optional[list[str]] = None
    Custom1: Optional[str] = None
    Custom2: Optional[str] = None
    Custom3: Optional[str] = None
    Custom4: Optional[str] = None
    Custom5: Optional[str] = None
    Custom6: Optional[str] = None
    Custom7: Optional[str] = None
    Custom8: Optional[str] = None
    Custom9: Optional[str] = None
    NotificationType: Optional[str] = None
    WebhookCallbackUrl: Optional[str] = None
    WebhookCallbackFormat: Optional[str] = None
    ReportTo: Optional[str] = None
    SendTime: Optional[str] = None
    Timezone: Optional[str] = None
    SubAccount: Optional[str] = None
    Department: Optional[str] = None
    ChargeCode: Optional[str] = None
    SendMode: Optional[str] = None

    _validate_attachment_count = field_validator("Attachments")(validate_attachment_count)


@router.post("/send")
def send(request: Request, body: SendWhatsAppRequest):
    client = TNZAPI(AuthToken=resolve_auth_token(request))

    # Custom1-9 live on the Destination, not the top-level model - matching
    # tnzapi-dotnet's own design (per-recipient template token substitution). WhatsApp's
    # AddDestination/Destinations list is never field-validated, so extra keys pass straight
    # through to the wire.
    destination = {"ToNumber": body.ToNumber}
    for field in _CUSTOM_FIELDS:
        value = getattr(body, field, None)
        if value is not None:
            destination[field] = value

    # ReportTo/ChargeCode are intentionally dropped - neither has an equivalent field in
    # tnzapi-python's v3.00 WhatsAppRequest.
    # FallbackMode: the SDK now joins a list into TNZ's real comma-separated wire
    # format itself (see tnzapi.core.fallback_mode.normalize_fallback_mode) - the
    # frontend's raw list is passed straight through, no local validation needed.
    result = client.Messaging.WhatsApp.SendMessage(
        Message=body.Message,
        Destinations=[destination],
        TemplateID=body.TemplateId,
        FromNumber=body.FromNumber,
        Files=[FileAttachment(Name=a.FileName, Data=a.FileContent) for a in body.Attachments] if body.Attachments else None,
        Reference=body.Reference,
        FallbackMode=body.FallbackMode,
        NotificationType=body.NotificationType,
        WebhookCallbackURL=body.WebhookCallbackUrl,
        WebhookCallbackFormat=body.WebhookCallbackFormat,
        SendTime=body.SendTime,
        Timezone=body.Timezone,
        SubAccount=body.SubAccount,
        Department=body.Department,
        Mode=body.SendMode,
    )
    return respond_with_result(result)


@router.get("/status/{message_id}")
def status(request: Request, message_id: str):
    client = TNZAPI(AuthToken=resolve_auth_token(request))
    result = client.Messaging.WhatsApp.Status(MessageID=message_id)
    return respond_with_result(result)


@router.patch("/{message_id}/abort")
def abort(request: Request, message_id: str):
    client = TNZAPI(AuthToken=resolve_auth_token(request))
    result = client.Messaging.WhatsApp.Abort(MessageID=message_id)
    return respond_with_result(result)


@router.patch("/{message_id}/reschedule")
def reschedule(request: Request, message_id: str, body: RescheduleRequest):
    client = TNZAPI(AuthToken=resolve_auth_token(request))
    result = client.Messaging.WhatsApp.Reschedule(MessageID=message_id, SendTime=body.SendTime.isoformat())
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
    result = client.Messaging.WhatsApp.Received(
        TimePeriod=time_period, DateFrom=date_from, DateTo=date_to,
        RecordsPerPage=records_per_page, Page=page,
    )
    return respond_with_result(result)
