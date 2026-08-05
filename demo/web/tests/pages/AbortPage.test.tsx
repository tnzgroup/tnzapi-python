import { describe, it, expect, vi, afterEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import AbortPage from '@/pages/actions/AbortPage'
import { apiRequest } from '@/lib/api-client'

vi.mock('@/lib/api-client', async () => {
  const actual = await vi.importActual<typeof import('@/lib/api-client')>('@/lib/api-client')
  return { ...actual, apiRequest: vi.fn() }
})

const mockedApiRequest = vi.mocked(apiRequest)

describe('AbortPage', () => {
  afterEach(() => {
    mockedApiRequest.mockReset()
  })

  it('submits Message ID and PATCHes the abort endpoint for the selected channel', async () => {
    mockedApiRequest.mockResolvedValue({ status: 200, data: { ActionResult: 'OK' } })
    const user = userEvent.setup()
    render(<AbortPage />)

    await user.type(screen.getByLabelText('Message ID'), 'abc-123')
    await user.click(screen.getByRole('button', { name: 'Abort' }))

    expect(mockedApiRequest).toHaveBeenCalledWith('/api/sms/abc-123/abort', expect.objectContaining({ method: 'PATCH' }))
  })

  it('URL-encodes a Message ID containing reserved characters', async () => {
    mockedApiRequest.mockResolvedValue({ status: 200, data: { ActionResult: 'OK' } })
    const user = userEvent.setup()
    render(<AbortPage />)

    await user.type(screen.getByLabelText('Message ID'), 'abc/123?x=1')
    await user.click(screen.getByRole('button', { name: 'Abort' }))

    expect(mockedApiRequest).toHaveBeenCalledWith('/api/sms/abc%2F123%3Fx%3D1/abort', expect.objectContaining({ method: 'PATCH' }))
  })

  it('rejects an empty Message ID without calling apiRequest', async () => {
    const user = userEvent.setup()
    render(<AbortPage />)

    await user.click(screen.getByRole('button', { name: 'Abort' }))

    expect(mockedApiRequest).not.toHaveBeenCalled()
    expect(await screen.findByText('Error (HTTP 400)')).toBeInTheDocument()
  })

  it('rejects a whitespace-only Message ID without calling apiRequest', async () => {
    const user = userEvent.setup()
    render(<AbortPage />)

    await user.type(screen.getByLabelText('Message ID'), '   ')
    await user.click(screen.getByRole('button', { name: 'Abort' }))

    expect(mockedApiRequest).not.toHaveBeenCalled()
    expect(await screen.findByText('Error (HTTP 400)')).toBeInTheDocument()
  })

  it('offers all 7 channels with an Actions facade, including WhatsApp and RCS', async () => {
    const user = userEvent.setup()
    render(<AbortPage />)

    await user.click(screen.getByLabelText('Channel'))

    for (const channel of ['SMS', 'Email', 'Fax', 'TTS', 'Voice', 'WhatsApp', 'RCS']) {
      expect(await screen.findByRole('option', { name: channel })).toBeInTheDocument()
    }
  })

  it('renders the response', async () => {
    mockedApiRequest.mockResolvedValue({ status: 200, data: { ActionResult: 'OK' } })
    const user = userEvent.setup()
    render(<AbortPage />)

    await user.type(screen.getByLabelText('Message ID'), 'abc-123')
    await user.click(screen.getByRole('button', { name: 'Abort' }))

    expect(await screen.findByText('Success (HTTP 200)')).toBeInTheDocument()
  })
})