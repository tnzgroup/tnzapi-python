import json
import requests

from tnzapi.api.reports.dtos.sms_message_in_dto import SMSMessageInDTO
from tnzapi.api.reports.dtos.sms_received_dto import SMSReceivedDTO
from tnzapi.core.dtos.error_with_message_id_dto import ErrorWithMessagIDDTO
from tnzapi.helpers.functions import Functions

class SMSReceivedResult(object):

    def __init__(self,**kwargs):
        
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

            data = SMSReceivedDTO()

            for key, value in response.items():

                if key == "Messages":
                    
                    messages = []

                    for msg in value:
                        
                        message = SMSMessageInDTO()
                        
                        for prop in msg:
                            
                            setattr(message, prop, msg[prop])

                        messages.append(message)

                    setattr(data, key, messages)

                else:
                    
                    setattr(data, key, value)

            self.Data = data

    """ Data """
    @property
    def Data(self) -> SMSReceivedDTO:
        
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
        return Functions.__pretty__(self, self.Data)

    def __str__(self):
        return 'SMSReceivedResult()'
