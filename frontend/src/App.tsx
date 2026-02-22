import { Chat } from './components/Chat'
import { UserMenu } from './components/UserMenu'
import { LoginPage } from './components/LoginPage'
import { useTheme } from './hooks/useTheme'
import { useAuth } from './hooks/useAuth'

function App() {
  const { theme, toggleTheme } = useTheme()
  const { isAuthenticated, isLoading, user, signOut } = useAuth()

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
          <div className="w-10" />
          <h1 className="text-xl font-bold text-gray-900 dark:text-gray-100">
            Trip Assistant
          </h1>
          {user && (
            <UserMenu
              user={user}
              theme={theme}
              toggleTheme={toggleTheme}
              signOut={signOut}
            />
          )}
        </div>
      </header>
      <main className="flex-1 min-h-0">
        <Chat />
      </main>
    </div>
  )
}

export default App
