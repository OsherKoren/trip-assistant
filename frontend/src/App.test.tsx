import { render, screen } from '@testing-library/react'
import App from './App'
import { AuthContext } from './auth/AuthContext'
import type { AuthContextType } from './auth/types'

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
    googleSignInUrl: 'https://example.com/oauth2/authorize',
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

  it('renders theme toggle when authenticated', () => {
    renderWithAuth({ isAuthenticated: true, user: { email: 'a@b.com' } })
    expect(screen.getByRole('button', { name: /switch to dark mode/i })).toBeInTheDocument()
  })

  it('displays user email when authenticated', () => {
    renderWithAuth({ isAuthenticated: true, user: { email: 'test@example.com' } })
    expect(screen.getByText('test@example.com')).toBeInTheDocument()
  })

  it('renders logout button when authenticated', () => {
    renderWithAuth({ isAuthenticated: true, user: { email: 'a@b.com' } })
    expect(screen.getByRole('button', { name: /sign out/i })).toBeInTheDocument()
  })
})
