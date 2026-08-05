import { useState, type FormEvent } from 'react'
import { Button } from '@/components/ui/button'
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from '@/components/ui/table'
import { TextField, type FieldValues } from '@/components/form-fields'
import { ResponseViewer } from '@/components/response-viewer'
import { apiRequest } from '@/lib/api-client'

type Contact = { ContactID?: string; FirstName?: string; LastName?: string }

// Mirrors tnzapi-ts-samples/nextjs/app/addressbook/group-contacts (client.Addressbook.Group.Contact
// — Add/List/Remove), with the same two fields dropped as ContactGroupsPage for real SDK gaps: no
// GroupCode alternative on Add, no pagination on List — see GroupContactsController.cs.
export default function GroupContactsPage() {
  const [createFields, setCreateFields] = useState<FieldValues>({})
  const [listGroupId, setListGroupId] = useState('')
  const [contacts, setContacts] = useState<Contact[]>([])
  const [status, setStatus] = useState<number | null>(null)
  const [data, setData] = useState<unknown>(null)

  async function handleCreate(e: FormEvent) {
    e.preventDefault()
    const result = await apiRequest('/api/addressbook/group-contacts', { method: 'POST', body: createFields })
    setStatus(result.status)
    setData(result.data)
  }

  async function handleList() {
    const result = await apiRequest<{ Contacts?: Contact[] }>(
      `/api/addressbook/group-contacts?groupID=${encodeURIComponent(listGroupId)}`,
    )
    setStatus(result.status)
    setData(result.data)
    if (result.status < 400) setContacts(result.data.Contacts ?? [])
  }

  async function handleRemove(contactId?: string) {
    if (!contactId) return
    const result = await apiRequest('/api/addressbook/group-contacts', {
      method: 'DELETE',
      body: { GroupID: listGroupId, ContactID: contactId },
    })
    setStatus(result.status)
    setData(result.data)
    if (result.status < 400) handleList()
  }

  return (
    <div className="max-w-3xl space-y-8">
      <div>
        <h1 className="text-xl font-semibold">Addressbook — Group Contacts</h1>
        <p className="text-sm text-muted-foreground">client.Addressbook.Group.Contact.Add / .List / .Remove</p>
      </div>

      <section className="space-y-4">
        <h2 className="font-medium">Add Contact To Group</h2>
        <form onSubmit={handleCreate} className="grid grid-cols-2 gap-4">
          <TextField label="Group ID" name="GroupID" values={createFields} onChange={(n, v) => setCreateFields((f) => ({ ...f, [n]: v }))} />
          <TextField label="Contact ID" name="ContactID" values={createFields} onChange={(n, v) => setCreateFields((f) => ({ ...f, [n]: v }))} />
          <Button type="submit" className="col-span-2 w-fit">
            Add
          </Button>
        </form>
      </section>

      <section className="space-y-4">
        <h2 className="font-medium">Contacts In A Group</h2>
        <div className="flex items-end gap-2">
          <div className="flex-1">
            <TextField id="list-GroupID" label="Group ID" name="GroupID" values={{ GroupID: listGroupId }} onChange={(_, v) => setListGroupId(v)} />
          </div>
          <Button type="button" variant="outline" onClick={handleList}>
            Load
          </Button>
        </div>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Name</TableHead>
              <TableHead>Contact ID</TableHead>
              <TableHead></TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {contacts.map((c) => (
              <TableRow key={c.ContactID}>
                <TableCell>
                  {c.FirstName} {c.LastName}
                </TableCell>
                <TableCell>{c.ContactID}</TableCell>
                <TableCell>
                  <Button type="button" variant="destructive" size="sm" onClick={() => handleRemove(c.ContactID)}>
                    Remove
                  </Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </section>

      <ResponseViewer status={status} data={data} />
    </div>
  )
}