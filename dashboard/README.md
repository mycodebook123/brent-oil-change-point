# Brent Oil Change Point Dashboard

Interactive dashboard for exploring the Bayesian change point analysis of
Brent crude oil prices (1987-2022).

## Structure

- `backend/` — Flask API serving processed price data, events, and change
  point model results
- `frontend/` — React (Vite) single-page dashboard with an interactive price
  chart, change point overlay, event markers, and date/category filtering

## Setup & Running

### Backend

```bash
cd backend
pip install -r ../../requirements.txt
python app.py
```

Runs on `http://127.0.0.1:5000`. Endpoints:

- `GET /api/health` — health check
- `GET /api/summary` — dataset summary statistics
- `GET /api/prices?granularity=monthly|daily&start=YYYY-MM-DD&end=YYYY-MM-DD` — price series
- `GET /api/events` — researched events dataset
- `GET /api/change-points` — Bayesian change point model results

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Runs on `http://localhost:5173`. Requires the backend running at
`http://127.0.0.1:5000` (CORS is enabled on the Flask side).

## Features

- Monthly-aggregated price chart (Recharts) with a dashed reference line
  marking the Bayesian-detected change point
- Event reference lines colored by category (Conflict, Geopolitical, Market
  Event, Economic, OPEC Policy, Sanctions)
- Date range filter (applies to both the chart and the event list)
- Category filter chips (toggle event types on/off)
- Summary stat cards: date range, observation count, price range, average
  price, and detected change point with posterior probability
