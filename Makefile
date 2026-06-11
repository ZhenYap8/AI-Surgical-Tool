.PHONY: install install-backend install-frontend dev backend frontend test test-backend test-frontend

install: install-backend install-frontend

install-backend:
	cd backend && python3 -m venv venv && . venv/bin/activate && pip install -r requirements.txt

install-frontend:
	cd frontend && npm install

dev:
	@echo "Starting backend (http://localhost:8000) and frontend (http://localhost:5173)..."
	@trap 'kill 0' EXIT; \
		cd backend && . venv/bin/activate && uvicorn app.main:app --reload --port 8000 & \
		cd frontend && npm run dev & \
		wait

backend:
	cd backend && . venv/bin/activate && uvicorn app.main:app --reload --port 8000

frontend:
	cd frontend && npm run dev

test: test-backend test-frontend

test-backend:
	cd backend && . venv/bin/activate && pytest -v

test-frontend:
	cd frontend && npm run test
