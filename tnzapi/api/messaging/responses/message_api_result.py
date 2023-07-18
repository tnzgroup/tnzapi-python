from tnzapi.api.messaging.dtos.message_api_result_dto import MessageApiResultDTO
from tnzapi.core.dtos.error_dto import ErrorDTO
from tnzapi.core.dtos.error_with_message_id_dto import ErrorWithMessagIDDTO
from tnzapi.helpers.functions import Functions

class MessageApiResult(object):

    def __init__(self, **kwargs):

        for key, value in kwargs.items():
            
            if key == "response":
                #print(key)
                self.ParseResponse(value)
            
            if key == "error":
                self.Data = MessageApiResultDTO(
                    Result = "Error",
                    ErrorMessage = [value]
                )

    def ParseResponse(self, r):

        if r.text:

            self.__response_string__ = r.text

            response = Functions.__parsejson__(self,r.text)

            data = MessageApiResultDTO()

            for key, value in response.items():
                                      
                setattr(data, key, value)

            self.Data = data

    """ Data """
    @property
    def Data(self) -> MessageApiResultDTO:
        
        if self.__data.Result != "Success":
            
            if self.__data.MessageID != None:

                return ErrorWithMessagIDDTO(
                    Result=self.__data.Result,
                    MessageID=self.__data.MessageID,
                    ErrorMessage=self.__data.ErrorMessage
                )
            
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
        return 'MessageResult('+ self.__response_string__ +')'

    