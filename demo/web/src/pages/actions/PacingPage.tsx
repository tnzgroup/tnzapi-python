import { useState, type FormEvent } from 'react'
import { Button } from '@/components/ui/button'
import { TextField, SelectField, type FieldValues } from '@/components/form-fields'
import { ResponseViewer } from '@/components/response-viewer'
import { apiRequest, resolveMessageId } from '@/lib/api-client'

// Mirrors tnzapi-ts-samples/nextjs/app/actions/pacing (client.Actions.Pacing.SendRequest), which
// already correctly limits this to TTS/Voice (confirmed via the .NET SDK's
// Core/Interfaces/Actions/{ITTSActionsApi,IVoiceActionsApi}.cs — no other channel has a Pacing
// method). NumberOfOperators is a required int on the .NET SDK's Pacing(MessageID, int) signature.
// Channel now only builds the URL (PATCH /api/{channel}/{messageId}/pacing) — it's no longer sent
// in the body, matching the real TNZ REST API's own per-channel wire shape.
const CHANNELS = ['TTS', 'Voice']

export default function PacingPage() {
  const [fields, setFields] = useState<FieldValues>({ MessageID: '', Channel: 'TTS', NumberOfOperators: '' })
  const [status, setStatus] = useState<number | null>(null)
  const [data, setData] = useState<unknown>(null)
  const [submitting, setSubmitting] = useState(false)

  function setText(name: string, value: string) {
    setFields((f) => ({ ...f, [name]: value }))
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    setSubmitting(true)
    const channel = ((fields.Channel as string) ?? 'TTS').toLowerCase()
    const resolved = resolveMessageId(fields.MessageID as string)
    if ('status' in resolved) {
      setStatus(resolved.status)
      setData(resolved.data)
      setSubmitting(false)
      return
    }
    const body = { NumberOfOperators: Number(fields.NumberOfOperators ?? 0) }
    const { status: resStatus, data: resData } = await apiRequest(`/api/${channel}/${resolved.messageId}/pacing`, { method: 'PATCH', body })
    setStatus(resStatus)
    setData(resData)
    setSubmitting(false)
  }

  return (
    <div className="max-w-2xl space-y-6">
      <div>
        <h1 className="text-xl font-semibold">Adjust Pacing</h1>
        <p className="text-sm text-muted-foreground">
          client.Actions.&lt;Channel&gt;.PacingAsync (supports TTS, Voice only)
        </p>
      </div>
      <form onSubmit={handleSubmit} className="space-y-4">
        <TextField label="Message ID" name="MessageID" values={fields} onChange={setText} />
        <SelectField label="Channel" name="Channel" values={fields} onChange={setText} options={CHANNELS} />
        <TextField label="Number Of Operators" name="NumberOfOperators" values={fields} onChange={setText} placeholder="5" />
        <Button type="submit" disabled={submitting}>
          {submitting ? 'Updating...' : 'Update Pacing'}
        </Button>
      </form>
      <ResponseViewer status={status} data={data} />
    </div>
  )
}