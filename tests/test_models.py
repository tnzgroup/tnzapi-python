import tnzapi.models as models

EXPECTED_NAMES = [
    "SMSResponse", "SMSStatus", "SMSRecipient", "SMSReply", "SMSActionResult", "SMSReceived",
    "EmailResponse", "EmailStatus", "EmailActionResult",
    "FaxResponse", "FaxStatus", "FaxActionResult",
    "TTSResponse", "TTSStatus", "TTSActionResult",
    "VoiceResponse", "VoiceStatus", "VoiceActionResult",
    "WhatsAppResponse", "WhatsAppStatus", "WhatsAppActionResult", "WhatsAppReceived",
    "RCSResponse", "RCSStatus", "RCSActionResult", "RCSReceived",
    "WorkflowResponse",
    "ReportError",
    "ActionError",
    "ContactResponse", "ContactListResponse", "ContactGroupResponse", "ContactGroupListResponse",
    "GroupResponse", "GroupListResponse", "GroupContactResponse", "GroupContactListResponse",
    "OptOutResponse", "OptOutListResponse",
    "SMSRequest", "EmailRequest", "FaxRequest", "TTSRequest", "VoiceRequest",
    "WhatsAppRequest", "RCSRequest", "WorkflowRequest",
    "ContactRequest", "GroupRequest",
    "OptOutRequest", "OptOutBatchRequest",
]


def test_all_matches_actual_exported_names():
    assert set(models.__all__) == set(EXPECTED_NAMES)


def test_every_expected_name_is_importable():
    for name in EXPECTED_NAMES:
        assert hasattr(models, name), f"tnzapi.models is missing {name}"


def test_sms_response_identity_matches_source_module():
    from tnzapi.api.v300.messaging.models.responses.sms_response import SMSResponse as SourceSMSResponse
    assert models.SMSResponse is SourceSMSResponse


def test_optout_list_response_identity_matches_source_module():
    from tnzapi.api.v300.optout.models.responses.optout_list_response import OptOutListResponse as SourceOptOutListResponse
    assert models.OptOutListResponse is SourceOptOutListResponse


def test_sms_request_identity_matches_source_module():
    from tnzapi.api.v300.messaging.models.requests.sms_request import SMSRequest as SourceSMSRequest
    assert models.SMSRequest is SourceSMSRequest
