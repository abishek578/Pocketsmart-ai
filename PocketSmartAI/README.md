# PocketSmart AI

PocketSmart AI is a FastAPI + Jinja2 web application based on the supplied project documentation. It provides three budget planners:

- Home Interior
- Party Planning
- Jewelry (with optional outfit image analysis)

The project keeps the documentation's required routes (`/generate-home`, `/generate-party`, `/generate-jewelry`, authentication/session routes, `/history`, and `/recommendations-details`) while using FastAPI as the final backend architecture described in Milestone 3.

## Important implementation note

The supplied document alternates between Flask and FastAPI. This implementation uses **FastAPI** because the later architecture explicitly specifies FastAPI, Jinja2, Uvicorn, structured models, CORS, JWT authentication, and a `main.py` entry point.

The document also mentions Amazon, Flipkart, IKEA, Swiggy, Zomato and OYO. Their private/live product APIs are not supplied. Therefore this project does **not** scrape those sites. It creates platform-specific search links from AI-generated search terms and labels prices as estimates. This makes the project runnable without pretending that an external retailer API is connected.

The documentation names Gemini 1.5 Flash Pro. That model name is kept configurable rather than hard-coded. Set `GEMINI_MODEL` in `.env`; the example defaults to a current Flash model. You can set it to a model available to your API key.

## Features

- Registration/login/logout with password hashing and JWT cookie sessions
- SQLite persistence via SQLAlchemy
- Protected planner pages
- Home, Party, Jewelry recommendation APIs
- Optional image upload for Jewelry
- Gemini text + multimodal integration
- Strict JSON output validation with Pydantic
- Deterministic fallback recommendations when Gemini is unavailable
- Platform-specific search links
- Recommendation history
- Responsive UI
- API docs at `/docs`
- Pytest coverage for core API flows

## Quick start

### Windows PowerShell

```powershell
cd PocketSmartAI
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
```

Open `.env` and set:

```env
SECRET_KEY=replace-with-a-long-random-value
GEMINI_API_KEY=your_google_ai_api_key
```

Then:

```powershell
python -m uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000

### Command Prompt

```bat
cd PocketSmartAI
py -3 -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python -m uvicorn app.main:app --reload
```

## Demo mode

The app also works without a Gemini key. In that case, the backend returns deterministic demo recommendations so you can test the entire UI, authentication, database, uploads, history, and routing. It is not real AI output.

## Test

```powershell
pytest -q
```

Tests use a temporary SQLite database and do not require Gemini.

## Main URLs

- `/` - landing page
- `/register` - registration
- `/login` - login
- `/dashboard` - dashboard
- `/home-planner` - home planner
- `/party-planner` - party planner
- `/jewelry-planner` - jewelry planner
- `/history-page` - history UI
- `/history` - history JSON API
- `/docs` - FastAPI Swagger UI
- `/health` - health check

## API endpoints

- `POST /register`
- `POST /login`
- `POST /logout`
- `GET /token`
- `GET /session-info`
- `GET /session-data`
- `POST /generate-home`
- `POST /generate-party`
- `POST /generate-jewelry`
- `GET /recommendations-details/{recommendation_id}`
- `GET /history`
- `GET /history/{recommendation_id}`

## Project structure

```text
PocketSmartAI/
├── app/
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── dependencies.py
│   ├── models/
│   │   ├── db.py
│   │   └── schemas.py
│   ├── routes/
│   │   ├── auth.py
│   │   ├── pages.py
│   │   └── recommendations.py
│   ├── services/
│   │   ├── ai_service.py
│   │   ├── fallback.py
│   │   ├── platform_links.py
│   │   └── prompts.py
│   ├── static/
│   │   ├── css/styles.css
│   │   └── js/app.js
│   └── templates/
│       ├── base.html
│       ├── index.html
│       ├── login.html
│       ├── register.html
│       ├── dashboard.html
│       ├── history.html
│       ├── home_planner.html
│       ├── party_planner.html
│       └── jewelry_planner.html
├── data/
├── tests/
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```
