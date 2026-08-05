import { describe, it, expect, vi, afterEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import ReceivedPage from '@/pages/reports/ReceivedPage'
import { apiRequest } from '@/lib/api-client'

vi.mock('@/lib/api-client', async () => {
  const actual = await vi.importActual<typeof import('@/lib/api-client')>('@/lib/api-client')
  return { ...actual, apiRequest: vi.fn() }
})

const mockedApiRequest = vi.mocked(apiRequest)

describe('ReceivedPage', () => {
  afterEach(() => {
    mockedApiRequest.mockReset()
  })

  it('defaults Channel to SMS and Time Period to 1440, polling /api/sms/received', async () => {
    mockedApiRequest.mockResolvedValue({ status: 200, data: { TotalRecords: 0 } })
    const user = userEvent.setup()
    render(<ReceivedPage />)

    await user.click(screen.getByRole('button', { name: 'Get Received Messages' }))

    expect(mockedApiRequest).toHaveBeenCalledWith('/api/sms/received?timePeriod=1440')
  })

  it('polls /api/whatsapp/received when Channel is switched to WhatsApp', async () => {
    mockedApiRequest.mockResolvedValue({ status: 200, data: { TotalRecords: 0 } })
    const user = userEvent.setup()
    render(<ReceivedPage />)

    await user.click(screen.getByLabelText('Channel'))
    await user.click(await screen.findByRole('option', { name: 'WhatsApp' }))
    await user.click(screen.getByRole('button', { name: 'Get Received Messages' }))

    expect(mockedApiRequest).toHaveBeenCalledWith('/api/whatsapp/received?timePeriod=1440')
  })

  it('polls /api/rcs/received when Channel is switched to RCS', async () => {
    mockedApiRequest.mockResolvedValue({ status: 200, data: { TotalRecords: 0 } })
    const user = userEvent.setup()
    render(<ReceivedPage />)

    await user.click(screen.getByLabelText('Channel'))
    await user.click(await screen.findByRole('option', { name: 'RCS' }))
    await user.click(screen.getByRole('button', { name: 'Get Received Messages' }))

    expect(mockedApiRequest).toHaveBeenCalledWith('/api/rcs/received?timePeriod=1440')
  })

  it('uses Date From / Date To instead of Time Period when both are supplied', async () => {
    mockedApiRequest.mockResolvedValue({ status: 200, data: { TotalRecords: 0 } })
    const user = userEvent.setup()
    render(<ReceivedPage />)

    await user.clear(screen.getByLabelText('Time Period (minutes, 1-1440)'))
    await user.type(screen.getByLabelText('Date From'), '2026-01-01 00:00:00')
    await user.type(screen.getByLabelText('Date To'), '2026-01-31 23:59:59')
    await user.click(screen.getByRole('button', { name: 'Get Received Messages' }))

    const url = mockedApiRequest.mock.calls[0][0]
    expect(url).toContain('dateFrom=2026-01-01')
    expect(url).toContain('dateTo=2026-01-31')
  })

  it('renders the response', async () => {
    mockedApiRequest.mockResolvedValue({ status: 200, data: { TotalRecords: 3 } })
    const user = userEvent.setup()
    render(<ReceivedPage />)

    await user.click(screen.getByRole('button', { name: 'Get Received Messages' }))

    expect(await screen.findByText('Success (HTTP 200)')).toBeInTheDocument()
  })
})
