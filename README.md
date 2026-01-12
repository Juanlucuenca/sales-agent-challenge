# Sales Agent Challenge

## Requirements

- Python 3.11+
- PostgreSQL database

## Installation

### Mac

1. Create a virtual environment:

```bash
python3 -m venv venv
```

2. Activate the virtual environment:

```bash
source venv/bin/activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

### Windows

1. Create a virtual environment:

```bash
python -m venv venv
```

2. Activate the virtual environment:

```bash
venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

## Configuration

Create a `.env` file in the root directory with the following variables:

```
DB_USER=your_database_user
DB_PASSWORD=your_database_password
DB_HOST=your_database_host
DB_PORT=your_database_port
DB_NAME=your_database_name
OPENROUTER_APIKEY=your_openrouter_api_key
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_PHONE_NUMBER=your_twilio_phone_number
```

## Run the application

### Mac / Windows

From the project root directory with the virtual environment activated:

```bash
cd app/api/v1
python main.py
```

Or using uvicorn directly:

```bash
uvicorn app.api.v1.main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at `http://localhost:8000`.

Health check endpoint: `http://localhost:8000/health`
# sales-agent-challenge
