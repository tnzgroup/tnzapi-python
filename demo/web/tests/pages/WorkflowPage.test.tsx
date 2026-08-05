import { describe, it, expect, vi, afterEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import WorkflowPage from '@/pages/messaging/WorkflowPage'
import { apiRequest } from '@/lib/api-client'

vi.mock('@/lib/api-client', async () => {
  const actual = await vi.importActual<typeof import('@/lib/api-client')>('@/lib/api-client')
  return { ...actual, apiRequest: vi.fn() }
})

const mockedApiRequest = vi.mocked(apiRequest)

describe('WorkflowPage', () => {
  afterEach(() => {
    mockedApiRequest.mockReset()
  })

  it('submits Workflow Template ID and recipient fields to /api/workflow/send', async () => {
    mockedApiRequest.mockResolvedValue({ status: 200, data: { Result: 'Success', MessageID: 'abc-123' } })
    const user = userEvent.setup()
    render(<WorkflowPage />)

    await user.type(screen.getByLabelText('Workflow Template ID'), 'tmpl-1')
    await user.type(screen.getByLabelText('To Number'), '+64211234567')
    await user.click(screen.getByRole('button', { name: 'Send' }))

    expect(mockedApiRequest).toHaveBeenCalledWith(
      '/api/workflow/send',
      expect.objectContaining({
        method: 'POST',
        body: expect.objectContaining({ WorkflowTemplateId: 'tmpl-1', ToNumber: '+64211234567' }),
      }),
    )
  })

  it('sends Contact IDs / Group IDs as raw comma-separated strings (backend splits them)', async () => {
    mockedApiRequest.mockResolvedValue({ status: 200, data: { Result: 'Success' } })
    const user = userEvent.setup()
    render(<WorkflowPage />)

    await user.type(screen.getByLabelText('Workflow Template ID'), 'tmpl-1')
    await user.type(screen.getByLabelText('Contact IDs'), 'contact-1, contact-2')
    await user.click(screen.getByRole('button', { name: 'Send' }))

    const body = mockedApiRequest.mock.calls[0][1]?.body as { ContactIds?: string }
    expect(body.ContactIds).toBe('contact-1, contact-2')
  })

  it('has no Check Status card — Workflow has no status endpoint', () => {
    render(<WorkflowPage />)

    expect(screen.queryByRole('heading', { name: 'Check Status' })).not.toBeInTheDocument()
  })

  it('renders the response on success', async () => {
    mockedApiRequest.mockResolvedValue({ status: 200, data: { Result: 'Success', MessageID: 'abc-123' } })
    const user = userEvent.setup()
    render(<WorkflowPage />)

    await user.type(screen.getByLabelText('Workflow Template ID'), 'tmpl-1')
    await user.type(screen.getByLabelText('To Number'), '+64211234567')
    await user.click(screen.getByRole('button', { name: 'Send' }))

    expect(await screen.findByText('Success (HTTP 200)')).toBeInTheDocument()
  })
})