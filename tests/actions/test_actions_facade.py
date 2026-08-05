from tnzapi.api.v300.actions import Actions


def test_actions_exposes_abort(api_user):
    actions = Actions(api_user)
    assert actions.Abort is not None


def test_actions_exposes_reschedule(api_user):
    actions = Actions(api_user)
    assert actions.Reschedule is not None


def test_actions_exposes_resubmit(api_user):
    actions = Actions(api_user)
    assert actions.Resubmit is not None


def test_actions_exposes_pacing(api_user):
    actions = Actions(api_user)
    assert actions.Pacing is not None
