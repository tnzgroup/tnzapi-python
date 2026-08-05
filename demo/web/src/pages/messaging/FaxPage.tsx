import { useState, type FormEvent } from 'react'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { TextField, SelectField, type FieldValues } from '@/components/form-fields'
import { AttachmentPicker, type AttachmentValue } from '@/components/attachment-picker'
import { ResponseViewer } from '@/components/response-viewer'
import { apiRequest } from '@/lib/api-client'
import type { SendFaxRequest, MessageApiResult, MessageStatusApiResult } from '@/lib/api-client'

function toOptionalNumber(value: string | undefined): number | undefined {
  if (!value) return undefined
  const n = Number(value)
  return Number.isFinite(n) ? n : undefined
}

export default function FaxPage() {
  const [sendFields, setSendFields] = useState<FieldValues>({ ToNumber: '' })
  const [attachments, setAttachments] = useState<AttachmentValue[]>([])
  const [sendStatus, setSendStatus] = useState<number | null>(null)
  const [sendData, setSendData] = useState<unknown>(null)
  const [sending, setSending] = useState(false)

  const [statusFields, setStatusFields] = useState<FieldValues>({ MessageID: '' })
  const [statusStatus, setStatusStatus] = useState<number | null>(null)
  const [statusData, setStatusData] = useState<unknown>(null)
  const [checkingStatus, setCheckingStatus] = useState(false)

  function setSendField(name: string, value: string) {
    setSendFields((f) => ({ ...f, [name]: value }))
  }
  function setStatusField(name: string, value: string) {
    setStatusFields((f) => ({ ...f, [name]: value }))
  }

  async function handleSend(e: FormEvent) {
    e.preventDefault()
    setSending(true)
    const body: SendFaxRequest = {
      ToNumber: (sendFields.ToNumber as string) ?? '',
      Attachments: attachments.length > 0 ? attachments : undefined,
      Reference: sendFields.Reference as string,
      TemplateId: sendFields.TemplateId as string,
      NotificationType: sendFields.NotificationType as string,
      WebhookCallbackUrl: sendFields.WebhookCallbackUrl as string,
      WebhookCallbackFormat: sendFields.WebhookCallbackFormat as string,
      ReportTo: sendFields.ReportTo as string,
      SendTime: sendFields.SendTime as string,
      Timezone: sendFields.Timezone as string,
      SubAccount: sendFields.SubAccount as string,
      Department: sendFields.Department as string,
      ChargeCode: sendFields.ChargeCode as string,
      Csid: sendFields.Csid as string,
      Resolution: sendFields.Resolution as string,
      WatermarkFolder: sendFields.WatermarkFolder as string,
      WatermarkFirstPage: sendFields.WatermarkFirstPage as string,
      WatermarkAllPages: sendFields.WatermarkAllPages as string,
      RetryAttempts: toOptionalNumber(sendFields.RetryAttempts as string | undefined),
      RetryPeriod: toOptionalNumber(sendFields.RetryPeriod as string | undefined),
      SendMode: sendFields.SendMode as string,
    }
    const { status, data } = await apiRequest<MessageApiResult>('/api/fax/send', { method: 'POST', body })
    setSendStatus(status)
    setSendData(data)
    if (data.MessageID) {
      setStatusField('MessageID', data.MessageID)
    }
    setSending(false)
  }

  async function handleCheckStatus(e: FormEvent) {
    e.preventDefault()
    setCheckingStatus(true)
    const id = (statusFields.MessageID as string) ?? ''
    const { status, data } = await apiRequest<MessageStatusApiResult>(
      `/api/fax/status/${encodeURIComponent(id)}`,
    )
    setStatusStatus(status)
    setStatusData(data)
    setCheckingStatus(false)
  }

  return (
    <div className="max-w-2xl space-y-6">
      <div>
        <h1 className="text-xl font-semibold">Send Fax</h1>
        <p className="text-sm text-muted-foreground">client.Messaging.Fax.SendMessageAsync</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Send Fax</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSend} className="space-y-4">
            <TextField
              label="To Number"
              name="ToNumber"
              values={sendFields}
              onChange={setSendField}
              placeholder="+6421000001"
            />
            <AttachmentPicker label="Document(s)" value={attachments} onChange={setAttachments} />

            <div className="border-t pt-4">
              <h2 className="mb-3 text-sm font-medium text-muted-foreground">Fax options</h2>
              <div className="grid grid-cols-2 gap-4">
                <TextField label="CSID" name="Csid" values={sendFields} onChange={setSendField} />
                <SelectField
                  label="Resolution"
                  name="Resolution"
                  values={sendFields}
                  onChange={setSendField}
                  options={['Low', 'High']}
                />
                <TextField label="Retry Attempts" name="RetryAttempts" values={sendFields} onChange={setSendField} />
                <TextField label="Retry Period" name="RetryPeriod" values={sendFields} onChange={setSendField} />
                <TextField label="Watermark Folder" name="WatermarkFolder" values={sendFields} onChange={setSendField} />
                <TextField label="Watermark First Page" name="WatermarkFirstPage" values={sendFields} onChange={setSendField} />
                <TextField label="Watermark All Pages" name="WatermarkAllPages" values={sendFields} onChange={setSendField} />
              </div>
            </div>

            <div className="border-t pt-4">
              <h2 className="mb-3 text-sm font-medium text-muted-foreground">Tracking &amp; template</h2>
              <div className="grid grid-cols-2 gap-4">
                <TextField label="Reference" name="Reference" values={sendFields} onChange={setSendField} />
                <TextField label="Template ID" name="TemplateId" values={sendFields} onChange={setSendField} />
              </div>
            </div>

            <div className="border-t pt-4">
              <h2 className="mb-3 text-sm font-medium text-muted-foreground">Scheduling</h2>
              <div className="grid grid-cols-2 gap-4">
                <TextField label="Send Time" name="SendTime" values={sendFields} onChange={setSendField} placeholder="2026-08-01 09:00:00" />
                <TextField label="Timezone" name="Timezone" values={sendFields} onChange={setSendField} placeholder="New Zealand" />
              </div>
            </div>

            <div className="border-t pt-4">
              <h2 className="mb-3 text-sm font-medium text-muted-foreground">Webhook &amp; notifications</h2>
              <div className="grid grid-cols-2 gap-4">
                <SelectField
                  label="Notification Type"
                  name="NotificationType"
                  values={sendFields}
                  onChange={setSendField}
                  options={['None', 'Webhook', 'Email']}
                />
                <SelectField
                  label="Webhook Callback Format"
                  name="WebhookCallbackFormat"
                  values={sendFields}
                  onChange={setSendField}
                  options={['JSON', 'XML', 'POST', 'GET']}
                />
                <TextField label="Webhook Callback URL" name="WebhookCallbackUrl" values={sendFields} onChange={setSendField} />
                <TextField label="Report To" name="ReportTo" values={sendFields} onChange={setSendField} placeholder="notify@example.com" />
              </div>
            </div>

            <div className="border-t pt-4">
              <h2 className="mb-3 text-sm font-medium text-muted-foreground">Account &amp; billing</h2>
              <div className="grid grid-cols-2 gap-4">
                <TextField label="Sub Account" name="SubAccount" values={sendFields} onChange={setSendField} />
                <TextField label="Department" name="Department" values={sendFields} onChange={setSendField} />
                <TextField label="Charge Code" name="ChargeCode" values={sendFields} onChange={setSendField} />
                <SelectField
                  label="Send Mode"
                  name="SendMode"
                  values={sendFields}
                  onChange={setSendField}
                  options={['Live', 'Test']}
                />
              </div>
            </div>

            <Button type="submit" disabled={sending}>
              {sending ? 'Sending...' : 'Send'}
            </Button>
            <ResponseViewer status={sendStatus} data={sendData} />
          </form>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Check Status</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleCheckStatus} className="space-y-4">
            <TextField label="Message ID" name="MessageID" values={statusFields} onChange={setStatusField} />
            <Button type="submit" disabled={checkingStatus}>
              {checkingStatus ? 'Checking...' : 'Check status'}
            </Button>
            <ResponseViewer status={statusStatus} data={statusData} />
          </form>
        </CardContent>
      </Card>
    </div>
  )
}