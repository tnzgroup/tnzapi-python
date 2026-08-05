import { useState, type FormEvent } from 'react'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { TextField, SelectField, type FieldValues } from '@/components/form-fields'
import { HtmlEditor } from '@/components/html-editor'
import { AttachmentPicker, type AttachmentValue } from '@/components/attachment-picker'
import { ResponseViewer } from '@/components/response-viewer'
import { apiRequest } from '@/lib/api-client'
import type { SendEmailRequest, MessageApiResult, MessageStatusApiResult } from '@/lib/api-client'

export default function EmailPage() {
  const [sendFields, setSendFields] = useState<FieldValues>({
    EmailAddress: '',
    Subject: 'Hello from TNZAPI Demo!',
  })
  const [messageHtml, setMessageHtml] = useState('<p>Hello from TNZAPI Demo!</p>')
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
    const body: SendEmailRequest = {
      EmailAddress: (sendFields.EmailAddress as string) ?? '',
      Subject: (sendFields.Subject as string) ?? '',
      MessageHtml: messageHtml,
      Reference: sendFields.Reference as string,
      TemplateId: sendFields.TemplateId as string,
      SmtpFrom: sendFields.SmtpFrom as string,
      From: sendFields.From as string,
      FromEmail: sendFields.FromEmail as string,
      ReplyTo: sendFields.ReplyTo as string,
      CcEmail: sendFields.CcEmail as string,
      WebhookCallbackUrl: sendFields.WebhookCallbackUrl as string,
      WebhookCallbackFormat: sendFields.WebhookCallbackFormat as string,
      ReportTo: sendFields.ReportTo as string,
      SendTime: sendFields.SendTime as string,
      Timezone: sendFields.Timezone as string,
      SubAccount: sendFields.SubAccount as string,
      Department: sendFields.Department as string,
      ChargeCode: sendFields.ChargeCode as string,
      NotificationType: sendFields.NotificationType as string,
      SendMode: sendFields.SendMode as string,
      Attachments: attachments.length > 0 ? attachments : undefined,
    }
    const { status, data } = await apiRequest<MessageApiResult>('/api/email/send', { method: 'POST', body })
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
      `/api/email/status/${encodeURIComponent(id)}`,
    )
    setStatusStatus(status)
    setStatusData(data)
    setCheckingStatus(false)
  }

  return (
    <div className="max-w-2xl space-y-6">
      <div>
        <h1 className="text-xl font-semibold">Send Email</h1>
        <p className="text-sm text-muted-foreground">client.Messaging.Email.SendMessageAsync</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Send Email</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSend} className="space-y-4">
            <TextField
              label="Email Address"
              name="EmailAddress"
              values={sendFields}
              onChange={setSendField}
              placeholder="test@example.com"
            />
            <TextField label="Subject" name="Subject" values={sendFields} onChange={setSendField} />
            <HtmlEditor label="Message" value={messageHtml} onChange={setMessageHtml} />
            <AttachmentPicker label="Attachments" value={attachments} onChange={setAttachments} />

            <div className="border-t pt-4">
              <h2 className="mb-3 text-sm font-medium text-muted-foreground">Sender</h2>
              <div className="grid grid-cols-2 gap-4">
                <TextField label="From" name="From" values={sendFields} onChange={setSendField} placeholder="Display name" />
                <TextField label="From Email" name="FromEmail" values={sendFields} onChange={setSendField} placeholder="sender@example.com" />
                <TextField label="SMTP From" name="SmtpFrom" values={sendFields} onChange={setSendField} />
                <TextField label="Reply To" name="ReplyTo" values={sendFields} onChange={setSendField} />
                <TextField label="CC Email" name="CcEmail" values={sendFields} onChange={setSendField} />
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
                <TextField label="Send Time" name="SendTime" values={sendFields} onChange={setSendField} placeholder="2026-07-15 09:00:00" />
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