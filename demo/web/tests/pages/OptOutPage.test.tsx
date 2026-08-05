import { describe, it, expect, vi, afterEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import OptOutPage from '@/pages/OptOutPage'
import { apiRequest } from '@/lib/api-client'

vi.mock('@/lib/api-client', async () => {
  const actual = await vi.importActual<typeof import('@/lib/api-client')>('@/lib/api-client')
  return { ...actual, apiRequest: vi.fn() }
})

const mockedApiRequest = vi.mocked(apiRequest)

describe('OptOutPage', () => {
  afterEach(() => {
    mockedApiRequest.mockReset()
  })

  it('loads the opt-out list on mount', async () => {
    mockedApiRequest.mockResolvedValue({
      status: 200,
      data: { OptOuts: [{ ID: 'o-1', Destination: '+64211234567', DestType: 'sms' }] },
    })
    render(<OptOutPage />)

    expect(await screen.findByText('+64211234567')).toBeInTheDocument()
    expect(mockedApiRequest).toHaveBeenCalledWith('/api/optout?recordsPerPage=50&page=1')
  })

  it('creates an opt-out and reloads the list on success', async () => {
    mockedApiRequest.mockResolvedValueOnce({ status: 200, data: { OptOuts: [] } })
    mockedApiRequest.mockResolvedValueOnce({ status: 200, data: { ID: 'o-1' } })
    mockedApiRequest.mockResolvedValueOnce({ status: 200, data: { OptOuts: [{ ID: 'o-1', Destination: '+64211234567' }] } })
    const user = userEvent.setup()
    render(<OptOutPage />)
    await screen.findByRole('heading', { name: 'Add Opt-Out' })

    await user.type(screen.getByLabelText('Destination'), '+64211234567')
    await user.type(screen.getByLabelText('DestType'), 'sms')
    await user.click(screen.getByRole('button', { name: 'Add' }))

    expect(mockedApiRequest).toHaveBeenNthCalledWith(
      2,
      '/api/optout',
      expect.objectContaining({ method: 'POST', body: expect.objectContaining({ Destination: '+64211234567', DestType: 'sms' }) }),
    )
  })

  it('Detail fetches a single opt-out and shows it in the response viewer', async () => {
    mockedApiRequest.mockResolvedValueOnce({ status: 200, data: { OptOuts: [{ ID: 'o-1', Destination: '+64211234567' }] } })
    mockedApiRequest.mockResolvedValueOnce({ status: 200, data: { ID: 'o-1', Destination: '+64211234567', Notes: 'test note' } })
    const user = userEvent.setup()
    render(<OptOutPage />)
    await screen.findByText('+64211234567')

    await user.click(screen.getByRole('button', { name: 'Detail' }))

    expect(mockedApiRequest).toHaveBeenCalledWith('/api/optout/o-1')
    expect(await screen.findByText(/test note/)).toBeInTheDocument()
  })

  it('Delete removes the opt-out and reloads the list', async () => {
    mockedApiRequest.mockResolvedValueOnce({ status: 200, data: { OptOuts: [{ ID: 'o-1', Destination: '+64211234567' }] } })
    mockedApiRequest.mockResolvedValueOnce({ status: 200, data: {} })
    mockedApiRequest.mockResolvedValueOnce({ status: 200, data: { OptOuts: [] } })
    const user = userEvent.setup()
    render(<OptOutPage />)
    await screen.findByText('+64211234567')

    await user.click(screen.getByRole('button', { name: 'Delete' }))

    expect(mockedApiRequest).toHaveBeenCalledWith('/api/optout/o-1', { method: 'DELETE' })
    await waitFor(() => expect(mockedApiRequest).toHaveBeenCalledTimes(3))
  })

  it('Refresh re-fetches the list', async () => {
    mockedApiRequest.mockResolvedValue({ status: 200, data: { OptOuts: [] } })
    const user = userEvent.setup()
    render(<OptOutPage />)
    await waitFor(() => expect(mockedApiRequest).toHaveBeenCalledTimes(1))

    await user.click(screen.getByRole('button', { name: 'Refresh' }))

    await waitFor(() => expect(mockedApiRequest).toHaveBeenCalledTimes(2))
  })
})