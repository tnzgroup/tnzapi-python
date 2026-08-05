class Messaging:

    def __init__(self, user):
        self.user = user

    @property
    def SMS(self):
        from tnzapi.api.v300.messaging.builders.sms import SMS
        return SMS(self.user)

    @property
    def Email(self):
        from tnzapi.api.v300.messaging.builders.email import Email
        return Email(self.user)

    @property
    def Fax(self):
        from tnzapi.api.v300.messaging.builders.fax import Fax
        return Fax(self.user)

    @property
    def TTS(self):
        from tnzapi.api.v300.messaging.builders.tts import TTS
        return TTS(self.user)

    @property
    def Voice(self):
        from tnzapi.api.v300.messaging.builders.voice import Voice
        return Voice(self.user)

    @property
    def WhatsApp(self):
        from tnzapi.api.v300.messaging.builders.whatsapp import WhatsApp
        return WhatsApp(self.user)

    @property
    def RCS(self):
        from tnzapi.api.v300.messaging.builders.rcs import RCS
        return RCS(self.user)

    @property
    def Workflow(self):
        from tnzapi.api.v300.messaging.builders.workflow import Workflow
        return Workflow(self.user)
