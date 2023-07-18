

from tnzapi.api.addressbook.groups.dtos.group_list_api_result_dto import GroupListApiResultDTO
from tnzapi.api.addressbook.groups.dtos.group_model import GroupModel
from tnzapi.core.dtos.error_dto import ErrorDTO
from tnzapi.helpers.functions import Functions

class GroupListApiResult(object):

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

            data = GroupListApiResultDTO()

            for key, value in response.items():

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
    def Data(self) -> GroupListApiResultDTO:
        
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
