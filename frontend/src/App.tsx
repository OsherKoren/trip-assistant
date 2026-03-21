import { Chat } from './components/Chat'
import { UserMenu } from './components/UserMenu'
import { LoginPage } from './components/LoginPage'
import { useTheme } from './hooks/useTheme'
import { useAuth } from './hooks/useAuth'
import { useMessages } from './hooks/useMessages'

function App() {
  const { theme, toggleTheme } = useTheme()
  const { isAuthenticated, isLoading, user, signOut } = useAuth()
  const { messages, isLoading: chatLoading, error, sendMessage, setFeedback, clearMessages } = useMessages()

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
          <button
            onClick={clearMessages}
            className="w-10 h-10 flex items-center justify-center rounded-lg text-gray-500 hover:bg-gray-100 dark:text-gray-400 dark:hover:bg-gray-700"
            aria-label="New chat"
          >
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" className="w-5 h-5">
              <path d="M12 20h9" />
              <path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z" />
            </svg>
          </button>
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
        <Chat
          messages={messages}
          isLoading={chatLoading}
          error={error}
          onSend={sendMessage}
          onFeedback={setFeedback}
        />
      </main>
    </div>
  )
}

export default App
