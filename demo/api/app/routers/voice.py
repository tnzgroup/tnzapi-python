from typing import Optional

from fastapi import APIRouter, Request
from pydantic import BaseModel

from app.responses import respond_with_result
from app.routers.auth import resolve_auth_token
from app.routers.common import PacingRequest, RescheduleRequest, ResubmitRequest
from tnzapi import TNZAPI

router = APIRouter(prefix="/api/voice")


class MessageKeypad(BaseModel):
    Tone: int
    Play: Optional[str] = None
    RouteNumber: Optional[str] = None
    PlaySection: Optional[str] = None
    PlayFile: Optional[str] = None
    File: Optional[str] = None


class SendVoiceRequest(BaseModel):
    ToNumber: str
    MessageToPeople: Optional[str] = None
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
    MessageToAnswerPhones: Optional[str] = None
    AnswerPhoneMode: Optional[str] = None
    Keypads: Optional[list[MessageKeypad]] = None
    KeypadOptionRequired: Optional[bool] = None
    CallRouteMessageOnWrongKey: Optional[str] = None
    CallRouteMessageToPeople: Optional[str] = None
    CallRouteMessageToOperators: Optional[str] = None
    EndCallMessage: Optional[str] = None
    NumberOfOperators: Optional[int] = None
    RetryAttempts: Optional[int] = None
    RetryPeriod: Optional[int] = None
    CallerId: Optional[str] = None
    Options: Optional[str] = None
    SendMode: Optional[str] = None


@router.post("/send")
def send(request: Request, body: SendVoiceRequest):
    client = TNZAPI(AuthToken=resolve_auth_token(request))

    # Same drop list as TTS: ChargeCode/EndCallMessage have no equivalent field in
    # tnzapi-python's v3.00 VoiceRequest.
    result = client.Messaging.Voice.SendMessage(
        Destinations=[{"ToNumber": body.ToNumber}],
        MessageToPeople=body.MessageToPeople,
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
        MessageToAnswerPhones=body.MessageToAnswerPhones,
        AnswerPhoneMode=body.AnswerPhoneMode,
        Keypads=[k.model_dump(exclude_none=True) for k in body.Keypads] if body.Keypads else None,
        KeypadOptionRequired=body.KeypadOptionRequired,
        CallRouteMessageOnWrongKey=body.CallRouteMessageOnWrongKey,
        CallRouteMessageToPeople=body.CallRouteMessageToPeople,
        CallRouteMessageToOperators=body.CallRouteMessageToOperators,
        NumberOfOperators=body.NumberOfOperators,
        RetryAttempts=body.RetryAttempts,
        RetryPeriod=body.RetryPeriod,
        CallerID=body.CallerId,
        Options=body.Options,
        Mode=body.SendMode,
    )
    return respond_with_result(result)


@router.get("/status/{message_id}")
def status(request: Request, message_id: str):
    client = TNZAPI(AuthToken=resolve_auth_token(request))
    result = client.Messaging.Voice.Status(MessageID=message_id)
    return respond_with_result(result)


@router.patch("/{message_id}/abort")
def abort(request: Request, message_id: str):
    client = TNZAPI(AuthToken=resolve_auth_token(request))
    result = client.Messaging.Voice.Abort(MessageID=message_id)
    return respond_with_result(result)


@router.patch("/{message_id}/reschedule")
def reschedule(request: Request, message_id: str, body: RescheduleRequest):
    client = TNZAPI(AuthToken=resolve_auth_token(request))
    result = client.Messaging.Voice.Reschedule(MessageID=message_id, SendTime=body.SendTime.isoformat())
    return respond_with_result(result)


@router.patch("/{message_id}/resubmit")
def resubmit(request: Request, message_id: str, body: ResubmitRequest):
    client = TNZAPI(AuthToken=resolve_auth_token(request))
    result = client.Messaging.Voice.Resubmit(MessageID=message_id, SendTime=body.SendTime.isoformat())
    return respond_with_result(result)


@router.patch("/{message_id}/pacing")
def pacing(request: Request, message_id: str, body: PacingRequest):
    client = TNZAPI(AuthToken=resolve_auth_token(request))
    result = client.Messaging.Voice.Pacing(MessageID=message_id, NumberOfOperators=body.NumberOfOperators)
    return respond_with_result(result)
