# Opt-Out Management

Programmatically manage contacts who have unsubscribed, so you can meet your obligations under anti-spam
regulations. Opt-outs are managed on a `SubAccount`, `Department`, and message-type (`DestType`) basis: a
contact can opt out of SMS marketing while still receiving important Email alerts, since each channel is
suppressed independently. Access it directly as `client.OptOut` — there's no intermediate `Configuration`
facade in this SDK.

Once a destination is opted out, sending to it doesn't fail outright: the API accepts the request, but
delivery is blocked and the response reports a `"Destination is blacklisted"` result. This gives you a
clear audit trail rather than a hard error. Use `List(...)` below to retrieve the full opt-out list for
auditing, reporting, or syncing with your own CRM.

→ [Common parameters & authentication](../README.md#opt-out-management)

`DestType` is a plain string field, not an enum type: this SDK has no equivalent of a typed `OptOutDestType`
enum. Accepted values, matched case-insensitively, are `fax`, `text`, `sms`, `email`, `speech`, and `voice`
— `sms` is accepted as an alias of `text`, and `voice` as an alias of `speech`. Comma-join multiple values
in a single string to apply to more than one channel at once, e.g. `"SMS,Email"`; whitespace around each
comma-separated part is tolerated on the way in, and stripped before the value is sent to the API. Any
value outside this list, on its own or as part of a comma-joined string, fails validation client-side with
`Result="Failed"` before any request is sent.

## Quick example

```python
from tnzapi import TNZAPI

client = TNZAPI(AuthToken="[Your Auth Token]")

response = client.OptOut.Create(
    DestType="SMS",
    Destination="+64211234567",
    Notes="Requested via support call",
)

if response.Result == "Success":
    print(f"Created OptOut ID={response.ID}")
```

## Fields (`OptOutRequest`)

| Field | Type | Description |
|---|---|---|
| `DestType` | `str` | Required. The channel this entry applies to. See the accepted values above. |
| `Destination` | `str` | The destination to suppress, e.g. `"+6421003004"` or an email address. Use `Destination` or `ContactID`, not both. |
| `ContactID` | `str` | Opt out an addressbook contact instead of a raw destination. Use `Destination` or `ContactID`, not both. |
| `SubAccount` | `str` | Scope this entry to a sub-account. Empty applies to all sub-accounts. |
| `Department` | `str` | Scope this entry to a department. Empty applies to all departments. |
| `StopMessage` | `str` | The opt-out phrase detected, e.g. `"Stop sending me these messages"`. |
| `Notes` | `str` | Free-text notes. |

## Code samples

### Create a single entry

Suppress future sends to one destination on a specific channel. `DestType` and either `Destination` or
`ContactID` are required; `Create(...)` validates both client-side before sending anything.

```python
response = client.OptOut.Create(
    DestType="SMS",
    Destination="+64211234567",
    Notes="Requested via support call",
)

if response.Result == "Success":
    print(f"Created OptOut ID={response.ID}")
```

### Opt out an addressbook contact

Suppress an addressbook contact by `ContactID` instead of a raw destination. Set `ContactID` or
`Destination`, not both.

```python
response = client.OptOut.Create(
    DestType="Email",
    ContactID="[Contact ID]",
)
```

### Opt out multiple destinations at once

`CreateBatch(DestType, Destination=None, Destinations=None, ContactID=None, ContactIDs=None, SubAccount=None, Department=None)`
takes explicit parameters rather than a builder or model — a different calling convention from every other
method on this page. It requires `DestType` plus at least one of `Destination`, `Destinations`,
`ContactID`, or `ContactIDs`; `SubAccount`/`Department` apply the same scoping as on a single entry, but
there's no `StopMessage`/`Notes` on the batch call.

```python
batch_response = client.OptOut.CreateBatch(
    DestType="SMS,Email",
    Destinations=["+64211234567", "+64221234567"],
)

if batch_response.Result == "Success":
    print(f"Batch opt-out created: ID={batch_response.ID}")
```

**Note:** `CreateBatch(...)` returns a single response object (the same shape as `Create(...)`/
`Details(...)`, with one `ID` field), not a list of one entry per destination. If you need the individual
opt-out records the batch created, look them up afterwards with `List(...)` filtered by
`DestType`/`ContactID`, or by the destinations you originally submitted.

### Update

Change the notes or scoping on an existing entry. `Update(...)` takes either a plain `OptOutID` string or
the response object a prior call returned, extracting its `ID` field automatically in the latter case.
This is a partial PATCH: only the fields you pass are changed, and unlike `Create(...)`, `DestType` is
only validated if you actually supply it in the call. `DestType` and `Destination`/`ContactID` can be
changed the same way, though moving an entry to a different destination is unusual — deleting and
re-creating is more common for that case.

```python
updated = client.OptOut.Update(response, Notes="Confirmed via follow-up call")

# A plain OptOutID string still works too, e.g. one stored from an earlier session
client.OptOut.Update(response.ID, Notes="Confirmed via follow-up call")
```

### Details, Delete, and List

Look up a single entry, remove an opt-out, or page through the full suppression list, filtering by
channel with a plain `DestType` string. The lookup method here is plural `Details(...)` — a real naming
inconsistency versus [Addressbook](addressbook.md)'s singular `Detail(...)` elsewhere in this SDK, worth
double-checking if you're switching between the two. `Details(...)` takes a plain `OptOutID` string only
(an empty or missing one raises `ValueError`); `Delete(...)` accepts either the string or the response
object, same as `Update(...)` above.

```python
details = client.OptOut.Details(response.ID)

client.OptOut.Delete(response)

list_result = client.OptOut.List(DestType="SMS", TimePeriod=30)

if list_result.Result == "Success":
    for entry in list_result.OptOuts:
        print(f"{entry.get('Destination')}, {entry.get('DestType')}")
```

`List(...)`'s signature is `List(TimePeriod=None, DestType=None, ContactID=None, Page=1, RecordsPerPage=100)`.
Two details are easy to miss if you're used to the rest of this SDK: `Page` comes *before*
`RecordsPerPage` in the parameter order, and the default `RecordsPerPage` is `100`, not the `20` used by
every other paginated method in this SDK. Both differences matter if you're calling positionally rather
than by keyword. Like every other `List(...)` in this SDK, it only ever returns the requested page — it
never auto-walks every page on your behalf.

### Full lifecycle

```python
destination = "+64211234567"

created = client.OptOut.Create(
    DestType="SMS",
    Destination=destination,
)

if created.Result != "Success":
    print("Create failed:", created.ErrorMessage)
else:
    opt_out_id = created.ID
    print(f"{destination} added to opt-out list ({opt_out_id})")

    client.OptOut.Delete(opt_out_id)
    print(f"{destination} removed from opt-out list")

    check = client.OptOut.Details(opt_out_id)
    print("Confirmed gone after removal:", check.Result != "Success")
```

## Response

### `Create(...)`/`Details(...)`/`Update(...)`/`Delete(...)`/`CreateBatch(...)` response

- `Result`, `ErrorMessage` — standard response fields.
- `ID` — this entry's ID. Note the field is plain `ID`, not `OptOutID`.
- `DestType` / `Destination` / `ContactID` / `SubAccount` / `Department` / `StopMessage` / `Notes` —
  echoed back. See the Fields table above.
- `OriginalMessage` — the original inbound message that triggered the opt-out, when it was created
  automatically from a `[[STOP]]`-style reply rather than via this API.
- `CreatedTimeLocal` / `CreatedTimeUTC` / `CreatedTimeUTC_RFC3339` — when the entry was created, in local
  time, UTC, and RFC3339 UTC respectively.
- `UpdatedTimeLocal` / `UpdatedTimeUTC` / `UpdatedTimeUTC_RFC3339` — when the entry was last updated.
- `Timezone` — timezone the local timestamps above are expressed in.

`CreateBatch(...)` returns this same response shape. See the note above the code sample above; it is
**not** a list of the destinations submitted.

### `List(...)` response

- `Result`, `ErrorMessage` — standard response fields.
- `TotalRecords` / `RecordsPerPage` / `PageCount` / `Page` (`int`) — pagination.
- `OptOuts` (`list[dict]`) — the matching entries for this page, each dict shaped like `Details(...)`'s
  result fields above. As elsewhere in this SDK, these are plain dicts: use `entry.get("Destination")`,
  not attribute access.

`OptOutResponse`/`OptOutListResponse` were named `...DTO` before this SDK's public response types dropped
that internal-architecture suffix; the old names still work (they emit a `DeprecationWarning`) — see
[messaging.md](messaging.md#response-shape).

## See also

- [README — Opt-Out Management](../README.md#opt-out-management)
- [Samples — optout_samples.py](../samples/optout/optout_samples.py)
