import { useEffect, useState } from 'react'
import { Chat } from './components/Chat'
import { Sidebar } from './components/Sidebar'
import { UserMenu } from './components/UserMenu'
import { LoginPage } from './components/LoginPage'
import { useTheme } from './hooks/useTheme'
import { useAuth } from './hooks/useAuth'
import { useMessages } from './hooks/useMessages'
import { useSessions } from './hooks/useSessions'

function App() {
  const { theme, toggleTheme } = useTheme()
  const { isAuthenticated, isLoading, user, signOut } = useAuth()
  const { messages, isLoading: chatLoading, error, sendMessage, setFeedback, clearMessages, loadMessages } = useMessages()
  const { sessions, activeSession, activeSessionId, createSession, selectSession, updateSession, deleteSession } = useSessions()
  const [isSidebarOpen, setIsSidebarOpen] = useState(false)

  // On mount: restore last active session or create a new one
  useEffect(() => {
    if (activeSession && activeSession.messages.length > 0) {
      loadMessages(activeSession.messages)
    } else if (!activeSessionId) {
      createSession()
    }
    // intentionally run only on mount
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  // Sync messages back to the active session after each change
  useEffect(() => {
    if (activeSessionId && messages.length > 0) {
      updateSession(activeSessionId, messages)
    }
  }, [messages, activeSessionId, updateSession])

  const handleNewChat = () => {
    createSession()
    clearMessages()
    setIsSidebarOpen(false)
  }

  const handleSelectSession = (id: string) => {
    selectSession(id)
    const session = sessions.find((s) => s.id === id)
    if (session) {
      loadMessages(session.messages)
    } else {
      clearMessages()
    }
    setIsSidebarOpen(false)
  }

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
          {/* Hamburger — mobile only; hidden on desktop where sidebar is always shown */}
          <button
            onClick={() => setIsSidebarOpen((o) => !o)}
            className="md:hidden w-10 h-10 flex items-center justify-center rounded-lg text-gray-500 hover:bg-gray-100 dark:text-gray-400 dark:hover:bg-gray-700"
            aria-label="Toggle sidebar"
          >
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" className="w-5 h-5">
              <line x1="3" y1="6" x2="21" y2="6" /><line x1="3" y1="12" x2="21" y2="12" /><line x1="3" y1="18" x2="21" y2="18" />
            </svg>
          </button>
          {/* Spacer so title stays centred on desktop */}
          <div className="hidden md:block w-10" />

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

      <div className="flex flex-1 min-h-0 overflow-hidden">
        {/* Sidebar: overlay on mobile, inline on desktop */}
        <aside
          className={[
            'fixed inset-y-0 left-0 z-30 w-60',
            'bg-white dark:bg-gray-800',
            'border-r border-gray-200 dark:border-gray-700',
            'transition-transform duration-200',
            'md:static md:z-auto md:translate-x-0',
            isSidebarOpen ? 'translate-x-0' : '-translate-x-full',
          ].join(' ')}
        >
          <Sidebar
            sessions={sessions}
            activeSessionId={activeSessionId}
            onNewChat={handleNewChat}
            onSelect={handleSelectSession}
            onDelete={deleteSession}
            onClose={() => setIsSidebarOpen(false)}
          />
        </aside>

        {/* Backdrop — mobile only */}
        {isSidebarOpen && (
          <div
            className="fixed inset-0 bg-black/30 z-20 md:hidden"
            onClick={() => setIsSidebarOpen(false)}
            aria-hidden="true"
          />
        )}

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
    </div>
  )
}

export default App
