import requests
import asyncio

from tnzapi.api.addressbook.contactgroups.dtos.contact_group_api_create_request_dto import ContactGroupApiCreateRequestDTO
from tnzapi.api.addressbook.contactgroups.responses.contact_group_api_result import ContactGroupApiResult
from tnzapi.api.addressbook.contactgroups.requests._common import Common
from tnzapi.helpers.functions import Functions

class ContactGroupCreate(Common):
    
    """ Constructor """
    def __init__(self, kwargs):
        
        super().__init__(kwargs)

    #
    # Properties
    #

    @property
    def Data(self):
        return ContactGroupApiCreateRequestDTO(
            GroupID=self.GroupID
        )
    
    #
    # Functions
    # 

    def __PostMessage(self):
        try:
            r = requests.post(f"{self.APIURL}/addressbook/contact/{self.ContactID}/group", Functions.__json_dump_dto__(self, self.Data), headers=self.APIHeaders)
            r.raise_for_status()
        except requests.exceptions.HTTPError as e:
            return ContactGroupApiResult(response=r)
        except requests.exceptions.RequestException as e:  # This is the correct syntax
            return ContactGroupApiResult(error=str(e))
        
        return ContactGroupApiResult(response=r)
    
    async def __PostMessageAsync(self):
        
        return self.__PostMessage()

    def Create(self, **kwargs):
        
        if kwargs != None and len(kwargs) > 0:
            self.__init__(kwargs)

        if not self.AuthToken:
            return ContactGroupApiResult(error="Missing Auth Token")
        
        if not self.ContactID:
            return ContactGroupApiResult(error="Missing ContactID")
        
        if not self.GroupID:
            return ContactGroupApiResult(error="Missing GroupID")
          
        return self.__PostMessage()
    
    async def CreateAsync(self, **kwargs):
        
        if kwargs != None and len(kwargs) > 0:
            self.__init__(kwargs)

        if not self.AuthToken:
            return ContactGroupApiResult(error="Missing Auth Token")
        
        if not self.ContactID:
            return ContactGroupApiResult(error="Missing ContactID")
        
        if not self.GroupID:
            return ContactGroupApiResult(error="Missing GroupID")
        
        return await asyncio.create_task(self.__PostMessageAsync())

    #
    # Global functions
    #
    def __repr__(self):
        return self.__pretty__(self.APIData)

    def __str__(self):

        return 'ContactGroupCreate(AuthToken='+self.AuthToken+ ')'