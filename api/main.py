import csv
import os
from datetime import datetime

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from api.risk_analyzer import predict_build_risk
from github_analyzer.repository_analyzer import analyze_github_repository


app = FastAPI(
    title="CI/CD Build Failure Risk Prediction API",
    description="GitHub-based AI system for CI/CD build failure risk prediction",
    version="7.1"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class GitHubRepoRequest(BaseModel):
    repo_url: str
    github_token: str = ""


class ConnectedCommitData(BaseModel):
    repository: str = ""
    repo_url: str = ""
    commit_id: str
    commit_message: str = ""

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
    previous_failed_step: str = ""
    previous_error_message: str = ""


class PostBuildFeedback(BaseModel):
    commit_id: str
    repository: str = ""
    predicted_risk_score: float
    predicted_risk_level: str
    actual_result: str
    actual_error_message: str = ""
    failed_step: str = ""


def save_prediction_history(source, commit_id, repository, result):
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
                "repository",
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
            repository,
            commit_id,
            result.get("final_failure_risk_score"),
            result.get("risk_level"),
            result.get("prediction"),
            result.get("ml_failure_probability"),
            result.get("rule_based_risk_score"),
            result.get("error_category")
        ])


def save_post_build_feedback(data):
    os.makedirs("data/processed", exist_ok=True)

    file_path = "data/processed/post_build_feedback.csv"

    file_exists = (
        os.path.exists(file_path)
        and os.path.getsize(file_path) > 0
    )

    with open(file_path, "a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        if not file_exists:
            writer.writerow([
                "timestamp",
                "repository",
                "commit_id",
                "predicted_risk_score",
                "predicted_risk_level",
                "actual_result",
                "actual_error_message",
                "failed_step"
            ])

        writer.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            data.repository,
            data.commit_id,
            data.predicted_risk_score,
            data.predicted_risk_level,
            data.actual_result,
            data.actual_error_message,
            data.failed_step
        ])


@app.get("/")
def home():
    return {
        "message": "BuildRisk AI GitHub-based API is running",
        "version": "7.1",
        "workflow": {
            "step_1": "connect GitHub repository and fetch latest commit/build evidence",
            "step_2": "predict risk only after user clicks Predict Risk",
            "step_3": "save prediction history after prediction",
            "step_4": "show repository-specific prediction history",
            "step_5": "submit post-build feedback for learning"
        },
        "endpoints": [
            "/connect-github-repo",
            "/predict-connected-repo",
            "/history?repository=owner/repo",
            "/post-build-feedback"
        ]
    }


@app.post("/connect-github-repo")
def connect_github_repo(data: GitHubRepoRequest):
    commit_data = analyze_github_repository(
        data.repo_url,
        data.github_token
    )

    if "error" in commit_data:
        return commit_data

    return {
        "message": "GitHub repository connected successfully",
        "connection_status": "connected",
        "commit_analysis": commit_data
    }


@app.post("/predict-connected-repo")
def predict_connected_repo(data: ConnectedCommitData):
    commit_data = data.dict()

    prediction = predict_build_risk(commit_data)

    prediction["repository"] = commit_data.get("repository", "")

    save_prediction_history(
        "github-repo",
        commit_data.get("commit_id", "unknown"),
        commit_data.get("repository", ""),
        prediction
    )

    return {
        "commit_analysis": commit_data,
        "prediction": prediction
    }


@app.get("/history")
def get_prediction_history(repository: str = ""):
    file_path = "history/prediction_history.csv"

    if not os.path.exists(file_path):
        return {
            "history": []
        }

    history = []

    with open(file_path, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            if repository == "" or row.get("repository", "") == repository:
                history.append(row)

    return {
        "history": history[-100:]
    }


@app.post("/post-build-feedback")
def post_build_feedback(data: PostBuildFeedback):
    save_post_build_feedback(dat

    return {
        "message": "Post-build feedback saved successfully",
        "learning_status": "Feedback added to continuous learning dataset"
    }