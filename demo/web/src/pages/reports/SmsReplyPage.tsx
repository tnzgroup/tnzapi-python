import { useState, type FormEvent } from 'react'
import { Button } from '@/components/ui/button'
import { TextField, type FieldValues } from '@/components/form-fields'
import { ResponseViewer } from '@/components/response-viewer'
import { apiRequest } from '@/lib/api-client'
import type { MessageStatusApiResult } from '@/lib/api-client'

// Mirrors tnzapi-ts-samples/nextjs/app/reports/sms-reply (client.Reports.SMSReply.Poll), adapted to
// how TNZAPI.NET actually exposes this: there's no unified Reports facade, and SMSReply is SMS-only
// — no other channel's SDK module has an equivalent method — so this hits the SMS controller's own
// GET /api/sms/reply/{id} (query-string RecordsPerPage/Page, matching the SDK's
// SMSReplyAsync(messageID, recordsPerPage, page) signature) rather than a POST with a JSON body.
// Reply text lives in each recipient's Recipients[].SMSReplies[].MessageText in the raw response.
export default function SmsReplyPage() {
  const [fields, setFields] = useState<FieldValues>({ MessageID: '' })
  const [status, setStatus] = useState<number | null>(null)
  const [data, setData] = useState<unknown>(null)
  const [submitting, setSubmitting] = useState(false)

  function setText(name: string, value: string) {
    setFields((f) => ({ ...f, [name]: value }))
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    setSubmitting(true)
    const id = (fields.MessageID as string) ?? ''
    const params = new URLSearchParams()
    if (fields.RecordsPerPage) params.set('recordsPerPage', fields.RecordsPerPage as string)
    if (fields.Page) params.set('page', fields.Page as string)
    const query = params.toString() ? `?${params.toString()}` : ''
    const { status: resStatus, data: resData } = await apiRequest<MessageStatusApiResult>(
      `/api/sms/reply/${encodeURIComponent(id)}${query}`,
    )
    setStatus(resStatus)
    setData(resData)
    setSubmitting(false)
  }

  return (
    <div className="max-w-2xl space-y-6">
      <div>
        <h1 className="text-xl font-semibold">SMS Replies</h1>
        <p className="text-sm text-muted-foreground">client.Messaging.SMS.SMSReplyAsync</p>
      </div>
      <form onSubmit={handleSubmit} className="space-y-4">
        <TextField label="Message ID" name="MessageID" values={fields} onChange={setText} />
        <div className="grid grid-cols-2 gap-4">
          <TextField label="Records Per Page" name="RecordsPerPage" values={fields} onChange={setText} />
          <TextField label="Page" name="Page" values={fields} onChange={setText} />
        </div>
        <Button type="submit" disabled={submitting}>
          {submitting ? 'Polling...' : 'Get Replies'}
        </Button>
      </form>
      <ResponseViewer status={status} data={data} />
    </div>
  )
}