import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import ComingSoonPage from '@/pages/ComingSoonPage'

describe('ComingSoonPage', () => {
  it('renders the given title as its heading', () => {
    render(<ComingSoonPage title="Something Placeholder" />)

    expect(screen.getByRole('heading', { name: 'Something Placeholder' })).toBeInTheDocument()
  })
})