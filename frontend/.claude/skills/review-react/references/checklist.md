# React/TypeScript/Tailwind Best Practices Checklist

## Component Patterns

- [ ] **Components are small and focused** - One responsibility per component
- [ ] **Business logic extracted to hooks** - Components handle rendering only
- [ ] **Props are typed with interfaces** - Not inline types or `any`
- [ ] **Default exports avoided** - Use named exports for better refactoring
- [ ] **Event handlers prefixed with `handle`** - `handleSubmit`, `handleClick`
- [ ] **Conditional rendering is clean** - Early returns or ternary, not nested `&&`

## Hooks

- [ ] **Custom hooks prefixed with `use`** - `useMessages`, `useScrollToBottom`
- [ ] **useEffect dependencies are correct** - No missing or extra dependencies
- [ ] **useEffect has cleanup** - Unsubscribe, cancel requests, clear timers
- [ ] **useState for simple state** - No Redux/context for local component state
- [ ] **Hooks return typed objects** - Explicit return type interface

## TypeScript

- [ ] **No `any` types** - Use specific types or `unknown` with type guards
- [ ] **Interfaces for object shapes** - `interface Message { ... }`
- [ ] **Union types for variants** - `role: 'user' | 'assistant'`
- [ ] **Function return types explicit** - Especially for hooks and API calls
- [ ] **Props interfaces named `{Component}Props`** - `MessageBubbleProps`
- [ ] **Enums avoided** - Use union types or `as const` objects instead

## State Management

- [ ] **Immutable updates** - Spread operator or functional updates
- [ ] **State co-located** - State lives in the closest common ancestor
- [ ] **Derived state not stored** - Compute from existing state, don't duplicate
- [ ] **Loading/error/data pattern** - All async state has three states
- [ ] **Optimistic updates where appropriate** - Add user message before API responds

## API Integration

- [ ] **API calls in hooks, not components** - Separation of concerns
- [ ] **Error handling for all fetch calls** - try/catch with user-friendly messages
- [ ] **Loading state managed** - Show indicators during async operations
- [ ] **Response types validated** - TypeScript interfaces match API response
- [ ] **Base URL from environment** - `import.meta.env.VITE_API_URL`

## Accessibility (a11y)

- [ ] **Semantic HTML elements** - `<button>`, `<form>`, `<main>`, `<nav>`
- [ ] **Form inputs have labels** - `<label>` or `aria-label`
- [ ] **Images have alt text** - Descriptive or empty for decorative
- [ ] **Keyboard navigation works** - Tab order, Enter/Space to activate
- [ ] **Focus management** - Auto-focus input, focus trap in modals
- [ ] **ARIA roles where needed** - `role="log"` for message list, `role="status"` for loading
- [ ] **Color contrast sufficient** - WCAG AA minimum (4.5:1 for text)
- [ ] **Screen reader text** - `sr-only` class for visual-only context

## Mobile-First Design

- [ ] **Default styles are mobile** - No breakpoint prefix = phone
- [ ] **Breakpoints scale up** - `md:` for tablet, `lg:` for desktop
- [ ] **Touch targets min 44px** - Buttons, links, interactive elements
- [ ] **No horizontal scroll** - Content fits viewport width
- [ ] **Viewport meta tag set** - `<meta name="viewport" content="width=device-width, initial-scale=1">`
- [ ] **Full-height layout** - `h-dvh` or `h-screen` for chat apps
- [ ] **Sticky input** - Message input fixed at bottom on mobile
- [ ] **Scroll behavior** - Auto-scroll to new messages

## Tailwind CSS v4

- [ ] **CSS-first config** - No `tailwind.config.js`; use `@theme` directive in CSS
- [ ] **Vite plugin used** - `@tailwindcss/vite` in `vite.config.ts`, not PostCSS
- [ ] **Import correct** - `@import 'tailwindcss'` (not `@tailwind base/components/utilities`)
- [ ] **Utility classes in JSX** - No separate CSS files unless necessary
- [ ] **Responsive prefixes correct** - Mobile-first (`md:` not `sm:` for overrides)
- [ ] **No magic numbers** - Use Tailwind spacing scale (`p-4` not `p-[17px]`)
- [ ] **Repeated patterns extracted** - Component or `@apply` for reused styles
- [ ] **v4 class names** - Use `ring-3` not `ring` for 3px, `bg-blue-500/50` not `bg-opacity-*`

## Performance

- [ ] **Lists have stable keys** - `key={item.id}` not `key={index}`
- [ ] **Large lists virtualized** - If > 100 items, consider virtualization
- [ ] **Memoization only when needed** - Don't prematurely optimize
- [ ] **Images optimized** - Correct size, lazy loading for off-screen
- [ ] **Bundle size checked** - No unnecessary large dependencies
