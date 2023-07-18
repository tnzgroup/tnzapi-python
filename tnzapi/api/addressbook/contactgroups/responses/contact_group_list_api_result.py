
from tnzapi.api.addressbook.contactgroups.dtos.contact_group_list_api_result_dto import ContactGroupListApiResultDTO
from tnzapi.api.addressbook.contacts.dtos.contact_model import ContactModel
from tnzapi.api.addressbook.groups.dtos.group_model import GroupModel
from tnzapi.core.dtos.error_dto import ErrorDTO
from tnzapi.helpers.functions import Functions

class ContactGroupListApiResult(object):

    def __init__(self, **kwargs):
        
        for key, value in kwargs.items():
            
            if key == "response":
                self.ParseResponse(value)
            
            if key == "error":
                self.Data = ContactGroupListApiResultDTO(
                    Result="Error",
                    ErrorMessage=[value]
                )

    def ParseResponse(self, r):

        if r.text:

            self.__response_string__ = r.text

            response = Functions.__parsejson__(self,r.text)

            data = ContactGroupListApiResultDTO()

            for key, value in response.items():
                
                #if contact is found, process it and check next key/value
                if key == "Contact":
                    
                    contact = ContactModel()

                    for ckey, cval in value.items():
                        if hasattr(contact, ckey):
                            setattr(contact, ckey, cval)

                    setattr(data,key,contact)

                    continue

                if key == "Groups":
                    
                    groups = []

                    for entity in value:
                        
                        group = GroupModel()
                        
                        for prop in entity:
                            
                            setattr(group, prop, entity[prop])

                        groups.append(group)

                    setattr(data, key, groups)

                else:
                    
                    setattr(data, key, value)

            self.Data = data

    """ Data """
    @property
    def Data(self) -> ContactGroupListApiResultDTO:
        
        if self.__data.Result != "Success":
            
            return ErrorDTO(
                Result=self.__data.Result,
                ErrorMessage=self.__data.ErrorMessage
            )
        
        return self.__data
    
    @Data.setter
    def Data(self, val):
        self.__data = val

    def __repr__(self):
        return Functions.__pretty__(self, self.Data)

    def __str__(self):
        return 'ContactResult('+ self.__response_string__ +')'
