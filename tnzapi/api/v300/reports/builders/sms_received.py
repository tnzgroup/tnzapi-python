from tnzapi.core.auth import TNZApiUser
from tnzapi.core.legacy_kwargs import accept_legacy_kwargs


class SMSReceived:

    def __init__(self, user: TNZApiUser):
        self.user = user

    @accept_legacy_kwargs({
        "time_period": "TimePeriod", "date_from": "DateFrom", "date_to": "DateTo",
        "records_per_page": "RecordsPerPage", "page": "Page",
    })
    def Poll(self, TimePeriod=None, DateFrom=None, DateTo=None, RecordsPerPage: int = 20, Page: int = 1):

        from tnzapi.api.v300.messaging.builders.sms import SMS

        return SMS(self.user).Received(TimePeriod, DateFrom, DateTo, RecordsPerPage, Page)
