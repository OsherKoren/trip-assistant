# Frontend Service - Development Tasks

> **Note**: This file tracks development progress and is kept in version control
> as a reference for project workflow. It is NOT part of the production frontend code.
> Each service in the monorepo has its own TASKS.md for independent tracking.

## Overview

Building a React chat interface for the trip assistant with mobile-first design.

**Architecture**: `S3 (static) → CloudFront (CDN) → User Browser → API Gateway`

---

## Phase 0: Claude Code Setup ✅

Configure Claude Code skills and hooks for the frontend service.

- [x] Create `frontend/.claude/skills/review-react/SKILL.md`
- [x] Create `frontend/.claude/skills/review-react/references/checklist.md`
- [x] Skill covers: React patterns, TypeScript, Tailwind, accessibility, mobile-first
- [x] Add `frontend/` detection to `.claude/hooks/pre-push-review.sh`
- [x] Hook now suggests `/review-react` when frontend files change
- [x] Create `frontend/.claude/settings.local.json`
- [x] Allow WebFetch for react.dev, tailwindcss.com, vitejs.dev

---

## Phase 1: Project Setup & Test Infrastructure ✅

Initialize Vite project, Tailwind CSS, and testing framework.

### Task 1.1: Initialize Vite + React 19 + TypeScript project
- [x] Run `npm create vite@latest . -- --template react-ts`
- [x] Verify React 19 is installed (`react@^19.2.0` in package.json)
- [x] Verify `npm install` and `npm run build` work

### Task 1.2: Install and configure Tailwind CSS v4
- [x] Install: `npm install tailwindcss @tailwindcss/vite`
- [x] Add Tailwind Vite plugin to `vite.config.ts`
- [x] Replace `src/index.css` content with `@import 'tailwindcss'`
- [x] No `tailwind.config.js`, no `postcss.config.js`, no `autoprefixer` needed
- [x] Verify Tailwind works: utility classes render in build output

### Task 1.3: Install and configure Vitest + Testing Library
- [x] Install dev dependencies: vitest, @testing-library/react, @testing-library/jest-dom, @testing-library/user-event, jsdom
- [x] Add test config to `vite.config.ts` (using `vitest/config` for type safety)
  - [x] Set environment: `jsdom`
  - [x] Set globals: `true`
- [x] Create `src/test/setup.ts` with `@testing-library/jest-dom` import
- [x] Add `"test": "vitest run"` and `"test:watch": "vitest"` to package.json
- [x] Exclude test files from `tsconfig.app.json` (avoid tsc errors on test globals)
- [x] Create smoke test: `src/App.test.tsx` — render App, verify it mounts
- [x] Run `npm test` (1 test passed)

### Task 1.4: Set up environment variables
- [x] Create `.env` with `VITE_API_URL=http://localhost:8000`
- [x] Add `.env` to `.gitignore`
- [x] Create `.env.example` with placeholder

### Task 1.5: Clean up Vite defaults
- [x] Remove default Vite boilerplate (App.css, react.svg, vite.svg, README.md)
- [x] Set up minimal `App.tsx` shell with Tailwind classes
- [x] Run `npm run build` (passed)
- [x] Run `npm test` (1 test passed)

**Actual versions**: React 19.2.0, Vite 7.3.1, TypeScript 5.9.3, Tailwind 4.2.0, Vitest 4.0.18

---

## Phase 2: Types and API Client

Define TypeScript interfaces and create the API client function.

### Task 2.1: Define TypeScript types
- [ ] Create `src/types.ts`

```typescript
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

### Task 2.2: Create API client
- [ ] Create `src/api/client.ts`

```typescript
const API_URL = import.meta.env.VITE_API_URL;

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

### Task 2.3: Unit tests for API client
- [ ] Create `src/api/client.test.ts`
  - [ ] Test `sendMessage` sends correct POST request (mock fetch)
  - [ ] Test `sendMessage` returns parsed MessageResponse
  - [ ] Test `sendMessage` throws on non-OK response (400, 500)
  - [ ] Test `sendMessage` throws on network error
  - [ ] Test request body contains `{ question }` JSON
- [ ] Run `npm test` (must pass)

**Mocking pattern** (like `monkeypatch` in Python):
```typescript
// vi.fn() replaces real fetch with a mock
globalThis.fetch = vi.fn().mockResolvedValue({
  ok: true,
  json: () => Promise.resolve(mockResponse),
});
```

---

## Phase 3: State Management

Create the custom hook that manages messages, loading, and errors.

### Task 3.1: Create useMessages hook
- [ ] Create `src/hooks/useMessages.ts`

