import { describe, it, expect, vi, afterEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import EmailPage from '@/pages/messaging/EmailPage'
import { apiRequest } from '@/lib/api-client'

vi.mock('@/lib/api-client', async () => {
  const actual = await vi.importActual<typeof import('@/lib/api-client')>('@/lib/api-client')
  return { ...actual, apiRequest: vi.fn() }
})

const mockedApiRequest = vi.mocked(apiRequest)

describe('EmailPage', () => {
  afterEach(() => {
    mockedApiRequest.mockReset()
  })

  it('submits Email Address, Subject, and the default HTML message body to /api/email/send', async () => {
    mockedApiRequest.mockResolvedValue({ status: 200, data: { Result: 'Success', MessageID: 'abc-123' } })
    const user = userEvent.setup()
    render(<EmailPage />)

    await user.type(screen.getByLabelText('Email Address'), 'test@example.com')
    await user.click(screen.getByRole('button', { name: 'Send' }))

    expect(mockedApiRequest).toHaveBeenCalledWith(
      '/api/email/send',
      expect.objectContaining({
        method: 'POST',
        body: expect.objectContaining({
          EmailAddress: 'test@example.com',
          Subject: 'Hello from TNZAPI Demo!',
          MessageHtml: '<p>Hello from TNZAPI Demo!</p>',
        }),
      }),
    )
  })

  it('renders the response and pre-fills Message ID in the Check Status card on success', async () => {
    mockedApiRequest.mockResolvedValue({ status: 200, data: { Result: 'Success', MessageID: 'abc-123' } })
    const user = userEvent.setup()
    render(<EmailPage />)

    await user.type(screen.getByLabelText('Email Address'), 'test@example.com')
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
    render(<EmailPage />)

    await user.type(screen.getByLabelText('Email Address'), 'test@example.com')
    await user.click(screen.getByRole('button', { name: 'Send' }))

    expect(await screen.findByText('Error (HTTP 400)')).toBeInTheDocument()
    expect(screen.getByLabelText('Message ID')).toHaveValue('')
  })

  it('checks status against /api/email/status/{id}', async () => {
    mockedApiRequest.mockResolvedValue({ status: 200, data: { Result: 'Success', JobStatus: 'Completed' } })
    const user = userEvent.setup()
    render(<EmailPage />)

    await user.type(screen.getByLabelText('Message ID'), 'abc-123')
    await user.click(screen.getByRole('button', { name: 'Check status' }))

    expect(mockedApiRequest).toHaveBeenCalledWith('/api/email/status/abc-123')
  })
})