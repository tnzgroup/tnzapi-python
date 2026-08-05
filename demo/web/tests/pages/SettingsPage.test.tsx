import { describe, it, expect, vi, afterEach, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import SettingsPage from '@/pages/SettingsPage'
import { apiRequest } from '@/lib/api-client'

vi.mock('@/lib/api-client', async () => {
  const actual = await vi.importActual<typeof import('@/lib/api-client')>('@/lib/api-client')
  return { ...actual, apiRequest: vi.fn() }
})

const mockedApiRequest = vi.mocked(apiRequest)

// The form renders two type="submit" Save buttons (top and bottom, for a long scrolling form) —
// either one submits the same form, so tests just need a single unambiguous reference.
function saveButton() {
  return screen.getAllByRole('button', { name: 'Save' })[0]
}

function mockGetResponses() {
  mockedApiRequest.mockImplementation(async (url) => {
    if (url === '/api/settings/api-url') return { status: 200, data: { ApiUrl: 'https://api.tnz.co.nz' } }
    if (url === '/api/settings/ssl-verification') return { status: 200, data: { Enabled: true } }
    if (url === '/api/settings/allow-insecure-http') return { status: 200, data: { Enabled: false } }
    return { status: 200, data: { Status: 'ok' } }
  })
}

describe('SettingsPage', () => {
  beforeEach(() => {
    localStorage.clear()
  })

  afterEach(() => {
    mockedApiRequest.mockReset()
  })

  it('loads the three connection settings via GET on mount when not remembering', async () => {
    mockGetResponses()
    render(<SettingsPage />)

    await waitFor(() => expect(screen.getByLabelText('API URL')).toHaveValue('https://api.tnz.co.nz'))
    expect(mockedApiRequest).toHaveBeenCalledWith('/api/settings/api-url')
    expect(mockedApiRequest).toHaveBeenCalledWith('/api/settings/ssl-verification')
    expect(mockedApiRequest).toHaveBeenCalledWith('/api/settings/allow-insecure-http')
  })

  it('Save posts all three connection settings and shows their responses', async () => {
    mockGetResponses()
    const user = userEvent.setup()
    render(<SettingsPage />)
    await waitFor(() => expect(screen.getByLabelText('API URL')).toHaveValue('https://api.tnz.co.nz'))
    mockedApiRequest.mockClear()
    mockGetResponses()

    await user.click(saveButton())

    await waitFor(() =>
      expect(mockedApiRequest).toHaveBeenCalledWith('/api/settings/api-url', {
        method: 'POST',
        body: { ApiUrl: 'https://api.tnz.co.nz' },
      }),
    )
    expect(mockedApiRequest).toHaveBeenCalledWith('/api/settings/ssl-verification', { method: 'POST', body: { Enabled: true } })
    expect(mockedApiRequest).toHaveBeenCalledWith('/api/settings/allow-insecure-http', { method: 'POST', body: { Enabled: false } })
  })

  it('Save does not post an Auth Token when the field is left blank', async () => {
    mockGetResponses()
    const user = userEvent.setup()
    render(<SettingsPage />)
    await waitFor(() => expect(screen.getByLabelText('API URL')).toHaveValue('https://api.tnz.co.nz'))
    mockedApiRequest.mockClear()
    mockGetResponses()

    await user.click(saveButton())
    await waitFor(() => expect(mockedApiRequest).toHaveBeenCalledWith('/api/settings/api-url', expect.anything()))

    expect(mockedApiRequest).not.toHaveBeenCalledWith('/api/auth/token', expect.anything())
  })

  it('Save posts the Auth Token when a value is entered', async () => {
    mockGetResponses()
    const user = userEvent.setup()
    render(<SettingsPage />)
    await waitFor(() => expect(screen.getByLabelText('API URL')).toHaveValue('https://api.tnz.co.nz'))
    mockedApiRequest.mockClear()
    mockGetResponses()

    await user.type(screen.getByLabelText('JWT Auth Token'), 'header.payload.signature')
    await user.click(saveButton())

    await waitFor(() =>
      expect(mockedApiRequest).toHaveBeenCalledWith('/api/auth/token', {
        method: 'POST',
        body: { Token: 'header.payload.signature' },
      }),
    )
  })

  it('Remember These Settings persists connection settings to localStorage on Save', async () => {
    mockGetResponses()
    const user = userEvent.setup()
    render(<SettingsPage />)
    await waitFor(() => expect(screen.getByLabelText('API URL')).toHaveValue('https://api.tnz.co.nz'))

    await user.click(screen.getByLabelText('Remember these settings in this browser'))
    await user.click(saveButton())

    await waitFor(() => expect(localStorage.getItem('tnzapi-demo-settings')).not.toBeNull())
    const stored = JSON.parse(localStorage.getItem('tnzapi-demo-settings')!)
    expect(stored.apiUrl).toBe('https://api.tnz.co.nz')
  })

  it('re-applies remembered settings via POST instead of GET when remembering is already on', async () => {
    localStorage.setItem('tnzapi-demo-remember-settings', 'true')
    localStorage.setItem(
      'tnzapi-demo-settings',
      JSON.stringify({ apiUrl: 'https://staging.example.com', sslVerificationEnabled: false, allowInsecureHttp: true }),
    )
    mockGetResponses()
    render(<SettingsPage />)

    await waitFor(() =>
      expect(mockedApiRequest).toHaveBeenCalledWith('/api/settings/api-url', {
        method: 'POST',
        body: { ApiUrl: 'https://staging.example.com' },
      }),
    )
    expect(await screen.findByLabelText('API URL')).toHaveValue('https://staging.example.com')
  })
})