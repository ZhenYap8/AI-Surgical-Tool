.PHONY: install install-backend install-frontend dev backend frontend test test-backend test-frontend

install: install-backend install-frontend

install-backend:
	cd backend && python3 -m venv venv && . venv/bin/activate && pip install -r requirements-dev.txt

install-frontend:
	cd frontend && npm install

dev:
	@echo "Starting backend (0.0.0.0:8000) and frontend (0.0.0.0:5173)..."
	@echo "On this machine: http://localhost:5173 — on phone (same Wi-Fi): use the Vite Network URL"
	@trap 'kill 0' EXIT; \
		cd backend && . venv/bin/activate && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 & \
		cd frontend && npm run dev & \
		wait

backend:
	cd backend && . venv/bin/activate && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

frontend:
	cd frontend && npm run dev

test: test-backend test-frontend

test-backend:
	cd backend && . venv/bin/activate && pytest -v

test-frontend:
	cd frontend && npm run test
