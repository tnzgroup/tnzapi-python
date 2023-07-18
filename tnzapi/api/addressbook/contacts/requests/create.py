import requests
import asyncio

from tnzapi.api.addressbook.contacts.dtos.contact_model import ContactModel
from tnzapi.api.addressbook.contacts.requests._common import Common
from tnzapi.api.addressbook.contacts.responses.contact_api_result import ContactApiResult
from tnzapi.helpers.functions import Functions

class ContactCreate(Common):
    
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
            r = requests.post(f"{self.APIURL}/addressbook/contact", Functions.__json_dump_dto__(self, self.Data), headers=self.APIHeaders)
            r.raise_for_status()
        except requests.exceptions.HTTPError as e:
            return ContactApiResult(response=r)
        except requests.exceptions.RequestException as e:  # This is the correct syntax
            return ContactApiResult(error=str(e))
        
        return ContactApiResult(response=r)
    
    async def __PostMessageAsync(self):
        
        return self.__PostMessage()

    def Create(self, **kwargs):
        
        if kwargs != None and len(kwargs) > 0:
            self.__init__(kwargs)

        if not self.AuthToken:
            return ContactApiResult(error="Missing Auth Token")
          
        return self.__PostMessage()
    
    async def CreateAsync(self, **kwargs):
        
        if kwargs != None and len(kwargs) > 0:
            self.__init__(kwargs)

        if not self.AuthToken:
            return ContactApiResult(error="Missing Auth Token")
        
        return await asyncio.create_task(self.__PostMessageAsync())

    #
    # Global functions
    #
    def __repr__(self):
        return self.__pretty__(self.APIData)

    def __str__(self):

        return 'ContactCreate(AuthToken='+self.AuthToken+ ')'