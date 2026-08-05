import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { TextField, SelectField, CheckboxField, type FieldValues } from '@/components/form-fields'

describe('TextField', () => {
  it('renders the current value from the values map', () => {
    render(<TextField label="To Number" name="ToNumber" values={{ ToNumber: '+64211234567' }} onChange={vi.fn()} />)

    expect(screen.getByLabelText('To Number')).toHaveValue('+64211234567')
  })

  it('renders an empty string when the field is absent from values', () => {
    render(<TextField label="To Number" name="ToNumber" values={{}} onChange={vi.fn()} />)

    expect(screen.getByLabelText('To Number')).toHaveValue('')
  })

  it('calls onChange with the field name and the typed value', async () => {
    const user = userEvent.setup()
    const onChange = vi.fn()
    render(<TextField label="Message" name="Message" values={{}} onChange={onChange} />)

    await user.type(screen.getByLabelText('Message'), 'Hi')

    // user.type fires one onChange per keystroke — the component doesn't debounce, it's a
    // controlled field with the parent owning state, so each call carries the field name and the
    // value at that keystroke (not accumulated, since `values` isn't updated between calls here).
    expect(onChange).toHaveBeenCalledWith('Message', 'H')
    expect(onChange).toHaveBeenCalledWith('Message', 'i')
  })

  it('renders a multiline field as a textarea', () => {
    render(<TextField label="Message" name="Message" values={{}} onChange={vi.fn()} multiline />)

    expect(screen.getByLabelText('Message').tagName).toBe('TEXTAREA')
  })

  it('disables the input when disabled is true', () => {
    render(<TextField label="To Number" name="ToNumber" values={{}} onChange={vi.fn()} disabled />)

    expect(screen.getByLabelText('To Number')).toBeDisabled()
  })
})

describe('SelectField', () => {
  it('renders options and calls onChange when one is selected', async () => {
    const user = userEvent.setup()
    const onChange = vi.fn()
    render(
      <SelectField
        label="Channel"
        name="Channel"
        values={{}}
        onChange={onChange}
        options={['SMS', 'Email', 'Fax']}
      />,
    )

    await user.click(screen.getByLabelText('Channel'))
    await user.click(await screen.findByRole('option', { name: 'Email' }))

    expect(onChange).toHaveBeenCalledWith('Channel', 'Email')
  })

  it('shows the placeholder when no value is set', () => {
    render(
      <SelectField label="Channel" name="Channel" values={{}} onChange={vi.fn()} options={['SMS']} placeholder="Pick one" />,
    )

    expect(screen.getByText('Pick one')).toBeInTheDocument()
  })
})

describe('CheckboxField', () => {
  it('reflects the checked state from values', () => {
    render(<CheckboxField label="Character Conversion" name="CharacterConversion" values={{ CharacterConversion: true }} onChange={vi.fn()} />)

    expect(screen.getByLabelText('Character Conversion')).toBeChecked()
  })

  it('is unchecked when the field is falsy/absent', () => {
    const values: FieldValues = {}
    render(<CheckboxField label="Character Conversion" name="CharacterConversion" values={values} onChange={vi.fn()} />)

    expect(screen.getByLabelText('Character Conversion')).not.toBeChecked()
  })

  it('calls onChange with the new boolean value on click', async () => {
    const user = userEvent.setup()
    const onChange = vi.fn()
    render(<CheckboxField label="Character Conversion" name="CharacterConversion" values={{}} onChange={onChange} />)

    await user.click(screen.getByLabelText('Character Conversion'))

    expect(onChange).toHaveBeenCalledWith('CharacterConversion', true)
  })
})