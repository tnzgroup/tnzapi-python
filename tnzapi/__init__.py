from tnzapi import _config

class TNZAPI():

    def __init__(self, **kwargs):
        self.AuthToken = kwargs.get("AuthToken")
        self.BaseURL = kwargs.get("BaseURL")

        for key, value in kwargs.items():

            if key == "AuthToken":
                _config.__AuthToken__ = value
                _config.__APIHeaders__["Authorization"] = f"Basic {value}"

            if key == "Sender":
                self.Sender = _config.__Sender__ = value

            if key == "APIKey":
                self.APIKey = _config.__APIKey__ = value

        self._send = None
        self._get = None
        self._set = None
        self._messaging = None
        self._reports = None
        self._actions = None
        self._addressbook = None
        self._optout = None

    #
    # Backward compatibility
    #

    @property
    def Send(self, **kwargs):

        """ tnzapi.messaging.__init__.py - Messaging() """

        if self._send == None:
            from tnzapi.legacy.pre_v203.send import Send

            self._send = Send(**kwargs)

        return self._send

    @property
    def Get(self, **kwargs):

        """ tnzapi.reports._reference.py - Reference() """

        if self._get == None:
            from tnzapi.legacy.pre_v203.get import Get
            self._get = Get(**kwargs)

        return self._get

    @property
    def Set(self, **kwargs):

        """ tnzapi.actions._reference.py - Reference() """

        if self._set == None:
            from tnzapi.legacy.pre_v203.set import Set
            self._set = Set(**kwargs)

        return self._set
    
    #
    # v3.00 API (Phases 0-6)
    #

    @property
    def Messaging(self):

        """ tnzapi.api.v300.messaging - Messaging() """

        if self._messaging == None:
            from tnzapi.core.auth import TNZApiUser
            from tnzapi.api.v300.messaging import Messaging

            self._messaging = Messaging(TNZApiUser(AuthToken=self.AuthToken, BaseURL=self.BaseURL))

        return self._messaging

    @property
    def Reports(self):

        """ tnzapi.api.v300.reports - Reports() """

        if self._reports == None:
            from tnzapi.core.auth import TNZApiUser
            from tnzapi.api.v300.reports import Reports

            self._reports = Reports(TNZApiUser(AuthToken=self.AuthToken, BaseURL=self.BaseURL))

        return self._reports

    @property
    def Actions(self):

        """ tnzapi.api.v300.actions - Actions() """

        if self._actions == None:
            from tnzapi.core.auth import TNZApiUser
            from tnzapi.api.v300.actions import Actions

            self._actions = Actions(TNZApiUser(AuthToken=self.AuthToken, BaseURL=self.BaseURL))

        return self._actions
    
    @property
    def Addressbook(self):

        """ tnzapi.api.v300.addressbook - Addressbook() """

        if self._addressbook == None:
            from tnzapi.core.auth import TNZApiUser
            from tnzapi.api.v300.addressbook import Addressbook

            self._addressbook = Addressbook(TNZApiUser(AuthToken=self.AuthToken, BaseURL=self.BaseURL))

        return self._addressbook

    @property
    def OptOut(self):

        """ tnzapi.api.v300.optout.builders.optout - OptOut() """

        if self._optout == None:
            from tnzapi.core.auth import TNZApiUser
            from tnzapi.api.v300.optout.builders.optout import OptOut

            self._optout = OptOut(TNZApiUser(AuthToken=self.AuthToken, BaseURL=self.BaseURL))

        return self._optout
