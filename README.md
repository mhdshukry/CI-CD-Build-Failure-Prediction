# CI/CD Build Failure Prediction
<img width="1920" height="3077" alt="Image" src="https://github.com/user-attachments/assets/134c2682-fc00-416e-aad8-23432b2c8975" />

This project predicts the risk of a CI/CD build failure from GitHub repository and commit signals. It combines repository analysis, feature engineering, and a trained machine learning model exposed through a FastAPI service.

## What It Does

- Analyzes a GitHub repository and its latest commit/build evidence.
- Predicts build failure risk using commit-level features such as files changed, lines added, workflow changes, and test changes.
- Stores prediction history in `history/prediction_history.csv`.
- Saves optional post-build feedback in `data/processed/post_build_feedback.csv` for continuous learning.

## Project Structure

- `api/` - FastAPI application and prediction logic.
- `ci_runner/` - CI-related helper scripts.
- `dashboard/` - Static dashboard UI.
- `data/raw/` - Raw source datasets.
- `data/processed/` - Cleaned and merged datasets used for training.
- `dataset_collector/` - Scripts for collecting GitHub data.
- `github_analyzer/` - GitHub repository analysis utilities.
- `local_analyzer/` - Local repository analysis utilities.
- `models/` - Model training scripts and saved model artifacts.
- `preprocessing/` - Dataset cleaning and dataset-building scripts.
- `reports/` - Training results and generated figures.

## Requirements

Install the Python dependencies from `requirements.txt`:

```bash
pip install -r requirements.txt
```

## Run the API

Start the FastAPI server with Uvicorn:

```bash
uvicorn api.main:app --reload
```

After it starts, open:

- `http://127.0.0.1:8000/` for the API status response
- `http://127.0.0.1:8000/docs` for the interactive Swagger UI

## Main API Endpoints

- `GET /` - Service status and workflow summary.
- `POST /connect-github-repo` - Analyze a GitHub repository.
- `POST /predict-connected-repo` - Predict build failure risk from collected commit data.
- `GET /history?repository=owner/repo` - View recent prediction history.
- `POST /post-build-feedback` - Save actual build feedback.

## Train or Refresh the Model

The active model used by `api/risk_analyzer.py` is saved at `models/saved/best_build_failure_model.pkl`.

To retrain and regenerate the model artifact, run:

```bash
python models/train_improved_models.py
```

This script reads `data/processed/final_ml_dataset.csv`, trains candidate models, saves the best model, and generates `reports/model_results.csv` plus `reports/figures/feature_importance.png`.

## Build the Final Dataset

If you need to rebuild the processed training dataset, run the preprocessing scripts in this order:

```bash
python preprocessing/clean_build_history.py
python preprocessing/create_final_dataset.py
```

## Optional Local Analysis

You can analyze a local repository with the scripts in `local_analyzer/`, or inspect the latest commit using the helper test script:

```bash
python local_analyzer/test_local_repo.py
```

## Notes

- The API writes prediction history to `history/prediction_history.csv`.
- The feedback endpoint writes to `data/processed/post_build_feedback.csv`.
- If the model file is missing, retrain it with `models/train_improved_models.py` before calling the prediction endpoint.
