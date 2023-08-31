import requests
import base64
import asyncio

from tnzapi.api.messaging.dtos.voice_api_request_dto import VoiceApiRequestDTO
from tnzapi.api.messaging.requests._common import Common
from tnzapi.api.messaging.responses import MessageApiResult
from tnzapi.core.messaging import Keypad
from tnzapi.helpers.functions import Functions

class VoiceApi(Common):
    
    VoiceFileData = {
        "MessageToPeople": None,
        "MessageToAnswerphones": None,
        "CallRouteMessageToPeople": None,
        "CallRouteMessageToOperators": None,
        "CallRouteMessageOnWrongKey": None
    }

    """ Constructor """
    def __init__(self, kwargs):

        super().__init__(kwargs)

        self.SetArgsChild(kwargs)

    """ Destructor """
    def __del__(self):
        self.APIMessageData = None

    """ Set Args """
    def SetArgsChild(self, kwargs):

        message_data = VoiceApiRequestDTO()

        for key, value in kwargs.items():

            if key == "Recipients":
                for recipient in value:
                    self.AddRecipient(recipient)
                continue
            
            if key == "Attachments":
                for attachment in value:
                    self.AddAttachment(attachment)
                continue

            if key == "Keypads":
                setattr(message_data, key, self.MapKeypadList(value))
                continue
            
            if key == "KeypadOptionRequired":
                setattr(message_data, key, value)
                continue

            if hasattr(message_data, key):
                setattr(message_data, key, value)

        self.APIMessageData = message_data

    """ API Data """
    @property
    def APIMessageData(self) -> VoiceApiRequestDTO:
        return self.__message_data
    
    @APIMessageData.setter
    def APIMessageData(self,value):
        self.__message_data = value

    @property
    def APIDataWithSender(self):
        return {
            "Sender": self.Sender,
            "APIKey": self.APIKey,
            "MessageData" : self.APIMessageData
        }
    
    @property
    def APIDataWithAuthToken(self):
        return {
            "MessageData" : self.APIMessageData
        }

    @property
    def APIData(self):
        if self.AuthToken :
            return self.APIDataWithAuthToken
        return self.APIDataWithSender

    """ Add Message Data """

    #
    # The background logic is lib hold file locations ONLY until SendMessage() fired,
    # when SendMessage() calls __PostMessage() then read file contents from the file locations
    #

    def AddMessageData(self, type, file):

        setattr(self.APIMessageData, type, file)

    def ReadFileContent(self, type, file):

        content = file

        try:
            if open(file,"rb").read():
                content = base64.b64encode(open(file,"rb").read()).decode("utf-8")

            setattr(self.APIMessageData, type, content)
        except:
            return

    def MapMessageData(self):
        
        if self.APIMessageData.MessageToPeople is not None:
            self.ReadFileContent("MessageToPeople",self.APIMessageData.MessageToPeople)

        if self.APIMessageData.MessageToAnswerphones is not None:
            self.ReadFileContent("MessageToAnswerphones",self.APIMessageData.MessageToAnswerphones)

        if self.APIMessageData.CallRouteMessageToPeople is not None:
            self.ReadFileContent("CallRouteMessageToPeople",self.APIMessageData.CallRouteMessageToPeople)
        
        if self.APIMessageData.CallRouteMessageToOperators is not None:
            self.ReadFileContent("CallRouteMessageToOperators",self.APIMessageData.CallRouteMessageToOperators)

        if self.APIMessageData.CallRouteMessageOnWrongKey is not None:
            self.ReadFileContent("CallRouteMessageOnWrongKey",self.APIMessageData.CallRouteMessageOnWrongKey)

    def AddKeypadData(self, keypadObj):
        
        keypad = keypadObj.Data
        
        if keypad.PlayFile != None and keypad.PlayFile != "":
            keypad.PlayFile = base64.b64encode(open(keypad.PlayFile,"rb").read()).decode("utf-8")

        self.APIMessageData.Keypads.append(keypad)
    
    """ Add Keypad """
    def AddKeypad(self, **kwargs):

        keypad = Keypad(**kwargs)
        
        self.AddKeypadData(keypad)

    def MapKeypadList(self, keypads):
        
        keypad_list = []

        for keypad in keypads:
            if keypad.Data.PlayFile != None and keypad.Data.PlayFile != "":
                keypad.Data.PlayFile = base64.b64encode(open(keypad.Data.PlayFile,"rb").read()).decode("utf-8")
            keypad_list.append(keypad.Data)

        return keypad_list


    """ Private function to POST message to TNZ REST API """
    def __PostMessage(self):
        
        #print(Functions.__json_dump_dto__(self, self.APIData))

        try:
            r = requests.post(f"{self.APIURL}/send/voice", data=Functions.__json_dump_dto__(self, self.APIData), headers=self.APIHeaders)
            r.raise_for_status()
        except requests.exceptions.HTTPError as e:
            return MessageApiResult(response=r)
        except requests.exceptions.RequestException as e:  # This is the correct syntax
            return MessageApiResult(error=str(e))

        return MessageApiResult(response=r)

    """ Private async function to POST message to TNZ REST API """
    async def __PostMessageAsync(self):

        return self.__PostMessage()

    """ Function to send message """
    def SendMessage(self, **kwargs):

        if kwargs != None and len(kwargs) > 0:
            self.__init__(kwargs)

        if not self.AuthToken :
            if not self.Sender :
                return MessageApiResult(error="Missing AuthToken")
            
            if not self.APIKey :
                return MessageApiResult(error="Missing AuthToken")

        if self.APIMessageData.WebhookCallbackURL and not self.APIMessageData.WebhookCallbackFormat :
            return MessageApiResult(error="Missing WebhookCallbackFormat - JSON or XML")
        
        # Backward compatibility
        if self.Recipients:
            for recipient in self.Recipients:
                self.APIMessageData.Destinations.append(recipient)

        if not self.APIMessageData.Destinations:
            return MessageApiResult(error="Empty Destination(s)")

        if not self.APIMessageData.MessageToPeople:
            return MessageApiResult(error="Missing MessageToPeople")
        
        if self.SendMode:
            self.APIMessageData.Mode = self.SendMode
        
        self.MapMessageData()

        return self.__PostMessage()

    """ Async Function to send message """
    async def SendMessageAsync(self, **kwargs):

        if kwargs != None and len(kwargs) > 0:
            self.__init__(kwargs)

        if not self.AuthToken :

            if not self.Sender :
                return MessageApiResult(error="Missing AuthToken")
            
            if not self.APIKey :
                return MessageApiResult(error="Missing AuthToken")

        if self.APIMessageData.WebhookCallbackURL and not self.APIMessageData.WebhookCallbackFormat :
            return MessageApiResult(error="Missing WebhookCallbackFormat - JSON or XML")
        
        # Backward compatibility
        if self.Recipients:
            for recipient in self.Recipients:
                self.APIMessageData.Destinations.append(recipient)
        
        if not self.APIMessageData.Destinations:
            return MessageApiResult(error="Empty Destination(s)")

        if not self.APIMessageData.MessageToPeople:
            return MessageApiResult(error="Missing MessageToPeople")
        
        if self.SendMode:
            self.APIMessageData.Mode = self.SendMode
        
        self.MapMessageData()

        return await asyncio.create_task(self.__PostMessageAsync())

    def __repr__(self):
        return self.__pretty__(self.APIData)

    def __str__(self):

        if not self.AuthToken :
            return 'VoiceApi(AuthToken=' + self.AuthToken + ')'

        return 'VoiceApi(Sender='+self.Sender+', APIKey='+str(self.APIKey)+ ')'