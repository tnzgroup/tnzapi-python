from typing import Optional

from fastapi import APIRouter, Request
from pydantic import BaseModel, field_validator

from app.attachments import validate_attachment_count, validate_file_content
from app.responses import respond_with_result
from app.routers.auth import resolve_auth_token
from app.routers.common import RescheduleRequest, ResubmitRequest
from tnzapi import TNZAPI
from tnzapi.core.file_attachment import FileAttachment

router = APIRouter(prefix="/api/email")


class MessageAttachment(BaseModel):
    FileName: str
    FileContent: str

    _validate_file_content = field_validator("FileContent")(validate_file_content)


class SendEmailRequest(BaseModel):
    EmailAddress: str
    Subject: str
    MessageHtml: Optional[str] = None
    MessagePlain: Optional[str] = None
    Reference: Optional[str] = None
    TemplateId: Optional[str] = None
    SmtpFrom: Optional[str] = None
    From: Optional[str] = None
    FromEmail: Optional[str] = None
    ReplyTo: Optional[str] = None
    CcEmail: Optional[str] = None
    BccEmail: Optional[str] = None
    WebhookCallbackUrl: Optional[str] = None
    WebhookCallbackFormat: Optional[str] = None
    ReportTo: Optional[str] = None
    SendTime: Optional[str] = None
    Timezone: Optional[str] = None
    SubAccount: Optional[str] = None
    Department: Optional[str] = None
    ChargeCode: Optional[str] = None
    NotificationType: Optional[str] = None
    SendMode: Optional[str] = None
    Attachments: Optional[list[MessageAttachment]] = None

    _validate_attachment_count = field_validator("Attachments")(validate_attachment_count)


@router.post("/send")
def send(request: Request, body: SendEmailRequest):
    client = TNZAPI(AuthToken=resolve_auth_token(request))

    # SmtpFrom/ChargeCode are intentionally dropped - no equivalent field exists in
    # tnzapi-python's v3.00 EmailRequest.
    result = client.Messaging.Email.SendMessage(
        EmailSubject=body.Subject,
        Destinations=[{"EmailAddress": body.EmailAddress}],
        MessageHTML=body.MessageHtml,
        MessagePlain=body.MessagePlain,
        Reference=body.Reference,
        TemplateID=body.TemplateId,
        From=body.From,
        FromEmail=body.FromEmail,
        ReplyTo=body.ReplyTo,
        CCEmail=body.CcEmail,
        BCCEmail=body.BccEmail,
        WebhookCallbackURL=body.WebhookCallbackUrl,
        WebhookCallbackFormat=body.WebhookCallbackFormat,
        ReportTo=body.ReportTo,
        SendTime=body.SendTime,
        Timezone=body.Timezone,
        SubAccount=body.SubAccount,
        Department=body.Department,
        NotificationType=body.NotificationType,
        Mode=body.SendMode,
        Files=[FileAttachment(Name=a.FileName, Data=a.FileContent) for a in body.Attachments] if body.Attachments else None,
    )
    return respond_with_result(result)


@router.get("/status/{message_id}")
def status(request: Request, message_id: str):
    client = TNZAPI(AuthToken=resolve_auth_token(request))
    result = client.Messaging.Email.Status(MessageID=message_id)
    return respond_with_result(result)


@router.patch("/{message_id}/abort")
def abort(request: Request, message_id: str):
    client = TNZAPI(AuthToken=resolve_auth_token(request))
    result = client.Messaging.Email.Abort(MessageID=message_id)
    return respond_with_result(result)


@router.patch("/{message_id}/reschedule")
def reschedule(request: Request, message_id: str, body: RescheduleRequest):
    client = TNZAPI(AuthToken=resolve_auth_token(request))
    result = client.Messaging.Email.Reschedule(MessageID=message_id, SendTime=body.SendTime.isoformat())
    return respond_with_result(result)


@router.patch("/{message_id}/resubmit")
def resubmit(request: Request, message_id: str, body: ResubmitRequest):
    client = TNZAPI(AuthToken=resolve_auth_token(request))
    result = client.Messaging.Email.Resubmit(MessageID=message_id, SendTime=body.SendTime.isoformat())
    return respond_with_result(result)
