import { describe, it, expect, vi, afterEach } from 'vitest'
import { render, screen, waitFor, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import GroupContactsPage from '@/pages/addressbook/GroupContactsPage'
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
  return within(screen.getByRole('heading', { name: 'Contacts In A Group' }).closest('section')!)
}

describe('GroupContactsPage', () => {
  afterEach(() => {
    mockedApiRequest.mockReset()
  })

  it('adds a contact to a group via /api/addressbook/group-contacts', async () => {
    mockedApiRequest.mockResolvedValue({ status: 200, data: { Contact: { ContactID: 'c-1' } } })
    const user = userEvent.setup()
    render(<GroupContactsPage />)

    await user.type(addSection().getByLabelText('Group ID'), 'g-1')
    await user.type(addSection().getByLabelText('Contact ID'), 'c-1')
    await user.click(addSection().getByRole('button', { name: 'Add' }))

    expect(mockedApiRequest).toHaveBeenCalledWith(
      '/api/addressbook/group-contacts',
      expect.objectContaining({ method: 'POST', body: { GroupID: 'g-1', ContactID: 'c-1' } }),
    )
  })

  it('loads the contacts in a group and lists them', async () => {
    mockedApiRequest.mockResolvedValue({ status: 200, data: { Contacts: [{ ContactID: 'c-1', FirstName: 'Jane', LastName: 'Doe' }] } })
    const user = userEvent.setup()
    render(<GroupContactsPage />)

    await user.type(listSection().getByLabelText('Group ID'), 'g-1')
    await user.click(listSection().getByRole('button', { name: 'Load' }))

    expect(mockedApiRequest).toHaveBeenCalledWith('/api/addressbook/group-contacts?groupID=g-1')
    expect(await screen.findByText('Jane Doe')).toBeInTheDocument()
  })

  it('the Add form and the list-lookup field are independent (no shared DOM id)', async () => {
    mockedApiRequest.mockResolvedValue({ status: 200, data: { Contacts: [] } })
    const user = userEvent.setup()
    render(<GroupContactsPage />)

    await user.type(addSection().getByLabelText('Group ID'), 'add-value')

    expect(listSection().getByLabelText('Group ID')).toHaveValue('')
  })

  it('Remove deletes the relation and reloads the list', async () => {
    mockedApiRequest.mockResolvedValueOnce({ status: 200, data: { Contacts: [{ ContactID: 'c-1', FirstName: 'Jane' }] } })
    mockedApiRequest.mockResolvedValueOnce({ status: 200, data: {} })
    mockedApiRequest.mockResolvedValueOnce({ status: 200, data: { Contacts: [] } })
    const user = userEvent.setup()
    render(<GroupContactsPage />)

    await user.type(listSection().getByLabelText('Group ID'), 'g-1')
    await user.click(listSection().getByRole('button', { name: 'Load' }))
    await screen.findByText('Jane')

    await user.click(screen.getByRole('button', { name: 'Remove' }))

    expect(mockedApiRequest).toHaveBeenCalledWith('/api/addressbook/group-contacts', {
      method: 'DELETE',
      body: { GroupID: 'g-1', ContactID: 'c-1' },
    })
    await waitFor(() => expect(mockedApiRequest).toHaveBeenCalledTimes(3))
  })
})