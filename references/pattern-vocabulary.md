# Pattern Vocabulary

Common code patterns detected across repositories during analysis.

## Naming Conventions

| Convention | Example | Common In |
|------------|---------|-----------|
| `snake_case` | `get_user_data` | Python, Ruby, Go |
| `camelCase` | `getUserData` | JavaScript, TypeScript, Java |
| `PascalCase` | `GetUserData` | Classes, Components, Types |
| `kebab-case` | `get-user-data` | CSS, URLs, file names |

## Architecture Patterns

| Pattern | Description | Quality Signal |
|---------|-------------|----------------|
| **Modular** | Feature-based folders (auth/, users/) | High — clear boundaries |
| **Layered** | Controllers/services/repos separation | High — separation of concerns |
| **Flat** | All files in one directory | Low — doesn't scale |
| **Library** | Exported functions, no entry point | Context-dependent |
| **CLI** | Command-line tool structure | Context-dependent |
| **Monorepo** | Multiple packages in one repo | High — shared code |
| **Microservices** | Separate services | High — independent deploy |

## Error Handling Patterns

| Pattern | Example | Quality |
|---------|---------|---------|
| **Try/Catch** | `try { ... } catch (e) { ... }` | Standard |
| **Result Type** | `Result<T, E>` / `Either<L, R>` | High — explicit |
| **Error Boundary** | React error boundaries | High — UI resilience |
| **Error Codes** | Return numeric codes | Low — unclear |
| **Null Returns** | Return null on error | Low — silent failures |

## Authentication Patterns

| Pattern | Description | Security |
|---------|-------------|----------|
| **JWT** | Stateless tokens | Medium — needs rotation |
| **Sessions** | Server-side storage | High — revocable |
| **OAuth2** | Third-party auth | High — delegated |
| **API Keys** | Static tokens | Low — hard to rotate |
| **Passkeys** | WebAuthn/FIDO2 | Highest — phishing-resistant |

## Validation Patterns

| Pattern | Example | Quality |
|---------|---------|---------|
| **Schema (Zod/Joi)** | `z.object({ name: z.string() })` | High — type-safe |
| **Decorator** | `@IsString()` class-validator | Medium — verbose |
| **Manual** | `if (!name) throw ...` | Low — error-prone |
| **Type Narrowing** | TypeScript type guards | High — compile-time |

## State Management Patterns

| Pattern | Example | Scalability |
|---------|---------|-------------|
| **Context/Provider** | React Context | Low — re-render issues |
| **Redux/Zustand** | Global store | Medium — boilerplate |
| **Signals** | Solid/Svelte signals | High — fine-grained |
| **Server State** | React Query/SWR | High — caching built-in |
| **CRDT** | Yjs/Automerge | Highest — collaborative |

## Anti-Patterns

| Pattern | Why It's Bad | Detection |
|---------|-------------|-----------|
| **God File** | >500 lines, hard to maintain | File length check |
| **God Class** | >20 methods, too many responsibilities | Method count |
| **Deep Nesting** | >4 levels, hard to read | AST depth |
| **Long Params** | >5 parameters, confusing API | Function signature |
| **Copy-Paste** | Duplication, bug-prone | Similarity detection |
| **Dead Code** | Unused, confusing | Import/usage analysis |
| **Mixed Concerns** | UI in DB code | Dependency analysis |

## API Design Patterns

| Pattern | Description | Quality |
|---------|-------------|---------|
| **RESTful** | Resource-based URLs | Standard |
| **GraphQL** | Single endpoint, query language | High — flexible |
| **gRPC** | Protocol buffers, streaming | High — performant |
| **tRPC** | End-to-end type safety | Highest — TypeScript |
| **WebSocket** | Real-time bidirectional | Context-dependent |

## Testing Patterns

| Pattern | Description | Coverage |
|---------|-------------|----------|
| **Unit** | Individual functions | Low — isolated |
| **Integration** | Component interactions | Medium — realistic |
| **E2E** | Full user flows | High — confidence |
| **Property-Based** | Random input testing | High — edge cases |
| **Contract** | API contract verification | Medium — API correctness |
