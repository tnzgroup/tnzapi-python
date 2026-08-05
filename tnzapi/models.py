"""Shallow public import surface for tnzapi's v300 request and response types.

Every class here is the SAME object as its "deep path" original (e.g.
tnzapi.api.v300.messaging.models.responses.sms_response.SMSResponse) - this module
is a pure re-export with no logic, so a consumer who wants to type-hint
against an SDK result doesn't have to reach into the internal
tnzapi.api.v300... package structure to do it:

    from tnzapi.models import SMSResponse

    def handle(result: SMSResponse) -> None:
        ...
"""

from tnzapi.api.v300.messaging.models.responses.sms_response import SMSResponse
from tnzapi.api.v300.messaging.models.responses.sms_status import SMSStatus
from tnzapi.api.v300.messaging.models.responses.sms_recipient import SMSRecipient
from tnzapi.api.v300.messaging.models.responses.sms_reply import SMSReply
from tnzapi.api.v300.messaging.models.responses.sms_action_result import SMSActionResult
from tnzapi.api.v300.messaging.models.responses.sms_received import SMSReceived

from tnzapi.api.v300.messaging.models.responses.email_response import EmailResponse
from tnzapi.api.v300.messaging.models.responses.email_status import EmailStatus
from tnzapi.api.v300.messaging.models.responses.email_action_result import EmailActionResult

from tnzapi.api.v300.messaging.models.responses.fax_response import FaxResponse
from tnzapi.api.v300.messaging.models.responses.fax_status import FaxStatus
from tnzapi.api.v300.messaging.models.responses.fax_action_result import FaxActionResult

from tnzapi.api.v300.messaging.models.responses.tts_response import TTSResponse
from tnzapi.api.v300.messaging.models.responses.tts_status import TTSStatus
from tnzapi.api.v300.messaging.models.responses.tts_action_result import TTSActionResult

from tnzapi.api.v300.messaging.models.responses.voice_response import VoiceResponse
from tnzapi.api.v300.messaging.models.responses.voice_status import VoiceStatus
from tnzapi.api.v300.messaging.models.responses.voice_action_result import VoiceActionResult

from tnzapi.api.v300.messaging.models.responses.whatsapp_response import WhatsAppResponse
from tnzapi.api.v300.messaging.models.responses.whatsapp_status import WhatsAppStatus
from tnzapi.api.v300.messaging.models.responses.whatsapp_action_result import WhatsAppActionResult
from tnzapi.api.v300.messaging.models.responses.whatsapp_received import WhatsAppReceived

from tnzapi.api.v300.messaging.models.responses.rcs_response import RCSResponse
from tnzapi.api.v300.messaging.models.responses.rcs_status import RCSStatus
from tnzapi.api.v300.messaging.models.responses.rcs_action_result import RCSActionResult
from tnzapi.api.v300.messaging.models.responses.rcs_received import RCSReceived

from tnzapi.api.v300.messaging.models.responses.workflow_response import WorkflowResponse

from tnzapi.api.v300.reports.models.responses.report_error import ReportError

from tnzapi.api.v300.actions.models.responses.action_error import ActionError

from tnzapi.api.v300.addressbook.models.responses.contact_response import ContactResponse
from tnzapi.api.v300.addressbook.models.responses.contact_list_response import ContactListResponse
from tnzapi.api.v300.addressbook.models.responses.contact_group_response import ContactGroupResponse
from tnzapi.api.v300.addressbook.models.responses.contact_group_list_response import ContactGroupListResponse
from tnzapi.api.v300.addressbook.models.responses.group_response import GroupResponse
from tnzapi.api.v300.addressbook.models.responses.group_list_response import GroupListResponse
from tnzapi.api.v300.addressbook.models.responses.group_contact_response import GroupContactResponse
from tnzapi.api.v300.addressbook.models.responses.group_contact_list_response import GroupContactListResponse

from tnzapi.api.v300.optout.models.responses.optout_response import OptOutResponse
from tnzapi.api.v300.optout.models.responses.optout_list_response import OptOutListResponse

from tnzapi.api.v300.messaging.models.requests.sms_request import SMSRequest
from tnzapi.api.v300.messaging.models.requests.email_request import EmailRequest
from tnzapi.api.v300.messaging.models.requests.fax_request import FaxRequest
from tnzapi.api.v300.messaging.models.requests.tts_request import TTSRequest
from tnzapi.api.v300.messaging.models.requests.voice_request import VoiceRequest
from tnzapi.api.v300.messaging.models.requests.whatsapp_request import WhatsAppRequest
from tnzapi.api.v300.messaging.models.requests.rcs_request import RCSRequest
from tnzapi.api.v300.messaging.models.requests.workflow_request import WorkflowRequest

from tnzapi.api.v300.addressbook.models.requests.contact_request import ContactRequest
from tnzapi.api.v300.addressbook.models.requests.group_request import GroupRequest

from tnzapi.api.v300.optout.models.requests.optout_request import OptOutRequest
from tnzapi.api.v300.optout.models.requests.optout_batch_request import OptOutBatchRequest

__all__ = [
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
