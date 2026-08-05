import { useState, type FormEvent } from 'react'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { TextField, SelectField, CheckboxField, type FieldValues } from '@/components/form-fields'
import { KeypadEditor, type KeypadValue } from '@/components/keypad-editor'
import { ResponseViewer } from '@/components/response-viewer'
import { apiRequest } from '@/lib/api-client'
import type { SendTtsRequest, MessageApiResult, MessageStatusApiResult } from '@/lib/api-client'

function toOptionalNumber(value: string | undefined): number | undefined {
  if (!value) return undefined
  const n = Number(value)
  return Number.isFinite(n) ? n : undefined
}

export default function TtsPage() {
  const [sendFields, setSendFields] = useState<FieldValues>({
    ToNumber: '',
    MessageToPeople: 'Hello from TNZAPI Demo!',
  })
  const [keypads, setKeypads] = useState<KeypadValue[]>([])
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
    const body: SendTtsRequest = {
      ToNumber: (sendFields.ToNumber as string) ?? '',
      MessageToPeople: (sendFields.MessageToPeople as string) ?? '',
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
      MessageToAnswerPhones: sendFields.MessageToAnswerPhones as string,
      AnswerPhoneMode: sendFields.AnswerPhoneMode as string,
      Keypads: keypads.length > 0 ? keypads : undefined,
      KeypadOptionRequired: Boolean(sendFields.KeypadOptionRequired),
      CallRouteMessageOnWrongKey: sendFields.CallRouteMessageOnWrongKey as string,
      CallRouteMessageToPeople: sendFields.CallRouteMessageToPeople as string,
      CallRouteMessageToOperators: sendFields.CallRouteMessageToOperators as string,
      EndCallMessage: sendFields.EndCallMessage as string,
      NumberOfOperators: toOptionalNumber(sendFields.NumberOfOperators as string | undefined),
      RetryAttempts: toOptionalNumber(sendFields.RetryAttempts as string | undefined),
      RetryPeriod: toOptionalNumber(sendFields.RetryPeriod as string | undefined),
      CallerId: sendFields.CallerId as string,
      Voice: sendFields.Voice as string,
      Options: sendFields.Options as string,
      SendMode: sendFields.SendMode as string,
    }
    const { status, data } = await apiRequest<MessageApiResult>('/api/tts/send', { method: 'POST', body })
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
      `/api/tts/status/${encodeURIComponent(id)}`,
    )
    setStatusStatus(status)
    setStatusData(data)
    setCheckingStatus(false)
  }

  return (
    <div className="max-w-2xl space-y-6">
      <div>
        <h1 className="text-xl font-semibold">Send TTS</h1>
        <p className="text-sm text-muted-foreground">client.Messaging.TTS.SendMessageAsync</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Send TTS</CardTitle>
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
            <TextField
              label="Message To People"
              name="MessageToPeople"
              values={sendFields}
              onChange={setSendField}
              multiline
            />

            <div className="border-t pt-4">
              <h2 className="mb-3 text-sm font-medium text-muted-foreground">Answering machine</h2>
              <div className="grid grid-cols-2 gap-4">
                <TextField
                  label="Message To Answer Phones"
                  name="MessageToAnswerPhones"
                  values={sendFields}
                  onChange={setSendField}
                  multiline
                />
                <SelectField
                  label="Answer Phone Mode"
                  name="AnswerPhoneMode"
                  values={sendFields}
                  onChange={setSendField}
                  options={['NDAS', 'NDAF', 'DAS', 'DAF']}
                />
              </div>
            </div>

            <div className="border-t pt-4">
              <h2 className="mb-3 text-sm font-medium text-muted-foreground">Keypad routing (IVR)</h2>
              <KeypadEditor label="Keypads" value={keypads} onChange={setKeypads} />
              <div className="mt-3">
                <CheckboxField
                  label="Keypad Option Required"
                  name="KeypadOptionRequired"
                  values={sendFields}
                  onChange={(name, value) => setSendFields((f) => ({ ...f, [name]: value }))}
                />
              </div>
              <div className="mt-3 grid grid-cols-2 gap-4">
                <TextField label="Call Route Message On Wrong Key" name="CallRouteMessageOnWrongKey" values={sendFields} onChange={setSendField} />
                <TextField label="Call Route Message To People" name="CallRouteMessageToPeople" values={sendFields} onChange={setSendField} />
                <TextField label="Call Route Message To Operators" name="CallRouteMessageToOperators" values={sendFields} onChange={setSendField} />
                <TextField label="End Call Message" name="EndCallMessage" values={sendFields} onChange={setSendField} />
                <TextField label="Number Of Operators" name="NumberOfOperators" values={sendFields} onChange={setSendField} />
              </div>
            </div>

            <div className="border-t pt-4">
              <h2 className="mb-3 text-sm font-medium text-muted-foreground">Voice &amp; delivery</h2>
              <div className="grid grid-cols-2 gap-4">
                <TextField label="Caller ID" name="CallerId" values={sendFields} onChange={setSendField} />
                <TextField label="Voice" name="Voice" values={sendFields} onChange={setSendField} />
                <TextField label="Options" name="Options" values={sendFields} onChange={setSendField} />
                <TextField label="Retry Attempts" name="RetryAttempts" values={sendFields} onChange={setSendField} />
                <TextField label="Retry Period" name="RetryPeriod" values={sendFields} onChange={setSendField} />
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