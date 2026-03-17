# ⚡ SwiftSync AI — Backend

Smart platform that redistributes unused resources (food, books, clothes, devices) to people who need them.

Built with **Django** + **Django REST Framework** + **JWT Authentication**

---

## 🚀 Setup (Run These Commands Once)

```bash
# 1. Install all packages
python3 -m pip install -r requirements.txt

# 2. Create the database tables
python3 manage.py makemigrations
python3 manage.py migrate

# 3. Create an admin user (for testing)
python3 manage.py createsuperuser

# 4. Start the server
python3 manage.py runserver
```

Server will be running at: **http://127.0.0.1:8000/**

---

## 🔑 Authentication Flow

### Step 1 — Register a new user
```
POST /api/auth/register/
{
  "username": "john",
  "email": "john@example.com",
  "password": "mypassword123",
  "password2": "mypassword123"
}
```

### Step 2 — Login to get your JWT token
```
POST /api/token/
{
  "username": "john",
  "password": "mypassword123"
}
```
Returns: `{ "access": "eyJ...", "refresh": "eyJ..." }`

### Step 3 — Use the token in all requests
Add this header to every request:
```
Authorization: Bearer eyJ...your_access_token...
```

---

## 📡 API Endpoints

| Method | URL | Description | Auth Required |
|--------|-----|-------------|---------------|
| POST | `/api/auth/register/` | Register new user | ❌ |
| GET/PUT | `/api/auth/profile/` | View/edit your profile | ✅ |
| POST | `/api/token/` | Login — get JWT tokens | ❌ |
| POST | `/api/token/refresh/` | Refresh access token | ❌ |
| GET | `/api/resources/` | List all resources | ✅ |
| POST | `/api/resources/` | Donate a resource | ✅ |
| GET | `/api/resources/{id}/` | Get one resource | ✅ |
| PUT/PATCH | `/api/resources/{id}/` | Update resource (donor only) | ✅ |
| DELETE | `/api/resources/{id}/` | Delete resource (donor only) | ✅ |
| GET | `/api/resources/my/` | Your donated resources | ✅ |
| PATCH | `/api/resources/{id}/mark_claimed/` | Mark as claimed | ✅ |
| GET | `/api/requests/` | List requests | ✅ |
| POST | `/api/requests/` | Request a resource | ✅ |
| GET | `/api/requests/{id}/` | Get one request | ✅ |
| DELETE | `/api/requests/{id}/` | Cancel your request | ✅ |
| GET | `/api/requests/my/` | Your submitted requests | ✅ |
| PATCH | `/api/requests/{id}/approve/` | Approve request (donor) | ✅ |
| PATCH | `/api/requests/{id}/reject/` | Reject request (donor) | ✅ |
| GET | `/api/stats/` | Platform statistics | ✅ |

---

## 🧪 Run Tests

```bash
python3 manage.py test api
```

---

## 🛠 Admin Panel

Go to: http://127.0.0.1:8000/admin/
Login with your superuser credentials.

---

## 📁 Project Structure

```
swiftsync/
  ├── api/
  │    ├── migrations/        ← database migration files
  │    ├── __init__.py
  │    ├── admin.py           ← admin panel config
  │    ├── apps.py            ← app config
  │    ├── models.py          ← Resource + Request database models
  │    ├── serializers.py     ← JSON conversion + validation
  │    ├── views.py           ← API logic / endpoints
  │    ├── urls.py            ← API URL routing
  │    └── tests.py           ← automated tests
  │
  ├── swiftsync/
  │    ├── __init__.py
  │    ├── asgi.py
  │    ├── settings.py        ← all project configuration
  │    ├── urls.py            ← main URL file
  │    └── wsgi.py
  │
  ├── manage.py               ← Django CLI tool
  ├── requirements.txt        ← package dependencies
  └── db.sqlite3              ← SQLite database (auto-created)
```
