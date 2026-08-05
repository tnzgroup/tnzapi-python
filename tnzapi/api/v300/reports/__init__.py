class Reports:

    def __init__(self, user):
        self.user = user

    @property
    def Status(self):
        from tnzapi.api.v300.reports.builders.status import Status
        return Status(self.user)

    @property
    def SMSReceived(self):
        from tnzapi.api.v300.reports.builders.sms_received import SMSReceived
        return SMSReceived(self.user)

    @property
    def SMSReply(self):
        from tnzapi.api.v300.reports.builders.sms_reply import SMSReply
        return SMSReply(self.user)
