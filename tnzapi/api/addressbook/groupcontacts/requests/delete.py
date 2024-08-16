import requests
import asyncio

from tnzapi.api.addressbook.groupcontacts.requests._common import Common
from tnzapi.api.addressbook.groupcontacts.responses.group_contact_api_result import GroupContactApiResult

class GroupContactDelete(Common):
    
    """ Constructor """
    def __init__(self, kwargs):
        
        super().__init__(kwargs)

        self.SetArgsChild(kwargs)

    """ Set Args """
    def SetArgsChild(self, kwargs):
               
        for key, value in kwargs.items():
          
            if key == "ContactID":
                
                self.ContactID = value

            if key == "GroupID":
                
                self.GroupID = value

    #
    # Functions
    # 

    def __PostMessage(self):
        try:
            r = requests.delete(f"{self.APIURL}/addressbook/group/{self.GroupID}/contact/{self.ContactID}", headers=self.APIHeaders)
            r.raise_for_status()
        except requests.exceptions.HTTPError as e:
            return GroupContactApiResult(response=r)
        except requests.exceptions.RequestException as e:  # This is the correct syntax
            return GroupContactApiResult(error=str(e))
        return GroupContactApiResult(response=r)
    
    async def __PostMessageAsync(self):
        
        return self.__PostMessage()

    def Delete(self, **kwargs):
        
        if kwargs != None and len(kwargs) > 0:
            self.__init__(kwargs)

        if not self.AuthToken:
            return GroupContactApiResult(error="Missing Auth Token")
        
        if not self.GroupID:
            return GroupContactApiResult(error="Missing GroupID")
        
        if not self.ContactID:
            return GroupContactApiResult(error="Missing ContactID")
        
        return self.__PostMessage()
    
    async def DeleteAsync(self, **kwargs):
        
        if kwargs != None and len(kwargs) > 0:
            self.__init__(kwargs)

        if not self.AuthToken:
            return GroupContactApiResult(error="Missing Auth Token")
        
        if not self.GroupID:
            return GroupContactApiResult(error="Missing GroupID")
        
        if not self.ContactID:
            return GroupContactApiResult(error="Missing ContactID")
                
        return await asyncio.create_task(self.__PostMessageAsync())

    #
    # Global functions
    #
    def __repr__(self):
        return self.__pretty__(self.APIData)

    def __str__(self):

        return 'GroupContactDelete(AuthToken='+self.AuthToken+ ')'