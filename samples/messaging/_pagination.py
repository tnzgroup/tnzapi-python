"""Shared pagination-walk helper for the GetAllInbound* recipes in
sms_samples.py/whatsapp_samples.py/rcs_samples.py - all three channels'
Received() calls share the identical Result/PageCount/Messages response
shape, so the "walk every page" loop only needs to be written once.
"""

from collections import namedtuple

PageWalkResult = namedtuple("PageWalkResult", ["messages", "error"])


def WalkAllPages(fetch_page, time_period_minutes: int = 1440, records_per_page: int = 100):
    """fetch_page is a bound Received(...) method - e.g. client.Messaging.SMS.Received.

    Returns a PageWalkResult(messages, error) - error is None on a complete
    walk, or the failing page's ErrorMessage if the walk stopped early, so a
    caller can tell a full result apart from a partial one instead of the two
    being indistinguishable.
    """
    page = 1
    total_pages = 1
    messages = []

    while page <= total_pages:
        result = fetch_page(
            TimePeriod=time_period_minutes,
            RecordsPerPage=records_per_page,
            Page=page
        )
        if result.Result != "Success":
            return PageWalkResult(messages, result.ErrorMessage or result.Result or "unknown error")

        total_pages = result.PageCount or 1
        messages.extend(result.Messages or [])
        page += 1

    return PageWalkResult(messages, None)
