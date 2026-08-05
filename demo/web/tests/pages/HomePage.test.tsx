import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import HomePage from '@/pages/HomePage'
import { NAV_SECTIONS } from '@/components/layout/nav-items'

describe('HomePage', () => {
  it('renders a link for every nav item across every section', () => {
    render(
      <MemoryRouter>
        <HomePage />
      </MemoryRouter>,
    )

    const allItems = NAV_SECTIONS.flatMap((section) => section.items)
    for (const item of allItems) {
      const link = screen.getByRole('link', { name: item.label })
      expect(link).toHaveAttribute('href', item.href)
    }
  })

  it('renders a heading for every nav section', () => {
    render(
      <MemoryRouter>
        <HomePage />
      </MemoryRouter>,
    )

    for (const section of NAV_SECTIONS) {
      expect(screen.getByRole('heading', { name: section.title })).toBeInTheDocument()
    }
  })
})