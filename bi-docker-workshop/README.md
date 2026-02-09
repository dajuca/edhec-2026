# BI Docker Workshop — Docker → Postgres/API → Power BI (+ BigQuery extension)

This repo is designed for a **3–4 hour Master 2 BI/Data** workshop.

## What students build
A reproducible BI backend (PostgreSQL + FastAPI) with Docker Compose, then connect:
- **Power BI Desktop (Windows)** → **PostgreSQL** (recommended)
- Power BI Desktop → **REST API** (Web connector)
- (Optional) Export to **BigQuery** for the “modern stack” extension

---

## 0) Prerequisites

### Windows users
- Docker Desktop
- VS Code + Docker extension

### macOS users (Power BI Desktop constraint)
Power BI Desktop is Windows-only.
You have two workable setups:

**Option A (recommended):**
- Docker Desktop on macOS
- Parallels (Windows 11) for Power BI Desktop

**Option B:**
- Use Power BI Service in browser (less ideal for teaching modeling)

---

## 1) Quickstart (everyone)

### 1. Clone
```bash
git clone https://github.com/<YOUR_ORG>/bi-docker-workshop.git
cd bi-docker-workshop
```

### 2. Run the stack
```bash
docker compose up --build
```

You should have:
- PostgreSQL on `localhost:5432`
- API on `http://localhost:8000`

### 3. Test the API
Open:
- `http://localhost:8000/health`
- `http://localhost:8000/sales`

---

## 2) Power BI Desktop connections

### A) PostgreSQL connector (best for BI)
In Power BI Desktop → **Get data** → **PostgreSQL**:

**Windows (native):**
- Server: `localhost`
- Port: `5432`
- Database: `sales`
- Username: `admin`
- Password: `admin`

**macOS (Power BI running inside Windows VM):**
Use the VM-safe hostname:
- Server: `host.docker.internal`
- Port: `5432`

> If you run Docker inside Windows (instead of macOS), then use `localhost`.

### B) REST API (Web)
Power BI Desktop → **Get data** → **Web**:
- `http://localhost:8000/sales`

or in a Windows VM on macOS:
- `http://host.docker.internal:8000/sales`

---

## 3) VS Code Dev Containers (optional)
This repo includes a `.devcontainer` config so students can open the project in a containerized dev environment in VS Code.

See `docs/devcontainer.md`.

---

## 4) BigQuery extension (optional)
See `docs/bigquery_extension.md` for a clean “Docker compute → BigQuery storage → Power BI semantic layer” extension.

---

## Troubleshooting
- If ports are busy, stop services:
  ```bash
  docker compose down
  ```
- Reset DB (wipes data):
  ```bash
  docker compose down -v
  docker compose up --build
  ```
