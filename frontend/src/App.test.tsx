import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import App from './App'
import { AuthContext } from './auth/AuthContext'
import type { AuthContextType } from './auth/types'

const mockClearMessages = vi.fn()

vi.mock('./hooks/useMessages', () => ({
  useMessages: () => ({
    messages: [],
    isLoading: false,
    error: null,
    sendMessage: vi.fn(),
    setFeedback: vi.fn(),
    clearMessages: mockClearMessages,
  }),
}))

function mockAuthContext(overrides: Partial<AuthContextType> = {}): AuthContextType {
  return {
    user: null,
    isAuthenticated: false,
    isLoading: false,
    signIn: vi.fn(),
    signUp: vi.fn(),
    signOut: vi.fn(),
    getToken: vi.fn().mockResolvedValue('token'),
    signInWithGoogle: vi.fn(),
    googleSignInUrl: null,
    ...overrides,
  }
}

function renderWithAuth(overrides: Partial<AuthContextType> = {}) {
  const ctx = mockAuthContext(overrides)
  render(
    <AuthContext.Provider value={ctx}>
      <App />
    </AuthContext.Provider>
  )
  return ctx
}

describe('App', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('shows loading spinner when auth is loading', () => {
    renderWithAuth({ isLoading: true })
    expect(screen.getByText('Loading...')).toBeInTheDocument()
  })

  it('shows login page when not authenticated', () => {
    renderWithAuth({ isAuthenticated: false })
    expect(screen.getByText('Sign in to continue')).toBeInTheDocument()
  })

  it('renders app header when authenticated', () => {
    renderWithAuth({ isAuthenticated: true, user: { email: 'a@b.com' } })
    expect(screen.getByText('Trip Assistant')).toBeInTheDocument()
  })

  it('renders Chat component when authenticated', () => {
    renderWithAuth({ isAuthenticated: true, user: { email: 'a@b.com' } })
    expect(screen.getByRole('textbox')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /send/i })).toBeInTheDocument()
  })

  it('renders user menu avatar when authenticated', () => {
    renderWithAuth({ isAuthenticated: true, user: { email: 'a@b.com' } })
    expect(screen.getByRole('button', { name: /user menu/i })).toBeInTheDocument()
  })

  it('does not show raw email in header', () => {
    renderWithAuth({ isAuthenticated: true, user: { email: 'test@example.com' } })
    expect(screen.queryByText('test@example.com')).not.toBeInTheDocument()
  })

  it('renders New Chat button when authenticated', () => {
    renderWithAuth({ isAuthenticated: true, user: { email: 'a@b.com' } })
    expect(screen.getByRole('button', { name: /new chat/i })).toBeInTheDocument()
  })

  it('calls clearMessages when New Chat button is clicked', async () => {
    renderWithAuth({ isAuthenticated: true, user: { email: 'a@b.com' } })

    await userEvent.click(screen.getByRole('button', { name: /new chat/i }))

    expect(mockClearMessages).toHaveBeenCalled()
  })
})
