import { describe, it, expect, vi, afterEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import PacingPage from '@/pages/actions/PacingPage'
import { apiRequest } from '@/lib/api-client'

vi.mock('@/lib/api-client', async () => {
  const actual = await vi.importActual<typeof import('@/lib/api-client')>('@/lib/api-client')
  return { ...actual, apiRequest: vi.fn() }
})

const mockedApiRequest = vi.mocked(apiRequest)

describe('PacingPage', () => {
  afterEach(() => {
    mockedApiRequest.mockReset()
  })

  it('submits Message ID, and PATCHes the pacing endpoint for the selected channel with Number Of Operators as a number', async () => {
    mockedApiRequest.mockResolvedValue({ status: 200, data: { ActionResult: 'OK' } })
    const user = userEvent.setup()
    render(<PacingPage />)

    await user.type(screen.getByLabelText('Message ID'), 'abc-123')
    await user.type(screen.getByLabelText('Number Of Operators'), '5')
    await user.click(screen.getByRole('button', { name: 'Update Pacing' }))

    expect(mockedApiRequest).toHaveBeenCalledWith(
      '/api/tts/abc-123/pacing',
      expect.objectContaining({ method: 'PATCH', body: { NumberOfOperators: 5 } }),
    )
  })

  it('defaults Number Of Operators to 0 when left blank', async () => {
    mockedApiRequest.mockResolvedValue({ status: 200, data: {} })
    const user = userEvent.setup()
    render(<PacingPage />)

    await user.type(screen.getByLabelText('Message ID'), 'abc-123')
    await user.click(screen.getByRole('button', { name: 'Update Pacing' }))

    const body = mockedApiRequest.mock.calls[0][1]?.body as { NumberOfOperators: number }
    expect(body.NumberOfOperators).toBe(0)
  })

  it('URL-encodes a Message ID containing reserved characters', async () => {
    mockedApiRequest.mockResolvedValue({ status: 200, data: { ActionResult: 'OK' } })
    const user = userEvent.setup()
    render(<PacingPage />)

    await user.type(screen.getByLabelText('Message ID'), 'abc/123?x=1')
    await user.type(screen.getByLabelText('Number Of Operators'), '5')
    await user.click(screen.getByRole('button', { name: 'Update Pacing' }))

    expect(mockedApiRequest).toHaveBeenCalledWith(
      '/api/tts/abc%2F123%3Fx%3D1/pacing',
      expect.objectContaining({ method: 'PATCH', body: { NumberOfOperators: 5 } }),
    )
  })

  it('rejects an empty Message ID without calling apiRequest', async () => {
    const user = userEvent.setup()
    render(<PacingPage />)

    await user.type(screen.getByLabelText('Number Of Operators'), '5')
    await user.click(screen.getByRole('button', { name: 'Update Pacing' }))

    expect(mockedApiRequest).not.toHaveBeenCalled()
    expect(await screen.findByText('Error (HTTP 400)')).toBeInTheDocument()
  })

  it('rejects a whitespace-only Message ID without calling apiRequest', async () => {
    const user = userEvent.setup()
    render(<PacingPage />)

    await user.type(screen.getByLabelText('Message ID'), '   ')
    await user.type(screen.getByLabelText('Number Of Operators'), '5')
    await user.click(screen.getByRole('button', { name: 'Update Pacing' }))

    expect(mockedApiRequest).not.toHaveBeenCalled()
    expect(await screen.findByText('Error (HTTP 400)')).toBeInTheDocument()
  })

  it('only offers TTS and Voice', async () => {
    const user = userEvent.setup()
    render(<PacingPage />)

    await user.click(screen.getByLabelText('Channel'))

    expect(await screen.findByRole('option', { name: 'TTS' })).toBeInTheDocument()
    expect(screen.getByRole('option', { name: 'Voice' })).toBeInTheDocument()
    expect(screen.queryByRole('option', { name: 'SMS' })).not.toBeInTheDocument()
  })

  it('renders the response', async () => {
    mockedApiRequest.mockResolvedValue({ status: 200, data: { ActionResult: 'OK' } })
    const user = userEvent.setup()
    render(<PacingPage />)

    await user.type(screen.getByLabelText('Message ID'), 'abc-123')
    await user.type(screen.getByLabelText('Number Of Operators'), '5')
    await user.click(screen.getByRole('button', { name: 'Update Pacing' }))

    expect(await screen.findByText('Success (HTTP 200)')).toBeInTheDocument()
  })
})