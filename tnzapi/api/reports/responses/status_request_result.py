import json
import requests

from tnzapi.api.reports.dtos.recipient_dto import RecipientDTO
from tnzapi.api.reports.dtos.status_dto import StatusDTO
from tnzapi.core.dtos.error_with_message_id_dto import ErrorWithMessagIDDTO
from tnzapi.helpers.functions import Functions

class StatusRequestResult(object):

    def __init__(self, **kwargs):
        
        for key, value in kwargs.items():
            
            if key == "response":
                #print(key)
                self.ParseResponse(value)
            
            if key == "error":
                self.__data.Result = "Error"
                self.__data.ErrorMessage = value
    
    def ParseResponse(self, r):

        if r.text:

            response = Functions.__parsejson__(self,r.text)

            data = StatusDTO()

            for key, value in response.items():

                if key == "Recipients":
                    
                    recipients = []

                    for recip in value:
                        
                        recipient = RecipientDTO()
                        
                        for prop in recip:
                            
                            setattr(recipient, prop, recip[prop])

                        recipients.append(recipient)

                    setattr(data, key, recipients)

                else:
                    
                    setattr(data, key, value)

            self.Data = data
                
    
    """ Data """
    @property
    def Data(self) -> StatusDTO:
        
        if self.__data.Result != "Success":
            
            return ErrorWithMessagIDDTO(
                Result=self.__data.Result,
                MessageID=self.__data.MessageID,
                ErrorMessage=self.__data.ErrorMessage
            )
        
        return self.__data
    
    @Data.setter
    def Data(self, val):
        self.__data = val

    def __repr__(self):
        return Functions.__pretty_class__(self, self.Data)

    def __str__(self):
        return 'def StatusRequestResult()'