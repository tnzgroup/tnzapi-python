import { Component, type ErrorInfo, type ReactNode } from 'react'

type ErrorBoundaryProps = {
  children: ReactNode
}

type ErrorBoundaryState = {
  error: Error | null
}

// React error boundaries have no hook equivalent — this must stay a class component. Catches a
// render-time throw from whatever page is currently mounted so it doesn't blank the entire app
// (sidebar included); the user can navigate elsewhere to recover without a full reload.
export class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  state: ErrorBoundaryState = { error: null }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { error }
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    console.error('Unhandled error in page render:', error, info.componentStack)
  }

  render() {
    if (this.state.error) {
      return (
        <div className="max-w-2xl space-y-4">
          <h1 className="text-xl font-semibold text-destructive">Something went wrong</h1>
          <p className="text-sm text-muted-foreground">
            This page hit an unexpected error. Try a different page from the sidebar, or reload.
          </p>
          <pre className="overflow-x-auto whitespace-pre-wrap rounded border border-red-400 bg-red-50 p-4 text-xs text-red-900">
            {this.state.error.message}
          </pre>
        </div>
      )
    }

    return this.props.children
  }
}