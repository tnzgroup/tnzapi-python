import { describe, it, expect, vi, afterEach } from 'vitest'
import { render, screen, waitFor, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import GroupsPage from '@/pages/addressbook/GroupsPage'
import { apiRequest } from '@/lib/api-client'

vi.mock('@/lib/api-client', async () => {
  const actual = await vi.importActual<typeof import('@/lib/api-client')>('@/lib/api-client')
  return { ...actual, apiRequest: vi.fn() }
})

const mockedApiRequest = vi.mocked(apiRequest)

function createSection() {
  return within(screen.getByRole('heading', { name: 'Create Group' }).closest('section')!)
}
function editSection() {
  return within(screen.getByRole('heading', { name: 'Edit / Delete Group' }).closest('section')!)
}

describe('GroupsPage', () => {
  afterEach(() => {
    mockedApiRequest.mockReset()
  })

  it('loads the group list on mount', async () => {
    mockedApiRequest.mockResolvedValue({ status: 200, data: { Groups: [{ GroupID: 'g-1', GroupName: 'Sales' }] } })
    render(<GroupsPage />)

    expect(await screen.findByText('Sales')).toBeInTheDocument()
    expect(mockedApiRequest).toHaveBeenCalledWith('/api/addressbook/groups?recordsPerPage=50&page=1')
  })

  it('creates a group and reloads the list on success', async () => {
    mockedApiRequest.mockResolvedValueOnce({ status: 200, data: { Groups: [] } })
    mockedApiRequest.mockResolvedValueOnce({ status: 200, data: { GroupID: 'g-1' } })
    mockedApiRequest.mockResolvedValueOnce({ status: 200, data: { Groups: [{ GroupID: 'g-1', GroupName: 'Sales' }] } })
    const user = userEvent.setup()
    render(<GroupsPage />)
    await screen.findByRole('heading', { name: 'Create Group' })

    await user.type(createSection().getByLabelText('GroupName'), 'Sales')
    await user.click(createSection().getByRole('button', { name: 'Create' }))

    expect(mockedApiRequest).toHaveBeenNthCalledWith(
      2,
      '/api/addressbook/groups',
      expect.objectContaining({ method: 'POST', body: expect.objectContaining({ GroupName: 'Sales' }) }),
    )
  })

  it('Load fetches group details into the edit form, distinct from the Create form fields', async () => {
    mockedApiRequest.mockResolvedValueOnce({ status: 200, data: { Groups: [] } })
    mockedApiRequest.mockResolvedValueOnce({ status: 200, data: { GroupID: 'g-1', GroupName: 'Sales' } })
    const user = userEvent.setup()
    render(<GroupsPage />)
    await screen.findByRole('heading', { name: 'Create Group' })

    await user.type(editSection().getByLabelText('Group ID'), 'g-1')
    await user.click(editSection().getByRole('button', { name: 'Load' }))

    await waitFor(() => expect(editSection().getByLabelText('GroupName')).toHaveValue('Sales'))
    // The Create form's own GroupName field must be untouched by the edit load.
    expect(createSection().getByLabelText('GroupName')).toHaveValue('')
  })

  it('Save PUTs the edited fields and reloads the list on success', async () => {
    mockedApiRequest.mockResolvedValueOnce({ status: 200, data: { Groups: [] } }) // initial load
    mockedApiRequest.mockResolvedValueOnce({ status: 200, data: { GroupID: 'g-1', GroupName: 'Sales' } }) // load
    mockedApiRequest.mockResolvedValueOnce({ status: 200, data: { GroupID: 'g-1' } }) // update
    mockedApiRequest.mockResolvedValueOnce({ status: 200, data: { Groups: [{ GroupID: 'g-1', GroupName: 'Sales NZ' }] } }) // reload
    const user = userEvent.setup()
    render(<GroupsPage />)
    await screen.findByRole('heading', { name: 'Create Group' })

    await user.type(editSection().getByLabelText('Group ID'), 'g-1')
    await user.click(editSection().getByRole('button', { name: 'Load' }))
    await waitFor(() => expect(editSection().getByLabelText('GroupName')).toHaveValue('Sales'))

    await user.clear(editSection().getByLabelText('GroupName'))
    await user.type(editSection().getByLabelText('GroupName'), 'Sales NZ')
    await user.click(editSection().getByRole('button', { name: 'Save' }))

    expect(mockedApiRequest).toHaveBeenNthCalledWith(
      3,
      '/api/addressbook/groups/g-1',
      expect.objectContaining({ method: 'PUT', body: expect.objectContaining({ GroupName: 'Sales NZ' }) }),
    )
    await waitFor(() => expect(mockedApiRequest).toHaveBeenCalledTimes(4))
  })

  it('Delete removes the group and clears the edit form', async () => {
    mockedApiRequest.mockResolvedValueOnce({ status: 200, data: { Groups: [] } }) // initial load
    mockedApiRequest.mockResolvedValueOnce({ status: 200, data: { GroupID: 'g-1', GroupName: 'Sales' } }) // load
    mockedApiRequest.mockResolvedValueOnce({ status: 200, data: {} }) // delete
    mockedApiRequest.mockResolvedValueOnce({ status: 200, data: { Groups: [] } }) // reload
    const user = userEvent.setup()
    render(<GroupsPage />)
    await screen.findByRole('heading', { name: 'Create Group' })

    await user.type(editSection().getByLabelText('Group ID'), 'g-1')
    await user.click(editSection().getByRole('button', { name: 'Load' }))
    await waitFor(() => expect(editSection().getByLabelText('GroupName')).toHaveValue('Sales'))

    await user.click(editSection().getByRole('button', { name: 'Delete' }))

    expect(mockedApiRequest).toHaveBeenCalledWith('/api/addressbook/groups/g-1', { method: 'DELETE' })
    // handleDelete's reload (a 4th, un-awaited apiRequest call) must be allowed to finish before the
    // test ends — same reasoning as ContactsPage's equivalent test.
    await waitFor(() => expect(mockedApiRequest).toHaveBeenCalledTimes(4))
    expect(editSection().getByLabelText('GroupName')).toHaveValue('')
  })
})