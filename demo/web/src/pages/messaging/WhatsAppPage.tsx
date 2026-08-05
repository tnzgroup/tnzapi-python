import { useState, type FormEvent } from 'react'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { TextField, SelectField, type FieldValues } from '@/components/form-fields'
import { AttachmentPicker, type AttachmentValue } from '@/components/attachment-picker'
import { ResponseViewer } from '@/components/response-viewer'
import { apiRequest } from '@/lib/api-client'
import type { SendWhatsAppRequest, MessageApiResult, MessageStatusApiResult } from '@/lib/api-client'

const FALLBACK_MODES = ['RCS', 'SMS', 'Voice']
const CUSTOM_FIELDS = Array.from({ length: 9 }, (_, i) => `Custom${i + 1}`)

export default function WhatsAppPage() {
  const [sendFields, setSendFields] = useState<FieldValues>({
    ToNumber: '',
    Message: 'Hello from TNZAPI Demo!',
  })
  const [attachments, setAttachments] = useState<AttachmentValue[]>([])
  const [fallbackMode, setFallbackMode] = useState<string[]>([])
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
  function toggleFallbackMode(mode: string, checked: boolean) {
    setFallbackMode((modes) => (checked ? [...modes, mode] : modes.filter((m) => m !== mode)))
  }

  async function handleSend(e: FormEvent) {
    e.preventDefault()
    setSending(true)
    const body: SendWhatsAppRequest = {
      ToNumber: (sendFields.ToNumber as string) ?? '',
      Message: (sendFields.Message as string) ?? '',
      Attachments: attachments.length > 0 ? attachments : undefined,
      Reference: sendFields.Reference as string,
      TemplateId: sendFields.TemplateId as string,
      FallbackMode: fallbackMode.length > 0 ? fallbackMode : undefined,
      FromNumber: sendFields.FromNumber as string,
      Custom1: sendFields.Custom1 as string,
      Custom2: sendFields.Custom2 as string,
      Custom3: sendFields.Custom3 as string,
      Custom4: sendFields.Custom4 as string,
      Custom5: sendFields.Custom5 as string,
      Custom6: sendFields.Custom6 as string,
      Custom7: sendFields.Custom7 as string,
      Custom8: sendFields.Custom8 as string,
      Custom9: sendFields.Custom9 as string,
      NotificationType: sendFields.NotificationType as string,
      WebhookCallbackUrl: sendFields.WebhookCallbackUrl as string,
      WebhookCallbackFormat: sendFields.WebhookCallbackFormat as string,
      ReportTo: sendFields.ReportTo as string,
      SendTime: sendFields.SendTime as string,
      Timezone: sendFields.Timezone as string,
      SubAccount: sendFields.SubAccount as string,
      Department: sendFields.Department as string,
      ChargeCode: sendFields.ChargeCode as string,
      SendMode: sendFields.SendMode as string,
    }
    const { status, data } = await apiRequest<MessageApiResult>('/api/whatsapp/send', { method: 'POST', body })
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
      `/api/whatsapp/status/${encodeURIComponent(id)}`,
    )
    setStatusStatus(status)
    setStatusData(data)
    setCheckingStatus(false)
  }

  return (
    <div className="max-w-2xl space-y-6">
      <div>
        <h1 className="text-xl font-semibold">Send WhatsApp</h1>
        <p className="text-sm text-muted-foreground">client.Messaging.WhatsApp.SendMessageAsync</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Send WhatsApp</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSend} className="space-y-4">
            <div className="rounded-md border border-amber-500/50 bg-amber-500/10 px-3 py-2 text-sm text-amber-700 dark:text-amber-400">
              WhatsApp requires a message template pre-approved and configured with TNZ — contact
              TNZ to set one up, then enter its Template ID below. The Message field is disabled
              until then, since its content must exactly match your approved template.
            </div>
            <TextField
              label="Template ID"
              name="TemplateId"
              values={sendFields}
              onChange={setSendField}
              placeholder="UUID"
            />
            <TextField
              label="To Number"
              name="ToNumber"
              values={sendFields}
              onChange={setSendField}
              placeholder="+6421000001"
            />
            <TextField label="Message" name="Message" values={sendFields} onChange={setSendField} multiline disabled />
            <AttachmentPicker label="Attachments" value={attachments} onChange={setAttachments} disabled />

            <div className="border-t pt-4">
              <h2 className="mb-3 text-sm font-medium text-muted-foreground">Personalisation</h2>
              <p className="mb-3 text-xs text-muted-foreground">
                Per-recipient values substituted into your template&apos;s [[Custom1]]..[[Custom9]] tokens.
              </p>
              <div className="grid grid-cols-3 gap-4">
                {CUSTOM_FIELDS.map((field) => (
                  <TextField key={field} label={field} name={field} values={sendFields} onChange={setSendField} />
                ))}
              </div>
            </div>

            <div className="border-t pt-4">
              <h2 className="mb-3 text-sm font-medium text-muted-foreground">Sender &amp; delivery</h2>
              <div className="grid grid-cols-2 gap-4">
                <TextField label="From Number" name="FromNumber" values={sendFields} onChange={setSendField} />
              </div>
              <div className="mt-3 space-y-1">
                <span className="text-sm font-medium">Fallback Mode</span>
                <div className="flex flex-wrap gap-4">
                  {FALLBACK_MODES.map((mode) => (
                    <label key={mode} className="flex items-center gap-2 text-sm">
                      <input
                        type="checkbox"
                        checked={fallbackMode.includes(mode)}
                        onChange={(e) => toggleFallbackMode(mode, e.target.checked)}
                      />
                      {mode}
                    </label>
                  ))}
                </div>
              </div>
            </div>

            <div className="border-t pt-4">
              <h2 className="mb-3 text-sm font-medium text-muted-foreground">Tracking</h2>
              <div className="grid grid-cols-2 gap-4">
                <TextField label="Reference" name="Reference" values={sendFields} onChange={setSendField} />
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