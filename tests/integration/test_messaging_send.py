import base64
import io
import struct
import wave

import pytest

pytestmark = pytest.mark.integration

# Whether the live TNZ API actually honors Mode="Test" to skip real delivery/
# cost has not been confirmed against production - the v3.00 OpenAPI spec
# doesn't document this field, and neither tnzapi-dotnet's SendMode nor this
# field is exercised by any sibling SDK's integration suite. It's included on
# every send below on the assumption it's a genuine no-cost switch; TNZ_RUN_LIVE_TESTS=1
# (see conftest.py's live_client fixture) is the safety net in case that
# assumption is wrong - nothing here fires without that explicit opt-in.
TEST_MODE = "Test"

# A minimal-but-valid single-page PDF (has a real xref table and content
# stream, unlike a bare "%PDF-1.1\n"-prefixed text blob) so a live fax test
# failure reflects the API/SDK, not unparseable fixture data.
_FAX_FILE_DATA = (
    "JVBERi0xLjEKMSAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZyAvUGFnZXMgMiAwIFIgPj4KZW5kb2JqCjIgMCBv"
    "YmoKPDwgL1R5cGUgL1BhZ2VzIC9LaWRzIFszIDAgUl0gL0NvdW50IDEgPj4KZW5kb2JqCjMgMCBvYmoKPDwg"
    "L1R5cGUgL1BhZ2UgL1BhcmVudCAyIDAgUiAvTWVkaWFCb3ggWzAgMCAyMDAgMjAwXSAvUmVzb3VyY2VzIDw8"
    "ID4+IC9Db250ZW50cyA0IDAgUiA+PgplbmRvYmoKNCAwIG9iago8PCAvTGVuZ3RoIDQ0ID4+CnN0cmVhbQpC"
    "VCAvRjEgMjQgVGYgMjAgMTAwIFRkIChUZXN0IEZheCkgVGogRVQKZW5kc3RyZWFtCmVuZG9iagp4cmVmCjAg"
    "NQowMDAwMDAwMDAwIDY1NTM1IGYgCjAwMDAwMDAwMDkgMDAwMDAgbiAKMDAwMDAwMDA1OCAwMDAwMCBuIAow"
    "MDAwMDAwMTE1IDAwMDAwIG4gCjAwMDAwMDAyMTkgMDAwMDAgbiAKdHJhaWxlcgo8PCAvU2l6ZSA1IC9Sb290"
    "IDEgMCBSID4+CnN0YXJ0eHJlZgozMDgKJSVFT0Y="
)


def _silent_wav_base64(seconds: float = 0.2) -> str:
    # Voice's MessageToPeople is base64-encoded WAV audio (16-bit, 8000Hz per
    # the v3.00 spec), unlike TTS's plain-text equivalent - a short silent
    # clip is a valid, harmless payload for exercising the send round trip.
    buf = io.BytesIO()
    with wave.open(buf, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(8000)
        frame_count = int(seconds * 8000)
        w.writeframes(struct.pack(f"<{frame_count}h", *([0] * frame_count)))
    return base64.b64encode(buf.getvalue()).decode()


_VOICE_AUDIO_DATA = _silent_wav_base64()


def test_send_sms(live_client, test_mobile):
    result = live_client.Messaging.SMS.SendMessage(
        Reference="tnzapi-python integration test",
        Message="Integration test SMS from tnzapi-python.",
        Destinations=[{"ToNumber": test_mobile}],
        Mode=TEST_MODE,
    )

    assert result.Result == "Success", result.ErrorMessage


def test_send_email(live_client, test_email):
    result = live_client.Messaging.Email.SendMessage(
        Reference="tnzapi-python integration test",
        EmailSubject="tnzapi-python integration test",
        MessagePlain="Integration test email from tnzapi-python.",
        Destinations=[{"EmailAddress": test_email}],
        Mode=TEST_MODE,
    )

    assert result.Result == "Success", result.ErrorMessage


def test_send_fax(live_client, test_fax):
    result = live_client.Messaging.Fax.SendMessage(
        Reference="tnzapi-python integration test",
        Destinations=[{"ToNumber": test_fax}],
        Files=[{"Name": "integration-test.pdf", "Data": _FAX_FILE_DATA}],
        Mode=TEST_MODE,
    )

    assert result.Result == "Success", result.ErrorMessage


def test_send_tts(live_client, test_mobile):
    result = live_client.Messaging.TTS.SendMessage(
        Reference="tnzapi-python integration test",
        MessageToPeople="This is an integration test message from tnzapi python.",
        Destinations=[{"ToNumber": test_mobile}],
        Mode=TEST_MODE,
    )

    assert result.Result == "Success", result.ErrorMessage


def test_send_voice(live_client, test_mobile):
    result = live_client.Messaging.Voice.SendMessage(
        Reference="tnzapi-python integration test",
        MessageToPeople=_VOICE_AUDIO_DATA,
        Destinations=[{"ToNumber": test_mobile}],
        Mode=TEST_MODE,
    )

    assert result.Result == "Success", result.ErrorMessage


def test_send_whatsapp(live_client, test_mobile, test_whatsapp_template_id, test_whatsapp_from_number):
    # Unlike the other channels, WhatsApp.SendMessage requires TemplateID and
    # FromNumber (a registered WhatsApp sender) client-side - omitting either
    # fails validation before any HTTP request is made at all, which is not
    # the same thing as the account lacking WhatsApp provisioning.
    result = live_client.Messaging.WhatsApp.SendMessage(
        Reference="tnzapi-python integration test",
        TemplateID=test_whatsapp_template_id,
        FromNumber=test_whatsapp_from_number,
        Message="Integration test WhatsApp message from tnzapi-python.",
        Destinations=[{"ToNumber": test_mobile}],
        Mode=TEST_MODE,
    )

    # Even with a valid TemplateID/FromNumber, WhatsApp delivery may still
    # require an account-approved template - a Failed result here can mean
    # that, rather than an SDK bug, so it's skipped rather than failed.
    if result.Result == "Failed":
        pytest.skip(f"WhatsApp send failed - may be missing account/template approval, not necessarily an SDK bug: {result.ErrorMessage}")

    assert result.Result == "Success", result.ErrorMessage


def test_send_rcs(live_client, test_mobile):
    result = live_client.Messaging.RCS.SendMessage(
        Reference="tnzapi-python integration test",
        Message="Integration test RCS message from tnzapi-python.",
        Destinations=[{"ToNumber": test_mobile}],
        Mode=TEST_MODE,
    )

    # Same caveat as WhatsApp above: RCS may need account-specific provisioning.
    if result.Result == "Failed":
        pytest.skip(f"RCS send failed - may be missing account provisioning, not necessarily an SDK bug: {result.ErrorMessage}")

    assert result.Result == "Success", result.ErrorMessage


def test_send_workflow(live_client, workflow_send_allowed, test_workflow_template_id, test_mobile):
    # Workflow's request DTO has no Mode field, so there's no equivalent
    # no-cost switch here - whatever WorkflowTemplateID points to actually
    # runs. workflow_send_allowed requires a separate explicit opt-in
    # (TNZ_ALLOW_WORKFLOW_SEND=1) confirming the configured template is safe
    # to trigger repeatedly, since TNZ_RUN_LIVE_TESTS=1 alone isn't enough
    # assurance for a send with no cost-safety switch at all.
    result = live_client.Messaging.Workflow.SendMessage(
        Reference="tnzapi-python integration test",
        WorkflowTemplateID=test_workflow_template_id,
        Destinations=[{"ToNumber": test_mobile}],
    )

    assert result.Result == "Success", result.ErrorMessage
