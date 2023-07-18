""" Reference to tnzapi.base.set.set_request_result.ActionResult """
def ActionApiResult(**kwargs):

    from tnzapi.api.actions.responses.action_api_result import ActionApiResult as process

    result = process(**kwargs)

    return result.Data