from typing import Optional

from fastapi import APIRouter, Request
from pydantic import BaseModel

from app.responses import respond_with_result
from app.routers.auth import resolve_auth_token
from app.routers.common import PacingRequest, RescheduleRequest, ResubmitRequest
from tnzapi import TNZAPI

router = APIRouter(prefix="/api/tts")


class MessageKeypad(BaseModel):
    Tone: int
    Play: Optional[str] = None
    RouteNumber: Optional[str] = None
    PlaySection: Optional[str] = None
    PlayFile: Optional[str] = None
    File: Optional[str] = None


class SendTtsRequest(BaseModel):
    ToNumber: str
    MessageToPeople: str
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
    Voice: Optional[str] = None
    Options: Optional[str] = None
    SendMode: Optional[str] = None


@router.post("/send")
def send(request: Request, body: SendTtsRequest):
    client = TNZAPI(AuthToken=resolve_auth_token(request))

    # ChargeCode and EndCallMessage are intentionally dropped - neither has an equivalent
    # field in tnzapi-python's v3.00 TTSRequest. Keypads' PlayFile/File are passed through
    # verbatim inside each keypad dict (not top-level DTO fields, so not translated here) -
    # tnzapi-python's own AddKeypad() doesn't model them either; whether the live API honors
    # them for TTS specifically is unconfirmed and not required for this plan's scope.
    result = client.Messaging.TTS.SendMessage(
        MessageToPeople=body.MessageToPeople,
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
        Voice=body.Voice,
        Options=body.Options,
        Mode=body.SendMode,
    )
    return respond_with_result(result)


@router.get("/status/{message_id}")
def status(request: Request, message_id: str):
    client = TNZAPI(AuthToken=resolve_auth_token(request))
    result = client.Messaging.TTS.Status(MessageID=message_id)
    return respond_with_result(result)


@router.patch("/{message_id}/abort")
def abort(request: Request, message_id: str):
    client = TNZAPI(AuthToken=resolve_auth_token(request))
    result = client.Messaging.TTS.Abort(MessageID=message_id)
    return respond_with_result(result)


@router.patch("/{message_id}/reschedule")
def reschedule(request: Request, message_id: str, body: RescheduleRequest):
    client = TNZAPI(AuthToken=resolve_auth_token(request))
    result = client.Messaging.TTS.Reschedule(MessageID=message_id, SendTime=body.SendTime.isoformat())
    return respond_with_result(result)


@router.patch("/{message_id}/resubmit")
def resubmit(request: Request, message_id: str, body: ResubmitRequest):
    client = TNZAPI(AuthToken=resolve_auth_token(request))
    result = client.Messaging.TTS.Resubmit(MessageID=message_id, SendTime=body.SendTime.isoformat())
    return respond_with_result(result)


@router.patch("/{message_id}/pacing")
def pacing(request: Request, message_id: str, body: PacingRequest):
    client = TNZAPI(AuthToken=resolve_auth_token(request))
    result = client.Messaging.TTS.Pacing(MessageID=message_id, NumberOfOperators=body.NumberOfOperators)
    return respond_with_result(result)
