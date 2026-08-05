import '@testing-library/jest-dom/vitest'
import { afterEach } from 'vitest'
import { cleanup } from '@testing-library/react'

// Unmounts any component rendered by a previous test — without this, DOM nodes (and any
// setInterval/effect they started) would accumulate across tests in the same file.
afterEach(() => {
  cleanup()
})