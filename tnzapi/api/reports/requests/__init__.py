class Reports(object):

    def __init__(self):
        self._status = None
        self._sms_received = None
        self._sms_reply = None
        self._result = None

    @property
    def Status(self,**kwargs):

        from tnzapi.api.reports.requests.status import Status

        if self._status != None:
            del(self._status)
            
        self._status = Status(kwargs)

        return self._status
    
    @property
    def SMSReceived(self,**kwargs):

        from tnzapi.api.reports.requests.sms_received import SMSReceived

        if self._sms_received != None:
            del(self._sms_received)
            
        self._sms_received = SMSReceived(kwargs)

        return self._sms_received

    @property
    def SMSReply(self, **kwargs):

        from tnzapi.api.reports.requests.sms_reply import SMSReply

        if self._sms_reply != None:
            del(self._sms_reply)

        self._sms_reply = SMSReply(kwargs)

        return self._sms_reply
    