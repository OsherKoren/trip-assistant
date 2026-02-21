import { Chat } from './components/Chat'
import { ThemeToggle } from './components/ThemeToggle'
import { LogoutButton } from './components/LogoutButton'
import { LoginPage } from './components/LoginPage'
import { useTheme } from './hooks/useTheme'
import { useAuth } from './hooks/useAuth'

function App() {
  const { theme, toggleTheme } = useTheme()
  const { isAuthenticated, isLoading, user } = useAuth()

  if (isLoading) {
    return (
      <div className="h-dvh flex items-center justify-center bg-gray-50 dark:bg-gray-900">
        <p className="text-gray-500 dark:text-gray-400">Loading...</p>
      </div>
    )
  }

  if (!isAuthenticated) {
    return <LoginPage />
  }

  return (
    <div className="h-dvh flex flex-col bg-gray-50 dark:bg-gray-900">
      <header className="shrink-0 border-b border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800">
        <div className="flex items-center justify-between p-3">
          <span className="text-sm text-gray-500 dark:text-gray-400 truncate max-w-[140px]">
            {user?.email}
          </span>
          <h1 className="text-xl font-bold text-gray-900 dark:text-gray-100">
            Trip Assistant
          </h1>
          <div className="flex items-center gap-1">
            <LogoutButton />
            <ThemeToggle theme={theme} onToggle={toggleTheme} />
          </div>
        </div>
      </header>
      <main className="flex-1 min-h-0">
        <Chat />
      </main>
    </div>
  )
}

export default App
