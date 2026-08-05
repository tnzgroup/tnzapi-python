import { describe, it, expect, vi, afterEach } from 'vitest'
import { render, screen, waitFor, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import ContactGroupsPage from '@/pages/addressbook/ContactGroupsPage'
import { apiRequest } from '@/lib/api-client'

vi.mock('@/lib/api-client', async () => {
  const actual = await vi.importActual<typeof import('@/lib/api-client')>('@/lib/api-client')
  return { ...actual, apiRequest: vi.fn() }
})

const mockedApiRequest = vi.mocked(apiRequest)

function addSection() {
  return within(screen.getByRole('heading', { name: 'Add Contact To Group' }).closest('section')!)
}
function listSection() {
  return within(screen.getByRole('heading', { name: 'Groups For A Contact' }).closest('section')!)
}

describe('ContactGroupsPage', () => {
  afterEach(() => {
    mockedApiRequest.mockReset()
  })

  it('adds a contact to a group via POST-backed /api/addressbook/contact-groups', async () => {
    mockedApiRequest.mockResolvedValue({ status: 200, data: { Group: { GroupID: 'g-1' } } })
    const user = userEvent.setup()
    render(<ContactGroupsPage />)

    await user.type(addSection().getByLabelText('Contact ID'), 'c-1')
    await user.type(addSection().getByLabelText('Group ID'), 'g-1')
    await user.click(addSection().getByRole('button', { name: 'Add' }))

    expect(mockedApiRequest).toHaveBeenCalledWith(
      '/api/addressbook/contact-groups',
      expect.objectContaining({ method: 'POST', body: { ContactID: 'c-1', GroupID: 'g-1' } }),
    )
  })

  it('loads the groups for a contact and lists them', async () => {
    mockedApiRequest.mockResolvedValue({ status: 200, data: { Groups: [{ GroupID: 'g-1', GroupName: 'Sales' }] } })
    const user = userEvent.setup()
    render(<ContactGroupsPage />)

    await user.type(listSection().getByLabelText('Contact ID'), 'c-1')
    await user.click(listSection().getByRole('button', { name: 'Load' }))

    expect(mockedApiRequest).toHaveBeenCalledWith('/api/addressbook/contact-groups?contactID=c-1')
    expect(await screen.findByText('Sales')).toBeInTheDocument()
  })

  it('the Add form and the list-lookup field are independent (no shared DOM id)', async () => {
    mockedApiRequest.mockResolvedValue({ status: 200, data: { Groups: [] } })
    const user = userEvent.setup()
    render(<ContactGroupsPage />)

    await user.type(addSection().getByLabelText('Contact ID'), 'add-value')

    expect(listSection().getByLabelText('Contact ID')).toHaveValue('')
  })

  it('Remove deletes the relation and reloads the list', async () => {
    mockedApiRequest.mockResolvedValueOnce({ status: 200, data: { Groups: [{ GroupID: 'g-1', GroupName: 'Sales' }] } }) // initial load
    mockedApiRequest.mockResolvedValueOnce({ status: 200, data: {} }) // remove
    mockedApiRequest.mockResolvedValueOnce({ status: 200, data: { Groups: [] } }) // reload
    const user = userEvent.setup()
    render(<ContactGroupsPage />)

    await user.type(listSection().getByLabelText('Contact ID'), 'c-1')
    await user.click(listSection().getByRole('button', { name: 'Load' }))
    await screen.findByText('Sales')

    await user.click(screen.getByRole('button', { name: 'Remove' }))

    expect(mockedApiRequest).toHaveBeenCalledWith('/api/addressbook/contact-groups', {
      method: 'DELETE',
      body: { ContactID: 'c-1', GroupID: 'g-1' },
    })
    await waitFor(() => expect(mockedApiRequest).toHaveBeenCalledTimes(3))
  })
})