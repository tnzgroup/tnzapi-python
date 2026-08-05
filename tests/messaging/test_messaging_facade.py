from tnzapi.api.v300.messaging import Messaging


def test_messaging_exposes_sms(api_user):
    messaging = Messaging(api_user)
    assert messaging.SMS is not None


def test_messaging_exposes_email(api_user):
    messaging = Messaging(api_user)
    assert messaging.Email is not None


def test_messaging_exposes_fax(api_user):
    messaging = Messaging(api_user)
    assert messaging.Fax is not None


def test_messaging_exposes_tts(api_user):
    messaging = Messaging(api_user)
    assert messaging.TTS is not None


def test_messaging_exposes_voice(api_user):
    messaging = Messaging(api_user)
    assert messaging.Voice is not None


def test_messaging_exposes_whatsapp(api_user):
    messaging = Messaging(api_user)
    assert messaging.WhatsApp is not None


def test_messaging_exposes_rcs(api_user):
    messaging = Messaging(api_user)
    assert messaging.RCS is not None


def test_messaging_exposes_workflow(api_user):
    messaging = Messaging(api_user)
    assert messaging.Workflow is not None
