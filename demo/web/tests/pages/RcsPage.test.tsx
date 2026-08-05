import { describe, it, expect, vi, afterEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import RcsPage from '@/pages/messaging/RcsPage'
import { apiRequest } from '@/lib/api-client'

vi.mock('@/lib/api-client', async () => {
  const actual = await vi.importActual<typeof import('@/lib/api-client')>('@/lib/api-client')
  return { ...actual, apiRequest: vi.fn() }
})

const mockedApiRequest = vi.mocked(apiRequest)

describe('RcsPage', () => {
  afterEach(() => {
    mockedApiRequest.mockReset()
  })

  it('submits To Number and default Message to /api/rcs/send', async () => {
    mockedApiRequest.mockResolvedValue({ status: 200, data: { Result: 'Success', MessageID: 'abc-123' } })
    const user = userEvent.setup()
    render(<RcsPage />)

    await user.type(screen.getByLabelText('To Number'), '+64211234567')
    await user.click(screen.getByRole('button', { name: 'Send' }))

    expect(mockedApiRequest).toHaveBeenCalledWith(
      '/api/rcs/send',
      expect.objectContaining({
        method: 'POST',
        body: expect.objectContaining({ ToNumber: '+64211234567', Message: 'Hello from TNZAPI Demo!' }),
      }),
    )
  })

  it('collects checked Fallback Mode checkboxes into the request body', async () => {
    mockedApiRequest.mockResolvedValue({ status: 200, data: { Result: 'Success' } })
    const user = userEvent.setup()
    render(<RcsPage />)

    await user.type(screen.getByLabelText('To Number'), '+64211234567')
    await user.click(screen.getByRole('checkbox', { name: 'SMS' }))
    await user.click(screen.getByRole('checkbox', { name: 'WhatsApp' }))
    await user.click(screen.getByRole('button', { name: 'Send' }))

    const body = mockedApiRequest.mock.calls[0][1]?.body as { FallbackMode?: string[] }
    expect(body.FallbackMode).toEqual(['SMS', 'WhatsApp'])
  })

  it('renders the response and pre-fills Message ID in the Check Status card on success', async () => {
    mockedApiRequest.mockResolvedValue({ status: 200, data: { Result: 'Success', MessageID: 'abc-123' } })
    const user = userEvent.setup()
    render(<RcsPage />)

    await user.type(screen.getByLabelText('To Number'), '+64211234567')
    await user.click(screen.getByRole('button', { name: 'Send' }))

    expect(await screen.findByText('Success (HTTP 200)')).toBeInTheDocument()
    expect(screen.getByLabelText('Message ID')).toHaveValue('abc-123')
  })

  it('checks status against /api/rcs/status/{id}', async () => {
    mockedApiRequest.mockResolvedValue({ status: 200, data: { Result: 'Success' } })
    const user = userEvent.setup()
    render(<RcsPage />)

    await user.type(screen.getByLabelText('Message ID'), 'abc-123')
    await user.click(screen.getByRole('button', { name: 'Check status' }))

    expect(mockedApiRequest).toHaveBeenCalledWith('/api/rcs/status/abc-123')
  })
})