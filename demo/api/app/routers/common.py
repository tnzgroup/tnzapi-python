from pydantic import BaseModel, Field, NaiveDatetime


# NaiveDatetime, not datetime: per the API spec, SendTime is always interpreted in the
# message's previously-set Timezone, not a fresh timezone-aware moment - there's no
# Timezone field on Reschedule/Resubmit to pair a UTC offset against. Accepting a
# timezone-aware value here would silently attach a meaningless +HH:MM suffix to the
# wire payload instead of erroring.
class RescheduleRequest(BaseModel):
    SendTime: NaiveDatetime


class ResubmitRequest(BaseModel):
    SendTime: NaiveDatetime


class PacingRequest(BaseModel):
    NumberOfOperators: int = Field(ge=1, le=99999)
