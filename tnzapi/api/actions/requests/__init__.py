class Actions(object):

    def __init__(self):
        self._abort = None
        self._pacing = None
        self._reschedule = None
        self._resubmit = None

    @property
    def Abort(self,**kwargs):

        from tnzapi.api.actions.requests.abort import Abort

        if self._abort != None:
            del(self._abort)
            
        self._abort = Abort(kwargs)

        return self._abort
    
    @property
    def Pacing(self,**kwargs):

        from tnzapi.api.actions.requests.pacing import Pacing

        if self._pacing != None:
            del(self._pacing)
            
        self._pacing = Pacing(kwargs)

        return self._pacing

    @property
    def Reschedule(self,**kwargs):

        from tnzapi.api.actions.requests.reschedule import Reschedule

        if self._reschedule != None:
            del(self._reschedule)

        self._reschedule = Reschedule(kwargs)
        
        return self._reschedule

    @property
    def Resubmit(self,**kwargs):

        from tnzapi.api.actions.requests.resubmit import Resubmit

        if self._resubmit != None:
            del(self._resubmit)
            
        self._resubmit = Resubmit(kwargs)

        return self._resubmit