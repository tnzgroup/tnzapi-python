import { describe, it, expect, vi, afterEach } from 'vitest'
import { render, screen, waitFor, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import ContactsPage from '@/pages/addressbook/ContactsPage'
import { apiRequest } from '@/lib/api-client'

vi.mock('@/lib/api-client', async () => {
  const actual = await vi.importActual<typeof import('@/lib/api-client')>('@/lib/api-client')
  return { ...actual, apiRequest: vi.fn() }
})

const mockedApiRequest = vi.mocked(apiRequest)

function createSection() {
  return within(screen.getByRole('heading', { name: 'Create Contact' }).closest('section')!)
}
function editSection() {
  return within(screen.getByRole('heading', { name: 'Edit / Delete Contact' }).closest('section')!)
}

describe('ContactsPage', () => {
  afterEach(() => {
    mockedApiRequest.mockReset()
  })

  it('loads the contact list on mount', async () => {
    mockedApiRequest.mockResolvedValue({
      status: 200,
      data: { Contacts: [{ ContactID: 'c-1', FirstName: 'Jane', LastName: 'Doe' }] },
    })
    render(<ContactsPage />)

    expect(await screen.findByText('Jane Doe')).toBeInTheDocument()
    expect(mockedApiRequest).toHaveBeenCalledWith('/api/addressbook/contacts?recordsPerPage=50&page=1')
  })

  it('creates a contact and reloads the list on success', async () => {
    mockedApiRequest.mockResolvedValueOnce({ status: 200, data: { Contacts: [] } }) // initial load
    mockedApiRequest.mockResolvedValueOnce({ status: 200, data: { ContactID: 'c-1' } }) // create
    mockedApiRequest.mockResolvedValueOnce({ status: 200, data: { Contacts: [{ ContactID: 'c-1', FirstName: 'Jane' }] } }) // reload
    const user = userEvent.setup()
    render(<ContactsPage />)
    await screen.findByRole('heading', { name: 'Create Contact' })

    await user.type(createSection().getByLabelText('FirstName'), 'Jane')
    await user.click(createSection().getByRole('button', { name: 'Create' }))

    expect(mockedApiRequest).toHaveBeenNthCalledWith(
      2,
      '/api/addressbook/contacts',
      expect.objectContaining({ method: 'POST', body: expect.objectContaining({ FirstName: 'Jane' }) }),
    )
    expect(mockedApiRequest).toHaveBeenCalledTimes(3) // load, create, reload
  })

  it('Load fetches contact details into the edit form', async () => {
    mockedApiRequest.mockResolvedValueOnce({ status: 200, data: { Contacts: [] } })
    mockedApiRequest.mockResolvedValueOnce({ status: 200, data: { ContactID: 'c-1', FirstName: 'Jane' } })
    const user = userEvent.setup()
    render(<ContactsPage />)
    await screen.findByRole('heading', { name: 'Create Contact' })

    await user.type(editSection().getByLabelText('Contact ID'), 'c-1')
    await user.click(editSection().getByRole('button', { name: 'Load' }))

    expect(mockedApiRequest).toHaveBeenCalledWith('/api/addressbook/contacts/c-1')
    await waitFor(() => expect(editSection().getByLabelText('FirstName')).toHaveValue('Jane'))
  })

  it('Save and Delete are disabled until a contact is loaded', async () => {
    // Every render triggers the mount-time loadList() call — it must resolve to something, or the
    // resulting rejection surfaces later as an unhandled error attributed to whichever test runs
    // next (Vitest doesn't attribute background promise rejections to the render() call site).
    mockedApiRequest.mockResolvedValue({ status: 200, data: { Contacts: [] } })
    render(<ContactsPage />)
    await screen.findByRole('heading', { name: 'Create Contact' })

    expect(editSection().getByRole('button', { name: 'Save' })).toBeDisabled()
    expect(editSection().getByRole('button', { name: 'Delete' })).toBeDisabled()
  })

  it('Delete removes the contact and clears the edit form', async () => {
    mockedApiRequest.mockResolvedValueOnce({ status: 200, data: { Contacts: [] } }) // initial load
    mockedApiRequest.mockResolvedValueOnce({ status: 200, data: { ContactID: 'c-1', FirstName: 'Jane' } }) // load
    mockedApiRequest.mockResolvedValueOnce({ status: 200, data: {} }) // delete
    mockedApiRequest.mockResolvedValueOnce({ status: 200, data: { Contacts: [] } }) // reload
    const user = userEvent.setup()
    render(<ContactsPage />)
    await screen.findByRole('heading', { name: 'Create Contact' })

    await user.type(editSection().getByLabelText('Contact ID'), 'c-1')
    await user.click(editSection().getByRole('button', { name: 'Load' }))
    await waitFor(() => expect(editSection().getByLabelText('FirstName')).toHaveValue('Jane'))

    await user.click(editSection().getByRole('button', { name: 'Delete' }))

    expect(mockedApiRequest).toHaveBeenCalledWith('/api/addressbook/contacts/c-1', { method: 'DELETE' })
    // handleDelete's reload (a 4th, un-awaited apiRequest call) must be allowed to finish before
    // the test ends — otherwise it resolves after the next test's afterEach has already reset the
    // mock, throwing an unhandled rejection that (harmlessly, but noisily) leaks into that test run.
    await waitFor(() => expect(mockedApiRequest).toHaveBeenCalledTimes(4))
    expect(editSection().getByRole('button', { name: 'Save' })).toBeDisabled()
  })
})