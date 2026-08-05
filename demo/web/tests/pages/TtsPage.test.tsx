import { describe, it, expect, vi, afterEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import TtsPage from '@/pages/messaging/TtsPage'
import { apiRequest } from '@/lib/api-client'

vi.mock('@/lib/api-client', async () => {
  const actual = await vi.importActual<typeof import('@/lib/api-client')>('@/lib/api-client')
  return { ...actual, apiRequest: vi.fn() }
})

const mockedApiRequest = vi.mocked(apiRequest)

describe('TtsPage', () => {
  afterEach(() => {
    mockedApiRequest.mockReset()
  })

  it('submits To Number and default Message To People to /api/tts/send', async () => {
    mockedApiRequest.mockResolvedValue({ status: 200, data: { Result: 'Success', MessageID: 'abc-123' } })
    const user = userEvent.setup()
    render(<TtsPage />)

    await user.type(screen.getByLabelText('To Number'), '+6421000001')
    await user.click(screen.getByRole('button', { name: 'Send' }))

    expect(mockedApiRequest).toHaveBeenCalledWith(
      '/api/tts/send',
      expect.objectContaining({
        method: 'POST',
        body: expect.objectContaining({
          ToNumber: '+6421000001',
          MessageToPeople: 'Hello from TNZAPI Demo!',
        }),
      }),
    )
  })

  it('includes keypads added via the Keypad Editor in the request body', async () => {
    mockedApiRequest.mockResolvedValue({ status: 200, data: { Result: 'Success' } })
    const user = userEvent.setup()
    render(<TtsPage />)

    await user.type(screen.getByLabelText('To Number'), '+6421000001')
    await user.click(screen.getByRole('button', { name: 'Add Keypad' }))
    await user.type(screen.getByLabelText('Play'), 'sales.wav')
    await user.click(screen.getByRole('button', { name: 'Send' }))

    const body = mockedApiRequest.mock.calls[0][1]?.body as { Keypads?: Array<{ Play: string }> }
    expect(body.Keypads).toHaveLength(1)
    expect(body.Keypads?.[0].Play).toBe('sales.wav')
  })

  it('renders the response and pre-fills Message ID in the Check Status card on success', async () => {
    mockedApiRequest.mockResolvedValue({ status: 200, data: { Result: 'Success', MessageID: 'abc-123' } })
    const user = userEvent.setup()
    render(<TtsPage />)

    await user.type(screen.getByLabelText('To Number'), '+6421000001')
    await user.click(screen.getByRole('button', { name: 'Send' }))

    expect(await screen.findByText('Success (HTTP 200)')).toBeInTheDocument()
    expect(screen.getByLabelText('Message ID')).toHaveValue('abc-123')
  })

  it('checks status against /api/tts/status/{id}', async () => {
    mockedApiRequest.mockResolvedValue({ status: 200, data: { Result: 'Success' } })
    const user = userEvent.setup()
    render(<TtsPage />)

    await user.type(screen.getByLabelText('Message ID'), 'abc-123')
    await user.click(screen.getByRole('button', { name: 'Check status' }))

    expect(mockedApiRequest).toHaveBeenCalledWith('/api/tts/status/abc-123')
  })
})