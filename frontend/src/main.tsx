import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import './auth/config' // Side-effect: must run before @aws-amplify/auth is loaded
import App from './App.tsx'
import { AuthProvider } from './auth/AuthContext'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <AuthProvider>
      <App />
    </AuthProvider>
  </StrictMode>,
)
