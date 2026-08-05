import { useState, type FormEvent } from 'react'
import { Button } from '@/components/ui/button'
import { TextField, SelectField, type FieldValues } from '@/components/form-fields'
import { ResponseViewer } from '@/components/response-viewer'
import { apiRequest, resolveMessageId } from '@/lib/api-client'

// Mirrors tnzapi-ts-samples/nextjs/app/actions/abort (client.Actions.Abort.SendRequest), with one
// fix: that reference's channel list is missing WhatsApp/RCS. The .NET SDK's own Actions interfaces
// (Core/Interfaces/Actions/*.cs) confirm Abort exists on all 7 channels that have an Actions facade
// at all — SMS/Email/Fax/TTS/Voice/WhatsApp/RCS. Workflow has no Actions facade (docs/workflow.md).
// Channel now only builds the URL (PATCH /api/{channel}/{messageId}/abort) — it's no longer sent
// in the body, matching the real TNZ REST API's own per-channel wire shape.
const CHANNELS = ['SMS', 'Email', 'Fax', 'TTS', 'Voice', 'WhatsApp', 'RCS']

export default function AbortPage() {
  const [fields, setFields] = useState<FieldValues>({ MessageID: '', Channel: 'SMS' })
  const [status, setStatus] = useState<number | null>(null)
  const [data, setData] = useState<unknown>(null)
  const [submitting, setSubmitting] = useState(false)

  function setText(name: string, value: string) {
    setFields((f) => ({ ...f, [name]: value }))
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    setSubmitting(true)
    const channel = ((fields.Channel as string) ?? 'SMS').toLowerCase()
    const resolved = resolveMessageId(fields.MessageID as string)
    if ('status' in resolved) {
      setStatus(resolved.status)
      setData(resolved.data)
      setSubmitting(false)
      return
    }
    const { status: resStatus, data: resData } = await apiRequest(`/api/${channel}/${resolved.messageId}/abort`, { method: 'PATCH' })
    setStatus(resStatus)
    setData(resData)
    setSubmitting(false)
  }

  return (
    <div className="max-w-2xl space-y-6">
      <div>
        <h1 className="text-xl font-semibold">Abort a Job</h1>
        <p className="text-sm text-muted-foreground">
          client.Actions.&lt;Channel&gt;.AbortAsync (supports SMS, Email, Fax, TTS, Voice, WhatsApp, RCS)
        </p>
      </div>
      <form onSubmit={handleSubmit} className="space-y-4">
        <TextField label="Message ID" name="MessageID" values={fields} onChange={setText} />
        <SelectField label="Channel" name="Channel" values={fields} onChange={setText} options={CHANNELS} />
        <Button type="submit" disabled={submitting}>
          {submitting ? 'Aborting...' : 'Abort'}
        </Button>
      </form>
      <ResponseViewer status={status} data={data} />
    </div>
  )
}