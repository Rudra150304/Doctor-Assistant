
# 🩺 Doctor Assistant (AI-Powered)

An AI-powered full-stack application that enables patients to book appointments and helps doctors manage schedules, stats, and real-time notifications — all through a conversational AI agent.

---

## 🚀 Live Demo

Frontend: [https://your-app.vercel.app](https://doctor-assistant-95spgrr6o-rudra150304s-projects.vercel.app/)

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

<img width="1920" height="1043" alt="image" src="https://github.com/user-attachments/assets/4bbb7f13-db86-4842-aa8e-85bf8e6fe47c" />
<img width="1920" height="1043" alt="image" src="https://github.com/user-attachments/assets/eb34151d-ab91-423d-8f97-791d4da72a84" />
<img width="1920" height="1043" alt="image" src="https://github.com/user-attachments/assets/5c0a8fd2-a724-4bb3-9d1e-15e2a6c2fd6f" />
<img width="1920" height="1043" alt="image" src="https://github.com/user-attachments/assets/e4de31fe-433c-4783-9b01-ce85655247a8" />
<img width="1920" height="1043" alt="image" src="https://github.com/user-attachments/assets/a2bc5f31-1b36-47f0-9855-89029050dbc0" />

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
