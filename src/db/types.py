from datetime import date, time

from msgspec import Struct


class CallReportLog(Struct, frozen=True, kw_only=True):
    """
    Represents a single Call Report Log entry.

    Attributes
    ----------
    log_id :class:'int'
        ID of the log that is created. Auto-generated via DB
    rep_num :class:'int'
        Rep phone number, in the format: 1231231234 (NO spaces / Dashes)
    date :class:'date'
        Date when the call took place
    time :class:'time'
        Time when the call took place
    customer_num :class:'int'
        Customers phone number, in the format: 1231231234 (NO spaces / Dashes)
    mins_on_phone :class:'int'
        How long the phone call was in minutes
    caller_location :class:'str'
        Location of the caller, if outgoing. (Inbound calls are labeled "INCOMING")
    """

    rep_num: int
    date: date
    time: time
    customer_num: int
    mins_on_phone: int
    caller_location: str

class CallReportRep(Struct, frozen=True, kw_only=True):
    """
    Represents a single Call Report Rep Log entry.

    Attributes
    ----------
    rep_id :class:'int'
        ID of the log that is created. Auto-generated via DB
    rep_num :class:'int'
        Rep phone number, in the format: 1231231234 (NO spaces / Dashes)
    rep_name :class:'str'
        Reps name, corresponding to their number.
    """
    rep_num: int
    rep_name: str | None
