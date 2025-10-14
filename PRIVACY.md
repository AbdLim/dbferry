# 🔐 Privacy Policy — dbferry

_Last updated: October 2025_

`dbferry` is designed with **privacy-first principles**. This document explains how the tool handles your data.

---

## 1. Local-First Architecture

All operations happen **entirely on your local machine**.  
There are **no remote servers**, **no analytics**, and **no telemetry**.

Your database credentials, schema, and data never leave your environment.

---

## 2. Data Access and Storage

`dbferry` connects to your databases only for the duration of the migration.  
It does **not** store or transmit credentials externally.

| Data Type       | Storage                         | Retention           |
| --------------- | ------------------------------- | ------------------- |
| Connection URLs | Local config (`migration.yml`)  | Until you delete it |
| Logs / Metadata | `.dbferry/` folder (local only) | Until you delete it |
| Credentials     | Never sent externally           | Never retained      |

You are in full control of all generated files.

---

## 3. Network Policy

`dbferry` makes **no external HTTP requests**.  
The only outbound connections are the ones you explicitly define (e.g., your source and target databases).

No auto-updates, telemetry, or background syncing are performed.

---

## 4. Optional Local Web UI

If you run `dbferry ui`, a **FastAPI-based web server** will start locally (`localhost` only).  
This does not expose data to the internet.

All API endpoints are local and protected by your operating system’s user-level permissions.

---

## 5. Open Source Transparency

`dbferry` is open-source under the Apache License.  
You are encouraged to **review the code** to verify these privacy claims.

Open development ensures no hidden data access paths exist.

---

## 6. Third-Party Dependencies

All dependencies are open-source and locally vendored through `uv`.  
No external SDKs or analytics packages are included.

---

## 7. Your Responsibility

-   Do not commit or share your `migration.yml` if it contains raw credentials.
-   Use environment variables for passwords when possible.
-   Always verify your database connection strings before running migrations.

---

## 8. Contact

For questions or privacy concerns, open an issue in the repository:  
[github.com/AbdLim/dbferry/issues](https://github.com/AbdLim/dbferry/issues)

---

**dbferry** — _your data stays yours._
