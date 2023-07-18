from tnzapi.api.addressbook.contacts.dtos.contact_list_api_result_dto import ContactListApiResultDTO
from tnzapi.api.addressbook.contacts.dtos.contact_model import ContactModel
from tnzapi.core.dtos.error_dto import ErrorDTO
from tnzapi.helpers.functions import Functions

class ContactListApiResult(object):

    def __init__(self, **kwargs):

        for key, value in kwargs.items():
            
            if key == "response":
                self.ParseResponse(value)
            
            if key == "error":
                self.Data.Result = "Error"
                self.Data.ErrorMessage = value

    def ParseResponse(self, r):

        if r.text:

            self.__response_string__ = r.text

            response = Functions.__parsejson__(self,r.text)

            data = ContactListApiResultDTO()

            for key, value in response.items():

                if key == "Contacts":
                    
                    contacts = []

                    for entity in value:
                        
                        contact = ContactModel()
                        
                        for prop in entity:
                            
                            setattr(contact, prop, entity[prop])

                        contacts.append(contact)

                    setattr(data, key, contacts)

                else:
                    
                    setattr(data, key, value)

            self.Data = data

    """ Data """
    @property
    def Data(self) -> ContactListApiResultDTO:
        
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
