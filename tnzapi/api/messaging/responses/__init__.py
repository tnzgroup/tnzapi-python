""" Reference to tnzapi.base.get.message_result.MessageResult """
def MessageApiResult(**kwargs):
    
    from tnzapi.api.messaging.responses.message_api_result import MessageApiResult as process

    response = process(**kwargs)

    return response.Data