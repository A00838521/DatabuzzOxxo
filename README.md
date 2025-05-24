# DatabuzzOxxo - Full Stack Application

This project consists of a Vue 3 + TypeScript frontend and a Python FastAPI backend.

## Project Structure

```
DatabuzzOxxo/
├── frontend/    # Vue 3 + TypeScript + Vite application
├── backend/     # Python FastAPI application
```

## Frontend

The frontend is built with Vue 3 and TypeScript using Vite as the build tool.

### Setup and Run

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build
```

Learn more about the recommended Vue 3 Project Setup and IDE Support in the [Vue Docs TypeScript Guide](https://vuejs.org/guide/typescript/overview.html#project-setup).

## Backend

The backend is built with Python using FastAPI framework.

### Setup and Run

```bash
# Navigate to backend directory
cd backend

# Create a virtual environment (recommended)
python -m venv venv

# Activate the virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the server
python -m uvicorn app.main:app --reload
```

### API Documentation

Once the backend server is running, you can access the API documentation at:

- Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
- ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

## Development

Both frontend and backend can be developed independently:

1. For frontend development, use `npm run dev` in the frontend directory.
2. For backend development, use `python -m uvicorn app.main:app --reload` in the backend directory.

## Configuration

- Backend configuration can be found in `backend/config.py`
- Frontend configuration can be adjusted in the respective Vue.js configuration files
