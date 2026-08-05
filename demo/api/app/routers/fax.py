from typing import Optional

from fastapi import APIRouter, Request
from pydantic import BaseModel, field_validator

from app.attachments import validate_attachment_count, validate_file_content
from app.responses import respond_with_result
from app.routers.auth import resolve_auth_token
from app.routers.common import RescheduleRequest, ResubmitRequest
from tnzapi import TNZAPI
from tnzapi.core.file_attachment import FileAttachment

router = APIRouter(prefix="/api/fax")


class MessageAttachment(BaseModel):
    FileName: str
    FileContent: str

    _validate_file_content = field_validator("FileContent")(validate_file_content)


class SendFaxRequest(BaseModel):
    ToNumber: str
    Attachments: Optional[list[MessageAttachment]] = None
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
    Csid: Optional[str] = None
    Resolution: Optional[str] = None
    WatermarkFolder: Optional[str] = None
    WatermarkFirstPage: Optional[str] = None
    WatermarkAllPages: Optional[str] = None
    RetryAttempts: Optional[int] = None
    RetryPeriod: Optional[int] = None
    SendMode: Optional[str] = None

    _validate_attachment_count = field_validator("Attachments")(validate_attachment_count)


@router.post("/send")
def send(request: Request, body: SendFaxRequest):
    client = TNZAPI(AuthToken=resolve_auth_token(request))

    # ChargeCode is intentionally dropped - no equivalent field exists in tnzapi-python's
    # v3.00 FaxRequest.
    result = client.Messaging.Fax.SendMessage(
        Destinations=[{"ToNumber": body.ToNumber}],
        Files=[FileAttachment(Name=a.FileName, Data=a.FileContent) for a in body.Attachments] if body.Attachments else None,
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
        CSID=body.Csid,
        Resolution=body.Resolution,
        WatermarkFolder=body.WatermarkFolder,
        WatermarkFirstPage=body.WatermarkFirstPage,
        WatermarkAllPages=body.WatermarkAllPages,
        RetryAttempts=body.RetryAttempts,
        RetryPeriod=body.RetryPeriod,
        Mode=body.SendMode,
    )
    return respond_with_result(result)


@router.get("/status/{message_id}")
def status(request: Request, message_id: str):
    client = TNZAPI(AuthToken=resolve_auth_token(request))
    result = client.Messaging.Fax.Status(MessageID=message_id)
    return respond_with_result(result)


@router.patch("/{message_id}/abort")
def abort(request: Request, message_id: str):
    client = TNZAPI(AuthToken=resolve_auth_token(request))
    result = client.Messaging.Fax.Abort(MessageID=message_id)
    return respond_with_result(result)


@router.patch("/{message_id}/reschedule")
def reschedule(request: Request, message_id: str, body: RescheduleRequest):
    client = TNZAPI(AuthToken=resolve_auth_token(request))
    result = client.Messaging.Fax.Reschedule(MessageID=message_id, SendTime=body.SendTime.isoformat())
    return respond_with_result(result)


@router.patch("/{message_id}/resubmit")
def resubmit(request: Request, message_id: str, body: ResubmitRequest):
    client = TNZAPI(AuthToken=resolve_auth_token(request))
    result = client.Messaging.Fax.Resubmit(MessageID=message_id, SendTime=body.SendTime.isoformat())
    return respond_with_result(result)
