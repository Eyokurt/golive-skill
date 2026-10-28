# Stage 03: Frontend Readiness

> **Objective**: Ensure client applications (SPA, SSR, mobile web) achieve high performance, reliability, accessibility, and strict adherence to enterprise design standards (Anti-AI-Slop principles) prior to deployment.

---

## 1. Action Items

### A. Production Build & Bundle Optimization
- [ ] **Clean Build**: Production compilation (`npm run build`, `vite build`, or `next build`) must succeed with zero TypeScript compiler errors and zero linter warnings.
- [ ] **Bundle Size & Code Splitting**:
  - The initial critical JavaScript bundle must be < 200 KB gzipped.
  - Apply route-based dynamic loading (`React.lazy`, dynamic `import()`).
  - Eliminate bloated legacy libraries (e.g., substitute Day.js for Moment.js, native methods for Lodash).
- [ ] **Static Asset Caching**:
  - Assets must be compiled with content-based hashes (e.g., `main.a8f29c.js`).
  - Set `Cache-Control: public, max-age=31536000, immutable` on hashed assets, and `Cache-Control: no-cache` on `index.html`.

### B. Resilience & Error Boundaries
- [ ] **Global & Sectional Error Boundaries**: Prevent unhandled JavaScript runtime exceptions from crashing the entire view into a blank white screen. Provide localized error feedback with clear "Retry" actions.
- [ ] **API Fallback & Offline States**: When upstream APIs fail or return 500 errors, the UI must avoid infinite loading spinners and present graceful, actionable error messaging.

### C. Anti-AI-Slop Standards & UI Hygiene
- [ ] **4-State Component Architecture**: Every interactive and data-fetching component must support four distinct states:
  1. *Loading*: Content-sized skeleton placeholders (never jarring oversized spinners).
  2. *Empty*: Informative, action-oriented empty states when datasets are null or empty.
  3. *Error*: Contextual error explanations with direct retry triggers.
  4. *Interactive*: Normal, hover, focus-visible, and disabled states.
- [ ] **Emoji Prohibition**: Absolutely no Unicode emojis (🚀, 💡, 🔥, 🤖) in button chrome, navigation bars, badges, or headers. Use monochromatic vector SVG icon libraries (Lucide, Heroicons, etc.).
- [ ] **Asset & Copy Hygiene**: Zero broken static paths (`/placeholder.svg`); use initials as fallbacks for missing user avatars; use realistic contextual copy instead of `Lorem Ipsum`.
- [ ] **Semantic HTML & Keyboard Accessibility**: Avoid `<div onClick>`; use native `<button>` and `<a>` elements with preserved `:focus-visible` styling for full keyboard navigation.

### D. Web Vitals
- [ ] Satisfy Core Web Vitals targets:
  - LCP (Largest Contentful Paint) < 2.5s
  - CLS (Cumulative Layout Shift) < 0.1
  - INP (Interaction to Next Paint) < 200ms

---

## 2. Exit Gate (Gate 03)

Stage 04 cannot commence until **all** of the following criteria are satisfied:
1. All Stage 03 checklist items are completed in `GOLIVE.md`.
2. Production build succeeds cleanly in CI/local environments and generates production artifacts.
3. Disconnecting network connectivity produces an informative offline/error screen rather than an unhandled blank page.
4. Static scans confirm zero Unicode emojis in button labels, badges, and headers.

---

## 3. Rationale

| Action Item | Why It Is Mandatory |
|:---|:---|
| Code Splitting | Unoptimized 5MB JavaScript bundles take 10+ seconds to download and parse on mobile connections, leading to severe user drop-off. |
| Cache-Control Distinction | Caching `index.html` causes browsers to retain references to old bundles after a release, leading to 404s and broken user sessions. |
| Error Boundaries | Isolates component-level errors (like `undefined.map()`) to specific widgets, preventing entire pages from collapsing. |
| 4-State Components | Prevents jarring layout shifts and layout breaks when data is delayed or empty. |
| Semantic HTML | Ensures compliance with accessibility standards (WCAG) so screen readers and keyboard users can operate the application. |

---

## 4. Common Pitfalls

- ❌ **Aggressively Caching `index.html`**: Preventing clients from discovering updated bundles and trapping users on outdated deployments.
- ❌ **Unterminated Loading Spinners**: Omitting `setIsLoading(false)` inside `catch` or `finally` blocks, leaving users trapped on infinite spinners upon failure.
- ❌ **Leaking Private Secrets in Client Bundles**: Prefixing private API credentials with `VITE_` or `NEXT_PUBLIC_` and baking them into client-facing bundles.
- ❌ **Cumulative Layout Shifts (CLS)**: Failing to set explicit `width` and `height` dimensions on images and dynamic containers, causing page contents to jump during rendering.
