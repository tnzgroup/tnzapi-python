import requests
import asyncio

from tnzapi.api.addressbook.groups.requests._common import Common
from tnzapi.api.addressbook.groups.responses.group_list_api_result import GroupListApiResult

from tnzapi.core.dtos.list_request_dto import ListRequestDTO

class GroupList(Common):
    
    """ Constructor """
    def __init__(self, kwargs):
        
        super().__init__(kwargs)

        self.Data = ListRequestDTO()

        self.SetArgsChild(kwargs)

    """ Set Args """
    def SetArgsChild(self, kwargs):
        
        list_request = self.Data
               
        for key, value in kwargs.items():
          
            if hasattr(list_request, key):
                setattr(list_request, key, value)

        self.Data = list_request

    #
    # Properties
    #

    @property
    def Data(self) -> ListRequestDTO:
        return self.__data
    
    @Data.setter
    def Data(self,val):
        self.__data = val

    #
    # Functions
    # 

    """ API URL """
    @property
    def BuildAPIURL(self):
        
        return f"{self.APIURL}/addressbook/group/list?recordsPerPage={self.Data.RecordsPerPage}&page={self.Data.Page}"

    def __PostMessage(self):
        try:
            r = requests.get(self.BuildAPIURL, headers=self.APIHeaders)
            r.raise_for_status()
        except requests.exceptions.HTTPError as e:
            return GroupListApiResult(response=r)
        except requests.exceptions.RequestException as e:  # This is the correct syntax
            return GroupListApiResult(error=str(e))
        return GroupListApiResult(response=r)
    
    async def __PostMessageAsync(self):
        
        return self.__PostMessage()

    def List(self, **kwargs):
        
        if kwargs != None and len(kwargs) > 0:
            self.__init__(kwargs)

        if not self.AuthToken:
            return GroupListApiResult(error="Missing Auth Token")
        
        return self.__PostMessage()
    
    async def ListAsync(self, **kwargs):
        
        if kwargs != None and len(kwargs) > 0:
            self.__init__(kwargs)

        if not self.AuthToken:
            return GroupListApiResult(error="Missing Auth Token")
                
        return await asyncio.create_task(self.__PostMessageAsync())

    #
    # Global functions
    #
    def __repr__(self):
        return self.__pretty__(self.APIData)

    def __str__(self):

        return 'GroupList(AuthToken='+self.AuthToken+ ')'