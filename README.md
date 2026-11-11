# DukaanAI v1.0 — Milestone 1

A local-first foundation for a Hindi-first kirana shop management PWA.

## Requirements
- Windows 11
- Python 3.12
- Node.js 20.9+ (LTS recommended)
- Git (optional but recommended)
- `uv` Python package manager

## 1. Backend setup (PowerShell)

Open PowerShell in the `dukaanai` folder:

```powershell
cd backend
uv venv --python 3.12
.\.venv\Scripts\Activate.ps1
uv pip install -r requirements.txt
Copy-Item .env.example .env
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Backend:
- API: http://127.0.0.1:8000
- Swagger docs: http://127.0.0.1:8000/docs
- Health: http://127.0.0.1:8000/health

Keep this terminal running.

## 2. Frontend setup

Open a second PowerShell terminal:

```powershell
cd frontend
Copy-Item .env.local.example .env.local
npm install
npm run dev
```

Open http://localhost:3000

## 3. First milestone acceptance checks

- Dashboard loads at `http://localhost:3000`.
- API status shows Connected.
- Today's sales, expenses, outstanding udhaar and low-stock counts load from FastAPI.
- FastAPI docs open at `http://127.0.0.1:8000/docs`.

## 4. Important notes
- SQLite is for local development only. Do not use this setup for real customer financial records.
- The dashboard currently uses demo seed data. It is clearly marked as sample data.
- No AI API key is required for Milestone 1.
- Do not commit `.env`, `.env.local`, database files, or secrets.
- Before onboarding real shops, implement authentication, tenant isolation, backups, audit logs and security tests.

## 5. Next milestones
1. Shop/user authentication and shop-specific data isolation.
2. Product catalogue and inventory movements.
3. Sales, expenses and customer ledger.
4. Hindi speech capture, transcript editing and confirmation.
5. Structured intent extraction with strict validation.
6. PWA installability and offline-safe drafts.
7. Supabase PostgreSQL migration and pilot deployment.
