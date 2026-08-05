import { useState, type FormEvent } from 'react'
import { Button } from '@/components/ui/button'
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from '@/components/ui/table'
import { TextField, type FieldValues } from '@/components/form-fields'
import { ResponseViewer } from '@/components/response-viewer'
import { apiRequest } from '@/lib/api-client'

type Group = { GroupID?: string; GroupCode?: string; GroupName?: string }

// Mirrors tnzapi-ts-samples/nextjs/app/addressbook/contact-groups (client.Addressbook.Contact.Group
// — Add/List/Remove), with two fields dropped for real SDK gaps rather than faked: the reference's
// create form has a "Group Code (alternative to Group ID)" field and its list call takes
// RecordsPerPage/Page, but .NET's IContactGroupApi.Add(ContactID, GroupID) has no GroupCode
// parameter and List(ContactID) takes no pagination — see ContactGroupsController.cs.
export default function ContactGroupsPage() {
  const [createFields, setCreateFields] = useState<FieldValues>({})
  const [listContactId, setListContactId] = useState('')
  const [groups, setGroups] = useState<Group[]>([])
  const [status, setStatus] = useState<number | null>(null)
  const [data, setData] = useState<unknown>(null)

  async function handleCreate(e: FormEvent) {
    e.preventDefault()
    const result = await apiRequest('/api/addressbook/contact-groups', { method: 'POST', body: createFields })
    setStatus(result.status)
    setData(result.data)
  }

  async function handleList() {
    const result = await apiRequest<{ Groups?: Group[] }>(
      `/api/addressbook/contact-groups?contactID=${encodeURIComponent(listContactId)}`,
    )
    setStatus(result.status)
    setData(result.data)
    if (result.status < 400) setGroups(result.data.Groups ?? [])
  }

  async function handleRemove(groupId?: string) {
    if (!groupId) return
    const result = await apiRequest('/api/addressbook/contact-groups', {
      method: 'DELETE',
      body: { ContactID: listContactId, GroupID: groupId },
    })
    setStatus(result.status)
    setData(result.data)
    if (result.status < 400) handleList()
  }

  return (
    <div className="max-w-3xl space-y-8">
      <div>
        <h1 className="text-xl font-semibold">Addressbook — Contact Groups</h1>
        <p className="text-sm text-muted-foreground">client.Addressbook.Contact.Group.Add / .List / .Remove</p>
      </div>

      <section className="space-y-4">
        <h2 className="font-medium">Add Contact To Group</h2>
        <form onSubmit={handleCreate} className="grid grid-cols-2 gap-4">
          <TextField label="Contact ID" name="ContactID" values={createFields} onChange={(n, v) => setCreateFields((f) => ({ ...f, [n]: v }))} />
          <TextField label="Group ID" name="GroupID" values={createFields} onChange={(n, v) => setCreateFields((f) => ({ ...f, [n]: v }))} />
          <Button type="submit" className="col-span-2 w-fit">
            Add
          </Button>
        </form>
      </section>

      <section className="space-y-4">
        <h2 className="font-medium">Groups For A Contact</h2>
        <div className="flex items-end gap-2">
          <div className="flex-1">
            <TextField id="list-ContactID" label="Contact ID" name="ContactID" values={{ ContactID: listContactId }} onChange={(_, v) => setListContactId(v)} />
          </div>
          <Button type="button" variant="outline" onClick={handleList}>
            Load
          </Button>
        </div>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Group Name</TableHead>
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
                  <Button type="button" variant="destructive" size="sm" onClick={() => handleRemove(g.GroupID)}>
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