import requests
import asyncio


from tnzapi.api.addressbook.contactgroups.requests._common import Common
from tnzapi.api.addressbook.contactgroups.responses.contact_group_list_api_result import ContactGroupListApiResult

from tnzapi.core.dtos.list_request_dto import ListRequestDTO

class ContactGroupList(Common):
    
    """ Constructor """
    def __init__(self, kwargs):
        
        super().__init__(kwargs)

        self.Data = ListRequestDTO()

        self.SetArgsChild(kwargs)

    """ Set Args """
    def SetArgsChild(self, kwargs):
        
        list_request = self.Data
               
        for key, value in kwargs.items():
          
            if key == "ContactID":
                
                self.ContactID = value

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
        
        return f"{self.APIURL}/addressbook/contact/{self.ContactID}/group/list?recordsPerPage={self.Data.RecordsPerPage}&page={self.Data.Page}"

    def __PostMessage(self):
        try:
            r = requests.get(self.BuildAPIURL, headers=self.APIHeaders)
            r.raise_for_status()
        except requests.exceptions.HTTPError as e:
            return ContactGroupListApiResult(response=r)
        except requests.exceptions.RequestException as e:  # This is the correct syntax
            return ContactGroupListApiResult(error=str(e))
        return ContactGroupListApiResult(response=r)
    
    async def __PostMessageAsync(self):
        
        return self.__PostMessage()

    def List(self, **kwargs):
        
        if kwargs != None and len(kwargs) > 0:
            self.__init__(kwargs)

        if not self.AuthToken:
            return ContactGroupListApiResult(error="Missing Auth Token")
        
        if not self.ContactID:
            return ContactGroupListApiResult(error="Missing ContactID")
        
        return self.__PostMessage()
    
    async def ListAsync(self, **kwargs):
        
        if kwargs != None and len(kwargs) > 0:
            self.__init__(kwargs)

        if not self.AuthToken:
            return ContactGroupListApiResult(error="Missing Auth Token")
        
        if not self.ContactID:
            return ContactGroupListApiResult(error="Missing ContactID")
                
        return await asyncio.create_task(self.__PostMessageAsync())

    #
    # Global functions
    #
    def __repr__(self):
        return self.__pretty__(self.APIData)

    def __str__(self):

        return 'ContactList(AuthToken='+self.AuthToken+ ')'