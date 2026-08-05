"""tnzapi reference-code samples.

This package is a browsable reference library, not something your application
imports at runtime - it is excluded from the built/installed `tnzapi` package
(see setup.py) and exists purely so you can copy-paste working examples
straight from source. Same concept as tnzapi-dotnet's TNZAPI.NET.Samples
project: one class per channel/area, one method per demonstrated operation.
Every class takes an optional pre-built `TNZAPI` client (falling back to
`TNZAPI()`, which itself falls back to the `TNZ_AUTH_TOKEN` environment
variable - see the README's Configuration section).

Browse by area, matching the README's own section layout:
    samples/messaging/    - SMS, Email, Fax, TTS, Voice, WhatsApp, RCS, Workflow
    samples/reports/      - Status polling
    samples/actions/      - Abort, Reschedule, Resubmit, Pacing
    samples/addressbook/  - Contact, Group, ContactGroup, GroupContact
    samples/optout/       - Opt-out management
    samples/webhooks/     - Parsing inbound TNZ webhook payloads

See README.md for the full field reference for every request.
"""
