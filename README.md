
# 🩺 Doctor Assistant (AI-Powered)

An AI-powered full-stack application that enables patients to book appointments and helps doctors manage schedules, stats, and real-time notifications — all through a conversational AI agent.

---

## 🚀 Live Demo

*(Add after deployment)*

Frontend: https://your-app.vercel.app
Backend: https://your-app.onrender.com

> ⚠️ Note: Backend may take ~10–20 seconds to wake up (Render free tier)

---

## ✨ Features

### 👤 Patient

* Check doctor availability
* Book appointments
* Cancel appointments
* Conversational AI interaction

### 🩺 Doctor

* View schedule (today & future)
* Check appointment statistics
* Receive real-time notifications
* Quick action dashboard

---

## 🧠 AI Capabilities

* Tool-based AI agent (not just chatbot)
* Context-aware conversations
* Multi-step reasoning (availability → booking → confirmation)
* Handles failures gracefully
* Supports multiple roles (Doctor / Patient)

---

## 🏗️ Tech Stack

### Frontend

* React (Vite)

### Backend

* FastAPI
* SQLAlchemy
* PostgreSQL

### AI

* OpenRouter (free-tier models)

### Infrastructure

* Render (Backend + Database)
* Vercel (Frontend)

---

## ⚙️ Architecture Overview

```
User → React Frontend
     → FastAPI Backend
     → AI Agent (OpenRouter)
     → Tool Execution (DB / Booking / Stats / Notifications)
     → Response → UI
```

---

## 🔌 API Endpoints

| Endpoint                     | Description          |
| ---------------------------- | -------------------- |
| `/chat`                      | AI interaction       |
| `/login/patient`             | Patient login        |
| `/login/doctor`              | Doctor login         |
| `/notifications/{doctor_id}` | Doctor notifications |

---

## 📦 Local Setup

### 1. Clone Repo

```
git clone https://github.com/yourusername/doctor-assistant.git
cd doctor-assistant
```

---

### 2. Backend Setup

```
cd backend
pip install -r requirements.txt
```

Create `.env`:

```
DATABASE_URL=postgresql://...
OPENROUTER_API_KEY=your_key
MAILTRAP_TOKEN=your_token
MAILTRAP_INBOX_ID=your_id
```

Run backend:

```
uvicorn app.main:app --reload
```

---

### 3. Frontend Setup

```
cd frontend
npm install
```

Create `.env`:

```
VITE_API_URL=http://localhost:8000
```

Run frontend:

```
npm run dev
```

---

## 🌐 Deployment

* Backend → Render
* Database → Render PostgreSQL
* Frontend → Vercel

---

## 🧪 Demo Flow

1. Login as patient
2. Ask for availability
3. Book appointment
4. Switch to doctor view
5. View notification + updated schedule
6. Cancel appointment

---

## 📸 Screenshots

*(Add after deployment)*

---

## 🐳 Docker

Docker setup included for local development (optional).

---

## 🧠 Future Improvements

* Role-based tool separation
* Better model routing (Groq / paid APIs)
* WebSocket-based notifications
* Authentication (JWT)
* Calendar integrations

---

## 📄 License

MIT License

---

## 🙌 Author

**Rudra Pratap Singh**
BTech CSE | Systems & AI Enthusiast

---
