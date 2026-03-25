# ⚡ SwiftSync AI — Backend

A smart platform that redistributes unused resources (food, books, clothes, devices) to people who need them.

---

## 🌍 Live API

Base URL:  
https://swiftsync-backend-vo54.onrender.com

---

## 🎯 Problem Statement

In daily life, valuable resources are often wasted while many people lack access to basic necessities.  
SwiftSync AI solves this by connecting surplus resources with individuals and organizations in need.

---

## 🧠 Key Features

* 📦 Resource donation system  
* 📥 Request & approval workflow  
* 🔐 Secure JWT authentication  
* 👤 User-based access control  
* 📊 Resource and request tracking  
* ⚡ RESTful API architecture  

---

## 🛠 Tech Stack

* Backend: Django  
* API: Django REST Framework  
* Authentication: JWT (SimpleJWT)  
* Database: SQLite (development) / Render environment (production)  

---

## 🚀 Setup Instructions (Local)

```bash
git clone https://github.com/kamakshirathore1980-create/swiftsync-backend.git
cd swiftsync-backend

# Install dependencies
python3 -m pip install -r requirements.txt

# Apply migrations
python3 manage.py migrate

# Create admin user
python3 manage.py createsuperuser

# Run server
python3 manage.py runserver
````

Server runs at:
[http://127.0.0.1:8000/](http://127.0.0.1:8000/)

---

## 🔐 Authentication Flow

### 1. Register

POST `/api/register/`

```json
{
  "username": "user1",
  "password": "pass123",
  "password2": "pass123"
}
```

---

### 2. Login

POST `/api/token/`

```json
{
  "username": "user1",
  "password": "pass123"
}
```

---

### Response

```json
{
  "access": "JWT_ACCESS_TOKEN",
  "refresh": "JWT_REFRESH_TOKEN"
}
```

---

### 3. Use Token

Include in headers:

```
Authorization: Bearer <access_token>
```

---

## 📡 API Endpoints

### 🔐 Authentication

* POST `/api/register/`
* POST `/api/token/`
* POST `/api/token/refresh/`

---

### 📦 Resources

* GET `/api/resources/`
* POST `/api/resources/`
* GET `/api/resources/{id}/`
* PUT `/api/resources/{id}/`
* DELETE `/api/resources/{id}/`
* GET `/api/resources/my/`

---

### 📥 Requests

* GET `/api/requests/`
* POST `/api/requests/`
* GET `/api/requests/my/`
* PATCH `/api/requests/{id}/approve/`
* PATCH `/api/requests/{id}/reject/`
* DELETE `/api/requests/{id}/`

---

### 📊 Stats

* GET `/api/stats/`

---

## ⚠️ Notes

* First request may take ~30–50 seconds (Render free tier cold start)
* JWT Access Token expires in 1 day
* Refresh Token expires in 7 days
* All protected routes require Authorization header

---

## 📁 Project Structure

```
swiftsync/
├── api/
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│
├── swiftsync/
│   ├── settings.py
│   ├── urls.py
│
├── manage.py
├── requirements.txt
```

---

## 🛠 Admin Panel

Access (local):
[http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)

---

## 🧪 Testing

```bash
python3 manage.py test api
```

---

## 🌍 Future Scope

* 🤖 AI-based smart resource matching
* 🏢 NGO verification system
* 🔔 Real-time notifications
* 📱 Mobile app integration

---

## 👨‍💻 Developed By

**Kamakshi Rathore**
Backend Developer — SwiftSync AI

```

