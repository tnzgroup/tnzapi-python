#from tnzapi import __Sender__, __APIKey__, __APIVersion__, __APIURL__

from tnzapi import _config
from tnzapi.api.addressbook.contacts.dtos.contact_model import ContactModel
from tnzapi.api.addressbook.groups.dtos.group_model import GroupModel
from tnzapi.api.messaging.dtos.recipient_model import RecipientModel
from tnzapi.helpers.functions import Functions

class Common:

    AuthToken       = _config.__AuthToken__
    Sender          = _config.__Sender__
    APIKey          = _config.__APIKey__
    APIVersion      = _config.__APIVersion__
    APIURL          = _config.__APIURL__
    APIHeaders      = _config.__APIHeaders__

    Attachments     = []
    Recipients      = []

    SendMode        = ""

    """ Constructor """
    def __init__(self, kwargs):

        #print("super().__init__()")

        self.AuthToken       = _config.__AuthToken__
        self.Sender          = _config.__Sender__
        self.APIKey          = _config.__APIKey__
        self.APIVersion      = _config.__APIVersion__
        self.APIURL          = _config.__APIURL__
        self.APIHeaders      = _config.__APIHeaders__

        self.Attachments     = []
        self.Recipients      = []

        self.SendMode        = ""

        self.SetArgsCommon(kwargs)

    def __del__(self):

        self.AuthToken      = ""
        self.Sender         = ""
        self.APIKey         = ""
        self.APIVersion     = ""
        self.APIURL         = ""
        self.APIHeaders     = ""

        self.Attachments     = []
        self.Recipients      = []

        self.SendMode        = ""
    

    """ Set Common Args """
    def SetArgsCommon(self, kwargs):

        #print("super().SetArgs()")
        #print(kwargs)

        #
        # AuthToken / Send / APIKey can be overriden in the TNZAPI.Send.xxx() functions
        # Default initialization happens in /__init__.py
        #

        if "AuthToken" in kwargs:
            self.AuthToken = _config.__AuthToken__ = kwargs.pop("AuthToken")
            self.APIHeaders["Authorization"] = _config.__APIHeaders__["Authorization"] = f"Basic {self.AuthToken}"

        if "Recipients" in kwargs:
            # clearing recipients as it generates duplication on async mode

            self.Recipients = []

            for recipient in kwargs.pop("Recipients"):
                self.AddRecipient(recipient)

        if "Attachments" in kwargs:
            # clearing attachments as it generates duplication on async mode

            self.Attachments = []

            for attachment in kwargs.pop("Attachments"):
                self.AddAttachment(attachment)
        
        if "SendMode" in kwargs:
            self.SendMode = kwargs.pop("SendMode")

    """ Add Recipient """
    def AddRecipient(self, recipient):
        
        if recipient:

            if isinstance(recipient,str):
                
                dest = {
                    "Recipient": recipient
                }

                self.Recipients.append(dest)
            
            elif isinstance(recipient, (list, tuple)):
                
                for key in recipient:
                    
                    dest = {
                        "Recipient": key
                    }

                    self.Recipients.append(dest)

            elif isinstance(recipient, RecipientModel):
                
                self.Recipients.append(recipient)

            elif isinstance(recipient, ContactModel):
                
                dest = {
                    "ContactID": recipient.ContactID
                }

                self.Recipients.append(dest)

            elif isinstance(recipient, GroupModel):
                
                dest = {
                    "GroupID": recipient.GroupID
                }

                self.Recipients.append(dest)

            elif isinstance(recipient,dict):
                
                self.Recipients.append(recipient)

        #print(self.Recipients)
            

    """ Add Attachment """
    def AddAttachment(self, attachment):
        
        if attachment:
            if isinstance(attachment,str):

                file = {
                    "Name": self.__getfilename__(attachment),
                    "Data": self.__getfilecontent__(attachment)
                }

                self.Attachments.append(file)

            elif isinstance(attachment, (list, tuple)):

                for key in attachment:

                    file = {
                        "Name": self.__getfilename__(key),
                        "Data": self.__getfilecontent__(key)
                    }

                    self.Attachments.append(file)

    def __getfilename__(self,filename):

        return Functions.__getfilename__(self, filename)

    def __getfilecontent__(self,filename):
        return Functions.__getfilecontents__(self, filename)
    
    def __pretty__(self,obj):

        return Functions.__pretty__(self,obj)