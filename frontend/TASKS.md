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
- [x] Create `src/types.ts`

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
- [x] Create `src/api/client.ts`

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
- [x] Create `src/api/client.test.ts`
  - [x] Test `sendMessage` sends correct POST request (mock fetch)
  - [x] Test `sendMessage` returns parsed MessageResponse
  - [x] Test `sendMessage` throws on non-OK response (400, 500)
  - [x] Test `sendMessage` throws on network error
  - [x] Test request body contains `{ question }` JSON
- [x] Run `npm test` (must pass)

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
- [x] Create `src/hooks/useMessages.ts`

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
- [x] Create `src/hooks/useMessages.test.ts`
  - [x] Test initial state: empty messages, not loading, no error
  - [x] Test `sendMessage` adds user message to state
  - [x] Test `sendMessage` sets isLoading while waiting
  - [x] Test `sendMessage` adds assistant response after API call
  - [x] Test `sendMessage` sets error on API failure
  - [x] Test `sendMessage` clears previous error on new message
  - [x] Test messages have unique IDs
  - [x] Test messages have timestamps
- [x] Run `npm test` (must pass)

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
- [x] Create `src/components/MessageBubble.tsx`
  - [x] User messages: right-aligned, blue background, white text
  - [x] Assistant messages: left-aligned, gray background, dark text
  - [x] Responsive: `max-w-xs` on mobile, `max-w-md` on `md:` screens
- [x] Create `src/components/MessageBubble.test.tsx`
  - [x] Test renders user message content
  - [x] Test renders assistant message content
  - [x] Test user message is right-aligned (has `justify-end` class)
  - [x] Test assistant message is left-aligned (has `justify-start` class)
- [x] Run `npm test` (must pass)

### Task 4.2: Create MessageList component
- [x] Create `src/components/MessageList.tsx`
  - [x] Render list of `MessageBubble` components
  - [x] Auto-scroll to bottom on new messages
  - [x] Show loading indicator when `isLoading` is true
- [x] Create `src/components/MessageList.test.tsx`
  - [x] Test renders multiple messages
  - [x] Test renders empty state when no messages
  - [x] Test shows loading indicator when isLoading=true
  - [x] Test hides loading indicator when isLoading=false
- [x] Run `npm test` (must pass)

### Task 4.3: Create MessageInput component
- [x] Create `src/components/MessageInput.tsx`
  - [x] Text input + send button
  - [x] Submit on Enter key or button click
  - [x] Disable input while loading
  - [x] Clear input after sending
  - [x] Accessible: label on input, button type="submit"
- [x] Create `src/components/MessageInput.test.tsx`
  - [x] Test renders input and send button
  - [x] Test calls onSend with input value on submit
  - [x] Test clears input after submit
  - [x] Test submits on Enter key press
  - [x] Test disables input and button when disabled=true
  - [x] Test does not submit empty input
- [x] Run `npm test` (must pass)

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
- [x] Create `src/components/Chat.tsx`
  - [x] Wire `useMessages` hook
  - [x] Compose `MessageList` + `MessageInput`
  - [x] Display error messages if present
- [x] Create `src/components/Chat.test.tsx`
  - [x] Test renders MessageList and MessageInput
  - [x] Test displays error message when error exists
  - [x] Test sends message through the full flow (mock API)
- [x] Run `npm test` (must pass)

### Task 4.5: Wire App component
- [x] Update `src/App.tsx` to render `Chat`
  - [x] Add app title/header
  - [x] Full-height layout for mobile chat experience
- [x] Update `src/App.test.tsx`
  - [x] Test renders app header
  - [x] Test renders Chat component
- [x] Run `npm test` (must pass)
- [x] Run `npm run build` (must pass)

---

## Phase 5: Styling and Polish

Refine mobile-first layout, loading/error UX, and dark/light mode.

### Task 5.1: Mobile-first responsive layout
- [x] Full viewport height chat layout (`h-dvh` or `h-screen`)
- [x] Sticky input at bottom
- [x] Scrollable message area
- [x] Touch-friendly button sizes (min 44px tap targets)

### Task 5.2: Loading and error states
- [x] Typing indicator / spinner while waiting for response
- [x] Error message display (inline, dismissible)
- [x] Empty state: welcome message when no messages yet

### Task 5.3: Styling tests
- [x] Create/update tests for visual states:
  - [x] Test welcome message shown when no messages
  - [x] Test typing indicator visible during loading
  - [x] Test error message displayed and dismissible
- [x] Run `npm test` (must pass)
- [x] Run `npm run build` (must pass)

### Task 5.4: Dark/light mode
- [x] Enable class-based dark mode in `src/index.css` (`@variant dark`)
- [x] Add flash-prevention script in `index.html`
- [x] Mock `matchMedia` in `src/test/setup.ts`
- [x] Create `useTheme` hook with localStorage persistence + system preference fallback
- [x] Create `useTheme.test.ts` (5 tests)
- [x] Create `ThemeToggle` component with sun/moon SVG icons
- [x] Create `ThemeToggle.test.tsx` (3 tests)
- [x] Wire theme toggle in `App.tsx` header
- [x] Add toggle assertion in `App.test.tsx`
- [x] Add `dark:` variants to all components (MessageBubble, MessageList, MessageInput, Chat)
- [x] Run `npm test` — 42 tests pass
- [x] Run `npm run build` — no TypeScript errors

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

### Task 8.1: GitHub Actions CI workflow
- [x] Create `.github/workflows/frontend-ci.yml`
  - [x] Trigger on `frontend/**` changes (push + PR)
  - [x] Job 0: Detect changes (dorny/paths-filter)
  - [x] Job 1: Unit tests (Node 20 + 22 matrix, `npm test`)
  - [x] Job 2: Build check (`npm run build`)
  - [x] Job 3: Code quality (ESLint via `npm run lint`)
- [x] Follows same pattern as `agent-ci.yml` and `api-ci.yml`

### Task 8.2: Final checks
- [ ] `npm run build` passes with no TypeScript errors
- [ ] `npm test` passes (all unit tests)
- [ ] `npm run preview` serves the app correctly
- [ ] Test on mobile viewport (Chrome DevTools device mode)
- [ ] Verify Android + iPhone rendering (responsive check)

---

## Completion Criteria

- [x] Phase 0 completed (Claude Code setup)
- [x] Phase 1 completed (Project setup & test infrastructure)
- [x] Phase 2 completed (Types & API client with tests)
- [x] Phase 3 completed (State management with tests)
- [x] Phase 4 completed (Components with tests)
- [x] Phase 5 completed (Styling & polish with tests)
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
