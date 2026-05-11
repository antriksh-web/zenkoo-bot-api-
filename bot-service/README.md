# Zenkoo Bot Service

## Run

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

## Google Sheets Memory Setup

Create a Google Cloud service account, enable Google Sheets API, share your target sheet with the service account email, then set:

```powershell
$env:GOOGLE_SHEETS_MEMORY_ENABLED="true"
$env:GOOGLE_SHEETS_MEMORY_SHEET_ID="your_google_sheet_id"
$env:GOOGLE_SHEETS_CREDENTIALS_PATH="C:\\path\\to\\service-account.json"
```

Expected tab name: `memories` with columns:
- `timestamp`
- `scope`
- `memory_key`
- `text`
- `importance`

## Apps Script Memory Setup (Easier)

If you deployed your sheet as a Google Apps Script Web App, set:

```powershell
$env:APPS_SCRIPT_MEMORY_ENABLED="true"
$env:APPS_SCRIPT_MEMORY_URL="https://script.google.com/macros/s/your_deployment_id/exec"
$env:APPS_SCRIPT_MEMORY_TIMEOUT_SECONDS="5"
```

Expected request contract:
- `appendMemory` action: `{ action, scope, memory_key, text, importance }`
- `recentMemories` action: `{ action, memory_key, limit }`

## Endpoints
- `POST /generate-reply`
- `POST /generate-room-activity`
- `POST /simulate-presence`
- `GET /active-bots`
- `GET /room-state/{room_id}`
- `GET /scheduler/pending`
- `GET /scheduler/sent`
