# ⚡ SwiftSync AI — Backend

A smart platform that redistributes unused resources (food, books, clothes, devices) to people who need them.

---

## 🎯 Problem Statement

In daily life, valuable resources are often wasted while many people lack access to basic necessities. SwiftSync AI solves this by connecting surplus resources with individuals and organizations in need.

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
* Database: SQLite

---

## 🚀 Setup Instructions

```bash
# Install dependencies
python3 -m pip install -r requirements.txt

# Apply migrations
python3 manage.py makemigrations
python3 manage.py migrate

# Create admin user
python3 manage.py createsuperuser

# Run server
python3 manage.py runserver
```

Server runs at: http://127.0.0.1:8000/

---

## 🔐 Authentication Flow

### 1. Register

POST /api/auth/register/

### 2. Login

POST /api/token/

### 3. Use Token

Authorization: Bearer <access_token>

---

## 📡 API Endpoints

### Authentication

* POST /api/auth/register/
* POST /api/token/
* POST /api/token/refresh/

### Resources

* GET /api/resources/
* POST /api/resources/
* GET /api/resources/{id}/
* PUT /api/resources/{id}/
* DELETE /api/resources/{id}/

### Requests

* POST /api/requests/
* GET /api/requests/
* DELETE /api/requests/{id}/

---

## 📁 Project Structure

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

---

## 🛠 Admin Panel

Access: http://127.0.0.1:8000/admin/

---

## 🧪 Testing

```bash
python3 manage.py test api
```

---

## 🌍 Future Scope

* AI-based smart matching
* NGO verification system
* Real-time notifications
* Mobile app integration

---

## 🧠 Developed For

Capstone Project — SwiftSync AI
Backend Module: API, Server & Database Management