```typescript
function useMessages() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const sendMessage = async (question: string) => {
    // 1. Add user message to state
    // 2. Set isLoading = true, clear error
    // 3. Call API client
    // 4. Add assistant response to state
    // 5. Handle errors, set isLoading = false
  };

  return { messages, isLoading, error, sendMessage };
}
```

### Task 3.2: Unit tests for useMessages hook
- [ ] Create `src/hooks/useMessages.test.ts`
  - [ ] Test initial state: empty messages, not loading, no error
  - [ ] Test `sendMessage` adds user message to state
  - [ ] Test `sendMessage` sets isLoading while waiting
  - [ ] Test `sendMessage` adds assistant response after API call
  - [ ] Test `sendMessage` sets error on API failure
  - [ ] Test `sendMessage` clears previous error on new message
  - [ ] Test messages have unique IDs
  - [ ] Test messages have timestamps
- [ ] Run `npm test` (must pass)

**Hook testing pattern** (like testing a Python class with state):
```typescript
import { renderHook, act } from '@testing-library/react';

const { result } = renderHook(() => useMessages());

await act(async () => {
  await result.current.sendMessage('What car did we rent?');
});

expect(result.current.messages).toHaveLength(2); // user + assistant
```

---

## Phase 4: Components

Build UI components with unit tests for each.

### Task 4.1: Create MessageBubble component
- [ ] Create `src/components/MessageBubble.tsx`
  - [ ] User messages: right-aligned, blue background, white text
  - [ ] Assistant messages: left-aligned, gray background, dark text
  - [ ] Responsive: `max-w-xs` on mobile, `max-w-md` on `md:` screens
- [ ] Create `src/components/MessageBubble.test.tsx`
  - [ ] Test renders user message content
  - [ ] Test renders assistant message content
  - [ ] Test user message is right-aligned (has `justify-end` class)
  - [ ] Test assistant message is left-aligned (has `justify-start` class)
- [ ] Run `npm test` (must pass)

### Task 4.2: Create MessageList component
- [ ] Create `src/components/MessageList.tsx`
  - [ ] Render list of `MessageBubble` components
  - [ ] Auto-scroll to bottom on new messages
  - [ ] Show loading indicator when `isLoading` is true
- [ ] Create `src/components/MessageList.test.tsx`
  - [ ] Test renders multiple messages
  - [ ] Test renders empty state when no messages
  - [ ] Test shows loading indicator when isLoading=true
  - [ ] Test hides loading indicator when isLoading=false
- [ ] Run `npm test` (must pass)

### Task 4.3: Create MessageInput component
- [ ] Create `src/components/MessageInput.tsx`
  - [ ] Text input + send button
  - [ ] Submit on Enter key or button click
  - [ ] Disable input while loading
  - [ ] Clear input after sending
  - [ ] Accessible: label on input, button type="submit"
- [ ] Create `src/components/MessageInput.test.tsx`
  - [ ] Test renders input and send button
  - [ ] Test calls onSend with input value on submit
  - [ ] Test clears input after submit
  - [ ] Test submits on Enter key press
  - [ ] Test disables input and button when disabled=true
  - [ ] Test does not submit empty input
- [ ] Run `npm test` (must pass)

**Component testing pattern** (render + interact + assert):
```typescript
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

render(<MessageInput onSend={mockFn} disabled={false} />);

const input = screen.getByRole('textbox');
await userEvent.type(input, 'Hello');
await userEvent.click(screen.getByRole('button', { name: /send/i }));

expect(mockFn).toHaveBeenCalledWith('Hello');
```

### Task 4.4: Create Chat container component
- [ ] Create `src/components/Chat.tsx`
  - [ ] Wire `useMessages` hook
  - [ ] Compose `MessageList` + `MessageInput`
  - [ ] Display error messages if present
- [ ] Create `src/components/Chat.test.tsx`
  - [ ] Test renders MessageList and MessageInput
  - [ ] Test displays error message when error exists
  - [ ] Test sends message through the full flow (mock API)
- [ ] Run `npm test` (must pass)

### Task 4.5: Wire App component
- [ ] Update `src/App.tsx` to render `Chat`
  - [ ] Add app title/header
  - [ ] Full-height layout for mobile chat experience
- [ ] Update `src/App.test.tsx`
  - [ ] Test renders app header
  - [ ] Test renders Chat component
- [ ] Run `npm test` (must pass)
- [ ] Run `npm run build` (must pass)

---

## Phase 5: Styling and Polish

Refine mobile-first layout and add loading/error UX.

### Task 5.1: Mobile-first responsive layout
- [ ] Full viewport height chat layout (`h-dvh` or `h-screen`)
- [ ] Sticky input at bottom
- [ ] Scrollable message area
- [ ] Touch-friendly button sizes (min 44px tap targets)

