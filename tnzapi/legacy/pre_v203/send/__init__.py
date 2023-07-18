class Send(object):

    def __init__(self):
        self._email = None
        self._fax = None
        self._sms = None
        self._tts = None
        self._voice = None

    def Email(self,**kwargs):

        from tnzapi.api.messaging.requests.email_api import EmailApi

        if self._email != None:
            del(self._email)
        
        self._email = EmailApi(kwargs)

        return self._email
    
    def Fax(self,**kwargs):

        from tnzapi.api.messaging.requests.fax_api import FaxApi

        if self._fax != None:
            del(self._fax)
            
        self._fax = FaxApi(kwargs)

        return self._fax

    def SMS(self,**kwargs):

        from tnzapi.api.messaging.requests.sms_api import SMSApi

        if self._sms != None:
            del(self._sms)
            
        self._sms = SMSApi(kwargs)

        return self._sms

    def TTS(self,**kwargs):

        from tnzapi.api.messaging.requests.tts_api import TTSApi

        if self._tts != None:
            del(self._tts)
            
        self._tts = TTSApi(kwargs)
        
        return self._tts
    
    def Voice(self,**kwargs):

        from tnzapi.api.messaging.requests.voice_api import VoiceApi

        if self._voice != None:
            del(self._voice)
            
        self._voice = VoiceApi(kwargs)

        return self._voice