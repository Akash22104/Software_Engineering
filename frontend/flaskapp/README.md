# Flask Frontend (Multi Page)

This Flask app provides a multi-page UI for your calorie tracker and consumes the existing Node backend APIs.

## Pages

- Add Meal (`/` and `/add-meal`)
- Analytics (`/analytics`)
- Recommendation (`/recommendation`)
- Coach (`/coach`)
- Health Diet (`/health-diet`)
- Rewards (`/rewards`)

## Run

1. Start backend API (port 5000)

```powershell
cd backend
node server.js
```

2. In a new terminal, run Flask frontend (port 8000)

```powershell
cd frontend/flaskapp
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

3. Open browser:

- `http://localhost:8000`
