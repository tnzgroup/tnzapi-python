from datetime import datetime
import requests
import json
import asyncio

from tnzapi.api.actions.requests._common import Common
from tnzapi.api.actions.responses import ActionApiResult

class Reschedule(Common):

    SendTime    = datetime.now()

    """ Constructor """
    def __init__(self, kwargs):

        super().__init__(kwargs)

        self.SetArgsChild(kwargs)

    """ Destructor """
    def __del__(self):
        self.SendTime = ""

    """ Update Data """
    def SetArgsChild(self, kwargs):

        #super().SetArgs(kwargs)

        for key, value in kwargs.items():

            if key == "SendTime":
                self.SendTime = datetime.fromisoformat(value)

    """ API Data """
    @property
    def APIDataWithSender(self):
        return {
            "Sender": self.Sender,
            "APIKey": self.APIKey,
            "MessageID" : self.MessageID,
            "SendTime": self.SendTime.strftime("%Y-%m-%dT%H:%M:%S")
        }

    @property
    def APIDataWithAuthToken(self):
        return {
            "SendTime": self.SendTime.strftime("%Y-%m-%dT%H:%M:%S")
        }

    @property
    def APIData(self):
        if self.AuthToken :
            return self.APIDataWithAuthToken
        return self.APIDataWithSender

    @property
    def BuildAPIURL(self):

        url = self.APIURL+"/set/reschedule"

        if self.AuthToken :
            url = f"{url}/{self.MessageID}"

        return url

    """ Private function to POST message to TNZ REST API """
    def __PostMessage(self):

        try:
            if self.AuthToken :
                r = requests.patch(self.BuildAPIURL, data=json.dumps(self.APIData), headers=self.APIHeaders)
            else :
                r = requests.post(self.BuildAPIURL, data=json.dumps(self.APIData), headers=self.APIHeaders)
            r.raise_for_status()
        except requests.exceptions.HTTPError as e:
            return ActionApiResult(response=r)
        except requests.exceptions.RequestException as e:  # This is the correct syntax
            return ActionApiResult(error=str(e))

        return ActionApiResult(response=r)

    """ Private async function to POST message to TNZ REST API """
    async def __PostMessageAsync(self):

        return self.__PostMessage()

    """ Function to send message """
    def SendRequest(self, **kwargs):

        if kwargs != None and len(kwargs) > 0:
            self.__init__(kwargs)

        if not self.AuthToken :
            if not self.Sender :
                return ActionApiResult(error="Missing AuthToken")
            
            if not self.APIKey :
                return ActionApiResult(error="Missing AuthToken")
        
        if not self.MessageID:
            return ActionApiResult(error="Missing MessageID")

        if not self.SendTime:
            return ActionApiResult(error="Missing SendTime")
        
        return self.__PostMessage()

    """ Async Function to send message """
    async def SendRequestAsync(self, **kwargs):

        if kwargs != None and len(kwargs) > 0:
            self.__init__(kwargs)

        if not self.AuthToken :
            if not self.Sender :
                return ActionApiResult(error="Missing AuthToken")
            
            if not self.APIKey :
                return ActionApiResult(error="Missing AuthToken")
        
        if not self.MessageID:
            return ActionApiResult(error="Missing MessageID")

        if not self.SendTime:
            return ActionApiResult(error="Missing SendTime")
        
        return await asyncio.create_task(self.__PostMessageAsync())

    def __repr__(self):
        return self.__pretty__(self.APIData)

    def __str__(self):

        if self.AuthToken :
            return 'Reschedule(AuthToken='+self.AuthToken+ ')'

        return 'Reschedule(Sender='+self.Sender+', APIKey='+str(self.APIKey)+ ')'