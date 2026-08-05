import { describe, it, expect, vi, afterEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import WhatsAppPage from '@/pages/messaging/WhatsAppPage'
import { apiRequest } from '@/lib/api-client'

vi.mock('@/lib/api-client', async () => {
  const actual = await vi.importActual<typeof import('@/lib/api-client')>('@/lib/api-client')
  return { ...actual, apiRequest: vi.fn() }
})

const mockedApiRequest = vi.mocked(apiRequest)

describe('WhatsAppPage', () => {
  afterEach(() => {
    mockedApiRequest.mockReset()
  })

  it('submits To Number, Template ID, and the default Message to /api/whatsapp/send', async () => {
    mockedApiRequest.mockResolvedValue({ status: 200, data: { Result: 'Success', MessageID: 'abc-123' } })
    const user = userEvent.setup()
    render(<WhatsAppPage />)

    await user.type(screen.getByLabelText('To Number'), '+64211234567')
    await user.type(screen.getByLabelText('Template ID'), 'tmpl-1')
    await user.click(screen.getByRole('button', { name: 'Send' }))

    expect(mockedApiRequest).toHaveBeenCalledWith(
      '/api/whatsapp/send',
      expect.objectContaining({
        method: 'POST',
        body: expect.objectContaining({
          ToNumber: '+64211234567',
          TemplateId: 'tmpl-1',
          Message: 'Hello from TNZAPI Demo!',
        }),
      }),
    )
  })

  it('the Message and Attachments fields are disabled — content must match the approved template', () => {
    render(<WhatsAppPage />)

    expect(screen.getByLabelText('Message')).toBeDisabled()
    expect(screen.getByLabelText('Attachments')).toBeDisabled()
  })

  it('renders the response and pre-fills Message ID in the Check Status card on success', async () => {
    mockedApiRequest.mockResolvedValue({ status: 200, data: { Result: 'Success', MessageID: 'abc-123' } })
    const user = userEvent.setup()
    render(<WhatsAppPage />)

    await user.type(screen.getByLabelText('To Number'), '+64211234567')
    await user.click(screen.getByRole('button', { name: 'Send' }))

    expect(await screen.findByText('Success (HTTP 200)')).toBeInTheDocument()
    expect(screen.getByLabelText('Message ID')).toHaveValue('abc-123')
  })

  it('checks status against /api/whatsapp/status/{id}', async () => {
    mockedApiRequest.mockResolvedValue({ status: 200, data: { Result: 'Success' } })
    const user = userEvent.setup()
    render(<WhatsAppPage />)

    await user.type(screen.getByLabelText('Message ID'), 'abc-123')
    await user.click(screen.getByRole('button', { name: 'Check status' }))

    expect(mockedApiRequest).toHaveBeenCalledWith('/api/whatsapp/status/abc-123')
  })
})