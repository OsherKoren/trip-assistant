import type { ChatSession } from '../types';

interface SidebarProps {
  sessions: ChatSession[];
  activeSessionId: string | null;
  onNewChat: () => void;
  onSelect: (id: string) => void;
  onDelete: (id: string) => void;
  onClose: () => void;
}

function getDateLabel(isoString: string): string {
  const date = new Date(isoString);
  const now = new Date();
  const todayStart = new Date(now.getFullYear(), now.getMonth(), now.getDate());
  const yesterdayStart = new Date(todayStart);
  yesterdayStart.setDate(yesterdayStart.getDate() - 1);
  const sessionDay = new Date(date.getFullYear(), date.getMonth(), date.getDate());

  if (sessionDay >= todayStart) return 'Today';
  if (sessionDay >= yesterdayStart) return 'Yesterday';
  return date.toLocaleDateString('en-US', { month: 'long', day: 'numeric' });
}

function groupSessions(sessions: ChatSession[]): { label: string; items: ChatSession[] }[] {
  const groups: { label: string; items: ChatSession[] }[] = [];
  const labelMap = new Map<string, ChatSession[]>();

  for (const session of sessions) {
    const label = getDateLabel(session.updatedAt);
    if (!labelMap.has(label)) {
      const items: ChatSession[] = [];
      labelMap.set(label, items);
      groups.push({ label, items });
    }
    labelMap.get(label)!.push(session);
  }

  return groups;
}

export function Sidebar({ sessions, activeSessionId, onNewChat, onSelect, onDelete, onClose }: SidebarProps) {
  const groups = groupSessions(sessions);

  return (
    <div className="flex flex-col h-full">
      {/* Header row */}
      <div className="flex items-center justify-between px-3 py-2 border-b border-gray-200 dark:border-gray-700">
        <span className="text-sm font-semibold text-gray-600 dark:text-gray-400">Chats</span>
        <button
          onClick={onClose}
          className="md:hidden w-8 h-8 flex items-center justify-center rounded-lg text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700"
          aria-label="Close sidebar"
        >
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" className="w-4 h-4">
            <path d="M18 6 6 18" /><path d="m6 6 12 12" />
          </svg>
        </button>
      </div>

      {/* New Chat button */}
      <div className="p-2">
        <button
          onClick={onNewChat}
          className="w-full flex items-center gap-2 px-3 py-2 rounded-lg text-sm text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
          aria-label="New chat"
        >
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" className="w-4 h-4 shrink-0">
            <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7" />
            <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z" />
          </svg>
          New Chat
        </button>
      </div>

      {/* Session list */}
      <div className="flex-1 overflow-y-auto py-1">
        {groups.length === 0 ? (
          <p className="text-xs text-gray-400 dark:text-gray-500 px-4 py-2">No conversations yet</p>
        ) : (
          groups.map((group) => (
            <div key={group.label}>
              <p className="text-xs font-medium text-gray-400 dark:text-gray-500 px-3 pt-3 pb-1">
                {group.label}
              </p>
              {group.items.map((session) => (
                <div
                  key={session.id}
                  className={`group relative flex items-center gap-1 mx-1 rounded-lg transition-colors ${
                    session.id === activeSessionId
                      ? 'bg-gray-100 dark:bg-gray-700'
                      : 'hover:bg-gray-50 dark:hover:bg-gray-700/50'
                  }`}
                >
                  <button
                    onClick={() => onSelect(session.id)}
                    className="flex-1 flex items-center px-3 py-2 text-left min-w-0"
                    aria-current={session.id === activeSessionId ? 'true' : undefined}
                  >
                    <span className="text-sm text-gray-700 dark:text-gray-300 truncate">
                      {session.title}
                    </span>
                  </button>
                  <button
                    onClick={() => onDelete(session.id)}
                    className="opacity-0 group-hover:opacity-100 shrink-0 w-6 h-6 flex items-center justify-center rounded text-gray-400 hover:text-red-500 dark:hover:text-red-400 transition-opacity mr-1"
                    aria-label={`Delete chat "${session.title}"`}
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" className="w-3.5 h-3.5">
                      <path d="M3 6h18" /><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6" /><path d="M8 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" />
                    </svg>
                  </button>
                </div>
              ))}
            </div>
          ))
        )}
      </div>
    </div>
  );
}
