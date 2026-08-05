import { describe, it, expect } from 'vitest'
import { useState } from 'react'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { KeypadEditor, type KeypadValue } from '@/components/keypad-editor'

// KeypadEditor is a controlled component — a page (TtsPage/VoicePage) owns `value`/`onChange`.
// This wrapper mimics that so tests exercise the same add/remove/update flow a real page would.
function ControlledKeypadEditor() {
  const [keypads, setKeypads] = useState<KeypadValue[]>([])
  return <KeypadEditor label="Keypads" value={keypads} onChange={setKeypads} />
}

function getPlayInputs() {
  return screen.getAllByLabelText('Play')
}

describe('KeypadEditor', () => {
  it('removing a keypad from the middle preserves the other rows values', async () => {
    // Regression test for the array-index-as-key bug fixed in the React best-practices pass:
    // removing row 1 used to misassign the remaining rows' focus/identity because React reused
    // the wrong DOM node. ids are now tracked in parallel state instead of the array index.
    const user = userEvent.setup()
    render(<ControlledKeypadEditor />)

    const addButton = screen.getByRole('button', { name: 'Add Keypad' })
    await user.click(addButton)
    await user.click(addButton)
    await user.click(addButton)

    const playInputsBeforeRemove = getPlayInputs()
    expect(playInputsBeforeRemove).toHaveLength(3)
    await user.type(playInputsBeforeRemove[0], 'row-0')
    await user.type(playInputsBeforeRemove[1], 'row-1')
    await user.type(playInputsBeforeRemove[2], 'row-2')

    const removeButtons = screen.getAllByRole('button', { name: 'Remove' })
    await user.click(removeButtons[1])

    const playInputsAfterRemove = getPlayInputs()
    expect(playInputsAfterRemove).toHaveLength(2)
    expect(playInputsAfterRemove[0]).toHaveValue('row-0')
    expect(playInputsAfterRemove[1]).toHaveValue('row-2')
  })

  it('adding a keypad appends an empty row without disturbing existing ones', async () => {
    const user = userEvent.setup()
    render(<ControlledKeypadEditor />)

    await user.click(screen.getByRole('button', { name: 'Add Keypad' }))
    await user.type(getPlayInputs()[0], 'first')
    await user.click(screen.getByRole('button', { name: 'Add Keypad' }))

    const playInputs = getPlayInputs()
    expect(playInputs).toHaveLength(2)
    expect(playInputs[0]).toHaveValue('first')
    expect(playInputs[1]).toHaveValue('')
  })

  it('renders no rows and no Play fields when value is empty', () => {
    render(<ControlledKeypadEditor />)

    expect(screen.queryAllByLabelText('Play')).toHaveLength(0)
  })

  it('hides Play File / File fields by default (TTS has no use for them)', async () => {
    const user = userEvent.setup()
    render(<ControlledKeypadEditor />)

    await user.click(screen.getByRole('button', { name: 'Add Keypad' }))

    expect(screen.queryByLabelText('Play File')).not.toBeInTheDocument()
    expect(screen.queryByLabelText('File', { exact: true })).not.toBeInTheDocument()
  })
})