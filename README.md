# tnzapi

## Documentation

The documentation for the TNZ API can be found [here][apidocs].

## Versions

`tnzapi` uses a modified version of [Semantic Versioning](https://semver.org) for all changes. [See this document](VERSIONS.md) for details.

### Supported Python Versions

This library supports the following Python implementations:

* Python 3.9
* Python 3.10
* Python 3.11
* Python 3.12

## Installation

Install from PyPi using [pip](http://www.pip-installer.org/en/latest/), a
package manager for Python.

    pip install tnzapi

Don't have pip installed? Try installing it, by running this from the command
line:

    $ curl https://raw.github.com/pypa/pip/master/contrib/get-pip.py | python

    python setup.py install

You may need to run the above commands with `sudo`.

## Getting Started

Getting started with the TNZ API couldn't be easier. Create a
`Client` and you're ready to go.

### API Credentials

The `TNZAPI` needs your TNZ API credentials (TNZ Auth Tokens). You can either pass these
directly to the constructor (see the code below) or via environment variables.

```python
from tnzapi import TNZAPI

client = TNZAPI(
    AuthToken = "[Your Auth Token]"
)
```

### Send Message

Send SMS/Email/Voice/Fax through `tnzapi` library.

#### Send SMS

```python
from tnzapi import TNZAPI

client = TNZAPI(
    AuthToken="[Your Auth Token]"
)

response = client.Messaging.SMS.SendMessage(
    Reference="Test",
    MessageText = "Test SMS Message click [[Reply]] to opt out",
    Recipients = ["+64211231234"],
)

print(response)
```

#### Send an Email

```python
from tnzapi import TNZAPI

client = TNZAPI(
    AuthToken="[Your Auth Token]"
)

response = client.Messaging.Email.SendMessage(
    EmailSubject = "Test Email",
    Recipients = [
        "recipient@example.com"
    ],
    MessagePlain = "Hi world!"
)

print(response)
```

#### Send a Fax Document

```python
from tnzapi import TNZAPI

client = TNZAPI(
    AuthToken="[Your Auth Token]"
)

response = client.Messaging.Fax.SendMessage(
    Recipients = "+6491232345",
    Attachments = ["C:\\Document.pdf"]
)

print(response)
```

#### Make a Call - Text-to-Speech (TTS)

```python
from tnzapi import TNZAPI

client = TNZAPI(
    AuthToken="[Your Auth Token]"
)

response = client.Messaging.TTS.SendMessage(
    Recipients = ["+64211232345"],
    Reference = "Voice Test - 64211232345",
    MessageToPeople = "Hi there!",
    Keypads = [
        Keypad(
            Tone=1,
            Play="You pressed 1",
            RouteNumber="+6491232345"
        )
    ]
)

print(response)
```

#### Make a Call - Upload MP3 / Wav File

```python
from tnzapi import TNZAPI

client = TNZAPI(
    AuthToken="[Your Auth Token]"
)

response = client.Messaging.Voice.SendMessage(
    Recipients = ["+64211232345"],
    Reference = "Voice Test - 64211232345",
    MessageToPeople = "C:\\file1.wav",
    MessageToAnswerPhones = "C:\\file2.wav",
    Keypads = [
        Keypad(
            Tone=1,
            RouteNumber="+6491232345",
            PlayFile="C:\\file3.wav"
        )
    ]
)

print(response)
```

### Reports

Retrieve your message status using `tnzapi` library.

#### Reports - Get Message Status

```python
from tnzapi import TNZAPI

client = TNZAPI(
    AuthToken="[Your Auth Token]"
)

response = client.Reports.Status.Poll(
    MessageID="ID123456"
)

print(response)
```

#### Reports - Get SMS Reply

```python
from tnzapi import TNZAPI

client = TNZAPI(
    AuthToken="[Your Auth Token]"
)

request = client.Reports.SMSReply.Poll(
    MessageID="ID123456"
)

print(response)
```

#### Reports - Get SMS Received List

```python
from tnzapi import TNZAPI

client = TNZAPI(
    AuthToken="[Your Auth Token]"
)

response = client.Reports.SMSReceived.Poll(
    #TimePeriod = 1440
    DateFrom="2023-07-01 00:00:00",
    DateTo="2023-08-01 00:00:00"
)

print(response)
```

### Actions

Amend your message using `tnzapi` library.

#### Actions - Abort Pending/Delayed Job

```python
from tnzapi import TNZAPI

client = TNZAPI(
    AuthToken="[Your Auth Token]"
)

response = client.Actions.Abort.SendRequest(
    MessageID="ID123456"
)

print(response)
```

#### Actions - Resubmit Failed Job

```python
from tnzapi import TNZAPI

client = TNZAPI(
    AuthToken="[Your Auth Token]"
)

response = client.Actions.Resubmit.SendRequest(
    MessageID="ID123456",
    SendTime="2023-07-10T09:00"    #optional
)

print(response)
```

#### Actions - Reschedule DELAYED Job

```python
from tnzapi import TNZAPI

client = TNZAPI(
    AuthToken="[Your Auth Token]"
)

response = client.Actions.Reschedule.SendRequest(
    MessageID="ID123456",
    SendTime=datetime.now()
)

print(response)
```

#### Actions - Set Number of Operators on TTS/Voice Job

```python
from tnzapi import TNZAPI

client = TNZAPI(
    AuthToken="[Your Auth Token]"
)

request = client.Set.Pacing(
    MessageID="ID123456",
    NumberOfOperators=10
)

print(response)
```

### Addressbook - Contacts

Manage your contacts using `tnzapi` library.

#### Contacts - List

```python
from tnzapi import TNZAPI

client = TNZAPI(
    AuthToken="[Your Auth Token]"
)

response = client.Addressbook.Contact.List(
    RecordsPerPage=10,
    Page=1
)

print(response)
```

#### Contacts - Detail

```python
from tnzapi import TNZAPI

client = TNZAPI(
    AuthToken="[Your Auth Token]"
)

response = client.Addressbook.Contact.Detail(
    ContactID="[Contact ID]"
)

print(response)
```

#### Contacts - Create

```python
from tnzapi import TNZAPI

client = TNZAPI(
    AuthToken="[Your Auth Token]"
)

response = client.Addressbook.Contact.Create(
    Title="Mr",
    Company="TNZ Group",
    FirstName="First",
    LastName="Last",
    MobilePhone="+642122223333",
    ViewPublic="Account",
    EditPublid="Account"
)

print(response)
```

#### Contacts - Update

```python
from tnzapi import TNZAPI

client = TNZAPI(
    AuthToken="[Your Auth Token]"
)

response = client.Addressbook.Contact.Update(
    ContactID="[Contact ID]",
    Attention="Test Attention"
)

print(response)
```

#### Contacts - Delete

```python
from tnzapi import TNZAPI

client = TNZAPI(
    AuthToken="[Your Auth Token]"
)

response = client.Addressbook.Contact.Delete(
    ContactID="[Contact ID]"
)

print(response)
```

### Addressbook - Contact Group

Manage your contact group relationship using `tnzapi` library.

#### Contact Group - List

```python
from tnzapi import TNZAPI

client = TNZAPI(
    AuthToken="[Your Auth Token]"
)

response = client.Addressbook.ContactGroup.List(
    RecordsPerPage=10,
    Page=1,
    ContactID="[Contact ID]"
)

print(response)
```

#### Contact Group - Detail

```python
from tnzapi import TNZAPI

client = TNZAPI(
    AuthToken="[Your Auth Token]"
)

response = client.Addressbook.ContactGroup.Detail(
    ContactID="[Contact ID]",
    GroupCode="[Group Code]"
)

print(response)
```

#### Contact Group - Create

```python
from tnzapi import TNZAPI

client = TNZAPI(
    AuthToken="[Your Auth Token]"
)

response = client.Addressbook.ContactGroup.Create(
    ContactID="[Contact ID]",
    GroupCode="[Group Code]"
)

print(response)
```

#### Contact Group - Delete

```python
from tnzapi import TNZAPI

client = TNZAPI(
    AuthToken="[Your Auth Token]"
)

response = client.Addressbook.ContactGroup.Delete(
    ContactID="[Contact ID]",
    GroupCode="[Group Code]"
)

print(response)
```

### Addressbook - Group

Manage your group using `tnzapi` library.

#### Group - List

```python
from tnzapi import TNZAPI

client = TNZAPI(
    AuthToken="[Your Auth Token]"
)

response = client.Addressbook.Group.List(
    RecordsPerPage=10,
    Page=1
)

print(response)
```

#### Group - Detail

```python
from tnzapi import TNZAPI

client = TNZAPI(
    AuthToken="[Your Auth Token]"
)

response = client.Addressbook.Group.Detail(
    GroupCode="[Group Code]"
)

print(response)
```

#### Group - Create

```python
from tnzapi import TNZAPI

client = TNZAPI(
    AuthToken="[Your Auth Token]"
)

response = client.Addressbook.Group.Create(
    GroupCode="[Group Code]",
    GroupName="[Group Name]"
)

print(response)
```

#### Group - Update

```python
from tnzapi import TNZAPI

client = TNZAPI(
    AuthToken="[Your Auth Token]"
)

response = client.Addressbook.Group.Update(
    GroupCode="[Group Code]",
    GroupName="[Group Name]"
)

print(response)
```

#### Group - Delete

```python
from tnzapi import TNZAPI

client = TNZAPI(
    AuthToken="[Your Auth Token]"
)

response = client.Addressbook.Group.Delete(
    GroupCode="[Group Code]"
)

print(response)
```

### Addressbook - Group Contact

Manage your group contact relationship using `tnzapi` library.

#### Group Contact - List

```python
from tnzapi import TNZAPI

client = TNZAPI(
    AuthToken="[Your Auth Token]"
)

response = client.Addressbook.GroupContact.List(
    RecordsPerPage=10,
    Page=1,
    GroupCode="[Group Code]"
)

print(response)
```

#### Group Contact - Detail

```python
from tnzapi import TNZAPI

client = TNZAPI(
    AuthToken="[Your Auth Token]"
)

response = client.Addressbook.GroupContact.Detail(
    GroupCode="[Group Code]",
    ContactID="[Contact ID]"
)

print(response)
```

#### Group Contact - Create

```python
from tnzapi import TNZAPI

client = TNZAPI(
    AuthToken="[Your Auth Token]"
)

response = client.Addressbook.GroupContact.Create(
    GroupCode="[Group Code]",
    ContactID="[Contact ID]"
)

print(response)
```

#### Group Contact - Delete

```python
from tnzapi import TNZAPI

client = TNZAPI(
    AuthToken="[Your Auth Token]"
)

response = client.Addressbook.GroupContact.Delete(
    GroupCode="[Group Code]",
    ContactID="[Contact ID]"
)

print(response)
```

### Getting help

If you need help installing or using the library, please check the [TNZ Contact](https://www.tnz.co.nz/About/Contact/) if you don't find an answer to your question.

[apidocs]: https://www.tnz.co.nz/Docs/PythonAPI/
