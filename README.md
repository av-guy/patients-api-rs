# Patients API

A FastAPI application for managing patients and therapists.

## Setup

Clone the repository:

```bash
git clone https://github.com/your-username/patients-api.git
cd patients-api
```

Create and activate a virtual environment, then install dependencies:

```bash
python -m venv venv
source venv/bin/activate # On Windows use: venv\Scripts\activate
pip install -r requirements.txt
```

## Running the Application

Start the FastAPI app with Uvicorn:

```bash
uvicorn patients_api.main:app --reload
```

Open http://127.0.0.1:8000/docs to explore the API.

## Running Tests

pytest
