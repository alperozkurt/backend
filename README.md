# GençCüzdan Backend API

FastAPI backend for the GençCüzdan financial management application.

## Features

- Financial summary tracking (income, expenses, savings)
- Transaction management (income and expenses)
- Investment profile management
- User profile management
- RESTful API with automatic OpenAPI documentation

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Seed the database with initial data:
```bash
python seed.py
```

3. Run the development server:
```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## API Documentation

Once the server is running, visit `http://localhost:8000/docs` for interactive API documentation.

## Database

The application uses SQLAlchemy ORM with SQLite for development. Set the `DATABASE_URL` environment variable for production databases.

---

NOTES FOR ME

update_repo.sh -> runs every 10 minutes on a timer and pulls this repo

restart-fastapi.sh -> runs pip install -r requirements then restarts fastapi-app.service

fastapi-app.service -> runs /srv/backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 1
