import requests
import asyncio

from tnzapi.api.messaging.dtos.fax_api_request_dto import FaxApiRequestDTO
from tnzapi.api.messaging.requests._common import Common
from tnzapi.api.messaging.responses import MessageApiResult
from tnzapi.helpers.functions import Functions

class FaxApi(Common):

    """ Constructor """
    def __init__(self, kwargs):

        super().__init__(kwargs)

        self.SetArgsChild(kwargs)

    """ Destructor """
    def __del__(self):
        
        self.APIMessageData = None

    """ Update Data """
    def SetArgsChild(self, kwargs):

        #super().SetArgs(kwargs)

        message_data = FaxApiRequestDTO()

        for key, value in kwargs.items():

            if key == "Recipients":
                for recipient in value:
                    self.AddRecipient(recipient)
                continue
            
            if key == "Attachments":
                for attachment in value:
                    self.AddAttachment(attachment)
                continue

            if hasattr(message_data, key):
                setattr(message_data, key, value)

        self.APIMessageData = message_data

    """ API Data """
    @property
    def APIMessageData(self) -> FaxApiRequestDTO:
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
            r = requests.post(f"{self.APIURL}/send/fax", data=Functions.__json_dump_dto__(self, self.APIData), headers=self.APIHeaders)
            r.raise_for_status()
        except requests.exceptions.HTTPError as e:
            return MessageApiResult(response=r)
        except requests.exceptions.RequestException as e:  # This is the correct syntax
            return MessageApiResult(error=str(e))

        return MessageApiResult(response=r)

    """ Private function to POST message to TNZ REST API """
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
            
        # Backward compatibility
        if self.Recipients:
            for recipient in self.Recipients:
                self.APIMessageData.Destinations.append(recipient)

        # Backward compatibility
        if self.Attachments:
            for attachment in self.Attachments:
                self.APIMessageData.Files.append(attachment)

        if self.SendMode:
            self.APIMessageData.Mode = self.SendMode

        if self.APIMessageData.WebhookCallbackURL and not self.APIMessageData.WebhookCallbackFormat :
            return MessageApiResult(error="Missing WebhookCallbackFormat - JSON or XML")
        
        if not self.APIMessageData.Destinations:
            return MessageApiResult(error="Empty Destination(s)")

        if not self.APIMessageData.Files:
            return MessageApiResult(error="Empty Files(s)")

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
            
        # Backward compatibility
        if self.Recipients:
            for recipient in self.Recipients:
                self.APIMessageData.Destinations.append(recipient)

        # Backward compatibility
        if self.Attachments:
            for attachment in self.Attachments:
                self.APIMessageData.Files.append(attachment)

        if self.SendMode:
            self.APIMessageData.Mode = self.SendMode

        if self.APIMessageData.WebhookCallbackURL and not self.APIMessageData.WebhookCallbackFormat :
            return MessageApiResult(error="Missing WebhookCallbackFormat - JSON or XML")
        
        if not self.APIMessageData.Destinations:
            return MessageApiResult(error="Empty Destination(s)")

        if not self.APIMessageData.Files:
            return MessageApiResult(error="Empty Files(s)")

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
    def Resolution(self): return self.APIMessageData.Resolution

    @Resolution.setter
    def Resolution(self,val): self.APIMessageData.Resolution = val

    @property
    def CSID(self): return self.APIMessageData.CSID

    @CSID.setter
    def CSID(self,val): self.APIMessageData.CSID = val

    @property
    def StampFormat(self): return self.APIMessageData.StampFormat

    @StampFormat.setter
    def StampFormat(self,val): self.APIMessageData.StampFormat = val

    @property
    def WatermarkFolder(self): return self.APIMessageData.WatermarkFolder

    @WatermarkFolder.setter
    def WatermarkFolder(self,val): self.APIMessageData.WatermarkFolder = val

    @property
    def WatermarkFirstPage(self): return self.APIMessageData.WatermarkFirstPage

    @WatermarkFirstPage.setter
    def WatermarkFirstPage(self,val): self.APIMessageData.WatermarkFirstPage = val

    @property
    def WatermarkAllPages(self): return self.APIMessageData.WatermarkAllPages

    @WatermarkAllPages.setter
    def WatermarkAllPages(self,val): self.APIMessageData.WatermarkAllPages = val

    @property
    def RetryAttempts(self): return self.APIMessageData.RetryAttempts

    @RetryAttempts.setter
    def RetryAttempts(self,val): self.APIMessageData.RetryAttempts = val

    @property
    def RetryPeriod(self): return self.APIMessageData.RetryPeriod

    @RetryPeriod.setter
    def RetryPeriod(self,val): self.APIMessageData.RetryPeriod = val

    @property
    def Destinations(self): return self.APIMessageData.Destinations
    
    @Destinations.setter
    def Destinations(self,val): self.APIMessageData.Destinations = val

    @property
    def Files(self): return self.APIMessageData.Files
    
    @Files.setter
    def Files(self,val): self.APIMessageData.Files = val

    #
    # ./ Backward compatbility
    #

    def __repr__(self):
        return self.__pretty__(self.APIData)

    def __str__(self):

        if self.AuthToken :
            return 'FaxApi(AuthToken=' + self.AuthToken + ')'

        return 'FaxApi(Sender='+self.Sender+', APIKey='+str(self.APIKey)+ ')'