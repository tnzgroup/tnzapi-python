from tnzapi import _config
from tnzapi.helpers.functions import Functions

class Common:

    AuthToken       = _config.__AuthToken__
    Sender          = _config.__Sender__
    APIKey          = _config.__APIKey__
    APIVersion      = _config.__APIVersion__
    APIURL          = _config.__APIURL__
    APIHeaders      = _config.__APIHeaders__

    GroupCode       = ""
    ContactID       = ""

    """ Constructor """
    def __init__(self,kwargs):

        self.AuthToken      = _config.__AuthToken__
        self.Sender         = _config.__Sender__
        self.APIKey         = _config.__APIKey__
        self.APIVersion     = _config.__APIVersion__
        self.APIURL         = _config.__APIURL__
        self.APIHeaders     = _config.__APIHeaders__

        self.GroupCode      = ""
        self.ContactID      = ""
        
        self.SetArgsCommon(kwargs)

    """ Destructor """
    def __del__(self):
        self.AuthToken      = ""
        self.Sender         = ""
        self.APIKey         = ""
        self.APIVersion     = ""
        self.APIURL         = ""
        self.APIHeaders     = ""

        self.GroupCode      = ""
        self.ContactID      = ""

    """ Set Args """
    def SetArgsCommon(self, kwargs):

        #
        # AuthToken / Send / APIKey can be overriden in the TNZAPI.Get.xxx() functions
        # Default initialization happens in /__init__.py
        #
        if "AuthToken" in kwargs:
            self.AuthToken = _config.__AuthToken__ = kwargs.pop("AuthToken")
            self.APIHeaders["Authorization"] = _config.__APIHeaders__["Authorization"] = f"Basic {self.AuthToken}"
            self.APIHeaders["User-Agent"] = f"tnzapi-python-{self.APIVersion}"

        if "Sender" in kwargs:
            self.Sender = _config.__Sender__ = kwargs.pop("Sender")

        if "APIKey" in kwargs:
            self.APIKey = _config.__APIKey__ = kwargs.pop("APIKey")
        
        if "GroupCode" in kwargs:
            self.GroupCode = kwargs.pop("GroupCode")

        if "ContactID" in kwargs:
            self.ContactID = kwargs.pop("ContactID")
    
    def __pretty__(self,obj):

        return Functions.__pretty__(self,obj)