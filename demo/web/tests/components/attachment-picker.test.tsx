import { describe, it, expect } from 'vitest'
import { useState } from 'react'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { AttachmentPicker, type AttachmentValue } from '@/components/attachment-picker'

// AttachmentPicker is a controlled component — every send page (SMS/Email/Fax/WhatsApp/RCS) owns
// `value`/`onChange`. This wrapper mimics that so tests exercise the same add/remove flow a real
// page would.
function ControlledAttachmentPicker({ disabled }: { disabled?: boolean } = {}) {
  const [files, setFiles] = useState<AttachmentValue[]>([])
  return <AttachmentPicker label="Attachments" value={files} onChange={setFiles} disabled={disabled} />
}

function makeFile(name: string, content: string) {
  return new File([content], name, { type: 'text/plain' })
}

describe('AttachmentPicker', () => {
  it('adds a selected file, base64-encoded with no data: prefix', async () => {
    const user = userEvent.setup()
    render(<ControlledAttachmentPicker />)

    await user.upload(screen.getByLabelText('Attachments'), makeFile('a.txt', 'hello'))

    expect(await screen.findByText('a.txt')).toBeInTheDocument()
  })

  it('appends newly selected files to the existing list instead of replacing it', async () => {
    const user = userEvent.setup()
    render(<ControlledAttachmentPicker />)

    await user.upload(screen.getByLabelText('Attachments'), makeFile('a.txt', 'hello'))
    await screen.findByText('a.txt')
    await user.upload(screen.getByLabelText('Attachments'), makeFile('b.txt', 'world'))

    expect(await screen.findByText('b.txt')).toBeInTheDocument()
    expect(screen.getByText('a.txt')).toBeInTheDocument()
  })

  it('Remove drops only the targeted file, preserving the others', async () => {
    const user = userEvent.setup()
    render(<ControlledAttachmentPicker />)

    await user.upload(screen.getByLabelText('Attachments'), makeFile('a.txt', 'hello'))
    await screen.findByText('a.txt')
    await user.upload(screen.getByLabelText('Attachments'), makeFile('b.txt', 'world'))
    await screen.findByText('b.txt')

    const removeButtons = screen.getAllByRole('button', { name: 'Remove' })
    await user.click(removeButtons[0])

    expect(screen.queryByText('a.txt')).not.toBeInTheDocument()
    expect(screen.getByText('b.txt')).toBeInTheDocument()
  })

  it('renders no file list when value is empty', () => {
    render(<ControlledAttachmentPicker />)

    expect(screen.queryByRole('button', { name: 'Remove' })).not.toBeInTheDocument()
  })

  it('disables the file input when disabled is set', () => {
    render(<ControlledAttachmentPicker disabled />)

    expect(screen.getByLabelText('Attachments')).toBeDisabled()
  })
})