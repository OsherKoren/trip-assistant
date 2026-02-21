---
name: review-react
description: |
  Review React/TypeScript frontend code for best practices and suggest refactorings.
  Use when: (1) After implementing new components or hooks, (2) Before creating
  a PR, (3) User requests code review, (4) Checking compliance with React/TypeScript
  patterns, (5) Reviewing accessibility and mobile-first design.
  Reviews recent changes by default, or specific files if requested.
  Complements the root review-python skill (which should NOT run on frontend code).
---

# React/TypeScript Code Review Skill

Automated code review for React + TypeScript + Tailwind CSS frontend implementations.

## What This Skill Does

1. **Analyzes recent changes** - Reviews git diff or specified files in `frontend/`
2. **Checks React patterns** - Component structure, hooks usage, state management
3. **Checks TypeScript** - Type safety, interfaces, no `any` types
4. **Checks accessibility** - Semantic HTML, ARIA attributes, keyboard navigation
5. **Checks mobile-first** - Responsive design, touch targets, viewport handling
6. **Suggests refactorings** - Provides specific code improvements

---

## Review Workflow

### 1. Identify Scope

By default, review recent uncommitted changes:
```bash
git diff --name-only -- frontend/        # Changed files
git diff --staged --name-only -- frontend/  # Staged files
```

Or review specific files if the user requests it.

### 2. Run Checklists

Apply all checklists from the `references/` directory:

1. **`references/checklist.md`** - React, TypeScript, Tailwind, accessibility patterns

### 3. Provide Feedback

For each issue found, provide:
- **What**: The specific problem
- **Why**: Which principle or pattern it violates
- **Fix**: Concrete code suggestion (before/after)

### 4. Suggest Refactorings

Look for broader refactoring opportunities:
- Components doing too much (split into smaller components)
- Business logic in components (extract to hooks)
- Inline styles or repeated Tailwind classes (extract patterns)
- Missing error boundaries or loading states
- Accessibility gaps

---

## Common Anti-Patterns to Catch

### State & Props

```tsx
// WRONG - Direct state mutation
const [items, setItems] = useState<Item[]>([]);
items.push(newItem);  // Mutates array!
setItems(items);

// CORRECT - Immutable update
setItems(prev => [...prev, newItem]);
```

```tsx
// WRONG - Object as default prop causes re-renders
function Chat({ options = {} }) { ... }

// CORRECT - Stable default
const DEFAULT_OPTIONS = {};
function Chat({ options = DEFAULT_OPTIONS }) { ... }
```

### Hooks

```tsx
// WRONG - Missing dependency in useEffect
useEffect(() => {
  fetchData(userId);
}, []);  // userId missing from deps!

// CORRECT
useEffect(() => {
  fetchData(userId);
}, [userId]);
```

```tsx
// WRONG - Business logic inside component
function Chat() {
  const [messages, setMessages] = useState([]);
  const sendMessage = async (q: string) => {
    const res = await fetch(...);  // API logic in component!
  };
}

// CORRECT - Extract to custom hook
function Chat() {
  const { messages, sendMessage } = useMessages();  // Clean separation
}
```

### TypeScript

```tsx
// WRONG - Using 'any'
function handleResponse(data: any) { ... }

// CORRECT - Specific type
function handleResponse(data: MessageResponse) { ... }
```

```tsx
// WRONG - Missing return type
function useMessages() { ... }

// CORRECT - Explicit return type
interface UseMessagesReturn {
  messages: Message[];
  isLoading: boolean;
  error: string | null;
  sendMessage: (question: string) => Promise<void>;
}

function useMessages(): UseMessagesReturn { ... }
```

### Accessibility

```tsx
// WRONG - Click handler on div
<div onClick={handleSubmit}>Send</div>

// CORRECT - Semantic button
<button onClick={handleSubmit} type="submit">Send</button>
```

```tsx
// WRONG - No label on input
<input type="text" placeholder="Ask a question..." />

// CORRECT - Accessible input
<label htmlFor="message-input" className="sr-only">Ask a question</label>
<input id="message-input" type="text" placeholder="Ask a question..." />
```

### Mobile-First

```tsx
// WRONG - Desktop-first (overriding large styles for small)
<div className="p-6 sm:p-4 xs:p-2">

// CORRECT - Mobile-first (default is mobile, scale up)
<div className="p-2 md:p-4 lg:p-6">
```

```tsx
// WRONG - Small tap targets
<button className="p-1 text-xs">Send</button>

// CORRECT - Touch-friendly (min 44px)
<button className="p-3 min-h-[44px] min-w-[44px]">Send</button>
```

### Tailwind v4

```css
/* WRONG - Tailwind v3 setup */
@tailwind base;
@tailwind components;
@tailwind utilities;

/* CORRECT - Tailwind v4 setup */
@import 'tailwindcss';
```

```tsx
// WRONG - Tailwind v3 opacity classes (removed in v4)
<div className="bg-blue-500 bg-opacity-50">

// CORRECT - Tailwind v4 color opacity syntax
<div className="bg-blue-500/50">
```

---

## Review Output Format

```markdown
## React Review: `<file or scope>`

### Good Practices
- <what's already done well>

### Issues Found
- **[REACT]** Component handles both data fetching and rendering — extract hook
- **[TYPESCRIPT]** `any` type used in handler — use `MessageResponse`
- **[A11Y]** Form input missing label — add `<label>` or `aria-label`
- **[MOBILE]** Button tap target too small — add `min-h-[44px]`
- **[TAILWIND]** Repeated class pattern — extract to component or `@apply`

### Refactoring Opportunities
- <broader improvement suggestions with before/after code>

### References
- See `references/checklist.md` > Component Patterns
```

---

## When NOT to Review

- Changes to non-frontend files (Python, YAML, configs)
- Trivial changes (typos, comment fixes)
- Auto-generated code or lock files (`package-lock.json`)
- Changes outside `frontend/` directory

This skill focuses on **React/TypeScript/Tailwind quality** — delegate Python concerns to `review-python`, `review-langgraph`, or `review-fastapi`.

---

## Process

1. **Determine scope**: Recent changes or specified files in `frontend/`
2. **Read relevant files**: Use Read tool for each file in scope
3. **Check against patterns**: Review using checklist
4. **Generate review**: Structured output with specific fixes
5. **Offer to apply fixes**: Ask if user wants Claude to refactor

---

## Quick Commands

After running the skill, offer:

```
Would you like me to:
1. Apply the suggested refactorings
2. Fix accessibility issues
3. Review a different file/scope
4. Run the build to verify changes
```
