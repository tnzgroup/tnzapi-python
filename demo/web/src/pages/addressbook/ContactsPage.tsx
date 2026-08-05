import { useEffect, useState, type FormEvent } from 'react'
import { Button } from '@/components/ui/button'
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from '@/components/ui/table'
import { TextField, type FieldValues } from '@/components/form-fields'
import { ResponseViewer } from '@/components/response-viewer'
import { apiRequest } from '@/lib/api-client'

type Contact = {
  ContactID?: string
  FirstName?: string
  LastName?: string
  Company?: string
  MobilePhone?: string
  EmailAddress?: string
}

// Mirrors tnzapi-ts-samples/nextjs/app/addressbook/contacts, with two differences forced by real
// SDK gaps rather than faked: (1) .NET's Create/Details/Update/Delete results are flat (per the
// SDK's own "Result shape convention" — response.FirstName, not response.Contact.FirstName), so
// this reads fields straight off the response instead of a nested `.Contact`; (2) the reference's
// create form includes a Timezone field, but .NET's ContactModel has no settable Timezone property
// (it's a read-only server-computed field on ContactDetail) — dropped here rather than sent as a
// silently-ignored no-op field. ViewBy/EditBy/AccessControl (enum pickers) are likewise left out,
// same as every other messaging page's approach to enum-typed optional fields.
const CREATE_FIELDS = ['FirstName', 'LastName', 'Company', 'MobilePhone', 'EmailAddress', 'FaxNumber', 'Title', 'Position']
const EDIT_FIELDS = ['FirstName', 'LastName', 'Company', 'MobilePhone', 'EmailAddress', 'FaxNumber', 'Title', 'Position', 'Custom1', 'Custom2']

export default function ContactsPage() {
  const [contacts, setContacts] = useState<Contact[]>([])
  const [createFields, setCreateFields] = useState<FieldValues>({})
  const [editId, setEditId] = useState('')
  const [editFields, setEditFields] = useState<FieldValues>({})
  const [status, setStatus] = useState<number | null>(null)
  const [data, setData] = useState<unknown>(null)

  async function loadList() {
    const result = await apiRequest<{ Contacts?: Contact[] }>('/api/addressbook/contacts?recordsPerPage=50&page=1')
    if (result.status < 400) setContacts(result.data.Contacts ?? [])
  }

  useEffect(() => {
    loadList()
  }, [])

  async function handleCreate(e: FormEvent) {
    e.preventDefault()
    const result = await apiRequest('/api/addressbook/contacts', { method: 'POST', body: createFields })
    setStatus(result.status)
    setData(result.data)
    if (result.status < 400) {
      setCreateFields({})
      loadList()
    }
  }

  async function handleLoad(id: string) {
    setEditId(id)
    const result = await apiRequest<FieldValues>(`/api/addressbook/contacts/${id}`)
    setStatus(result.status)
    setData(result.data)
    if (result.status < 400) {
      setEditFields(result.data)
    }
  }

  async function handleUpdate(e: FormEvent) {
    e.preventDefault()
    if (!editId) return
    const result = await apiRequest(`/api/addressbook/contacts/${editId}`, { method: 'PUT', body: editFields })
    setStatus(result.status)
    setData(result.data)
    if (result.status < 400) loadList()
  }

  async function handleDelete() {
    if (!editId) return
    const result = await apiRequest(`/api/addressbook/contacts/${editId}`, { method: 'DELETE' })
    setStatus(result.status)
    setData(result.data)
    if (result.status < 400) {
      setEditId('')
      setEditFields({})
      loadList()
    }
  }

  return (
    <div className="max-w-4xl space-y-8">
      <div>
        <h1 className="text-xl font-semibold">Addressbook — Contacts</h1>
        <p className="text-sm text-muted-foreground">
          client.Addressbook.Contact.List / .Create / .Details / .Update / .Delete
        </p>
      </div>

      <section className="space-y-4">
        <h2 className="font-medium">Contacts</h2>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Name</TableHead>
              <TableHead>Company</TableHead>
              <TableHead>Mobile</TableHead>
              <TableHead>Email</TableHead>
              <TableHead></TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {contacts.map((c) => (
              <TableRow key={c.ContactID}>
                <TableCell>
                  {c.FirstName} {c.LastName}
                </TableCell>
                <TableCell>{c.Company}</TableCell>
                <TableCell>{c.MobilePhone}</TableCell>
                <TableCell>{c.EmailAddress}</TableCell>
                <TableCell>
                  <Button type="button" variant="outline" size="sm" onClick={() => c.ContactID && handleLoad(c.ContactID)}>
                    Edit
                  </Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </section>

      <section className="space-y-4">
        <h2 className="font-medium">Create Contact</h2>
        <form onSubmit={handleCreate} className="grid grid-cols-2 gap-4">
          {CREATE_FIELDS.map((name) => (
            <TextField
              key={name}
              label={name}
              name={name}
              values={createFields}
              onChange={(n, v) => setCreateFields((f) => ({ ...f, [n]: v }))}
            />
          ))}
          <Button type="submit" className="col-span-2 w-fit">
            Create
          </Button>
        </form>
      </section>

      <section className="space-y-4">
        <h2 className="font-medium">Edit / Delete Contact</h2>
        <div className="flex items-end gap-2">
          <div className="flex-1">
            <TextField label="Contact ID" name="ContactID" values={{ ContactID: editId }} onChange={(_, v) => setEditId(v)} />
          </div>
          <Button type="button" variant="outline" onClick={() => handleLoad(editId)}>
            Load
          </Button>
        </div>
        <form onSubmit={handleUpdate} className="grid grid-cols-2 gap-4">
          {EDIT_FIELDS.map((name) => (
            <TextField
              key={name}
              id={`edit-${name}`}
              label={name}
              name={name}
              values={editFields}
              onChange={(n, v) => setEditFields((f) => ({ ...f, [n]: v }))}
            />
          ))}
          <div className="col-span-2 flex gap-2">
            <Button type="submit" disabled={!editId}>
              Save
            </Button>
            <Button type="button" variant="destructive" disabled={!editId} onClick={handleDelete}>
              Delete
            </Button>
          </div>
        </form>
      </section>

      <ResponseViewer status={status} data={data} />
    </div>
  )
}