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
- [x] Multi-stage build: node:20-alpine builder + nginx:alpine server

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

- [x] Create `.dockerignore`
  - [x] Exclude `node_modules`, `.env`, `.git`
  - [x] Exclude `coverage/`, `.claude/`

### Task 6.2: Commit
- [x] Commit phase 6 changes

---

## Phase 7: Integration Tests

End-to-end tests with real API (like agent/api integration test phases).

### Task 7.1: Integration test setup
- [x] Create `src/test/integration/` directory
- [x] Create `src/test/integration/setup.ts`
  - [x] Skip if `VITE_API_URL` not set or API not reachable
- [x] Add `"test:integration"` script to `package.json`
  - [x] `vitest run --config vitest.integration.config.ts`
- [x] Create `vitest.integration.config.ts`

### Task 7.2: Integration tests (real API)
- [x] Create `src/test/integration/chat.integration.test.tsx`
  - [x] Test full flow: render Chat → type question → submit → real response appears
  - [x] Test flight question returns flight-related answer
  - [x] Test error handling when API is down
  - [x] Test multiple messages in sequence
- [x] Run `npm test` — 46 tests pass (integration tests skip gracefully without API)

### Task 7.3: Commit
- [x] Commit phase 7 changes

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
- [x] `npm run build` passes with no TypeScript errors
- [x] `npm test` passes (all unit tests)
- [x] `npm run preview` serves the app correctly *(manual)*
- [x] Test on mobile viewport (Chrome DevTools device mode) *(manual)*
- [x] Verify Android + iPhone rendering (responsive check) *(manual)*

### Task 8.3: Commit
- [x] Commit phase 8 changes

---

## Phase 9: Auth Integration (Cognito) ✅

Add login/logout flow using AWS Cognito (deployed in Phase 17 infra).

### Task 9.1: Install Amplify auth packages
- [x] `npm install @aws-amplify/auth @aws-amplify/core`

### Task 9.2: Create auth module
- [x] Create `src/auth/config.ts` — `configureAuth()` reads `VITE_COGNITO_*` env vars
- [x] Create `src/auth/types.ts` — `AuthUser`, `AuthContextType` interfaces
- [x] Create `src/auth/context.ts` — `AuthContext` (separate file for fast refresh)
- [x] Create `src/auth/AuthContext.tsx` — `AuthProvider` with session restore, Hub listener
- [x] Create `src/hooks/useAuth.ts` — convenience hook with error guard
- [x] Create `src/auth/AuthContext.test.tsx` — 7 tests (restore, signIn, signUp, signOut, getToken)

### Task 9.3: Create auth UI components
- [x] Create `src/components/LoginPage.tsx` — email/password form + Google sign-in
- [x] Create `src/components/LoginPage.test.tsx` — 7 tests
- [x] Create `src/components/LogoutButton.tsx` — header sign-out button
- [x] Create `src/components/LogoutButton.test.tsx` — 2 tests

### Task 9.4: Wire auth into app
- [x] Update `src/main.tsx` — call `configureAuth()`, wrap in `<AuthProvider>`
- [x] Update `src/App.tsx` — conditional rendering (loading/login/chat), user email + logout button
- [x] Update `src/api/client.ts` — add `getToken` parameter, `Authorization: Bearer` header
- [x] Update `src/hooks/useMessages.ts` — pass `getToken` from `useAuth`
- [x] Update `.env.example` — add Cognito env vars

### Task 9.5: Update tests
- [x] Update `src/App.test.tsx` — 7 tests (loading, unauthenticated, authenticated states)
- [x] Update `src/api/client.test.ts` — 7 tests (auth header verification)
- [x] Update `src/hooks/useMessages.test.ts` — 9 tests (mock useAuth)
- [x] Update `src/components/Chat.test.tsx` — mock useAuth for useMessages
- [x] Update `src/test/integration/chat.integration.test.tsx` — mock useAuth

### Task 9.6: Verify and commit
- [x] `npm test` — 68 tests pass
- [x] `npm run build` — TypeScript compiles, no errors
- [x] `npm run lint` — ESLint passes
- [x] Commit

---

## Phase 10: Message Feedback (Thumbs Up/Down) ✅

Add thumbs up/down feedback buttons on assistant messages. Thumbs down opens a textarea; "Send feedback" opens a mailto link to oshrats@gmail.com. No backend changes.

### Task 10.1: Add Feedback types
- [x] Add `FeedbackRating`, `Feedback` types and optional `feedback` field to `Message` in `src/types.ts`