### Task 5.2: Loading and error states
- [ ] Typing indicator / spinner while waiting for response
- [ ] Error message display (inline, dismissible)
- [ ] Empty state: welcome message when no messages yet

### Task 5.3: Styling tests
- [ ] Create/update tests for visual states:
  - [ ] Test welcome message shown when no messages
  - [ ] Test typing indicator visible during loading
  - [ ] Test error message displayed and dismissible
- [ ] Run `npm test` (must pass)
- [ ] Run `npm run build` (must pass)

---

## Phase 6: Dockerfile

Create production Docker image.

### Task 6.1: Create Dockerfile
- [ ] Multi-stage build: node:20-alpine builder + nginx:alpine server

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

- [ ] Create `.dockerignore`
  - [ ] Exclude `node_modules`, `.env`, `.git`
  - [ ] Exclude `coverage/`, `.claude/`

---

## Phase 7: Integration Tests

End-to-end tests with real API (like agent/api integration test phases).

### Task 7.1: Integration test setup
- [ ] Create `src/test/integration/` directory
- [ ] Create `src/test/integration/setup.ts`
  - [ ] Skip if `VITE_API_URL` not set or API not reachable
- [ ] Add `"test:integration"` script to `package.json`
  - [ ] `vitest run --config vitest.integration.config.ts`

### Task 7.2: Integration tests (real API)
- [ ] Create `src/test/integration/chat.integration.test.tsx`
  - [ ] Test full flow: render Chat → type question → submit → real response appears
  - [ ] Test flight question returns flight-related answer
  - [ ] Test error handling when API is down
  - [ ] Test multiple messages in sequence
- [ ] Run `npm run test:integration` (must pass with API running)

**Integration test pattern** (like Python `@pytest.mark.integration`):
```typescript
// Uses real API, no mocks
// Requires: API running at VITE_API_URL
describe.skipIf(!import.meta.env.VITE_API_URL)('Integration', () => {
  it('sends a real question and gets an answer', async () => {
    render(<Chat />);
    await userEvent.type(screen.getByRole('textbox'), 'What car did we rent?');
    await userEvent.click(screen.getByRole('button', { name: /send/i }));

    // Wait for real API response
    await waitFor(() => {
      expect(screen.getByText(/sixt|car/i)).toBeInTheDocument();
    }, { timeout: 15000 });
  });
});
```

---

## Phase 8: Build and Verify

Final validation before PR.

### Task 8.1: Final checks
- [ ] `npm run build` passes with no TypeScript errors
- [ ] `npm test` passes (all unit tests)
- [ ] `npm run preview` serves the app correctly
- [ ] Test on mobile viewport (Chrome DevTools device mode)
- [ ] Verify Android + iPhone rendering (responsive check)

---

## Completion Criteria

- [x] Phase 0 completed (Claude Code setup)
- [ ] Phase 1 completed (Project setup & test infrastructure)
- [ ] Phase 2 completed (Types & API client with tests)
- [ ] Phase 3 completed (State management with tests)
- [ ] Phase 4 completed (Components with tests)
- [ ] Phase 5 completed (Styling & polish with tests)
- [ ] Phase 6 completed (Dockerfile)
- [ ] Phase 7 completed (Integration tests with real API)
- [ ] Phase 8 completed (Final build & verify)
- [ ] All unit tests passing (mocked API)
- [ ] Integration tests ready (skip without API)
- [ ] `npm run build` passes with no errors
- [ ] Ready for S3 + CloudFront deployment

---

## Test Organization

```
src/
├── api/
│   ├── client.ts
│   └── client.test.ts            # Unit: mock fetch
├── hooks/
│   ├── useMessages.ts
│   └── useMessages.test.ts       # Unit: mock API client
├── components/
│   ├── MessageBubble.tsx
│   ├── MessageBubble.test.tsx     # Unit: render + assert
│   ├── MessageList.tsx
│   ├── MessageList.test.tsx       # Unit: render + assert
│   ├── MessageInput.tsx
│   ├── MessageInput.test.tsx      # Unit: render + interact + assert
│   ├── Chat.tsx
│   └── Chat.test.tsx              # Unit: mock API, full component
├── App.tsx
├── App.test.tsx                   # Unit: smoke test
└── test/
    ├── setup.ts                   # Test setup (DOM matchers)
    └── integration/
        ├── setup.ts               # Skip if no API
        └── chat.integration.test.tsx  # Real API tests
```

## Running Tests

```bash
# All unit tests (fast, mocked, no API needed)
npm test

# Watch mode during development
npm run test -- --watch

# Integration tests (requires API at VITE_API_URL)
npm run test:integration

# Build check (TypeScript compilation)
npm run build
```
