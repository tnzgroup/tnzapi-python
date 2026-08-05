import { useState, type FormEvent } from 'react'
import { Button } from '@/components/ui/button'
import { TextField, SelectField, type FieldValues } from '@/components/form-fields'
import { ResponseViewer } from '@/components/response-viewer'
import { apiRequest } from '@/lib/api-client'

// Mirrors tnzapi-ts-samples/nextjs/app/reports/sms-received (client.Reports.SMSReceived.Poll),
// adapted to TNZAPI.NET: no unified Reports facade, so this hits each channel's own controller GET
// /api/<channel>/received (query-string params, matching <X>Api.cs's ReceivedAsync(timePeriod,
// recordsPerPage, page, dateFrom, dateTo) signature) rather than a POST with a JSON body. Received
// is only implemented for SMS/WhatsApp/RCS (see Sms/WhatsApp/RcsController.Received) — Email/Fax/
// TTS/Voice/Workflow have no equivalent endpoint, so they're excluded from the channel list, the
// same SDK-capability-gap reasoning StatusPage uses to exclude Workflow from its own channel list.
// dateFrom/dateTo (both or neither) take precedence over timePeriod when supplied — the SDK
// validates that mutual-exclusivity/range client-side, so this page doesn't duplicate it, same as
// leaving other SDK-validated constraints to surface via the response rather than guessing at them
// here.
// Explicit label -> route-segment map, not label.toLowerCase() — relying on that convention holding
// for every future label (e.g. one with a space or slash) would silently hit the wrong endpoint;
// this keeps CHANNELS as the single source of truth for what's selectable while keeping the actual
// route segment explicit.
const CHANNELS = ['SMS', 'WhatsApp', 'RCS']
const CHANNEL_ROUTES: Record<string, string> = { SMS: 'sms', WhatsApp: 'whatsapp', RCS: 'rcs' }

export default function ReceivedPage() {
  const [fields, setFields] = useState<FieldValues>({ Channel: 'SMS', TimePeriod: '1440' })
  const [status, setStatus] = useState<number | null>(null)
  const [data, setData] = useState<unknown>(null)
  const [submitting, setSubmitting] = useState(false)

  function setText(name: string, value: string) {
    setFields((f) => ({ ...f, [name]: value }))
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    setSubmitting(true)
    const channel = CHANNEL_ROUTES[fields.Channel as string] ?? 'sms'
    const params = new URLSearchParams()
    const usingDateRange = Boolean(fields.DateFrom) || Boolean(fields.DateTo)
    // TimePeriod defaults to '1440' and stays populated even once a date field is filled in — don't
    // send it alongside DateFrom/DateTo, or the backend's dateFrom-takes-precedence dispatch still
    // works but a stale TimePeriod value sitting in the query string is confusing at best.
    if (fields.TimePeriod && !usingDateRange) params.set('timePeriod', fields.TimePeriod as string)
    if (fields.DateFrom) params.set('dateFrom', fields.DateFrom as string)
    if (fields.DateTo) params.set('dateTo', fields.DateTo as string)
    if (fields.RecordsPerPage) params.set('recordsPerPage', fields.RecordsPerPage as string)
    if (fields.Page) params.set('page', fields.Page as string)
    const query = params.toString() ? `?${params.toString()}` : ''
    const { status: resStatus, data: resData } = await apiRequest<Record<string, unknown>>(
      `/api/${channel}/received${query}`,
    )
    setStatus(resStatus)
    setData(resData)
    setSubmitting(false)
  }

  return (
    <div className="max-w-2xl space-y-6">
      <div>
        <h1 className="text-xl font-semibold">Received</h1>
        <p className="text-sm text-muted-foreground">client.Messaging.&lt;Channel&gt;.ReceivedAsync</p>
      </div>
      <form onSubmit={handleSubmit} className="space-y-4">
        <SelectField label="Channel" name="Channel" values={fields} onChange={setText} options={CHANNELS} />
        <TextField label="Time Period (minutes, 1-1440)" name="TimePeriod" values={fields} onChange={setText} />
        <div className="grid grid-cols-2 gap-4">
          <TextField label="Date From" name="DateFrom" values={fields} onChange={setText} placeholder="2026-08-01 09:00:00" />
          <TextField label="Date To" name="DateTo" values={fields} onChange={setText} placeholder="2026-08-01 17:00:00" />
        </div>
        <p className="text-xs text-muted-foreground">Date To requires Date From — both or neither.</p>
        <div className="grid grid-cols-2 gap-4">
          <TextField label="Records Per Page" name="RecordsPerPage" values={fields} onChange={setText} />
          <TextField label="Page" name="Page" values={fields} onChange={setText} />
        </div>
        <Button type="submit" disabled={submitting}>
          {submitting ? 'Polling...' : 'Get Received Messages'}
        </Button>
      </form>
      <ResponseViewer status={status} data={data} />
    </div>
  )
}
