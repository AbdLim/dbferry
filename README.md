# 🐬 dbferry

> A secure, local-first database migration tool — move your data safely between PostgreSQL, MySQL, SQLite, and more.

`dbferry` lets you migrate databases **without exposing credentials or data** to any third-party service. It’s **open-source**, **local-first**, and **transparent** by design.

---

## ✨ Key Features

-   🔐 **Local-first security** — No telemetry, no external calls, no remote logs.
-   🧱 **Schema + Data migration** — Migrate structure and contents seamlessly.
-   🧩 **Cross-engine support** — PostgreSQL, MySQL, SQLite, and more (extensible via adapters).
-   🧠 **Resumable** — Continue failed migrations without losing progress.
-   📊 **Verifiable** — Check row counts and checksums for consistency.
-   🧰 **Simple YAML config** — Readable, declarative, and versionable.
-   🌐 **Optional Local UI** — Inspect and manage migrations with FastAPI-based web UI.

---

## 🚀 Quick Start

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
    url: postgresql://user:password@localhost/source_db

target:
    type: mysql
    url: mysql://user:password@localhost/target_db

options:
    migrate_schema: true
    migrate_data: true
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

## 🧭 Philosophy

`dbferry` is built on a few simple but strict principles:

| Principle           | Meaning                                               |
| ------------------- | ----------------------------------------------------- |
| **Local-first**     | Everything runs on your machine. Nothing is sent out. |
| **Transparent**     | Open code, auditable behavior.                        |
| **Composable**      | Extend it for new databases or workflows.             |
| **Safe by default** | Never modifies the source database.                   |
| **Verifiable**      | Trust built through evidence, not claims.             |

---

## 🧩 Roadmap

-   [ ] PostgreSQL → MySQL/SQLite migrations
-   [ ] Checkpoint + resume system
-   [ ] Incremental sync support
-   [ ] CLI + Web UI parity
-   [ ] Plugin API for non-SQL engines (Mongo, ClickHouse, etc.)

---

## 🛡️ Security Promise

`dbferry` will **never**:

-   Send telemetry or logs to external servers
-   Store credentials outside your environment
-   Require network access beyond your databases

Everything happens locally — inspect the source and verify it yourself.

---

## 🤝 Contributing

We welcome community contributions!  
Open an issue or PR at [github.com/AbdLim/dbferry](https://github.com/AbdLim/dbferry)

---

## 📜 License

Licensed under the **Apache License** — see [LICENSE](LICENSE) for details.

---

> “Move your data safely. Locally. Transparently.”  
> — The dbferry Project
