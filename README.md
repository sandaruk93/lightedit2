# Full-Stack React FastAPI Application

This is a full-stack application built with React (frontend) and FastAPI (backend).

## Project Structure
```
.
├── backend/           # FastAPI backend
│   ├── app/
│   ├── requirements.txt
│   └── main.py
└── frontend/         # React frontend
    ├── src/
    ├── package.json
    └── public/
```

## Backend Setup
1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the backend server:
```bash
uvicorn main:app --reload
```

The backend will be available at http://localhost:8000

## Frontend Setup
1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Run the development server:
```bash
npm start
```

The frontend will be available at http://localhost:3000

## Features
- File upload functionality
- RESTful API endpoints
- Modern React frontend with TypeScript
- FastAPI backend with automatic API documentation 