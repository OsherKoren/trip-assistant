import { render, screen } from '@testing-library/react'
import App from './App'

describe('App', () => {
  it('renders app header', () => {
    render(<App />)
    expect(screen.getByText('Trip Assistant')).toBeInTheDocument()
  })

  it('renders Chat component', () => {
    render(<App />)
    expect(screen.getByRole('textbox')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /send/i })).toBeInTheDocument()
  })

  it('renders theme toggle', () => {
    render(<App />)
    expect(screen.getByRole('button', { name: /switch to dark mode/i })).toBeInTheDocument()
  })
})
