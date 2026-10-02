# FitBuddy — AI Fitness Plan Generator using Gemini

A complete local web application based on the supplied project brief. It includes a FastAPI backend, Jinja2/HTML frontend, SQLite persistence, Gemini-powered workout generation and nutrition tips, feedback-based plan updates, a coach dashboard, and API docs.

## Features

- Personalized 7-day workout plans using goal, age, weight, intensity, and experience.
- Nutrition/recovery tip tailored to the selected goal.
- Feedback form to revise and save a plan while preserving the original.
- SQLite database with SQLAlchemy models.
- Coach dashboard to view profiles and original/latest plans.
- Delete profile action on the dashboard.
- Responsive layout, validation, health endpoint, and Swagger API docs.
- Demo mode works without an API key, using clearly labelled starter-plan content.

## Requirements

- Python 3.10+ (Python 3.11 or 3.12 recommended)
- Internet connection and Google AI Studio API key for live Gemini responses.

## Run on Windows

1. Extract the project ZIP.
2. Open the extracted `FitBuddy_AI_Fitness_Plan_Generator` folder.
3. Double-click `run_windows.bat`, or use the commands below in Command Prompt/PowerShell:

```powershell
python -m venv .venv
.venv\\Scripts\\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
copy .env.example .env
```

4. Open `.env` in a text editor and set `GOOGLE_API_KEY` to your own API key. The app automatically loads `.env` at startup. Never share or commit this key. If you leave the demo value, FitBuddy runs in clearly labelled demo mode.
5. Start the server:

```powershell
python -m uvicorn app.main:app --reload
```

6. Open:
   - App: http://127.0.0.1:8000
   - API documentation: http://127.0.0.1:8000/docs
   - Health check: http://127.0.0.1:8000/health
   - Coach dashboard: http://127.0.0.1:8000/view-all-users

## Run on macOS/Linux

```bash
chmod +x run_mac_linux.sh
./run_mac_linux.sh
```

Then add your API key to `.env` and restart the server if needed.

## Gemini model configuration

The app uses the current `google-genai` SDK and defaults to `gemini-2.5-flash` for both plan and tip generation. Set `GEMINI_WORKOUT_MODEL` and `GEMINI_TIP_MODEL` in `.env` to model IDs available to your Google AI Studio API key. Model availability can vary by account and may change over time.

## Main routes

| Method | Route | Purpose |
|---|---|---|
| GET | `/` | Home page and fitness profile form |
| POST | `/generate-workout` | Validate profile, generate plan and tip, save records |
| POST | `/submit-feedback` | Generate and save a revised plan |
| GET | `/view-all-users` | Coach dashboard |
| POST | `/delete-user/{user_id}` | Delete a user and associated plans |
| GET | `/health` | Health status |
| GET | `/docs` | Interactive OpenAPI docs |

## Project structure

```text
FitBuddy_AI_Fitness_Plan_Generator/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── routes.py
│   ├── database.py
│   ├── schemas.py
│   ├── gemini_generator.py
│   ├── templates/
│   │   ├── index.html
│   │   ├── result.html
│   │   └── all_users.html
│   └── static/
│       ├── css/style.css
│       └── js/app.js
├── data/
├── requirements.txt
├── .env.example
├── .gitignore
├── run_windows.bat
├── run_mac_linux.sh
└── README.md
```

## Verification

The included app has been syntax-checked and exercised locally for the home page, health endpoint, Swagger docs, demo plan generation, feedback revision, dashboard rendering, validation handling, and profile deletion.

## Notes and safety

- Without a configured key, FitBuddy displays a clearly labelled demo plan; no Gemini request is made.
- User IDs are unique. Reusing an ID updates the profile and creates a new plan record.
- This is a local development project. The coach dashboard and delete action are not protected by authentication; add authentication and authorization before exposing it to a network or the public.
- Fitness and nutrition content is general information, not medical advice. Users should adapt activity to their abilities and seek professional advice when appropriate.
- Do not commit `.env` or publish API keys.
