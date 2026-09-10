# Course: Web Development & Frontend Frameworks
Domain: Technologies
Sub-Domain: Web Development & ReactJS
Course ID: 150

## Module: ReactJS Components, State Management & Responsive Layouts
Source: Modern Web Development Curriculum — Modules 3 to 6
Section: Component Architecture, React Hooks & CSS Systems

### 1. React Architecture & Virtual DOM
React uses a declarative component model to construct user interfaces.
- **Virtual DOM**: React maintains an in-memory representation of the real DOM. When component state changes, React computes the minimal set of DOM mutations via a reconciliation diffing algorithm, avoiding expensive direct browser reflows and repaints.
- **JSX (JavaScript XML)**: Syntactic extension that compiles to `React.createElement()` function calls.

### 2. React Hooks
- `useState(initialState)`: Declares state variables in functional components. Returns `[state, setState]` pair. Updates schedule a re-render.
- `useEffect(effectFn, deps)`: Handles side effects (data fetching, DOM listeners, timers).
  - No dependency array: Runs after every render.
  - Empty array `[]`: Runs once on mount; return cleanup function runs on unmount.
  - `[dep1, dep2]`: Runs only when specified dependencies mutate.
- `useCallback(fn, deps)`: Returns a memoized callback instance, preventing child re-renders when passing functions.
- `useMemo(computeFn, deps)`: Returns a memoized computed value, preventing costly recalculations across renders.

### 3. CSS Layout Systems: Flexbox vs Grid
- **CSS Flexbox (One-Dimensional)**:
  - Designed for laying out items in a single dimension (as either a row or a column).
  - Main axis properties: `justify-content` (flex-start, center, space-between, space-around).
  - Cross axis properties: `align-items` (stretch, center, flex-start, flex-end).
  - Flex items: `flex-grow`, `flex-shrink`, `flex-basis`.
- **CSS Grid (Two-Dimensional)**:
  - Designed for complex simultaneous row and column placement.
  - Container properties: `grid-template-columns`, `grid-template-rows`, `gap`.
  - Item placement: `grid-column: 1 / 3`, `grid-row: span 2`.

### 4. RESTful API Principles
- Uniform Interface, Statelessness, Cacheability, Client-Server Separation, Layered System.
- Standard HTTP verbs: `GET` (retrieve), `POST` (create), `PUT` (full update), `PATCH` (partial update), `DELETE` (remove).
- HTTP Status Codes: `200 OK`, `201 Created`, `400 Bad Request`, `401 Unauthorized`, `403 Forbidden`, `404 Not Found`, `500 Internal Server Error`.
