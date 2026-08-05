import { describe, it, expect, vi, afterEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import SmsReplyPage from '@/pages/reports/SmsReplyPage'
import { apiRequest } from '@/lib/api-client'

vi.mock('@/lib/api-client', async () => {
  const actual = await vi.importActual<typeof import('@/lib/api-client')>('@/lib/api-client')
  return { ...actual, apiRequest: vi.fn() }
})

const mockedApiRequest = vi.mocked(apiRequest)

describe('SmsReplyPage', () => {
  afterEach(() => {
    mockedApiRequest.mockReset()
  })

  it('polls /api/sms/reply/{id} with no query string when paging fields are blank', async () => {
    mockedApiRequest.mockResolvedValue({ status: 200, data: { Result: 'Success' } })
    const user = userEvent.setup()
    render(<SmsReplyPage />)

    await user.type(screen.getByLabelText('Message ID'), 'abc-123')
    await user.click(screen.getByRole('button', { name: 'Get Replies' }))

    expect(mockedApiRequest).toHaveBeenCalledWith('/api/sms/reply/abc-123')
  })

  it('adds recordsPerPage/page query params when supplied', async () => {
    mockedApiRequest.mockResolvedValue({ status: 200, data: { Result: 'Success' } })
    const user = userEvent.setup()
    render(<SmsReplyPage />)

    await user.type(screen.getByLabelText('Message ID'), 'abc-123')
    await user.type(screen.getByLabelText('Records Per Page'), '25')
    await user.type(screen.getByLabelText('Page'), '2')
    await user.click(screen.getByRole('button', { name: 'Get Replies' }))

    expect(mockedApiRequest).toHaveBeenCalledWith('/api/sms/reply/abc-123?recordsPerPage=25&page=2')
  })

  it('renders the response', async () => {
    mockedApiRequest.mockResolvedValue({ status: 200, data: { Result: 'Success' } })
    const user = userEvent.setup()
    render(<SmsReplyPage />)

    await user.type(screen.getByLabelText('Message ID'), 'abc-123')
    await user.click(screen.getByRole('button', { name: 'Get Replies' }))

    expect(await screen.findByText('Success (HTTP 200)')).toBeInTheDocument()
  })
})