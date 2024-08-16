import requests
import asyncio

from tnzapi.api.addressbook.groups.dtos.group_model import GroupModel
from tnzapi.api.addressbook.groups.requests._common import Common
from tnzapi.api.addressbook.groups.responses.group_api_result import GroupApiResult
from tnzapi.helpers.functions import Functions

class GroupUpdate(Common):
    
    """ Constructor """
    def __init__(self, kwargs):
        
        super().__init__(kwargs)

        self.Data = GroupModel()

        self.SetArgsChild(kwargs)

    """ Set Args """
    def SetArgsChild(self, kwargs):

        group = self.Data

        for key, value in kwargs.items():

            if hasattr(group, key):
                setattr(group, key, value)
        
        self.Data = group

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
            r = requests.patch(f"{self.APIURL}/addressbook/group/{self.GroupID}", Functions.__json_dump_dto__(self, self.Data), headers=self.APIHeaders)
            r.raise_for_status()
        except requests.exceptions.HTTPError as e:
            return GroupApiResult(response=r)
        except requests.exceptions.RequestException as e:  # This is the correct syntax
            return GroupApiResult(error=str(e))
        
        return GroupApiResult(response=r)
    
    async def __PostMessageAsync(self):
        
        return self.__PostMessage()

    def Update(self, **kwargs):
        
        if kwargs != None and len(kwargs) > 0:
            self.__init__(kwargs)

        if not self.AuthToken:
            return GroupApiResult(error="Missing Auth Token")
        
        if not self.GroupID:
            return GroupApiResult(error="Missing GroupID")
          
        return self.__PostMessage()
    
    async def UpdateAsync(self, **kwargs):
        
        if kwargs != None and len(kwargs) > 0:
            self.__init__(kwargs)

        if not self.AuthToken:
            return GroupApiResult(error="Missing Auth Token")
        
        if not self.GroupID:
            return GroupApiResult(error="Missing GroupID")
        
        return await asyncio.create_task(self.__PostMessageAsync())

    #
    # Global functions
    #
    def __repr__(self):
        return self.__pretty__(self.APIData)

    def __str__(self):

        return 'GroupUpdate(AuthToken='+self.AuthToken+ ')'