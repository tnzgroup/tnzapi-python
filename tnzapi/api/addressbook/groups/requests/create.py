import requests
import asyncio

from tnzapi.api.addressbook.groups.dtos.group_model import GroupModel
from tnzapi.api.addressbook.groups.requests._common import Common
from tnzapi.api.addressbook.groups.responses.group_api_result import GroupApiResult

from tnzapi.helpers.functions import Functions

class GroupCreate(Common):
    
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
            r = requests.post(f"{self.APIURL}/addressbook/group", Functions.__json_dump_dto__(self, self.Data), headers=self.APIHeaders)
            r.raise_for_status()
        except requests.exceptions.HTTPError as e:
            return GroupApiResult(response=r)
        except requests.exceptions.RequestException as e:  # This is the correct syntax
            return GroupApiResult(error=str(e))
        
        return GroupApiResult(response=r)
    
    async def __PostMessageAsync(self):
        
        return self.__PostMessage()

    def Create(self, **kwargs):
        
        if kwargs != None and len(kwargs) > 0:
            self.__init__(kwargs)

        if not self.AuthToken:
            return GroupApiResult(error="Missing Auth Token")
          
        return self.__PostMessage()
    
    async def CreateAsync(self, **kwargs):
        
        if kwargs != None and len(kwargs) > 0:
            self.__init__(kwargs)

        if not self.AuthToken:
            return GroupApiResult(error="Missing Auth Token")
        
        return await asyncio.create_task(self.__PostMessageAsync())

    #
    # Global functions
    #
    def __repr__(self):
        return self.__pretty__(self.APIData)

    def __str__(self):

        return 'GroupCreate(AuthToken='+self.AuthToken+ ')'