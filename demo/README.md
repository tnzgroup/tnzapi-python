# tnzapi-python demo

A small full-stack demo: a FastAPI backend (`demo/api/`) paired with a **shared** React + Vite frontend (`demo/web/`, a git submodule pointing at `github-mirror/tnzapi-demo-web`) — the same frontend `tnzapi-dotnet`'s own demo uses. The frontend's wire format (field names like `SendMode`, `TemplateId`, `ChargeCode`) is fixed and shared; each backend translates it to its own SDK's native field names internally (see `demo/api/app/routers/sms.py` for the pattern).

**Implemented:** Health, Auth (session-based token override), Settings (`api-url` / `allow-insecure-http` fully working; `ssl-verification` returns a documented 501 — `tnzapi-python`'s `HttpClient` has no equivalent knob), every messaging channel (SMS, Email, Fax, TTS, Voice, WhatsApp, RCS, Workflow), Actions (Abort/Reschedule/Resubmit/Pacing, per-channel `PATCH` endpoints), Addressbook (Contact/Group CRUD, ContactGroups/GroupContacts join endpoints), and OptOut (CRUD). Every page the shared frontend renders has a working backend behind it.

## First-time setup

```bash
git submodule update --init demo/web
```

(Anyone who clones this repo fresh needs this — submodules aren't checked out automatically by a plain `git clone`.)

> ⚠️ This demo is for local development and evaluation only — see the warning banner on its own Settings page for why it should never be pointed at a production deployment. `demo/api/` also has no request-level authentication of its own and trusts whatever Auth Token it's configured with, so never run it anywhere reachable beyond your own machine.

## Running it with Docker (recommended)

All commands below assume your terminal's current directory is `demo/` (this folder).

1. Create a file named `.env` in this folder containing your token:

   ```
   TNZ_AUTH_TOKEN=your-token-here
   ```

2. Build and start both containers:

   ```bash
   docker-compose up --build
   ```

   The first run downloads and builds everything (a few minutes). Wait for output like:

   ```
   api-1  | Uvicorn running on http://0.0.0.0:5080
   web-1  |   VITE v6.4.3  ready in 1479 ms
   ```

3. Visit `http://localhost:5373`.

Stop with `Ctrl+C` in that terminal; `docker-compose down` afterward removes the containers (optional). Editing files under `demo/api/` or `demo/web/` while the containers are running picks up live (uvicorn `--reload` / Vite dev server), no rebuild needed — except changes to `.env` or `requirements.txt`/`package.json`, which need `docker-compose up --build` again.

**Troubleshooting:**
- *"port is already allocated"*: something else on your machine is using `5080` or `5373`. Free it, or edit the port numbers in `docker-compose.yml`.
- *SMS page (or any action) returns `"Result": "Unauthorized"`*: expected if `TNZ_AUTH_TOKEN` isn't set to a real token yet — it means the demo reached the real TNZ API and got told the credentials are invalid, not that something's broken.
- *Want to point at something running on your own machine, not TNZ's real API*: inside a container, `localhost` means the container itself. Use `http://host.docker.internal:<port>` in the Settings page's API URL field instead.

## Running it without Docker

Backend (from repo root, after `pip install -e .[test]`):

```bash
cd demo/api
pip install -r requirements.txt
TNZ_AUTH_TOKEN=your-token uvicorn app.main:app --reload --port 5080
```

Frontend:

```bash
cd demo/web
npm install
npm run dev
```

Visit `http://localhost:5373` (or pass `-- --port <n>` to run alongside `tnzapi-dotnet`'s own demo web on the same machine).

## Updating the shared frontend

The frontend lives in its own repo (`github-mirror/tnzapi-demo-web`) so both `tnzapi-dotnet` and `tnzapi-python` can use the exact same code. To pull in a change made from either project:

```bash
cd demo/web
git checkout main
git pull
cd ../..
git add demo/web
git commit -m "chore: bump shared demo web submodule"
```

To make a change to the shared frontend from here, edit inside `demo/web/`, commit and push from *within* that directory (it's its own git repository), then bump the pointer in this repo the same way.

## Testing

```bash
cd demo/api && pytest
cd demo/web && npm run test:types && npm test
```

Neither test suite is collected by the main SDK's own `pytest`/`tests/`.

## Known tradeoffs (deliberate, not bugs)

- `demo/api`'s Settings/Auth endpoints have no caller authentication and `api-url` accepts any URL with no allowlist — this exactly mirrors `tnzapi-dotnet`'s own demo API, gated by the same "Development / demo use only" warning already shown in the shared frontend's Settings page. Not hardened for this plan; revisit both demos together if ever needed.
- SMS/RCS/WhatsApp's `FallbackMode` is a single string field in `tnzapi-python`'s v3.00 DTOs (matching the real v3.00 API spec), unlike `tnzapi-dotnet`'s flags-enum model. The frontend's multi-select checkbox list can still select more than one - selecting more than one is rejected with a 400 rather than silently keeping only the first, since silently dropping a caller's selection would be worse than an explicit error.
