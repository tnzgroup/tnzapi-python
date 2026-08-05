import { useEffect, useState, type FormEvent } from 'react'
import { Button } from '@/components/ui/button'
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from '@/components/ui/table'
import { TextField, type FieldValues } from '@/components/form-fields'
import { ResponseViewer } from '@/components/response-viewer'
import { apiRequest } from '@/lib/api-client'

type Group = { GroupID?: string; GroupName?: string; ViewEditBy?: string }

// Mirrors tnzapi-ts-samples/nextjs/app/addressbook/groups, adjusted for the same flat-result
// convention difference as ContactsPage: .NET's Create/Details/Update/Delete results are flat
// (response.GroupName, not response.Group.GroupName — see the SDK's "Result shape convention").
const CREATE_FIELDS = ['GroupName', 'ViewEditBy', 'SubAccount', 'Department']
const EDIT_FIELDS = ['GroupName', 'ViewEditBy', 'SubAccount', 'Department']

export default function GroupsPage() {
  const [groups, setGroups] = useState<Group[]>([])
  const [createFields, setCreateFields] = useState<FieldValues>({})
  const [editId, setEditId] = useState('')
  const [editFields, setEditFields] = useState<FieldValues>({})
  const [status, setStatus] = useState<number | null>(null)
  const [data, setData] = useState<unknown>(null)

  async function loadList() {
    const result = await apiRequest<{ Groups?: Group[] }>('/api/addressbook/groups?recordsPerPage=50&page=1')
    if (result.status < 400) setGroups(result.data.Groups ?? [])
  }

  useEffect(() => {
    loadList()
  }, [])

  async function handleCreate(e: FormEvent) {
    e.preventDefault()
    const result = await apiRequest('/api/addressbook/groups', { method: 'POST', body: createFields })
    setStatus(result.status)
    setData(result.data)
    if (result.status < 400) {
      setCreateFields({})
      loadList()
    }
  }

  async function handleLoad(id: string) {
    setEditId(id)
    const result = await apiRequest<FieldValues>(`/api/addressbook/groups/${id}`)
    setStatus(result.status)
    setData(result.data)
    if (result.status < 400) {
      setEditFields(result.data)
    }
  }

  async function handleUpdate(e: FormEvent) {
    e.preventDefault()
    if (!editId) return
    const result = await apiRequest(`/api/addressbook/groups/${editId}`, { method: 'PUT', body: editFields })
    setStatus(result.status)
    setData(result.data)
    if (result.status < 400) loadList()
  }

  async function handleDelete() {
    if (!editId) return
    const result = await apiRequest(`/api/addressbook/groups/${editId}`, { method: 'DELETE' })
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
        <h1 className="text-xl font-semibold">Addressbook — Groups</h1>
        <p className="text-sm text-muted-foreground">
          client.Addressbook.Group.List / .Create / .Details / .Update / .Delete
        </p>
      </div>

      <section className="space-y-4">
        <h2 className="font-medium">Groups</h2>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Name</TableHead>
              <TableHead>Group ID</TableHead>
              <TableHead></TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {groups.map((g) => (
              <TableRow key={g.GroupID}>
                <TableCell>{g.GroupName}</TableCell>
                <TableCell>{g.GroupID}</TableCell>
                <TableCell>
                  <Button type="button" variant="outline" size="sm" onClick={() => g.GroupID && handleLoad(g.GroupID)}>
                    Edit
                  </Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </section>

      <section className="space-y-4">
        <h2 className="font-medium">Create Group</h2>
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
        <h2 className="font-medium">Edit / Delete Group</h2>
        <div className="flex items-end gap-2">
          <div className="flex-1">
            <TextField label="Group ID" name="GroupID" values={{ GroupID: editId }} onChange={(_, v) => setEditId(v)} />
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