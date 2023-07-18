
from tnzapi.api.addressbook.groups.dtos.group_api_result_dto import GroupApiResultDTO
from tnzapi.api.addressbook.groups.dtos.group_model import GroupModel

from tnzapi.core.dtos.error_dto import ErrorDTO
from tnzapi.helpers.functions import Functions

class GroupApiResult(object):

    def __init__(self, **kwargs):

        self.Data = GroupApiResultDTO()

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

            data = GroupApiResultDTO()

            for key, value in response.items():
                
                #if group is found, process it and check next key/value
                if key == "Group":
                    
                    group = GroupModel()

                    for ckey, cval in value.items():
                        if hasattr(group, ckey):
                            setattr(group, ckey, cval)

                    setattr(data,key,group)

                    continue

                setattr(data, key, value)

            self.Data = data

    """ Data """
    @property
    def Data(self) -> GroupApiResultDTO:
        
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
