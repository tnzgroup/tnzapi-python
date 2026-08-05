class Actions:

    def __init__(self, user):
        self.user = user

    @property
    def Abort(self):
        from tnzapi.api.v300.actions.builders.abort import Abort
        return Abort(self.user)

    @property
    def Reschedule(self):
        from tnzapi.api.v300.actions.builders.reschedule import Reschedule
        return Reschedule(self.user)

    @property
    def Resubmit(self):
        from tnzapi.api.v300.actions.builders.resubmit import Resubmit
        return Resubmit(self.user)

    @property
    def Pacing(self):
        from tnzapi.api.v300.actions.builders.pacing import Pacing
        return Pacing(self.user)
