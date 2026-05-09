# GençCüzdan Backend API

FastAPI backend for the GençCüzdan financial management application.

## Features

- Financial summary tracking (income, expenses, savings)
- Transaction management (income and expenses)
- Investment profile management
- User profile management
- RESTful API with automatic OpenAPI documentation

## API Documentation

Once the server is running, visit `https://api.alperlab.lol/docs` for interactive API documentation.


---

NOTES FOR ME

update_repo.sh -> runs git fetch on this repo

restart-fastapi.sh -> runs pip install -r requirements then restarts fastapi-app.service

fastapi-app.service -> runs /srv/backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 1
