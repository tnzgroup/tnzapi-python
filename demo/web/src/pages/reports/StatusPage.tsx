import { useState, type FormEvent } from 'react'
import { Button } from '@/components/ui/button'
import { TextField, SelectField, type FieldValues } from '@/components/form-fields'
import { ResponseViewer } from '@/components/response-viewer'
import { apiRequest } from '@/lib/api-client'
import type { MessageStatusApiResult } from '@/lib/api-client'

// Mirrors tnzapi-ts-samples/nextjs/app/reports/status (client.Reports.Status.Poll) as closely as
// TNZAPI.NET's actual capabilities allow. Two genuine SDK gaps, not faked here:
// - No unified client.Reports facade in TNZAPI.NET — v3.00 folded the old XML API's Reports concept
//   into each messaging module's own Status method (client.Messaging.<X>.StatusAsync), so this page
//   is a thin channel-selector wrapper over the per-channel /api/<channel>/status/{id} endpoints
//   already built for each Send page's own "Check Status" card.
// - No RecordsPerPage/Page pagination params — tnzapi-ts's Reports.Status.Poll accepts them,
//   TNZAPI.NET's Status(MessageID) method doesn't expose them at all, so they're omitted rather than
//   added as non-functional fields.
// Workflow is excluded from the channel list — it has no Status endpoint at all (docs/workflow.md).
// Every label's lowercase form matches its /api/<channel> route segment exactly (WhatsApp ->
// whatsapp, RCS -> rcs, TTS -> tts, ...), so no separate label-to-route map is needed.
const CHANNELS = ['SMS', 'Email', 'Fax', 'TTS', 'Voice', 'WhatsApp', 'RCS']

export default function StatusPage() {
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
    const channel = ((fields.Channel as string) || 'SMS').toLowerCase()
    const id = (fields.MessageID as string) ?? ''
    const { status: resStatus, data: resData } = await apiRequest<MessageStatusApiResult>(
      `/api/${channel}/status/${encodeURIComponent(id)}`,
    )
    setStatus(resStatus)
    setData(resData)
    setSubmitting(false)
  }

  return (
    <div className="max-w-2xl space-y-6">
      <div>
        <h1 className="text-xl font-semibold">Poll Message Status</h1>
        <p className="text-sm text-muted-foreground">client.Messaging.&lt;Channel&gt;.StatusAsync</p>
      </div>
      <form onSubmit={handleSubmit} className="space-y-4">
        <TextField label="Message ID" name="MessageID" values={fields} onChange={setText} />
        <SelectField label="Channel" name="Channel" values={fields} onChange={setText} options={CHANNELS} />
        <Button type="submit" disabled={submitting}>
          {submitting ? 'Polling...' : 'Poll Status'}
        </Button>
      </form>
      <ResponseViewer status={status} data={data} />
    </div>
  )
}