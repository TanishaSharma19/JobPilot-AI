import os
from google.cloud import firestore
from google.oauth2 import service_account

PROJECT_ID = "master-choir-506517-b8"
DATABASE_ID = "jobpilot-db"

credentials_json = os.getenv("GOOGLE_APPLICATION_CREDENTIALS_JSON")

if credentials_json:
    credentials = service_account.Credentials.from_service_account_info(
        __import__("json").loads(credentials_json)
    )

    db = firestore.Client(
        project=PROJECT_ID,
        database=DATABASE_ID,
        credentials=credentials,
    )
else:
    db = firestore.Client(
        project=PROJECT_ID,
        database=DATABASE_ID,
    )


def get_user_by_email(email: str):
    users = db.collection("users").where("email", "==", email).limit(1).stream()
    for user in users:
        data = user.to_dict()
        data["user_id"] = user.id
        return data
    return None


def get_user_by_id(user_id: str):
    user = db.collection("users").document(user_id).get()
    if not user.exists:
        return None
    data = user.to_dict()
    data["user_id"] = user.id
    return data


def create_user(user_id: str, email: str, name: str, password_hash: str):
    db.collection("users").document(user_id).set({
        "email": email,
        "name": name,
        "password_hash": password_hash,
        "created_at": firestore.SERVER_TIMESTAMP,
    })


def update_user_password(user_id: str, password_hash: str):
    db.collection("users").document(user_id).update({
        "password_hash": password_hash,
        "reset_token_hash": firestore.DELETE_FIELD,
        "reset_token_expires_at": firestore.DELETE_FIELD,
    })


def save_password_reset(user_id: str, token_hash: str, expires_at):
    db.collection("users").document(user_id).update({
        "reset_token_hash": token_hash,
        "reset_token_expires_at": expires_at,
    })


def get_user_by_reset_token(token_hash: str):
    for user in db.collection("users").where("reset_token_hash", "==", token_hash).limit(1).stream():
        data = user.to_dict()
        data["user_id"] = user.id
        return data
    return None


def save_job_analysis(
    user_id: str,
    job_description: str,
    candidate_profile: str,
    analysis: dict,
):
    doc_ref = (
        db.collection("users")
        .document(user_id)
        .collection("job_analyses")
        .document()
    )

    doc_ref.set({
        "user_id": user_id,
        "job_description": job_description,
        "candidate_profile": candidate_profile,
        "analysis": analysis,
        "status": "Analyzed",
        "created_at": firestore.SERVER_TIMESTAMP,
    })

    return doc_ref.id


def get_job_analyses(user_id: str):
    docs = (
        db.collection("users")
        .document(user_id)
        .collection("job_analyses")
        .order_by("created_at", direction=firestore.Query.DESCENDING)
        .stream()
    )

    analyses = []

    for doc in docs:
        data = doc.to_dict()
        data["analysis_id"] = doc.id
        analyses.append(data)

    return analyses


def update_job_analysis_status(user_id: str, analysis_id: str, status: str):
    doc_ref = db.collection("users").document(user_id).collection("job_analyses").document(analysis_id)
    if not doc_ref.get().exists:
        return False
    doc_ref.update({"status": status})
    return True
