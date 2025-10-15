# 🐬 dbferry

> A secure, local-first database migration tool — move your data safely between 2 Postgres Databases.

`dbferry` lets you migrate databases **without exposing credentials or data** to any third-party service. It’s **open-source**, **local-first**, and **transparent** by design.

---

## Key Features

-   **Local-first security** — No telemetry, no external calls, no remote logs.
-   **Schema + Data migration** — Migrate structure and contents seamlessly.
-   **Cross-engine support** — PostgreSQL, MySQL, SQLite, and more (extensible via adapters).
-   **Verifiable** — Check row counts and checksums for consistency.
-   **Simple YAML config** — Readable, declarative, and versionable.

---

## Quick Start

```bash
# Install using pip (simplest method)
pip install dbferry

# Install using uv tool
uv tool install dbferry

# Install using pipx (recommended for CLI tools)
pipx install dbferry

# Install directly from GitHub (latest development version)
pip install git+https://github.com/AbdLim/dbferry.git
```

Initialize your migration:

```bash
dbferry init
```

Then edit your generated `migration.yml`:

```yaml
source:
    type: postgres
    host: localhost
    port: 5432
    database: my-awesomedb
    user: postgres
    password: postgres
    sslmode: require

target:
    type: postgres
    host: localhost
    port: 5432
    database: targetdb
    user: postgres
    password: postgres
    sslmode: require

options:
    tables:
        - "*"
    verify_after_migration: true
```

Run the migration:

```bash
dbferry migrate --config migration.yml
```

Verify:

```bash
dbferry verify --config migration.yml
```

---

## Philosophy

`dbferry` is built on a few simple but strict principles:

| Principle           | Meaning                                               |
| ------------------- | ----------------------------------------------------- |
| **Local-first**     | Everything runs on your machine. Nothing is sent out. |
| **Transparent**     | Open code, auditable behavior.                        |
| **Composable**      | Extend it for new databases or workflows.             |
| **Safe by default** | Never modifies the source database.                   |
| **Verifiable**      | Trust built through evidence, not claims.             |

---

## Roadmap

-   [ ] PostgreSQL → MySQL/SQLite migrations
-   [ ] Checkpoint + resume system
-   [ ] Incremental sync support
-   [ ] CLI + Web UI parity
-   [ ] Plugin API for non-SQL engines (Mongo, ClickHouse, etc.)

---

## Security Promise

`dbferry` will **never**:

-   Send telemetry or logs to external servers
-   Store credentials outside your environment
-   Require network access beyond your databases

Everything happens locally — inspect the source and verify it yourself.

---

## Contributing

We welcome community contributions!  
Open an issue or PR at [github.com/AbdLim/dbferry](https://github.com/AbdLim/dbferry)

---

## License

Licensed under the **Apache License** — see [LICENSE](LICENSE) for details.

---

> “Move your data safely. Locally. Transparently.”  
> — The dbferry Project
