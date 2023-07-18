import json
from tnzapi.core.messaging.keypad_dto import KeypadDTO
from tnzapi.helpers.custom_json_encoder import CustomJSONEncoder
from tnzapi.helpers.functions import Functions

class Keypad(object):

    def __init__(self, **kwargs):

        keypad = KeypadDTO()

        for key, value in kwargs.items():
            
            if hasattr(keypad, key):
                setattr(keypad, key, value)

        self.Data = keypad

    """ Data """
    @property
    def Data(self) -> KeypadDTO:
        return self.__data
    
    @Data.setter
    def Data(self, value):
        self.__data = value

    def __repr__(self):
        return Functions.__pretty_class__(self, self.Data)
    
    def __str__(self):
        return json.dumps(dict(self.Data), cls=CustomJSONEncoder, ensure_ascii=False)
