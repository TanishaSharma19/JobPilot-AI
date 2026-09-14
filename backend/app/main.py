from fastapi import Depends, FastAPI, Header, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
load_dotenv()
from datetime import datetime, timedelta, timezone
import base64
import hashlib
import hmac
import json
import os
import secrets

from app.schemas import JobAnalysisResult

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from app.agent.jobpilot_workflow import jobpilot_workflow
from services.firestore_service import (
    create_user,
    get_job_analyses,
    get_user_by_email,
    get_user_by_id,
    get_user_by_reset_token,
    save_job_analysis,
    save_password_reset,
    update_job_analysis_status,
    update_user_password,
)

app = FastAPI(
    title="JobPilot AI",
    description="Agentic AI Career Assistant",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

session_service = InMemorySessionService()
TOKEN_SECRET = os.getenv("JOBPILOT_TOKEN_SECRET", "local-development-secret-change-me").encode()
runner = Runner(
    agent=jobpilot_workflow,
    app_name="jobpilot_ai",
    session_service=session_service,
)


class JobAnalysisRequest(BaseModel):
    job_description: str
    candidate_profile: str


class AuthRequest(BaseModel):
    email: str
    password: str
    name: str = ""


class ForgotPasswordRequest(BaseModel):
    email: str


class ResetPasswordRequest(BaseModel):
    token: str
    password: str


class StatusRequest(BaseModel):
    status: str


class JobAnalysisResponse(BaseModel):
    status: str
    agent: str
    analysis_id: str
    analysis: JobAnalysisResult


def hash_password(password: str, salt: bytes | None = None):
    salt = salt or secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 240_000)
    return f"{base64.urlsafe_b64encode(salt).decode()}${base64.urlsafe_b64encode(digest).decode()}"


def verify_password(password: str, stored_hash: str):
    try:
        salt_encoded, digest_encoded = stored_hash.split("$", 1)
        expected = hash_password(password, base64.urlsafe_b64decode(salt_encoded))
        return hmac.compare_digest(expected.split("$", 1)[1], digest_encoded)
    except (ValueError, TypeError):
        return False


def create_token(user_id: str):
    payload = f"{user_id}:{int((datetime.now(timezone.utc) + timedelta(days=7)).timestamp())}"
    encoded = base64.urlsafe_b64encode(payload.encode()).decode().rstrip("=")
    signature = hmac.new(TOKEN_SECRET, encoded.encode(), hashlib.sha256).hexdigest()
    return f"{encoded}.{signature}"


