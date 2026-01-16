# How to Start the Application

## Prerequisites
- Python 3.8+ installed
- Node.js and npm installed
- Virtual environment activated (if using one)

## Step 1: Start the Backend Server

Open a terminal/command prompt and run:

```bash
# Navigate to the backend directory
cd backend

# Activate virtual environment (if using one)
# On Windows:
..\venv\Scripts\activate
# On Mac/Linux:
# source ../venv/bin/activate

# Start the backend server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

## Step 2: Start the Frontend Server

Open a **NEW** terminal/command prompt and run:

```bash
# Navigate to the frontend directory
cd frontend

# Install dependencies (only needed first time)
npm install

# Start the frontend development server
npm start
```

The frontend will automatically open in your browser at `http://localhost:3000`

## Verification

1. **Backend Health Check**: Open `http://localhost:8000/health` in your browser. You should see:
   ```json
   {"status":"active","system":"Car Lease Assistant"}
   ```

2. **Frontend Status**: The Home page will show a green "Backend server connected" banner if the backend is running, or a red warning banner if it's not.

## Troubleshooting

### "Cannot connect to backend server" error

1. **Check if backend is running**: Look for the uvicorn process in your terminal
2. **Check the port**: Make sure nothing else is using port 8000
3. **Check firewall**: Windows Firewall might be blocking the connection
4. **Try different host**: If `localhost` doesn't work, try `127.0.0.1:8000`

### Port already in use

If port 8000 is already in use:
- Find and stop the process using port 8000
- Or change the port in `backend/main.py` and update frontend API calls

### Import errors

Make sure all Python dependencies are installed:
```bash
pip install -r ../requirements.txt
```
