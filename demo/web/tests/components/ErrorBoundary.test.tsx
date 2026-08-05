import { describe, it, expect, vi, afterEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import { ErrorBoundary } from '@/components/ErrorBoundary'

function Bomb(): never {
  throw new Error('Boom')
}

describe('ErrorBoundary', () => {
  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('renders children normally when nothing throws', () => {
    render(
      <ErrorBoundary>
        <div>All good</div>
      </ErrorBoundary>,
    )

    expect(screen.getByText('All good')).toBeInTheDocument()
  })

  it('catches a render-time throw and shows the fallback instead of blanking the page', () => {
    // React logs the caught error to console.error itself (on top of componentDidCatch's own
    // logging) — silence it so the test's own output isn't drowned in an expected stack trace.
    vi.spyOn(console, 'error').mockImplementation(() => {})

    render(
      <ErrorBoundary>
        <Bomb />
      </ErrorBoundary>,
    )

    expect(screen.getByText('Something went wrong')).toBeInTheDocument()
    expect(screen.getByText('Boom')).toBeInTheDocument()
  })

  it('logs the caught error via componentDidCatch', () => {
    const consoleError = vi.spyOn(console, 'error').mockImplementation(() => {})

    render(
      <ErrorBoundary>
        <Bomb />
      </ErrorBoundary>,
    )

    expect(consoleError).toHaveBeenCalledWith('Unhandled error in page render:', expect.any(Error), expect.anything())
  })

  it('remounting with a new key (App.tsx keys by route pathname) clears a previously caught error', () => {
    vi.spyOn(console, 'error').mockImplementation(() => {})

    const { rerender } = render(
      <ErrorBoundary key="/messaging/sms">
        <Bomb />
      </ErrorBoundary>,
    )
    expect(screen.getByText('Something went wrong')).toBeInTheDocument()

    // A different key forces React to unmount the old instance (and its error state) and mount a
    // fresh one — this is the mechanism App.tsx relies on so navigating away from a broken page
    // actually recovers, instead of being permanently stuck on the fallback.
    rerender(
      <ErrorBoundary key="/messaging/email">
        <div>Email page</div>
      </ErrorBoundary>,
    )

    expect(screen.queryByText('Something went wrong')).not.toBeInTheDocument()
    expect(screen.getByText('Email page')).toBeInTheDocument()
  })
})