# Frontend Service

React chat interface for the trip assistant. Hosted on S3 + CloudFront.

## Architecture

```
S3 (static) → CloudFront (CDN) → User Browser → API Gateway
```

## Tech Stack

| Technology | Why |
|------------|-----|
| React 18 | Industry standard, simple component model |
| TypeScript | Catches errors, better IDE support |
| Vite | Modern build tool (CRA is deprecated) |
| Tailwind CSS | Utility-first CSS, fast prototyping |
| fetch API | Built-in, no extra HTTP library needed |

## Key Files

```
frontend/
├── src/
│   ├── main.tsx          # Entry point
│   ├── App.tsx           # Main app component
│   ├── components/
│   │   ├── Chat.tsx      # Chat container (message list + input)
│   │   ├── MessageList.tsx
│   │   ├── MessageBubble.tsx
│   │   └── MessageInput.tsx
│   ├── hooks/
│   │   └── useMessages.ts  # State + API logic
│   ├── api/
│   │   └── client.ts     # API client functions
│   └── types.ts          # TypeScript interfaces
├── public/
├── index.html
├── Dockerfile
├── package.json
├── tsconfig.json
├── vite.config.ts
└── tailwind.config.js
```

## Component Structure

```
App
└── Chat
    ├── MessageList
    │   └── MessageBubble (repeated)
    └── MessageInput
```

## State Management

Using React's built-in `useState` - no Redux needed for this simple app.

```typescript
// hooks/useMessages.ts
interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  category?: string;
}

function useMessages() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const sendMessage = async (question: string) => {
    // Add user message, call API, add assistant response
  };

  return { messages, isLoading, error, sendMessage };
}
```

## API Integration

```typescript
// api/client.ts
const API_URL = import.meta.env.VITE_API_URL;

interface MessageResponse {
  answer: string;
  category: string;
  confidence: number;
  source: string | null;
}

export async function sendMessage(question: string): Promise<MessageResponse> {
  const response = await fetch(`${API_URL}/api/messages`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question }),
  });

  if (!response.ok) {
    throw new Error('Failed to send message');
  }

  return response.json();
}
```

## Types

```typescript
// types.ts
export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  category?: string;
  timestamp: Date;
}

export interface MessageResponse {
  answer: string;
  category: string;
  confidence: number;
  source: string | null;
}
```

## Styling Approach

Tailwind CSS utility classes directly in JSX:

```tsx
// Example: MessageBubble.tsx
function MessageBubble({ message }: { message: Message }) {
  const isUser = message.role === 'user';

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div className={`max-w-xs md:max-w-md px-4 py-2 rounded-lg ${
        isUser
          ? 'bg-blue-500 text-white'
          : 'bg-gray-200 text-gray-800'
      }`}>
        {message.content}
      </div>
    </div>
  );
}
```

## Dockerfile

```dockerfile
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
EXPOSE 80
```

## Dependencies

```json
{
  "dependencies": {
    "react": "^18.3.0",
    "react-dom": "^18.3.0"
  },
  "devDependencies": {
    "@types/react": "^18.3.0",
    "@types/react-dom": "^18.3.0",
    "@vitejs/plugin-react": "^4.3.0",
    "autoprefixer": "^10.4.0",
    "postcss": "^8.4.0",
    "tailwindcss": "^3.4.0",
    "typescript": "^5.5.0",
    "vite": "^5.4.0"
  }
}
```

## Dev Commands

```bash
cd frontend

# Install dependencies
npm install

# Start dev server (http://localhost:5173)
npm run dev

# Build for production
npm run build

# Preview production build locally
npm run preview
```

## Environment Variables

Create `.env` for local development:
```
VITE_API_URL=http://localhost:8000
```

For production (set in build or S3):
```
VITE_API_URL=https://your-api-gateway-url.amazonaws.com
```

## Mobile-First Design

Tailwind's responsive prefixes:
- Default styles = mobile
- `md:` prefix = tablet and up
- `lg:` prefix = desktop

```tsx
<div className="p-2 md:p-4 lg:p-6">
  {/* padding increases on larger screens */}
</div>
```

## Deployment

1. `npm run build` produces `dist/` folder
2. Upload `dist/` contents to S3 bucket
3. CloudFront serves the files with HTTPS
