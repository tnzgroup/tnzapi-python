""" Reference to tnzapi.base.get.status_request_result.StatusRequestResult """
def StatusRequestResult(**kwargs):

    from tnzapi.api.reports.responses.status_request_result import StatusRequestResult as run

    response = run(**kwargs)

    return response.Data

""" Reference to tnzapi.base.get.sms_reply_result.SMSReceivedResult """
def SMSReplyResult(**kwargs):

    from tnzapi.api.reports.responses.sms_reply_result import SMSReplyResult as run

    response = run(**kwargs)

    return response.Data

""" Reference to tnzapi.base.get.sms_received_result.SMSReceivedResult """
def SMSReceivedResult(**kwargs):

    from  tnzapi.api.reports.responses.sms_received_result import SMSReceivedResult as run

    response = run(**kwargs)

    return response.Data