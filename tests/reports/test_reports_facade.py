from tnzapi.api.v300.reports import Reports


def test_reports_exposes_status(api_user):
    reports = Reports(api_user)
    assert reports.Status is not None


def test_reports_exposes_sms_received(api_user):
    reports = Reports(api_user)
    assert reports.SMSReceived is not None


def test_reports_exposes_sms_reply(api_user):
    reports = Reports(api_user)
    assert reports.SMSReply is not None
