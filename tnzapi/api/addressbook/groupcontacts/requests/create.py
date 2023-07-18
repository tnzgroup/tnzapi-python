import requests
import asyncio

from tnzapi.api.addressbook.groupcontacts.requests._common import Common
from tnzapi.api.addressbook.groupcontacts.dtos.group_contact_api_create_request_dto import GroupContactApiCreateRequestDTO
from tnzapi.api.addressbook.groupcontacts.responses.group_contact_api_result import GroupContactApiResult
from tnzapi.helpers.functions import Functions

class GroupContactCreate(Common):
    
    """ Constructor """
    def __init__(self, kwargs):
        
        super().__init__(kwargs)

    #
    # Properties
    #

    @property
    def Data(self):
        return GroupContactApiCreateRequestDTO(
            ContactID=self.ContactID
        )
    
    #
    # Functions
    # 

    def __PostMessage(self):
        try:
            r = requests.post(f"{self.APIURL}/addressbook/group/{self.GroupCode}/contact", Functions.__json_dump_dto__(self, self.Data), headers=self.APIHeaders)
            r.raise_for_status()
        except requests.exceptions.HTTPError as e:
            return GroupContactApiResult(response=r)
        except requests.exceptions.RequestException as e:  # This is the correct syntax
            return GroupContactApiResult(error=str(e))
        
        return GroupContactApiResult(response=r)
    
    async def __PostMessageAsync(self):
        
        return self.__PostMessage()

    def Create(self, **kwargs):
        
        if kwargs != None and len(kwargs) > 0:
            self.__init__(kwargs)

        if not self.AuthToken:
            return GroupContactApiResult(error="Missing Auth Token")
        
        if not self.GroupCode:
            return GroupContactApiResult(error="Missing GroupCode")
        
        if not self.ContactID:
            return GroupContactApiResult(error="Missing ContactID")
          
        return self.__PostMessage()
    
    async def CreateAsync(self, **kwargs):
        
        if kwargs != None and len(kwargs) > 0:
            self.__init__(kwargs)

        if not self.AuthToken:
            return GroupContactApiResult(error="Missing Auth Token")
        
        if not self.GroupCode:
            return GroupContactApiResult(error="Missing GroupCode")
        
        if not self.ContactID:
            return GroupContactApiResult(error="Missing ContactID")
        
        return await asyncio.create_task(self.__PostMessageAsync())

    #
    # Global functions
    #
    def __repr__(self):
        return self.__pretty__(self.APIData)

    def __str__(self):

        return 'GroupContactCreate(AuthToken='+self.AuthToken+ ')'