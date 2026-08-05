import { describe, it, expect, vi, afterEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import ResubmitPage from '@/pages/actions/ResubmitPage'
import { apiRequest } from '@/lib/api-client'

vi.mock('@/lib/api-client', async () => {
  const actual = await vi.importActual<typeof import('@/lib/api-client')>('@/lib/api-client')
  return { ...actual, apiRequest: vi.fn() }
})

const mockedApiRequest = vi.mocked(apiRequest)

describe('ResubmitPage', () => {
  afterEach(() => {
    mockedApiRequest.mockReset()
  })

  it('submits Message ID and New Send Time, and PATCHes the resubmit endpoint for the selected channel', async () => {
    mockedApiRequest.mockResolvedValue({ status: 200, data: { ActionResult: 'OK' } })
    const user = userEvent.setup()
    render(<ResubmitPage />)

    await user.type(screen.getByLabelText('Message ID'), 'abc-123')
    await user.type(screen.getByLabelText('New Send Time'), '2026-08-01 09:00:00')
    await user.click(screen.getByRole('button', { name: 'Resubmit' }))

    expect(mockedApiRequest).toHaveBeenCalledWith(
      '/api/email/abc-123/resubmit',
      expect.objectContaining({ method: 'PATCH', body: { SendTime: '2026-08-01 09:00:00' } }),
    )
  })

  it('URL-encodes a Message ID containing reserved characters', async () => {
    mockedApiRequest.mockResolvedValue({ status: 200, data: { ActionResult: 'OK' } })
    const user = userEvent.setup()
    render(<ResubmitPage />)

    await user.type(screen.getByLabelText('Message ID'), 'abc/123?x=1')
    await user.type(screen.getByLabelText('New Send Time'), '2026-08-01 09:00:00')
    await user.click(screen.getByRole('button', { name: 'Resubmit' }))

    expect(mockedApiRequest).toHaveBeenCalledWith(
      '/api/email/abc%2F123%3Fx%3D1/resubmit',
      expect.objectContaining({ method: 'PATCH', body: { SendTime: '2026-08-01 09:00:00' } }),
    )
  })

  it('rejects an empty Message ID without calling apiRequest', async () => {
    const user = userEvent.setup()
    render(<ResubmitPage />)

    await user.type(screen.getByLabelText('New Send Time'), '2026-08-01 09:00:00')
    await user.click(screen.getByRole('button', { name: 'Resubmit' }))

    expect(mockedApiRequest).not.toHaveBeenCalled()
    expect(await screen.findByText('Error (HTTP 400)')).toBeInTheDocument()
  })

  it('rejects a whitespace-only Message ID without calling apiRequest', async () => {
    const user = userEvent.setup()
    render(<ResubmitPage />)

    await user.type(screen.getByLabelText('Message ID'), '   ')
    await user.type(screen.getByLabelText('New Send Time'), '2026-08-01 09:00:00')
    await user.click(screen.getByRole('button', { name: 'Resubmit' }))

    expect(mockedApiRequest).not.toHaveBeenCalled()
    expect(await screen.findByText('Error (HTTP 400)')).toBeInTheDocument()
  })

  it('only offers Email/Fax/TTS/Voice — not SMS/WhatsApp/RCS', async () => {
    const user = userEvent.setup()
    render(<ResubmitPage />)

    await user.click(screen.getByLabelText('Channel'))

    for (const channel of ['Email', 'Fax', 'TTS', 'Voice']) {
      expect(await screen.findByRole('option', { name: channel })).toBeInTheDocument()
    }
    expect(screen.queryByRole('option', { name: 'SMS' })).not.toBeInTheDocument()
    expect(screen.queryByRole('option', { name: 'WhatsApp' })).not.toBeInTheDocument()
    expect(screen.queryByRole('option', { name: 'RCS' })).not.toBeInTheDocument()
  })

  it('renders the response', async () => {
    mockedApiRequest.mockResolvedValue({ status: 200, data: { ActionResult: 'OK' } })
    const user = userEvent.setup()
    render(<ResubmitPage />)

    await user.type(screen.getByLabelText('Message ID'), 'abc-123')
    await user.type(screen.getByLabelText('New Send Time'), '2026-08-01 09:00:00')
    await user.click(screen.getByRole('button', { name: 'Resubmit' }))

    expect(await screen.findByText('Success (HTTP 200)')).toBeInTheDocument()
  })
})