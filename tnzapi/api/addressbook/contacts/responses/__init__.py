from tnzapi import _config

class TNZAPI():

    def __init__(self, **kwargs):
        for key, value in kwargs.items():

            if key == "AuthToken":
                self.AuthToken = _config.__AuthToken__ = value
                _config.__APIHeaders__["Authorization"] = f"Basic {self.AuthToken}"

            if key == "Sender":
                self.Sender = _config.__Sender__ = value

            if key == "APIKey":
                self.APIKey = _config.__APIKey__ = value

        self._messaging = None
        self._reports = None
        self._actions = None
        self._addressbook = None

    #
    # Backward compatibility
    #

    @property
    def Send(self, **kwargs):
    
        """ tnzapi.messaging.__init__.py - Messaging() """

        if self._messaging == None:
            from tnzapi.legacy.pre_v203.send import Send

            self._messaging = Send(**kwargs)

        return self._messaging

    @property
    def Get(self, **kwargs):
    
        """ tnzapi.reports._reference.py - Reference() """
        
        if self._reports == None:
            from tnzapi.legacy.pre_v203.get import Get
            self._reports = Get(**kwargs)
    
        return self._reports

    @property
    def Set(self, **kwargs):

        """ tnzapi.actions._reference.py - Reference() """

        if self._actions == None:
            from tnzapi.legacy.pre_v203.set import Set
            self._actions = Set(**kwargs)
    
        return self._actions
    
    #
    # Renamed since v2.3.0.0
    #

    @property
    def Messaging(self, **kwargs):
        
        """ tnzapi.messaging.__init__.py - Messaging() """

        if self._messaging == None:
            from tnzapi.api.messaging.requests import Messaging

            self._messaging = Messaging(**kwargs)

        return self._messaging
    
    @property
    def Reports(self, **kwargs):
    
        """ tnzapi.reports._reference.py - Reference() """
        
        if self._reports == None:
            from tnzapi.api.reports.requests import Reports
            self._reports = Reports(**kwargs)
    
        return self._reports
    
    @property
    def Actions(self, **kwargs):

        """ tnzapi.actions._reference.py - Reference() """

        if self._actions == None:
            from tnzapi.api.actions.requests import Actions
            self._actions = Actions(**kwargs)
    
        return self._actions
    
    @property
    def Addressbook(self, **kwargs):
        
        if self._addressbook == None:
            from tnzapi.api.addressbook import Addressbook
            self._addressbook = Addressbook(**kwargs)

        return self._addressbook