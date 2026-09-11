# Architecture — taskia

## Stack

```mermaid
graph TD
  Browser([Browser]) --> FE
  FE["React"] --> API
  API["Python"] --> DB
  DB[("PostgreSQL")]
  FE --> Hosting["AWS"]
```

## Data Model

```mermaid
erDiagram
  %% No entities defined
```

## Key Decisions

- File structure: feature-based
- Error handling: Result pattern
- Auth model: RBAC
