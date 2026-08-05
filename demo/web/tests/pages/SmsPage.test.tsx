import { describe, it, expect, vi, afterEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import SmsPage from '@/pages/messaging/SmsPage'
import { apiRequest } from '@/lib/api-client'

vi.mock('@/lib/api-client', async () => {
  const actual = await vi.importActual<typeof import('@/lib/api-client')>('@/lib/api-client')
  return { ...actual, apiRequest: vi.fn() }
})

const mockedApiRequest = vi.mocked(apiRequest)

describe('SmsPage', () => {
  afterEach(() => {
    mockedApiRequest.mockReset()
  })

  it('submits the To Number and default Message to /api/sms/send', async () => {
    mockedApiRequest.mockResolvedValue({ status: 200, data: { Result: 'Success', MessageID: 'abc-123' } })
    const user = userEvent.setup()
    render(<SmsPage />)

    await user.type(screen.getByLabelText('To Number'), '+64211234567')
    await user.click(screen.getByRole('button', { name: 'Send' }))

    expect(mockedApiRequest).toHaveBeenCalledWith(
      '/api/sms/send',
      expect.objectContaining({
        method: 'POST',
        body: expect.objectContaining({
          ToNumber: '+64211234567',
          Message: 'Hello from TNZAPI Demo!',
        }),
      }),
    )
  })

  it('renders the response and pre-fills Message ID in the Check Status card on success', async () => {
    mockedApiRequest.mockResolvedValue({ status: 200, data: { Result: 'Success', MessageID: 'abc-123' } })
    const user = userEvent.setup()
    render(<SmsPage />)

    await user.type(screen.getByLabelText('To Number'), '+64211234567')
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
    render(<SmsPage />)

    await user.type(screen.getByLabelText('To Number'), '+64211234567')
    await user.click(screen.getByRole('button', { name: 'Send' }))

    expect(await screen.findByText('Error (HTTP 400)')).toBeInTheDocument()
    expect(screen.getByLabelText('Message ID')).toHaveValue('')
  })

  it('checks status against /api/sms/status/{id} with the entered Message ID', async () => {
    mockedApiRequest.mockResolvedValue({ status: 200, data: { Result: 'Success', JobStatus: 'Completed' } })
    const user = userEvent.setup()
    render(<SmsPage />)

    await user.type(screen.getByLabelText('Message ID'), 'abc-123')
    await user.click(screen.getByRole('button', { name: 'Check status' }))

    expect(mockedApiRequest).toHaveBeenCalledWith('/api/sms/status/abc-123')
  })
})