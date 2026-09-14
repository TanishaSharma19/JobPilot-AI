# 🤖 JobPilot AI

### Agentic AI Career Assistant

JobPilot AI is a full-stack **Agentic AI career assistant** that helps job seekers understand job opportunities, analyze their fit, identify skill gaps, and receive personalized career guidance using AI.

The project combines a **React frontend**, **FastAPI backend**, and **Google ADK + Gemini** to create an AI-powered career analysis workflow.

---

## ✨ Features

* 🔐 User authentication
* 💼 Job description analysis
* 🎯 Job–candidate matching
* 📊 Skill and gap analysis
* 🤖 AI-powered career recommendations
* 📚 Previous analysis history

---

## 🏗️ Architecture

```text
                    ┌──────────────────┐
                    │      User        │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │ React Frontend   │
                    └────────┬─────────┘
                             │ REST API
                             ▼
                    ┌──────────────────┐
                    │  FastAPI Backend │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │  Google ADK      │
                    │   AI Agent       │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │ Gemini / GenAI   │
                    └────────┬─────────┘
                             │
                             ▼
               ┌────────────────────────────┐
               │ Career Analysis & Insights │
               └────────────────────────────┘
```

---

## 🛠️ Tech Stack

### Frontend

* React.js
* JavaScript
* HTML5
* CSS3

### Backend

* Python
* FastAPI
* Pydantic
* Uvicorn

### AI / Agentic AI

* Google ADK
* Gemini
* Google GenAI
* AI Agent Workflows

### Data & Services

* Firebase / Firestore
* REST APIs
* Session Management

---

## 🔄 How It Works

1. User creates an account and logs in.
2. User provides a job description.
3. JobPilot sends the candidate and job information to the FastAPI backend.
4. The Google ADK agent processes the request using Gemini.
5. The system evaluates the candidate's fit for the role.
6. The user receives relevant strengths, skill gaps, and career recommendations.

---

## 📂 Project Structure

```text
JobPilot-AI/
│
├── backend/
│   ├── app/
│   ├── agent/
│   ├── services/
│   └── ...
│
├── frontend/
│   ├── src/
│   └── ...
│
└── README.md
```

---

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/TanishaSharma19/JobPilot-AI.git
cd JobPilot-AI
```

### 2. Backend Setup

```bash
cd backend

python -m venv .venv
```

#### Windows

```powershell
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Configure the required environment variables in `.env`.

Start the backend:

```bash
uvicorn app.main:app --reload
```

Backend:

```text
http://127.0.0.1:8000
```

API documentation:

```text
http://127.0.0.1:8000/docs
```

### 3. Frontend Setup

Open another terminal:

```bash
cd frontend
npm install
npm run dev
```

Open the frontend URL shown by the development server.

---

## 🔑 Environment Variables

Create a `.env` file for your local configuration and add the required credentials.

**Never commit API keys, service-account credentials, or other secrets to GitHub.**

For deployment, configure secrets through the hosting platform's environment-variable settings.

---

## 📌 API

Key backend functionality includes:

| Endpoint            | Purpose                       |
| ------------------- | ----------------------------- |
| `POST /auth/login`  | User authentication           |
| `GET /auth/me`      | Current user information      |
| `POST /analyze-job` | Analyze job and candidate fit |
| `GET /analyses`     | Retrieve previous analyses    |
| `GET /insights`     | Retrieve career insights      |

---

## 🎯 Project Goal

JobPilot AI was built to explore how **Agentic AI can be applied to real-world career workflows**.

The project demonstrates practical experience with:

* AI agent development
* LLM integration
* REST API development
* Full-stack application architecture
* Authentication
* AI-powered decision support
* Frontend–backend integration

---

## 👩‍💻 Author

**Tanisha Sharma**

[GitHub](https://github.com/TanishaSharma19) · [LinkedIn](https://www.linkedin.com/in/tanisha-sharma2019/)
