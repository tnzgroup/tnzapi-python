import requests
import asyncio

from tnzapi.api.messaging.dtos.tts_api_request_dto import TTSApiRequestDTO
from tnzapi.api.messaging.requests._common import Common
from tnzapi.api.messaging.responses import MessageApiResult
from tnzapi.core.messaging import Keypad
from tnzapi.helpers.functions import Functions

class TTSApi(Common):

    """ Constructor """
    def __init__(self, kwargs):

        super().__init__(kwargs)

        self.SetArgsChild(kwargs)

    """ Destructor """
    def __del__(self):
        
        self.APIMessageData = None

    """ Set Args """
    def SetArgsChild(self, kwargs):

        #super().SetArgs(kwargs)

        message_data = TTSApiRequestDTO()

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
            
            if key == "TTSVoiceType":
                setattr(message_data, "Voice", value)
                continue

            if hasattr(message_data, key):
                setattr(message_data, key, value)

        self.APIMessageData = message_data

    """ API Data """
    @property
    def APIMessageData(self) -> TTSApiRequestDTO:
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

    """ Private function to POST message to TNZ REST API """
    def __PostMessage(self):
        
        try:
            r = requests.post(f"{self.APIURL}/send/tts", data=Functions.__json_dump_dto__(self, self.APIData), headers=self.APIHeaders)
            r.raise_for_status()
        except requests.exceptions.HTTPError as e:
            return MessageApiResult(response=r)
        except requests.exceptions.RequestException as e:  # This is the correct syntax
            return MessageApiResult(error=str(e))

        return MessageApiResult(response=r)

    """ Private async function to POST message to TNZ REST API """
    async def __PostMessageAsync(self):

        return self.__PostMessage()
    
    def AddKeypadData(self, keypadObj):

        #self.KeypadList.append(keypadObj.Data)
        self.APIMessageData.Keypads.append(keypadObj.Data)

    """ AddKeypad Function """
    def AddKeypad(self, **kwargs):

        keypad = Keypad(**kwargs)

        self.AddKeypadData(keypad)

    def MapKeypadList(self, keypads):
        
        keypad_list = []

        for keypad in keypads:
            keypad_list.append(keypad.Data)

        return keypad_list


    """ Function to send message """
    def SendMessage(self, **kwargs):

        if kwargs != None and len(kwargs) > 0:
            self.__init__(kwargs)

        if not self.AuthToken :

            if not self.Sender :
                return MessageApiResult(error="Missing AuthToken")
            
            if not self.APIKey :
                return MessageApiResult(error="Missing AuthToken")

        if self.WebhookCallbackURL and not self.WebhookCallbackFormat :
            return MessageApiResult(error="Missing WebhookCallbackFormat - JSON or XML")
        
        # Backward compatibility
        if self.Recipients:
            for recipient in self.Recipients:
                self.APIMessageData.Destinations.append(recipient)

        if self.SendMode:
            self.APIMessageData.Mode = self.SendMode
        
        if not self.APIMessageData.Destinations:
            return MessageApiResult(error="Empty destination(s)")

        if not self.APIMessageData.MessageToPeople:
            return MessageApiResult(error="Empty MessageToPeople")

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

        if self.WebhookCallbackURL and not self.WebhookCallbackFormat :
            return MessageApiResult(error="Missing WebhookCallbackFormat - JSON or XML")
        
        # Backward compatibility
        if self.Recipients:
            for recipient in self.Recipients:
                self.APIMessageData.Destinations.append(recipient)

        if self.SendMode:
            self.APIMessageData.Mode = self.SendMode
        
        if not self.APIMessageData.Destinations:
            return MessageApiResult(error="Empty destination(s)")

        if not self.APIMessageData.MessageToPeople:
            return MessageApiResult(error="Empty MessageToPeople")

        return await asyncio.create_task(self.__PostMessageAsync())
    
    #
    # Backward compatiblity
    #

    # Recipicents & Attachments been taken care in common class

    @property
    def MessageID(self): return self.APIMessageData.MessageID
    
    @MessageID.setter
    def MessageID(self,val): self.APIMessageData.MessageID = val

    @property
    def Reference(self): return self.APIMessageData.Reference
    
    @Reference.setter
    def Reference(self,val): self.APIMessageData.Reference = val

    @property
    def WebhookCallbackURL(self): return self.APIMessageData.WebhookCallbackURL
    
    @WebhookCallbackURL.setter
    def WebhookCallbackURL(self,val): self.APIMessageData.WebhookCallbackURL = val

    @property
    def WebhookCallbackFormat(self): return self.APIMessageData.WebhookCallbackFormat
    
    @WebhookCallbackFormat.setter
    def WebhookCallbackFormat(self,val): self.APIMessageData.WebhookCallbackFormat = val

    @property
    def SendTime(self): return self.APIMessageData.SendTime
    
    @SendTime.setter
    def SendTime(self,val): self.APIMessageData.SendTime = val

    @property
    def TimeZone(self): return self.APIMessageData.TimeZone
    
    @TimeZone.setter
    def TimeZone(self,val): self.APIMessageData.TimeZone = val

    @property
    def SubAccount(self): return self.APIMessageData.SubAccount
    
    @SubAccount.setter
    def SubAccount(self,val): self.APIMessageData.SubAccount = val

    @property
    def Department(self): return self.APIMessageData.Department
    
    @Department.setter
    def Department(self,val): self.APIMessageData.Department = val

    @property
    def ChargeCode(self): return self.APIMessageData.ChargeCode
    
    @ChargeCode.setter
    def ChargeCode(self,val): self.APIMessageData.ChargeCode = val

    @property
    def CallerID(self): return self.APIMessageData.CallerID

    @CallerID.setter
    def CallerID(self,val): self.APIMessageData.CallerID = val

    @property
    def BillingAccount(self): return self.APIMessageData.BillingAccount

    @BillingAccount.setter
    def BillingAccount(self,val): self.APIMessageData.BillingAccount = val

    @property
    def ReportTo(self): return self.APIMessageData.ReportTo

    @ReportTo.setter
    def ReportTo(self,val): self.APIMessageData.ReportTo = val
    
    @property
    def RetryAttempts(self): return self.APIMessageData.RetryAttempts

    @RetryAttempts.setter
    def RetryAttempts(self,val): self.APIMessageData.RetryAttempts = val

    @property
    def RetryPeriod(self): return self.APIMessageData.RetryPeriod

    @RetryPeriod.setter
    def RetryPeriod(self,val): self.APIMessageData.RetryPeriod = val

    @property
    def MessageToPeople(self): return self.APIMessageData.MessageToPeople

    @MessageToPeople.setter
    def MessageToPeople(self,val): self.APIMessageData.MessageToPeople = val

    @property
    def MessageToAnswerphones(self): return self.APIMessageData.MessageToAnswerphones

    @MessageToAnswerphones.setter
    def MessageToAnswerphones(self,val): self.APIMessageData.MessageToAnswerphones = val
    
    @property
    def CallRouteMessageToPeople(self): return self.APIMessageData.CallRouteMessageToPeople

    @CallRouteMessageToPeople.setter
    def CallRouteMessageToPeople(self,val): self.APIMessageData.CallRouteMessageToPeople = val

    @property
    def CallRouteMessageToOperators(self): return self.APIMessageData.CallRouteMessageToOperators

    @CallRouteMessageToOperators.setter
    def CallRouteMessageToOperators(self,val): self.APIMessageData.CallRouteMessageToOperators = val
    
    @property
    def CallRouteMessageOnWrongKey(self): return self.APIMessageData.CallRouteMessageOnWrongKey

    @CallRouteMessageOnWrongKey.setter
    def CallRouteMessageOnWrongKey(self,val): self.APIMessageData.CallRouteMessageOnWrongKey = val
    
    @property
    def NumberOfOperators(self): return self.APIMessageData.NumberOfOperators

    @NumberOfOperators.setter
    def NumberOfOperators(self,val): self.APIMessageData.NumberOfOperators = val
    
    @property
    def TTSVoiceType(self): return self.APIMessageData.Voice

    @TTSVoiceType.setter
    def TTSVoiceType(self,val): self.APIMessageData.Voice = val
    
    @property
    def Options(self): return self.APIMessageData.Options

    @Options.setter
    def Options(self,val): self.APIMessageData.Options = val
    
    @property
    def Keypads(self): return self.APIMessageData.Keypads

    @Keypads.setter
    def Keypads(self,val):
        for keypad in val:
            self.AddKeypad(keypad)

    @property
    def Destinations(self): return self.APIMessageData.Destinations
    
    @Destinations.setter
    def Destinations(self,val): self.APIMessageData.Destinations = val

    #
    # ./ Backward compatbility
    #

    def __repr__(self):
        return self.__pretty__(self.APIData)

    def __str__(self):

        if self.AuthToken :
            return 'TTS(AuthToken=' + self.AuthToken + ')'

        return 'TTS(Sender='+self.Sender+', APIKey='+str(self.APIKey)+ ')'