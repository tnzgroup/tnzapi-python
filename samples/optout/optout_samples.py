"""Opt-Out Management sample code. Full field reference: README.md > Opt-Out Management.

DestType accepts Fax, Text, SMS, Email, Speech or Voice (comma-separated for
more than one) - SMS and Voice are accepted as aliases of Text and Speech
respectively.
"""

from tnzapi import TNZAPI


class OptOutSamples:

    def __init__(self, client: TNZAPI = None):
        self.client = client or TNZAPI()

    def Create(self):
        client = self.client
        return client.OptOut.Create(
            DestType="SMS",
            Destination="+64211234567",
            Notes="Requested via support call"
        )

    def CreateBatch(self):
        client = self.client
        return client.OptOut.CreateBatch(
            DestType="SMS,Email",
            Destinations=["+64211234567", "+64221234567"]
        )

    def List(self):
        client = self.client
        return client.OptOut.List(
            DestType="SMS",
            RecordsPerPage=20,
            Page=1
        )

    def Details(self, OptOutID: str):
        client = self.client
        return client.OptOut.Details(OptOutID)

    def Update(self, OptOutID: str):
        """Update is partial - only the fields you pass are changed."""
        client = self.client
        return client.OptOut.Update(OptOutID, Notes="Updated notes")

    def Delete(self, OptOutID: str):
        client = self.client
        return client.OptOut.Delete(OptOutID)

    def OptOutLifecycle(self):
        """Recipe: add, capture the generated ID, remove, confirm removal."""
        client = self.client
        destination = "+64211234567"

        created = client.OptOut.Create(DestType="SMS", Destination=destination)
        if created.Result != "Success":
            print("Create failed:", created.ErrorMessage)
            return

        opt_out_id = created.ID
        print(f"{destination} added to opt-out list ({opt_out_id})")

        client.OptOut.Delete(opt_out_id)
        print(f"{destination} removed from opt-out list")

        check = client.OptOut.Details(opt_out_id)
        print("Confirmed gone after removal:", check.Result != "Success")
