import csv
import os
from datetime import datetime

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from api.risk_analyzer import predict_build_risk
from local_analyzer.local_repo_analyzer import analyze_latest_commit


app = FastAPI(
    title="CI/CD Build Failure Risk Prediction API",
    description="AI-based CI/CD build failure risk prediction with explainable suggestions",
    version="4.0"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class CommitData(BaseModel):
    files_changed: int
    lines_added: int
    lines_deleted: int
    total_changes: int
    dependency_file_changed: int
    test_file_changed: int
    workflow_changed: int
    source_file_changed: int
    risk_file_count: int
    changed_files: str = ""
    previous_build_status: str = "unknown"
    previous_error_message: str = ""
    previous_failed_step: str = ""


class LocalRepoPath(BaseModel):
    repo_path: str
    previous_build_status: str = "unknown"
    previous_error_message: str = ""
    previous_failed_step: str = ""


def save_prediction_history(source, commit_id, result):
    os.makedirs("history", exist_ok=True)

    file_path = "history/prediction_history.csv"

    file_exists = (
        os.path.exists(file_path)
        and os.path.getsize(file_path) > 0
    )

    with open(file_path, "a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        if not file_exists:
            writer.writerow([
                "timestamp",
                "source",
                "commit_id",
                "risk_score",
                "risk_level",
                "prediction",
                "ml_probability",
                "rule_score",
                "error_category"
            ])

        writer.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            source,
            commit_id,
            result.get("final_failure_risk_score"),
            result.get("risk_level"),
            result.get("prediction"),
            result.get("ml_failure_probability"),
            result.get("rule_based_risk_score"),
            result.get("error_category")
        ])


@app.get("/")
def home():
    return {
        "message": "CI/CD Build Failure Risk Prediction API is running",
        "version": "4.0",
        "endpoints": [
            "/predict",
            "/analyze-local-repo",
            "/history"
        ]
    }


@app.post("/predict")
def predict(data: CommitData):
    result = predict_build_risk(data.dict())

    save_prediction_history(
        "manual",
        "manual-input",
        result
    )

    return result


@app.post("/analyze-local-repo")
def analyze_local_repo(data: LocalRepoPath):
    commit_data = analyze_latest_commit(data.repo_path)

    if "error" in commit_data:
        return commit_data

    commit_data["previous_build_status"] = data.previous_build_status
    commit_data["previous_error_message"] = data.previous_error_message
    commit_data["previous_failed_step"] = data.previous_failed_step

    prediction = predict_build_risk(commit_data)

    save_prediction_history(
        "local-repo",
        commit_data.get("commit_id", "unknown"),
        prediction
    )

    return {
        "commit_analysis": commit_data,
        "prediction": prediction
    }


@app.get("/history")
def get_prediction_history():
    file_path = "history/prediction_history.csv"

    if not os.path.exists(file_path):
        return {
            "history": []
        }

    history = []

    with open(file_path, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            history.append(row)

    return {
        "history": history[-20:]
    }