import { describe, it, expect, vi, afterEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import FaxPage from '@/pages/messaging/FaxPage'
import { apiRequest } from '@/lib/api-client'

vi.mock('@/lib/api-client', async () => {
  const actual = await vi.importActual<typeof import('@/lib/api-client')>('@/lib/api-client')
  return { ...actual, apiRequest: vi.fn() }
})

const mockedApiRequest = vi.mocked(apiRequest)

describe('FaxPage', () => {
  afterEach(() => {
    mockedApiRequest.mockReset()
  })

  it('submits To Number to /api/fax/send', async () => {
    mockedApiRequest.mockResolvedValue({ status: 200, data: { Result: 'Success', MessageID: 'abc-123' } })
    const user = userEvent.setup()
    render(<FaxPage />)

    await user.type(screen.getByLabelText('To Number'), '+6495006000')
    await user.click(screen.getByRole('button', { name: 'Send' }))

    expect(mockedApiRequest).toHaveBeenCalledWith(
      '/api/fax/send',
      expect.objectContaining({
        method: 'POST',
        body: expect.objectContaining({ ToNumber: '+6495006000' }),
      }),
    )
  })

  it('converts Retry Attempts/Period text fields to numbers, or undefined when blank', async () => {
    mockedApiRequest.mockResolvedValue({ status: 200, data: { Result: 'Success' } })
    const user = userEvent.setup()
    render(<FaxPage />)

    await user.type(screen.getByLabelText('To Number'), '+6495006000')
    await user.type(screen.getByLabelText('Retry Attempts'), '3')
    await user.click(screen.getByRole('button', { name: 'Send' }))

    const body = mockedApiRequest.mock.calls[0][1]?.body as { RetryAttempts?: number; RetryPeriod?: number }
    expect(body.RetryAttempts).toBe(3)
    expect(body.RetryPeriod).toBeUndefined()
  })

  it('renders the response and pre-fills Message ID in the Check Status card on success', async () => {
    mockedApiRequest.mockResolvedValue({ status: 200, data: { Result: 'Success', MessageID: 'abc-123' } })
    const user = userEvent.setup()
    render(<FaxPage />)

    await user.type(screen.getByLabelText('To Number'), '+6495006000')
    await user.click(screen.getByRole('button', { name: 'Send' }))

    expect(await screen.findByText('Success (HTTP 200)')).toBeInTheDocument()
    expect(screen.getByLabelText('Message ID')).toHaveValue('abc-123')
  })

  it('shows the trimmed failure response without pre-filling Message ID', async () => {
    mockedApiRequest.mockResolvedValue({
      status: 400,
      data: { Result: 'Unauthorized', ErrorMessage: ['Access denied'] },
    })
    const user = userEvent.setup()
    render(<FaxPage />)

    await user.type(screen.getByLabelText('To Number'), '+6495006000')
    await user.click(screen.getByRole('button', { name: 'Send' }))

    expect(await screen.findByText('Error (HTTP 400)')).toBeInTheDocument()
    expect(screen.getByLabelText('Message ID')).toHaveValue('')
  })

  it('checks status against /api/fax/status/{id}', async () => {
    mockedApiRequest.mockResolvedValue({ status: 200, data: { Result: 'Success' } })
    const user = userEvent.setup()
    render(<FaxPage />)

    await user.type(screen.getByLabelText('Message ID'), 'abc-123')
    await user.click(screen.getByRole('button', { name: 'Check status' }))

    expect(mockedApiRequest).toHaveBeenCalledWith('/api/fax/status/abc-123')
  })
})