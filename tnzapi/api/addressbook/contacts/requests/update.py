import requests
import asyncio

from tnzapi.api.addressbook.contacts.dtos.contact_model import ContactModel
from tnzapi.api.addressbook.contacts.requests._common import Common
from tnzapi.api.addressbook.contacts.responses.contact_api_result import ContactApiResult
from tnzapi.helpers.functions import Functions

class ContactUpdate(Common):
    
    """ Constructor """
    def __init__(self, kwargs):
        
        super().__init__(kwargs)

        self.Data = ContactModel()

        self.SetArgsChild(kwargs)

    """ Set Args """
    def SetArgsChild(self, kwargs):

        contact = self.Data

        for key, value in kwargs.items():

            if hasattr(contact, key):
                setattr(contact, key, value)

        self.Data = contact

    #
    # Properties
    #

    @property
    def Data(self):
        return self.__data
    
    @Data.setter
    def Data(self,val):
        self.__data = val

    #
    # Functions
    # 

    def __PostMessage(self):
        try:
            r = requests.patch(f"{self.APIURL}/addressbook/contact/{self.ContactID}", Functions.__json_dump_dto__(self, self.Data), headers=self.APIHeaders)
            r.raise_for_status()
        except requests.exceptions.HTTPError as e:
            return ContactApiResult(response=r)
        except requests.exceptions.RequestException as e:  # This is the correct syntax
            return ContactApiResult(error=str(e))
        
        return ContactApiResult(response=r)
    
    async def __PostMessageAsync(self):
        
        return self.__PostMessage()

    def Update(self, **kwargs):
        
        if kwargs != None and len(kwargs) > 0:
            self.__init__(kwargs)

        if not self.AuthToken:
            return ContactApiResult(error="Missing Auth Token")
        
        if not self.ContactID:
            return ContactApiResult(error="Missing ContactID")
          
        return self.__PostMessage()
    
    async def UpdateAsync(self, **kwargs):
        
        if kwargs != None and len(kwargs) > 0:
            self.__init__(kwargs)

        if not self.AuthToken:
            return ContactApiResult(error="Missing Auth Token")
        
        if not self.ContactID:
            return ContactApiResult(error="Missing Contact ID")
        
        return await asyncio.create_task(self.__PostMessageAsync())

    #
    # Global functions
    #
    def __repr__(self):
        return self.__pretty__(self.APIData)

    def __str__(self):

        return 'ContactUpdate(AuthToken='+self.AuthToken+ ')'