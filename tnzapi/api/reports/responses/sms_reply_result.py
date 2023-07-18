import json
import requests

from tnzapi.api.reports.dtos.sms_reply_dto import SMSReplyDTO
from tnzapi.api.reports.dtos.sms_reply_recipient_dto import SMSReplyRecipientDTO
from tnzapi.api.reports.dtos.sms_reply_recipient_reply_dto import SMSReplyRecipientReplyDTO
from tnzapi.core.dtos.error_with_message_id_dto import ErrorWithMessagIDDTO

from tnzapi.helpers.functions import Functions

class SMSReplyResult(object):

    def __init__(self,**kwargs):

        self.SMSReceived = []

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

            data = SMSReplyDTO()

            for key, value in response.items():

                if key == "Recipients":
                    
                    recipients = []

                    for recip in value:
                        
                        recipient = SMSReplyRecipientDTO()

                        for prop in recip:
                            
                            if prop == "SMSReplies":
                                
                                messages = []
                            
                                for reply in recip[prop]:
                                
                                    message = SMSReplyRecipientReplyDTO()

                                    for rprop in reply:
                                        
                                        setattr(message,rprop,reply[rprop])

                                    messages.append(message)

                                setattr(recipient, prop, messages)

                            else:
                                
                                setattr(recipient, prop, recip[prop])

                        recipients.append(recipient)

                    setattr(data, key, recipients)

                else:
                    
                    setattr(data, key, value)

            self.Data = data

    """ Data """
    @property
    def Data(self) -> SMSReplyDTO:

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
        return 'SMSReplyResult()'
    
