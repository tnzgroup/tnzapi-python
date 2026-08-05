import { useEffect, useState, type FormEvent } from 'react'
import { Button } from '@/components/ui/button'
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from '@/components/ui/table'
import { TextField, type FieldValues } from '@/components/form-fields'
import { ResponseViewer } from '@/components/response-viewer'
import { apiRequest } from '@/lib/api-client'

type OptOut = { ID?: string; Destination?: string; DestType?: string; CreatedTimeLocal?: string }

// Mirrors tnzapi-ts-samples/nextjs/app/optout (client.Configuration.OptOut.List / .Create / .Details
// / .Delete) field-for-field — no gaps, .NET's OptOutModel matches the reference's create field set
// exactly. Update exists on the SDK but isn't exposed here, matching the reference page's own scope
// (List/Create/Detail/Delete only).
const CREATE_FIELDS = ['Destination', 'DestType', 'Department', 'SubAccount', 'ContactID', 'StopMessage', 'Notes']

export default function OptOutPage() {
  const [optOuts, setOptOuts] = useState<OptOut[]>([])
  const [createFields, setCreateFields] = useState<FieldValues>({})
  const [status, setStatus] = useState<number | null>(null)
  const [data, setData] = useState<unknown>(null)

  async function loadList() {
    const result = await apiRequest<{ OptOuts?: OptOut[] }>('/api/optout?recordsPerPage=50&page=1')
    setStatus(result.status)
    setData(result.data)
    if (result.status < 400) setOptOuts(result.data.OptOuts ?? [])
  }

  useEffect(() => {
    loadList()
  }, [])

  async function handleCreate(e: FormEvent) {
    e.preventDefault()
    const result = await apiRequest('/api/optout', { method: 'POST', body: createFields })
    setStatus(result.status)
    setData(result.data)
    if (result.status < 400) {
      setCreateFields({})
      loadList()
    }
  }

  async function handleDetail(id?: string) {
    if (!id) return
    const result = await apiRequest(`/api/optout/${id}`)
    setStatus(result.status)
    setData(result.data)
  }

  async function handleDelete(id?: string) {
    if (!id) return
    const result = await apiRequest(`/api/optout/${id}`, { method: 'DELETE' })
    setStatus(result.status)
    setData(result.data)
    if (result.status < 400) loadList()
  }

  return (
    <div className="max-w-4xl space-y-8">
      <div>
        <h1 className="text-xl font-semibold">Opt-Out Management</h1>
        <p className="text-sm text-muted-foreground">client.Configuration.OptOut.List / .Create / .Details / .Delete</p>
      </div>

      <section className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="font-medium">Opt-Outs</h2>
          <Button type="button" variant="outline" size="sm" onClick={loadList}>
            Refresh
          </Button>
        </div>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Destination</TableHead>
              <TableHead>Type</TableHead>
              <TableHead>Created</TableHead>
              <TableHead></TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {optOuts.map((o) => (
              <TableRow key={o.ID}>
                <TableCell>{o.Destination}</TableCell>
                <TableCell>{o.DestType}</TableCell>
                <TableCell>{o.CreatedTimeLocal}</TableCell>
                <TableCell className="flex gap-2">
                  <Button type="button" variant="outline" size="sm" onClick={() => handleDetail(o.ID)}>
                    Detail
                  </Button>
                  <Button type="button" variant="destructive" size="sm" onClick={() => handleDelete(o.ID)}>
                    Delete
                  </Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </section>

      <section className="space-y-4">
        <h2 className="font-medium">Add Opt-Out</h2>
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
            Add
          </Button>
        </form>
      </section>

      <ResponseViewer status={status} data={data} />
    </div>
  )
}