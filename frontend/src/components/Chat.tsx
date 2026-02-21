import { useMessages } from '../hooks/useMessages';
import { MessageList } from './MessageList';
import { MessageInput } from './MessageInput';

export function Chat() {
  const { messages, isLoading, error, sendMessage } = useMessages();

  return (
    <div className="flex flex-col h-full">
      <MessageList messages={messages} isLoading={isLoading} />
      {error && (
        <div role="alert" className="mx-4 mb-2 px-4 py-2 bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400 rounded-lg text-sm">
          {error}
        </div>
      )}
      <MessageInput onSend={sendMessage} disabled={isLoading} />
    </div>
  );
}
