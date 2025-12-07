# Chili Backend

RESTful API service with user authentication, avatar management, and real-time WebSocket notifications.

## Tech Stack

- **FastAPI** — modern Python web framework
- **SQLite** — lightweight database (no setup required)
- **SQLAlchemy** — ORM for database operations
- **JWT** — stateless authentication (python-jose)
- **WebSockets** — real-time notifications
- **Passlib** — secure password hashing (PBKDF2-SHA256)
- **Docker** — containerized deployment
- **pytest** — testing framework

## Requirements

**Option A: Local Development**
- Python 3.10+
- pip

**Option B: Docker**
- Docker
- Docker Compose

## How to Run

### Option 1: Run with Docker (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd chili_backend

# Build and run with one command
docker-compose up --build

# Or run in background
docker-compose up --build -d
```

Server runs at: http://localhost:8000

> **Note:** Database and avatars are persisted in `./data/` and `./static/` directories via Docker volumes.

**Stop the container:**
```bash
docker-compose down
```

### Option 2: Run Locally (Development)

```bash
# 1. Clone the repository
git clone <repository-url>
cd chili_backend

# 2. Create and activate virtual environment
python -m venv .venv

# Windows (PowerShell)
.\.venv\Scripts\Activate.ps1

# Windows (CMD)
.\.venv\Scripts\activate.bat

# Linux/macOS
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# Alternative: install manually
# pip install fastapi uvicorn[standard] sqlalchemy python-jose passlib python-multipart

# 4. Start the server
uvicorn app.main:app --reload
```

Server runs at: http://127.0.0.1:8000

> **Note:** SQLite database file (`data/dev.db`) is created automatically on first run — no external database setup required.

## Running Tests

```bash
# Make sure dependencies are installed
pip install -r requirements.txt

# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_users.py
pytest tests/test_auth_api.py
```

### Test Coverage

| Test File | Tests | Description |
|-----------|-------|-------------|
| `test_users.py` | 4 | User service: create, duplicate, authenticate |
| `test_auth_api.py` | 6 | API endpoints: register, login, avatar, delete |

Tests use a **temporary file SQLite database** that is automatically cleaned up after each test run.

## How to Use

### API Documentation

Open **Swagger UI** at: http://127.0.0.1:8000/docs

### Authentication Flow

1. **Register** — `POST /auth/register`
   ```json
   {
     "identifier": "john@example.com",
     "password": "secret123"
   }
   ```

2. **Login** — `POST /auth/login` (same payload)
   
   **Example response:**
   ```json
   {
     "status": "success",
     "data": {
       "user": {
         "id": 1,
         "identifier": "john@example.com",
         "avatar_url": null
       },
       "token": {
         "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
         "token_type": "bearer"
       }
     }
   }
   ```

3. **Authorize in Swagger** — Click "Authorize" button, paste the `access_token`, click "Authorize"

4. **Upload Avatar** — `POST /auth/avatar` (select image file)

5. **Delete Account** — `DELETE /auth/me`

### WebSocket Connection

Connect to receive real-time avatar change notifications.

**Browser Console Snippet:**
```javascript
// Replace with your actual JWT token
let token = "YOUR_JWT_TOKEN_HERE";

let ws = new WebSocket("ws://127.0.0.1:8000/ws?token=" + token);

ws.onopen = () => console.log("WebSocket connected");
ws.onmessage = (msg) => console.log("Received:", JSON.parse(msg.data));
ws.onclose = () => console.log("WebSocket closed");
ws.onerror = (err) => console.log("Error:", err);
```

> **Note:** When deploying behind HTTPS, use `wss://` instead of `ws://`.

**Expected message on avatar change:**
```json
{
  "event": "avatar_changed",
  "avatar_url": "/static/avatars/user_1_20251205120000.png"
}
```

## API Endpoints

| Method | Path | Auth Required | Description |
|--------|------|---------------|-------------|
| POST | `/auth/register` | No | Create new user account |
| POST | `/auth/login` | No | Login and get JWT token |
| POST | `/auth/avatar` | Yes | Upload/replace avatar image |
| DELETE | `/auth/me` | Yes | Delete user and avatar |
| GET | `/auth/ping` | No | Auth service health check |
| GET | `/health/` | No | Service health check |
| WS | `/ws?token=JWT` | Yes | WebSocket for real-time events |

## Response Format (JSend)

All HTTP responses follow [JSend](https://github.com/omniti-labs/jsend) specification:

**Success:**
```json
{
  "status": "success",
  "data": { ... }
}
```

**Fail (4xx):**
```json
{
  "status": "fail",
  "data": { "field": "error message" }
}
```

**Error (5xx):**
```json
{
  "status": "error",
  "message": "Internal server error"
}
```

## Authentication (JWT)

This API uses **stateless JWT authentication**. The server does not store session data — each request is validated independently using the token signature.

**How token invalidation works:**
- When a user is deleted, their record is removed from the database
- Any previously issued tokens become invalid because the `user_id` in the token no longer exists
- No token blacklist is needed

## Testing Tips

### Reset Database

```bash
# Linux/macOS
rm -rf data/

# Windows (PowerShell/CMD)
rmdir /s /q data
```

The database will be recreated automatically on next server start.

### Avatar Storage

Avatar files are stored in `static/avatars/` directory, which is created automatically on first upload.

## Project Structure

```
chili_backend/
├── app/
│   ├── api/v1/           # Route handlers
│   │   ├── auth.py       # Auth endpoints
│   │   ├── health.py     # Health check
│   │   └── ws.py         # WebSocket endpoint
│   ├── core/             # Core modules
│   │   ├── config.py     # Configuration
│   │   ├── deps.py       # Dependencies (auth)
│   │   ├── security.py   # JWT & password utils
│   │   ├── jsend.py      # Response helpers
│   │   └── ws_manager.py # WebSocket manager
│   ├── db/               # Database
│   │   ├── base.py       # Engine & session
│   │   └── models.py     # SQLAlchemy models
│   ├── schemas/          # Pydantic models
│   ├── services/         # Business logic
│   └── main.py           # App entrypoint
├── tests/                # Test suite
│   ├── conftest.py       # Pytest fixtures
│   ├── test_users.py     # User service tests
│   └── test_auth_api.py  # API endpoint tests
├── static/avatars/       # Uploaded avatars
├── data/                 # SQLite database (gitignored)
├── Dockerfile            # Container build instructions
├── docker-compose.yml    # Container orchestration
└── requirements.txt      # Python dependencies
```

## License

MIT
