import { describe, it, expect, vi, afterEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import StatusPage from '@/pages/reports/StatusPage'
import { apiRequest } from '@/lib/api-client'

vi.mock('@/lib/api-client', async () => {
  const actual = await vi.importActual<typeof import('@/lib/api-client')>('@/lib/api-client')
  return { ...actual, apiRequest: vi.fn() }
})

const mockedApiRequest = vi.mocked(apiRequest)

describe('StatusPage', () => {
  afterEach(() => {
    mockedApiRequest.mockReset()
  })

  it('defaults to the SMS channel and polls /api/sms/status/{id}', async () => {
    mockedApiRequest.mockResolvedValue({ status: 200, data: { Result: 'Success' } })
    const user = userEvent.setup()
    render(<StatusPage />)

    await user.type(screen.getByLabelText('Message ID'), 'abc-123')
    await user.click(screen.getByRole('button', { name: 'Poll Status' }))

    expect(mockedApiRequest).toHaveBeenCalledWith('/api/sms/status/abc-123')
  })

  it('lowercases the selected channel into the URL segment (e.g. WhatsApp -> whatsapp)', async () => {
    mockedApiRequest.mockResolvedValue({ status: 200, data: { Result: 'Success' } })
    const user = userEvent.setup()
    render(<StatusPage />)

    await user.type(screen.getByLabelText('Message ID'), 'abc-123')
    await user.click(screen.getByLabelText('Channel'))
    await user.click(await screen.findByRole('option', { name: 'WhatsApp' }))
    await user.click(screen.getByRole('button', { name: 'Poll Status' }))

    expect(mockedApiRequest).toHaveBeenCalledWith('/api/whatsapp/status/abc-123')
  })

  it('does not offer Workflow as a channel — it has no Status endpoint', async () => {
    const user = userEvent.setup()
    render(<StatusPage />)

    await user.click(screen.getByLabelText('Channel'))

    expect(screen.queryByRole('option', { name: 'Workflow' })).not.toBeInTheDocument()
  })

  it('renders the response', async () => {
    mockedApiRequest.mockResolvedValue({ status: 200, data: { Result: 'Success', JobStatus: 'Completed' } })
    const user = userEvent.setup()
    render(<StatusPage />)

    await user.type(screen.getByLabelText('Message ID'), 'abc-123')
    await user.click(screen.getByRole('button', { name: 'Poll Status' }))

    expect(await screen.findByText('Success (HTTP 200)')).toBeInTheDocument()
  })
})