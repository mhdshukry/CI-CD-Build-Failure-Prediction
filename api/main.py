from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from api.risk_analyzer import predict_build_risk

app = FastAPI(
    title="CI/CD Build Failure Risk Prediction API",
    description="AI-based CI/CD build failure risk prediction with explainable suggestions",
    version="2.0"
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

@app.get("/")
def home():
    return {"message": "CI/CD Build Failure Risk Prediction API is running"}

@app.post("/predict")
def predict(data: CommitData):
    return predict_build_risk(data.dict())