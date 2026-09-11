<!-- nybo:managed:start:stack-summary -->
## Stack

react + PostgreSQL
<!-- nybo:managed:end:stack-summary -->

The frontend UI is built with [Material UI](https://mui.com/) (`@mui/material`,
`@mui/icons-material`, `@emotion/react`, `@emotion/styled`) — a single theme
(`src/frontend/theme.ts`) drives palette/typography, and the main navigation
switches responsively between a bottom tab bar (mobile, < 600px) and a top
app bar with tabs (desktop, ≥ 600px).

<!-- nybo:managed:start:quick-start -->
## Quick Start

```sh
npm install
npm run dev
```
<!-- nybo:managed:end:quick-start -->

## Backend (Python)

```sh
pip install -r requirements-dev.txt
python3 -m pytest
uvicorn src.api.main:app --reload
```

`DATABASE_URL` defaults to an in-memory SQLite (used by the test suite);
set it to a PostgreSQL DSN for real runs, e.g.
`postgresql+psycopg2://user:pass@localhost:5432/taskia`.