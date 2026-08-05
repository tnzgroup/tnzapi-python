# Addressbook

Centralise your contacts with the Addressbook: a single source of truth that simplifies your integration
and enables data-rich personalisation across every messaging channel. Manage contacts, groups, and
contact–group relationships; keep contact data synchronised with your CRM, HR system, or spreadsheets;
organise contacts into groups to message thousands with a single `GroupID`; and reduce payload size by
referencing a `ContactID`/`GroupID` instead of sending full recipient details on every send. The same
`ContactID`/`GroupID` values documented here work directly as `ContactID=`/`GroupID=` arguments to
`AddDestination(...)` on any messaging channel — see [sms.md](sms.md). Personalisation fields (`FirstName`,
`Company`, `Custom1`–`Custom4`) work as `[[FirstName]]`-style merge tags in your message body, and
contacts/groups created here are also usable directly in the TNZ Dashboard. Groups have no custom fields
of their own; personalisation always comes from the contact.

→ [Common parameters & authentication](../README.md#addressbook)

**Requires Address Book API Access** — your API user needs this permission enabled separately from
general API access: Dashboard → Users → API User → API → Address Book API Access.

`client.Addressbook` exposes four properties, each returning a fresh request object on every access:
`.Contact`, `.Group`, `.ContactGroup`, and `.GroupContact`. This is **flat**: contact–group relationships
are managed through the separate `ContactGroup`/`GroupContact` properties directly off `client.Addressbook`,
not through nested chaining off `Contact` or `Group` themselves.

## Contact

### Fields (`ContactRequest`)

| Field | Type | Description |
|---|---|---|
| `ExType` | `str` | External system type tag, for correlating this contact with your own CRM/system. |
| `ExID` | `str` | External system ID, for correlating this contact with your own CRM/system. |
| `ViewBy` | `str` | Who can view this contact in the Dashboard: `"Account"`, `"SubAccount"`, `"Department"`, or `"No"`. |
| `EditBy` | `str` | Who can edit this contact in the Dashboard, same values as `ViewBy`. |
| `AccessControl` | `str` | `"Limited"` or `"Granted"`. |
| `Attention` | `str` | Personalisation token `[[Attention]]`. |
| `Title` | `str` | e.g. `"Mr"`, `"Dr"`. |
| `Company` | `str` | Personalisation token `[[Company]]`. |
| `RecipDepartment` | `str` | The contact's department at their company. Not related to your TNZ `Department` code. |
| `FirstName` | `str` | Personalisation token `[[FirstName]]`. |
| `LastName` | `str` | Personalisation token `[[LastName]]`. |
| `Position` | `str` | Job title. |
| `StreetAddress` / `Suburb` / `City` / `State` / `Country` / `Postcode` | `str` | Postal address fields. |
| `MainPhone` | `str` | Primary phone number. |
| `AltPhone1`–`AltPhone8` | `str` | Up to 8 additional phone numbers. |
| `MobilePhone` | `str` | Mobile number, used as the SMS/WhatsApp/RCS destination when sending via `ContactID`. |
| `FaxNumber` | `str` | Fax destination. |
| `EmailAddress` | `str` | Email destination. |
| `WebAddress` | `str` | Website URL. |
| `Custom1`–`Custom4` | `str` | Personalisation tokens `[[Custom1]]`–`[[Custom4]]`. |
| `Notes` | `str` | Free-text notes. Not exposed as a personalisation token. |

There's no `DirectPhone` field — this SDK's contact fields stop at `MainPhone` and `AltPhone1`–`AltPhone8`.

### Create

Pass fields as keyword arguments directly to `Create(...)`, or build one first with `Set(...)`/`Build()` if
you want to construct the request ahead of time and pass it as `model=`. Both are equivalent; the samples
below use plain keyword arguments. `model=` also accepts a response object from an earlier call (e.g.
`Detail(...)`), useful for cloning a contact: only the fields the request actually declares are copied
across, so read-only fields like `ContactID`/`Owner`/timestamps are dropped automatically rather than
causing an error.

```python
response = client.Addressbook.Contact.Create(
    Attention="API Test",
    FirstName="API",
    LastName="Test",
    MobilePhone="+64211231234",
    EmailAddress="test@example.com",
    MainPhone="+6491112222",
)

if response.Result == "Success":
    print(f"Created ContactID={response.ContactID}")
```

### Detail

Look up a contact's stored fields by `ContactID`. The method name is singular `Detail(...)`, not
`Details(...)` — a real naming inconsistency versus [OptOut](optout.md)'s `Details(...)` elsewhere in this
SDK, worth double-checking if you're switching between the two. An empty or missing `ContactID` raises
`ValueError` rather than silently sending a broken request.

```python
details = client.Addressbook.Contact.Detail(response.ContactID)

if details.Result == "Success":
    print(f"{details.FirstName} {details.LastName}, {details.EmailAddress}")
```

### Update and Delete

Change or remove a contact. `Update(...)`/`Delete(...)` take either a plain `ContactID` string or the
response object a prior call returned, extracting the ID automatically in the latter case. `Update(...)`
is a partial PATCH: only the fields you pass are changed.

```python
updated = client.Addressbook.Contact.Update(response, Company="Example Company")

client.Addressbook.Contact.Delete(response)

# A plain ContactID string still works too, e.g. one stored from an earlier session
client.Addressbook.Contact.Update(response.ContactID, Company="Example Company")
```

### Search and List

Find contacts by any combination of `EmailAddress` (full match) or
`MobilePhone`/`MainPhone`/`Attention`/`FirstName`/`LastName`/`Company` (partial match), or page through
your full contact list. Both default to `RecordsPerPage=20, Page=1` and only cover the requested page —
this SDK never auto-walks every page on your behalf.

```python
results = client.Addressbook.Contact.Search(
    FirstName="Alice",
    Company="Example Company",
    RecordsPerPage=100,
    Page=1,
)

if results.Result == "Success":
    for contact in results.Contacts:
        print(f"{contact.get('ContactID')}: {contact.get('FirstName')} {contact.get('LastName')}")

page = client.Addressbook.Contact.List(RecordsPerPage=100, Page=1)

if page.Result == "Success":
    for contact in page.Contacts:
        print(f"{contact.get('ContactID')}: {contact.get('FirstName')} {contact.get('LastName')}")
```

## Group

### Fields (`GroupRequest`)

| Field | Type | Description |
|---|---|---|
| `GroupName` | `str` | Display name for the group. |
| `SubAccount` | `str` | Sub-account code. |
| `Department` | `str` | Department code. |
| `ViewEditBy` | `str` | Who can view and edit this group in the Dashboard: `"Account"`, `"SubAccount"`, `"Department"`, or `"No"`. Unlike Contact, Group has one combined permission rather than separate `ViewBy`/`EditBy` fields. |
| `AccessControl` | `str` | `"Limited"` or `"Granted"`. |

### Create

Same keyword-argument pattern as Contact. `GroupCode` is server-assigned; it's returned on the response,
not something you set.

```python
response = client.Addressbook.Group.Create(
    GroupName="API Test Group",
    SubAccount="SALES",
    ViewEditBy="SubAccount",
)

if response.Result == "Success":
    print(f"Created GroupID={response.GroupID}, GroupCode={response.GroupCode}")
```

### Detail, Update, Delete, and List

Manage a group the same way as a contact: look up, rename, remove, or page through all groups. Like
Contact, the lookup method is singular `Detail(...)`, and `Update(...)`/`Delete(...)` accept either a
`GroupID` string or the response object itself.

```python
details = client.Addressbook.Group.Detail(response.GroupID)
client.Addressbook.Group.Update(response, GroupName="Renamed Group")
client.Addressbook.Group.Delete(response)

page = client.Addressbook.Group.List(RecordsPerPage=100, Page=1)
```

## Contact ↔ Group relationships

`ContactGroup` (contact's-side view) and `GroupContact` (group's-side view) both manage the same
underlying membership, and both support the same four operations: `List(...)`, `Create(...)`,
`Delete(...)`, and `Detail(...)`. Three things worth noting:

- The method names are `Create`/`Delete`, not `Add`/`Remove`.
- Neither class has a `Set(...)`/`Build()` builder — both take their arguments as plain positional/keyword
  parameters.
- Neither accepts a response object in place of an ID the way `Contact`/`Group` do — every
  `ContactID`/`GroupID` here must be a plain string (an empty or missing one raises `ValueError`).

`ContactGroup.Create(ContactID, GroupID)` and `GroupContact.Create(GroupID, ContactID)` dispatch to the
exact same underlying endpoint; only the Python argument order differs (which ID comes first), matching
whichever side reads more naturally at your call site. The same is true of their respective `Delete(...)`
methods.

```python
# Groups a contact belongs to
groups = client.Addressbook.ContactGroup.List(contact_id)

# Add a contact to a group, from the contact's side
add_result = client.Addressbook.ContactGroup.Create(contact_id, group_id)

if add_result.Result == "Success":
    print(f"Added to group: {add_result.Group.get('GroupName')}")

# Look up a single contact-group relation
relation = client.Addressbook.ContactGroup.Detail(contact_id, group_id)

# Remove a contact from a group
client.Addressbook.ContactGroup.Delete(contact_id, group_id)

# Contacts belonging to a group
contacts = client.Addressbook.GroupContact.List(group_id)

if contacts.Result == "Success":
    for contact in contacts.Contacts:
        print(f"{contact.get('FirstName')} {contact.get('LastName')}")

# Add a contact to a group, from the group's side (same wire endpoint as above)
group_add_result = client.Addressbook.GroupContact.Create(group_id, contact_id)

if group_add_result.Result == "Success":
    contact = group_add_result.Contact
    print(f"Added {contact.get('FirstName')} {contact.get('LastName')} to group")

# Remove a contact from a group, from the group's side
client.Addressbook.GroupContact.Delete(group_id, contact_id)

# Look up a single group-contact relation
group_relation = client.Addressbook.GroupContact.Detail(group_id, contact_id)
```

**`Detail(...)` on both `ContactGroup` and `GroupContact` has no dedicated wire endpoint behind it.** It's
synthesised client-side: internally it calls `List(...)` for one page and scans the results for a matching
`GroupID`/`ContactID`, returning `Result="RecordNotFound"` if it isn't on that page. It deliberately does
**not** auto-paginate to keep searching — that could mean an unbounded number of HTTP calls for a contact
or group with many memberships. If you suspect the match is on a later page, inspect `List(...)`'s
`PageCount` yourself and pass a larger `RecordsPerPage` or a specific `Page`. This is also why
`Detail(...)`'s default `RecordsPerPage` is `100`, not the `20` used everywhere else in this SDK: a larger
default page reduces the odds of a false `RecordNotFound` on a contact/group with many memberships.

## Response

Every Addressbook result carries `Result` and `ErrorMessage`: check `Result == "Success"` before reading
other fields. List-style results additionally carry `TotalRecords`/`RecordsPerPage`/`PageCount`/`Page`
(all `int`) for pagination. As with the rest of this SDK, list/nested fields below are **plain `dict`
objects**, not typed classes: access them with `contact.get("FirstName")` or `contact["FirstName"]`, not
attribute access.

### `Contact.Create(...)`/`Detail(...)`/`Update(...)`/`Delete(...)` response

- `Result`, `ErrorMessage` — standard response fields.
- `ContactID` — the contact's ID.
- `Owner` — the TNZ user who owns this contact.
- `CreatedTimeLocal` / `CreatedTimeUTC` / `CreatedTimeUTC_RFC3339` — when the contact was created.
- `UpdatedTimeLocal` / `UpdatedTimeUTC` / `UpdatedTimeUTC_RFC3339` — when the contact was last updated.
- `Timezone` — timezone the local timestamps above are expressed in.
- `Groups` (`list[dict]`) — the groups this contact belongs to.
- Every `Contact` field from the Fields table above — echoed back (`FirstName`, `EmailAddress`,
  `Custom1`–`Custom4`, etc.).

### `Contact.Search(...)`/`List(...)` response

- `Result`, `ErrorMessage` — standard response fields.
- `Contacts` (`list[dict]`) — the matching contacts for this page, each dict shaped like
  `Contact.Detail(...)`'s result fields.

### `Group.Create(...)`/`Detail(...)`/`Update(...)`/`Delete(...)` response

- `Result`, `ErrorMessage` — standard response fields.
- `GroupID` — the group's ID.
- `GroupCode` — server-assigned lookup code. Read-only; there's no matching field in the Fields table
  above to set it.
- `GroupName` / `SubAccount` / `Department` / `ViewEditBy` / `AccessControl` — echoed back.
- `Owner` — the TNZ user who owns this group.
- `CreatedTimeLocal` / `CreatedTimeUTC` / `CreatedTimeUTC_RFC3339` — when the group was created. Unlike
  Contact, Group has no `Updated*` timestamps.
- `Timezone` — timezone the local timestamp above is expressed in.

### `Group.List(...)` response

- `Result`, `ErrorMessage` — standard response fields.
- `Groups` (`list[dict]`) — the groups for this page, each dict shaped like `Group.Detail(...)`'s result
  fields.

### `ContactGroup.List(...)` response

- `Result`, `ErrorMessage` — standard response fields.
- `TotalRecords`/`RecordsPerPage`/`PageCount`/`Page` (`int`) — pagination fields.
- `Contact` (`dict`) — the contact whose groups you're listing.
- `Groups` (`list[dict]`) — the groups this contact belongs to, for this page.

### `GroupContact.List(...)` response

- `Result`, `ErrorMessage` — standard response fields.
- `TotalRecords`/`RecordsPerPage`/`PageCount`/`Page` (`int`) — pagination fields.
- `Group` (`dict`) — the group whose members you're listing.
- `Contacts` (`list[dict]`) — the contacts belonging to this group, for this page.

### `ContactGroup.Create(...)`/`Delete(...)`/`Detail(...)` response

- `Result` — standard, plus `Detail(...)` can also return `"RecordNotFound"` (see the note above).
- `ErrorMessage` — standard response field.
- `Contact` (`dict`) — the contact side of this relation.
- `Group` (`dict`) — the group side of this relation.

### `GroupContact.Create(...)`/`Delete(...)`/`Detail(...)` response

- `Result` — standard, plus `Detail(...)` can also return `"RecordNotFound"` (see the note above).
- `ErrorMessage` — standard response field.
- `Group` (`dict`) — the group side of this relation.
- `Contact` (`dict`) — the contact side of this relation.

These last two result types carry no pagination fields, unlike the `List(...)` results above; each always
describes exactly one contact–group relation.

`ContactResponse`/`ContactListResponse`/`GroupResponse`/`GroupListResponse`/`ContactGroupResponse`/`ContactGroupListResponse`/`GroupContactResponse`/`GroupContactListResponse` were named `...DTO` before this SDK's public response types dropped that internal-architecture suffix; the old names still work (they emit a `DeprecationWarning`) — see [messaging.md](messaging.md#response-shape).

## See also

- [README — Addressbook](../README.md#addressbook)
- [Samples — contact_samples.py](../samples/addressbook/contact_samples.py)
- [Samples — group_samples.py](../samples/addressbook/group_samples.py)
- [Samples — contact_group_samples.py](../samples/addressbook/contact_group_samples.py)
- [Samples — group_contact_samples.py](../samples/addressbook/group_contact_samples.py)
