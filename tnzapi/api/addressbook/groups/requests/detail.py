import requests
import asyncio

from tnzapi.api.addressbook.groups.requests._common import Common
from tnzapi.api.addressbook.groups.responses.group_api_result import GroupApiResult

class GroupDetail(Common):
    
    """ Constructor """
    def __init__(self, kwargs):
        
        super().__init__(kwargs)

        self.SetArgsChild(kwargs)

    """ Set Args """
    def SetArgsChild(self, kwargs):
               
        for key, value in kwargs.items():
          
            if key == "GroupID":
                
                self.GroupID = value

    #
    # Functions
    # 

    def __PostMessage(self):
        try:
            r = requests.get(f"{self.APIURL}/addressbook/group/{self.GroupID}", headers=self.APIHeaders)
            r.raise_for_status()
        except requests.exceptions.HTTPError as e:
            return GroupApiResult(response=r)
        except requests.exceptions.RequestException as e:  # This is the correct syntax
            return GroupApiResult(error=str(e))
        return GroupApiResult(response=r)
    
    async def __PostMessageAsync(self):
        
        return self.__PostMessage()

    def Detail(self, **kwargs):
        
        if kwargs != None and len(kwargs) > 0:
            self.__init__(kwargs)

        if not self.AuthToken:
            return GroupApiResult(error="Missing Auth Token")
        
        if not self.GroupID:
            return GroupApiResult(error="Missing GroupID - Please specify ConactID")
        
        return self.__PostMessage()
    
    async def DetailAsync(self, **kwargs):
        
        if kwargs != None and len(kwargs) > 0:
            self.__init__(kwargs)

        if not self.AuthToken:
            return GroupApiResult(error="Missing Auth Token")
        
        if not self.GroupID:
            return GroupApiResult(error="Missing GroupID - Please specify ConactID")
        
        return await asyncio.create_task(self.__PostMessageAsync())

    #
    # Global functions
    #
    def __repr__(self):
        return self.__pretty__(self.APIData)

    def __str__(self):

        return 'GroupDetail(AuthToken='+self.AuthToken+ ')'