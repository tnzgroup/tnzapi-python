import { useState, type FormEvent } from 'react'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { TextField, SelectField, type FieldValues } from '@/components/form-fields'
import { ResponseViewer } from '@/components/response-viewer'
import { apiRequest } from '@/lib/api-client'
import type { SendWorkflowRequest, MessageApiResult } from '@/lib/api-client'

export default function WorkflowPage() {
  const [sendFields, setSendFields] = useState<FieldValues>({})
  const [sendStatus, setSendStatus] = useState<number | null>(null)
  const [sendData, setSendData] = useState<unknown>(null)
  const [sending, setSending] = useState(false)

  function setSendField(name: string, value: string) {
    setSendFields((f) => ({ ...f, [name]: value }))
  }

  async function handleSend(e: FormEvent) {
    e.preventDefault()
    setSending(true)
    const body: SendWorkflowRequest = {
      WorkflowTemplateId: (sendFields.WorkflowTemplateId as string) ?? '',
      ToNumber: sendFields.ToNumber as string,
      MainPhone: sendFields.MainPhone as string,
      EmailAddress: sendFields.EmailAddress as string,
      ContactIds: sendFields.ContactIds as string,
      GroupIds: sendFields.GroupIds as string,
      Reference: sendFields.Reference as string,
      NotificationType: sendFields.NotificationType as string,
      WebhookCallbackUrl: sendFields.WebhookCallbackUrl as string,
      WebhookCallbackFormat: sendFields.WebhookCallbackFormat as string,
      SubAccount: sendFields.SubAccount as string,
      Department: sendFields.Department as string,
      ChargeCode: sendFields.ChargeCode as string,
      SendTime: sendFields.SendTime as string,
      Timezone: sendFields.Timezone as string,
      SendMode: sendFields.SendMode as string,
    }
    const { status, data } = await apiRequest<MessageApiResult>('/api/workflow/send', { method: 'POST', body })
    setSendStatus(status)
    setSendData(data)
    setSending(false)
  }

  return (
    <div className="max-w-2xl space-y-6">
      <div>
        <h1 className="text-xl font-semibold">Send Workflow</h1>
        <p className="text-sm text-muted-foreground">client.Messaging.Workflow.SendMessageAsync</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Trigger Workflow</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSend} className="space-y-4">
            <p className="rounded-md border border-input bg-muted/50 px-3 py-2 text-sm text-muted-foreground">
              Workflow triggers a pre-configured, no-code Workflow Template built in the TNZ
              Dashboard — it has no message text or attachments of its own, and no status/received
              endpoints. At least one recipient (To Number/Main Phone/Email Address, or a Contact ID
              / Group ID) is required.
            </p>
            <TextField
              label="Workflow Template ID"
              name="WorkflowTemplateId"
              values={sendFields}
              onChange={setSendField}
              placeholder="UUID"
            />

            <div className="border-t pt-4">
              <h2 className="mb-3 text-sm font-medium text-muted-foreground">Recipient</h2>
              <p className="mb-3 text-xs text-muted-foreground">
                To Number / Main Phone / Email Address combine onto a single recipient — the
                Workflow Template decides which channel(s) actually get used.
              </p>
              <div className="grid grid-cols-2 gap-4">
                <TextField label="To Number" name="ToNumber" values={sendFields} onChange={setSendField} placeholder="+6421000001" />
                <TextField label="Main Phone" name="MainPhone" values={sendFields} onChange={setSendField} placeholder="+6421000002" />
                <TextField label="Email Address" name="EmailAddress" values={sendFields} onChange={setSendField} placeholder="test@example.com" />
              </div>
              <div className="mt-3 grid grid-cols-2 gap-4">
                <TextField
                  label="Contact IDs"
                  name="ContactIds"
                  values={sendFields}
                  onChange={setSendField}
                  placeholder="comma-separated addressbook Contact IDs"
                />
                <TextField
                  label="Group IDs"
                  name="GroupIds"
                  values={sendFields}
                  onChange={setSendField}
                  placeholder="comma-separated addressbook Group IDs"
                />
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
    </div>
  )
}