bash -c "cd frontend && npm run build:watch" &
bash -c "uv run fastapi dev ./backend/app.py"
