import requests
import json
import asyncio

from tnzapi.api.reports.requests._common import Common
from tnzapi.api.reports.responses import SMSReceivedResult

class SMSReceived(Common):

    TimePeriod  = 1440
    DateFrom    = None
    DateTo      = None

    RecordsPerPage  = 100
    Page            = 1

    """ Constructor """
    def __init__(self, kwargs):

        super().__init__(kwargs)

        self.SetArgsChild(kwargs)

    """ Set Args """
    def SetArgsChild(self, kwargs):

        #super().SetArgs(kwargs)

        for key, value in kwargs.items():

            if key == "TimePeriod":
                self.TimePeriod = value

            if key == "DateFrom":
                self.DateFrom = value

            if key == "DateTo":
                self.DateTo = value

            if key == "RecordsPerPage":
                self.RecordsPerPage = value

            if key == "Page":
                self.Page = value



    """ API Data """
    @property
    def APIData(self):
        return {
            "Sender": self.Sender,
            "APIKey": self.APIKey,
            "TimePeriod" : self.TimePeriod
        }

    """ API URL """
    @property
    def BuildAPIURL(self):

        url = self.APIURL+"/get/sms/received"

        if self.AuthToken :

            if self.DateFrom and self.DateTo:
                url = f"{url}?dateFrom={self.DateFrom}&dateTo={self.DateTo}&recordsPerPage={self.RecordsPerPage}&page={self.Page}"
            else :
                url = f"{url}?timePeriod={self.TimePeriod}&recordsPerPage={self.RecordsPerPage}&page={self.Page}"

        return url


    """ Private function to POST message to TNZ REST API """
    def __PostMessage(self):

        try:
            if self.AuthToken :
                r = requests.get(self.BuildAPIURL, headers=self.APIHeaders)
            else :
                r = requests.post(self.BuildAPIURL, data=json.dumps(self.APIData), headers=self.APIHeaders)

            r.raise_for_status()
        except requests.exceptions.HTTPError as e:
            return SMSReceivedResult(response=r)
        except requests.exceptions.RequestException as e:  # This is the correct syntax
            return SMSReceivedResult(error=str(e))

        return SMSReceivedResult(response=r)

    """ Private async function to POST message to TNZ REST API """
    async def __PostMessageAsync(self):

        return self.__PostMessage()

    """ Function to send message """
    def Poll(self, **kwargs):

        if kwargs != None and len(kwargs) > 0:
            self.__init__(kwargs)
        
        """ Checking validity """
        if not self.AuthToken :

            if not self.Sender :
                return SMSReceivedResult(error="Missing AuthToken")
            
            if not self.APIKey :
                return SMSReceivedResult(error="Missing AuthToken")
        
        if not self.TimePeriod:
            return SMSReceivedResult(error="Missing TimePeriod")
        
        return self.__PostMessage()

    """ Function to send message """
    async def PollAsync(self, **kwargs):

        if kwargs != None and len(kwargs) > 0:
            self.__init__(kwargs)
        
        """ Checking validity """
        if not self.AuthToken :

            if not self.Sender :
                return SMSReceivedResult(error="Missing AuthToken")
            
            if not self.APIKey :
                return SMSReceivedResult(error="Missing AuthToken")
        
        if not self.TimePeriod:

            return SMSReceivedResult(error="Missing TimePeriod")
        
        return await asyncio.create_task(self.__PostMessageAsync())

    def __repr__(self):
        return self.__pretty__(self.APIData)

    def __str__(self):

        if self.AuthToken :
            return 'SMSReceived(AuthToken=' + self.AuthToken + ')'

        return 'SMSReceived(Sender='+self.Sender+', APIKey='+str(self.APIKey)+ ')'