### Task 10.2: Add setFeedback to useMessages hook
- [x] New `setFeedback(messageId, feedback)` function updates message state
- [x] Add 2 tests to `src/hooks/useMessages.test.ts` (up rating, down rating with comment)

### Task 10.3: Create MessageFeedback component
- [x] Create `src/components/MessageFeedback.tsx` — thumbs up/down buttons, textarea on down, mailto send
- [x] Create `src/components/MessageFeedback.test.tsx` — 8 tests (render, click up, click down, textarea, mailto, disabled, highlight up, highlight down)

### Task 10.4: Wire feedback through component tree
- [x] Update `MessageBubble` — render `<MessageFeedback>` below assistant messages only
- [x] Update `MessageBubble.test.tsx` — add 2 tests (feedback shown for assistant, not for user)
- [x] Update `MessageList` — accept and pass `onFeedback` prop
- [x] Update `MessageList.test.tsx` — pass `onFeedback` prop
- [x] Update `Chat` — get `setFeedback` from hook, pass to `MessageList`

### Task 10.5: Verify
- [x] `npm test` — 90 tests pass
- [x] `npm run build` — no TypeScript errors

---

## Phase 11: Connect Feedback to API ✅

Replace mailto-based feedback with API calls to the backend feedback endpoint (DynamoDB + SES).

### Task 11.1: Add sendFeedback to API client
- [x] Edit `src/api/client.ts` — add `sendFeedback(feedback, getToken)` (same pattern as sendMessage)
- [x] Add `FeedbackRequest` and `FeedbackResponse` types to `src/types.ts`
- [x] Add 3 tests to `src/api/client.test.ts` (POST request, response parsing, error handling)

### Task 11.2: Update MessageFeedback component
- [x] Remove `mailto:` logic and `import.meta.env.VITE_FEEDBACK_EMAIL`
- [x] Call `sendFeedback()` from API client on thumbs up/down
- [x] Add loading state and inline error handling for the API call
- [x] Use `useAuth` for token

### Task 11.3: Remove VITE_FEEDBACK_EMAIL
- [x] Remove from `.env.example`
- [x] No remaining references in source code

### Task 11.4: Update tests
- [x] Mock `sendFeedback` and `useAuth` in `MessageFeedback.test.tsx`
- [x] Add API call assertions for thumbs up and send feedback button
- [x] Remove mailto assertions (replaced with sendFeedback assertions)
- [x] Add `useAuth` mock to `MessageBubble.test.tsx` and `MessageList.test.tsx`

### Task 11.5: Verify
- [x] `npm test` — 94 tests pass
- [x] `npm run build` — no errors

---

## Phase 12: Confidence Indicator ✅

Display the LLM confidence score as a color-coded pill on assistant messages.

### Task 12.1: Add confidence to Message type and hook
- [x] Add `confidence?: number` to `Message` interface in `src/types.ts`
- [x] Store `response.confidence` in assistant message in `src/hooks/useMessages.ts`

### Task 12.2: Display confidence pill in MessageBubble
- [x] Render percentage pill below assistant messages alongside feedback icons
- [x] Convert 0.0–1.0 to percentage: `Math.round(confidence * 100)`
- [x] Use single-hue blue gradient (accessible, colorblind-safe):
  - >= 80%: strong blue (`bg-blue-100 text-blue-700`)
  - 50–79%: medium blue (`bg-blue-50 text-blue-500`)
  - < 50%: faint blue (`bg-blue-50/50 text-blue-400`)
- [x] Dark mode variants included
- [x] `npx tsc --noEmit` passes

---

## Completion Criteria

- [x] Phase 0 completed (Claude Code setup)
- [x] Phase 1 completed (Project setup & test infrastructure)
- [x] Phase 2 completed (Types & API client with tests)
- [x] Phase 3 completed (State management with tests)
- [x] Phase 4 completed (Components with tests)
- [x] Phase 5 completed (Styling & polish with tests)
- [x] Phase 6 completed (Dockerfile)
- [x] Phase 7 completed (Integration tests with real API)
- [x] Phase 8 completed (Final build & verify)
- [x] Phase 9 completed (Auth integration with Cognito)
- [x] Phase 10 completed (Message feedback — thumbs up/down)
- [x] Phase 11 completed (Connect feedback to API)
- [x] Phase 12 completed (Confidence indicator pill)
- [x] All unit tests passing (94 tests, mocked API)
- [x] Integration tests ready (skip without API)
- [x] `npm run build` passes with no errors
- [x] Ready for S3 + CloudFront deployment

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
│   ├── MessageFeedback.tsx
│   ├── MessageFeedback.test.tsx   # Unit: render + interact + mailto
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
