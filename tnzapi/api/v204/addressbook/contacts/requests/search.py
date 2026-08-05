from dataclasses import asdict
from urllib.parse import urlencode
import requests
import asyncio

from tnzapi.api.v204.addressbook.contacts.requests._common import Common
from tnzapi.api.v204.addressbook.contacts.responses.contact_list_api_result import ContactListApiResult
from tnzapi.api.v204.addressbook.contacts.dtos.contact_search_request_dto import ContactSearchRequestDTO

class ContactSearch(Common):
    
    """ Constructor """
    def __init__(self, kwargs):
        
        super().__init__(kwargs)

        self.Data = ContactSearchRequestDTO()

        self.SetArgsChild(kwargs)

    """ Set Args """
    def SetArgsChild(self, kwargs):
        
        conditions = self.Data

        for key, value in kwargs.items():

            if hasattr(conditions, key):
                setattr(conditions, key, value)

        self.Data = conditions

    #
    # Properties
    #

    @property
    def Data(self) -> ContactSearchRequestDTO:
        return self.__data
    
    @Data.setter
    def Data(self,val):
        self.__data = val

    def build_query_string(self, dto: ContactSearchRequestDTO) -> str:
        dto_dict = asdict(dto)
        filtered = {k: v for k, v in dto_dict.items() if v != "" and v is not None}
        return urlencode(filtered)

    #
    # Functions
    # 

    def __PostMessage(self):
        try:
            r = requests.get(f"{self.APIURL}/addressbook/contact/search?{self.build_query_string(self.Data)}", headers=self.APIHeaders)
            r.raise_for_status()
        except requests.exceptions.HTTPError as e:
            return ContactListApiResult(response=r)
        except requests.exceptions.RequestException as e:  # This is the correct syntax
            return ContactListApiResult(error=str(e))
        return ContactListApiResult(response=r)
    
    async def __PostMessageAsync(self):
        
        return self.__PostMessage()

    def Search(self, **kwargs):
        
        if kwargs != None and len(kwargs) > 0:
            self.__init__(kwargs)

        if not self.AuthToken:
            return ContactListApiResult(error="Missing Auth Token")
        
        return self.__PostMessage()
    
    async def SearchAsync(self, **kwargs):
        
        if kwargs != None and len(kwargs) > 0:
            self.__init__(kwargs)

        if not self.AuthToken:
            return ContactListApiResult(error="Missing Auth Token")
        
        return await asyncio.create_task(self.__PostMessageAsync())

    #
    # Global functions
    #
    def __repr__(self):
        return self.__pretty__(self.APIData)

    def __str__(self):

        return 'ContactSearch(AuthToken='+self.AuthToken+ ')'