def get_current_user(authorization: str | None = Header(default=None)):
    authorization = authorization or ""
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Sign in required")
    try:
        encoded, signature = authorization[7:].split(".", 1)
        expected = hmac.new(TOKEN_SECRET, encoded.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(signature, expected):
            raise ValueError
        user_id, expires_at = base64.urlsafe_b64decode(encoded + "===").decode().split(":", 1)
        if int(expires_at) < datetime.now(timezone.utc).timestamp():
            raise ValueError
    except (ValueError, TypeError, UnicodeDecodeError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired session")
    user = get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


def public_user(user: dict):
    return {"user_id": user["user_id"], "email": user["email"], "name": user.get("name", "")}


@app.get("/")
def root():
    return {
        "message": "JobPilot AI is running 🚀"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


@app.post("/auth/register")
def register(request: AuthRequest):
    email = request.email.strip().lower()
    if len(request.password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters")
    if "@" not in email:
        raise HTTPException(status_code=400, detail="Enter a valid email address")
    if get_user_by_email(email):
        raise HTTPException(status_code=409, detail="An account with this email already exists")
    user_id = hashlib.sha256(email.encode()).hexdigest()[:24]
    name = request.name.strip() or email.split("@")[0]
    create_user(user_id, email, name, hash_password(request.password))
    user = {"user_id": user_id, "email": email, "name": name}
    return {"token": create_token(user_id), "user": public_user(user)}


@app.post("/auth/login")
def login(request: AuthRequest):
    user = get_user_by_email(request.email.strip().lower())
    if not user or not verify_password(request.password, user.get("password_hash", "")):
        raise HTTPException(status_code=401, detail="Email or password is incorrect")
    return {"token": create_token(user["user_id"]), "user": public_user(user)}


@app.get("/auth/me")
def me(user: dict = Depends(get_current_user)):
    return {"user": public_user(user)}


@app.post("/auth/forgot-password")
def forgot_password(request: ForgotPasswordRequest):
    user = get_user_by_email(request.email.strip().lower())
    if not user:
        return {"message": "If an account exists, password reset instructions have been prepared."}
    reset_token = secrets.token_urlsafe(32)
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=30)
    save_password_reset(user["user_id"], hashlib.sha256(reset_token.encode()).hexdigest(), expires_at)
    return {"message": "Password reset token created. Use it to set a new password.", "reset_token": reset_token}


@app.post("/auth/reset-password")
def reset_password(request: ResetPasswordRequest):
    token_hash = hashlib.sha256(request.token.encode()).hexdigest()
    user = get_user_by_reset_token(token_hash)
    if not user:
        raise HTTPException(status_code=400, detail="Invalid reset token")
    expires_at = user.get("reset_token_expires_at")
    if not expires_at or expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="Reset token has expired")
    if len(request.password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters")
    update_user_password(user["user_id"], hash_password(request.password))
    return {"message": "Password updated successfully"}


@app.post("/analyze-job", response_model=JobAnalysisResponse)
async def analyze_job(request: JobAnalysisRequest, user: dict = Depends(get_current_user)):
    user_id = user["user_id"]
    session_id = f"jobpilot_session_{user_id}"

    session = await session_service.get_session(
        app_name="jobpilot_ai",
        user_id=user_id,
        session_id=session_id,
    )

    if session is None:
        await session_service.create_session(
            app_name="jobpilot_ai",
            user_id=user_id,
            session_id=session_id,
        )

    prompt = f"""
    Analyze this job opportunity for the candidate.

    JOB DESCRIPTION:
    {request.job_description}

    CANDIDATE PROFILE:
    {request.candidate_profile}

    Return the complete JobPilot analysis using the required output schema.

    Do not invent qualifications or experience.
    """

    message = types.Content(
        role="user",
        parts=[
            types.Part(text=prompt)
        ],
    )

    final_response = None

    async for event in runner.run_async(
        user_id=user_id,
        session_id=session_id,
        new_message=message,
    ):
        if event.is_final_response():
            if event.content and event.content.parts:
                final_response = event.content.parts[0].text

    try:
        analysis = json.loads(final_response)
    except (json.JSONDecodeError, TypeError):
        analysis = {
            "raw_response": final_response
        }

    analysis_id = save_job_analysis(
        user_id=user_id,
        job_description=request.job_description,
        candidate_profile=request.candidate_profile,
        analysis=analysis,
    )

    return {
        "status": "success",
        "agent": jobpilot_workflow.name,
        "analysis_id": analysis_id,
        "analysis": analysis,
    }


@app.get("/analyses")
def get_analyses(user: dict = Depends(get_current_user)):
    analyses = get_job_analyses(user["user_id"])
    return {"status": "success", "count": len(analyses), "analyses": analyses}


@app.patch("/analyses/{analysis_id}/status")
def update_analysis_status(analysis_id: str, request: StatusRequest, user: dict = Depends(get_current_user)):
    allowed_statuses = {"Analyzed", "Applied", "Interview", "Offer", "Archived"}
    if request.status not in allowed_statuses:
        raise HTTPException(status_code=400, detail="Unsupported application status")
    if not update_job_analysis_status(user["user_id"], analysis_id, request.status):
        raise HTTPException(status_code=404, detail="Analysis not found")
    return {"status": request.status}
