import joblib
import pandas as pd


model = joblib.load("models/saved/best_build_failure_model.pkl")


features = [
    "files_changed",
    "lines_added",
    "lines_deleted",
    "total_changes",
    "dependency_file_changed",
    "test_file_changed",
    "workflow_changed",
    "source_file_changed",
    "risk_file_count"
]


def safe_number(data, key, default=0):
    try:
        return int(data.get(key, default))
    except Exception:
        return default


def safe_text(data, key, default=""):
    value = data.get(key, default)

    if value is None:
        return default

    return str(value)


def detect_error_category(error):
    e = str(error).lower()

    if e.strip() == "":
        return "No previous error available"

    if (
        "modulenotfounderror" in e
        or "cannot find module" in e
        or "dependency" in e
        or "no module named" in e
        or "module not found" in e
    ):
        return "Dependency Error"

    if (
        "syntaxerror" in e
        or "compilation" in e
        or "compile" in e
        or "build failed" in e
    ):
        return "Syntax / Compilation Error"

    if (
        "test failed" in e
        or "assertion" in e
        or "pytest" in e
        or "junit" in e
        or "failed tests" in e
    ):
        return "Test Failure"

    if "docker" in e:
        return "Docker Error"

    if "permission denied" in e:
        return "Permission Error"

    if (
        "yaml" in e
        or "workflow" in e
        or "github action" in e
        or "actions" in e
    ):
        return "CI/CD Workflow Error"

    return "General Build Error"


def find_risky_files(changed_files):
    risky_keywords = [
        "requirements.txt",
        "package.json",
        "package-lock.json",
        "yarn.lock",
        "pom.xml",
        "build.gradle",
        "composer.json",
        "pyproject.toml",
        "dockerfile",
        ".github/workflows",
        "settings.py",
        "application.properties",
        "application.yml",
        ".env",
        "env",
        "config"
    ]

    files = [
        f.strip()
        for f in str(changed_files).split(",")
        if f.strip()
    ]

    risky = []

    for file in files:
        low = file.lower()

        if any(key in low for key in risky_keywords):
            risky.append(file)

    return risky


def calculate_rule_score(data):
    files_changed = safe_number(data, "files_changed")
    total_changes = safe_number(data, "total_changes")
    dependency_changed = safe_number(data, "dependency_file_changed")
    workflow_changed = safe_number(data, "workflow_changed")
    test_changed = safe_number(data, "test_file_changed")
    source_changed = safe_number(data, "source_file_changed")
    risk_file_count = safe_number(data, "risk_file_count")

    previous_status = safe_text(
        data,
        "previous_build_status",
        "unknown"
    ).lower()

    previous_error = safe_text(
        data,
        "previous_error_message",
        ""
    ).strip()

    score = 0

    if files_changed >= 10:
        score += 15

    if total_changes >= 300:
        score += 20

    if dependency_changed == 1:
        score += 20

    if workflow_changed == 1:
        score += 20

    if test_changed == 0 and source_changed == 1:
        score += 15

    if risk_file_count >= 3:
        score += 10

    if previous_status == "failure":
        score += 15

    if previous_error != "":
        score += 10

    return min(score, 100)


def get_risk_level(score):
    if score >= 70:
        return "High Risk"

    if score >= 40:
        return "Medium Risk"

    return "Low Risk"


def generate_reasons(data):
    files_changed = safe_number(data, "files_changed")
    total_changes = safe_number(data, "total_changes")
    dependency_changed = safe_number(data, "dependency_file_changed")
    workflow_changed = safe_number(data, "workflow_changed")
    test_changed = safe_number(data, "test_file_changed")
    source_changed = safe_number(data, "source_file_changed")

    previous_status = safe_text(
        data,
        "previous_build_status",
        "unknown"
    ).lower()

    previous_error = safe_text(
        data,
        "previous_error_message",
        ""
    ).strip()

    reasons = []

    if files_changed >= 10:
        reasons.append("Large number of files changed")

    if total_changes >= 300:
        reasons.append("High code churn detected")

    if dependency_changed == 1:
        reasons.append("Dependency or configuration file changed")

    if workflow_changed == 1:
        reasons.append("CI/CD workflow file changed")

    if test_changed == 0 and source_changed == 1:
        reasons.append("Source code changed but test files were not updated")

    if previous_status == "failure":
        reasons.append("Previous CI/CD build failed")

    if previous_error != "":
        reasons.append("Previous build error evidence detected")

    if not reasons:
        reasons.append("No major risk pattern detected")

    return reasons


def generate_suggestions(data, error_category, risky_files):
    dependency_changed = safe_number(data, "dependency_file_changed")
    workflow_changed = safe_number(data, "workflow_changed")
    total_changes = safe_number(data, "total_changes")
    files_changed = safe_number(data, "files_changed")
    test_changed = safe_number(data, "test_file_changed")
    source_changed = safe_number(data, "source_file_changed")

    suggestions = []

    if dependency_changed == 1 or error_category == "Dependency Error":
        suggestions.append(
            "Check dependency versions and update requirements/package/build files"
        )

    if workflow_changed == 1 or error_category == "CI/CD Workflow Error":
        suggestions.append(
            "Validate GitHub Actions workflow YAML syntax"
        )

    if total_changes >= 300:
        suggestions.append(
            "Review large code changes carefully before CI execution"
        )

    if test_changed == 0 and source_changed == 1:
        suggestions.append(
            "Add or update related test cases before running CI"
        )

    if files_changed >= 10:
        suggestions.append(
            "Split large commit into smaller commits if possible"
        )

    if error_category == "Test Failure":
        suggestions.append(
            "Run local unit tests and fix failing test cases"
        )

    if error_category == "Docker Error":
        suggestions.append(
            "Check Dockerfile, image version and build command"
        )

    if risky_files:
        suggestions.append(
            "Review risky files before pushing: "
            + ", ".join(risky_files[:5])
        )

    if not suggestions:
        suggestions.append(
            "Run standard local tests before pushing"
        )

    return suggestions


def build_model_input(input_data):
    clean_data = {}

    for feature in features:
        clean_data[feature] = safe_number(input_data, feature)

    return pd.DataFrame([clean_data])[features]


def predict_build_risk(input_data):
    df = build_model_input(input_data)

    ml_probability = float(model.predict_proba(df)[0][1] * 100)

    rule_score = calculate_rule_score(input_data)

    final_score = round(
        (ml_probability * 0.6)
        + (rule_score * 0.4),
        2
    )

    previous_error = safe_text(
        input_data,
        "previous_error_message",
        ""
    )

    error_category = detect_error_category(previous_error)

    risky_files = find_risky_files(
        safe_text(
            input_data,
            "changed_files",
            ""
        )
    )

    return {
        "ml_failure_probability": round(ml_probability, 2),
        "rule_based_risk_score": rule_score,
        "final_failure_risk_score": final_score,
        "prediction": (
            "Failure Risk Detected"
            if final_score >= 40
            else "Likely Success"
        ),
        "risk_level": get_risk_level(final_score),
        "previous_build_status": safe_text(
            input_data,
            "previous_build_status",
            "unknown"
        ),
        "previous_error_message": safe_text(
            input_data,
            "previous_error_message",
            ""
        ),
        "previous_failed_step": safe_text(
            input_data,
            "previous_failed_step",
            ""
        ),
        "error_category": error_category,
        "risky_files": risky_files,
        "reasons": generate_reasons(input_data),
        "suggestions": generate_suggestions(
            input_data,
            error_category,
            risky_files
        ),
        "post_build_learning_status": (
            "Ready to update dataset after actual CI/CD result"
        )
    }