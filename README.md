NOTES FOR ME

update_repo.sh -> runs every 10 minutes on a timer and pulls this repo

restart-fastapi.sh -> runs pip install -r requirements then restarts fastapi-app.service

fastapi-app.service -> runs /srv/backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 1
