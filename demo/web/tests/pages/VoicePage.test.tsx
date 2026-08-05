import { describe, it, expect, vi, afterEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import VoicePage from '@/pages/messaging/VoicePage'
import { apiRequest } from '@/lib/api-client'

vi.mock('@/lib/api-client', async () => {
  const actual = await vi.importActual<typeof import('@/lib/api-client')>('@/lib/api-client')
  return { ...actual, apiRequest: vi.fn() }
})

const mockedApiRequest = vi.mocked(apiRequest)

describe('VoicePage', () => {
  afterEach(() => {
    mockedApiRequest.mockReset()
  })

  it('submits To Number with an empty MessageToPeople when no audio file is chosen', async () => {
    mockedApiRequest.mockResolvedValue({ status: 200, data: { Result: 'Success', MessageID: 'abc-123' } })
    const user = userEvent.setup()
    render(<VoicePage />)

    await user.type(screen.getByLabelText('To Number'), '+6421000001')
    await user.click(screen.getByRole('button', { name: 'Send' }))

    expect(mockedApiRequest).toHaveBeenCalledWith(
      '/api/voice/send',
      expect.objectContaining({
        method: 'POST',
        body: expect.objectContaining({ ToNumber: '+6421000001', MessageToPeople: '' }),
      }),
    )
  })

  it('reads an uploaded audio file as base64 and sends it as MessageToPeople', async () => {
    mockedApiRequest.mockResolvedValue({ status: 200, data: { Result: 'Success' } })
    const user = userEvent.setup()
    render(<VoicePage />)

    await user.type(screen.getByLabelText('To Number'), '+6421000001')
    const file = new File(['hello'], 'greeting.wav', { type: 'audio/wav' })
    await user.upload(screen.getByLabelText('Message To People'), file)

    // FileReader.readAsDataURL resolves asynchronously — wait for the picker to show the chosen
    // filename before submitting, otherwise the send could race ahead of the base64 read finishing.
    expect(await screen.findByText('greeting.wav')).toBeInTheDocument()

    await user.click(screen.getByRole('button', { name: 'Send' }))

    const body = mockedApiRequest.mock.calls[0][1]?.body as { MessageToPeople: string }
    expect(body.MessageToPeople.length).toBeGreaterThan(0)
  })

  it('shows Play File / File fields in the Keypad Editor (Voice, unlike TTS, uses them)', async () => {
    const user = userEvent.setup()
    render(<VoicePage />)

    await user.click(screen.getByRole('button', { name: 'Add Keypad' }))

    expect(screen.getByLabelText('Play File')).toBeInTheDocument()
    expect(screen.getByLabelText('File', { exact: true })).toBeInTheDocument()
  })

  it('checks status against /api/voice/status/{id}', async () => {
    mockedApiRequest.mockResolvedValue({ status: 200, data: { Result: 'Success' } })
    const user = userEvent.setup()
    render(<VoicePage />)

    await user.type(screen.getByLabelText('Message ID'), 'abc-123')
    await user.click(screen.getByRole('button', { name: 'Check status' }))

    expect(mockedApiRequest).toHaveBeenCalledWith('/api/voice/status/abc-123')
  })
})