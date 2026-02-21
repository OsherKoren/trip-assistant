import { Chat } from './components/Chat'
import { ThemeToggle } from './components/ThemeToggle'
import { useTheme } from './hooks/useTheme'

function App() {
  const { theme, toggleTheme } = useTheme()

  return (
    <div className="h-dvh flex flex-col bg-gray-50 dark:bg-gray-900">
      <header className="shrink-0 border-b border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800">
        <div className="flex items-center justify-between p-3">
          <div className="w-9" />
          <h1 className="text-xl font-bold text-gray-900 dark:text-gray-100">
            Trip Assistant
          </h1>
          <ThemeToggle theme={theme} onToggle={toggleTheme} />
        </div>
      </header>
      <main className="flex-1 min-h-0">
        <Chat />
      </main>
    </div>
  )
}

export default App
