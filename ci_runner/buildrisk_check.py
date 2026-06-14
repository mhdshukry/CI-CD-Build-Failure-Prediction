import sys
import os

sys.path.append(os.getcwd())

from local_analyzer.local_repo_analyzer import analyze_latest_commit
from api.risk_analyzer import predict_build_risk


print("==============================")
print("BuildRisk AI CI Scanner")
print("==============================")

repo_path = os.getcwd()

commit = analyze_latest_commit(repo_path)

if "error" in commit:
    print(commit["error"])
    sys.exit(1)


commit["previous_build_status"] = "unknown"
commit["previous_error_message"] = ""
commit["previous_failed_step"] = ""


prediction = predict_build_risk(commit)


print()
print("Commit:")
print(commit["commit_id"])

print()
print("Risk Score:")
print(prediction["final_failure_risk_score"], "%")

print()
print("Risk Level:")
print(prediction["risk_level"])

print()
print("Prediction:")
print(prediction["prediction"])

print()
print("Reasons:")
for reason in prediction["reasons"]:
    print("-", reason)

print()
print("Suggestions:")
for suggestion in prediction["suggestions"]:
    print("-", suggestion)


summary_path = os.environ.get("GITHUB_STEP_SUMMARY")

if summary_path:
    with open(summary_path, "a", encoding="utf-8") as summary:
        summary.write("# 🚀 BuildRisk AI Report\n\n")
        summary.write("| Item | Value |\n")
        summary.write("|---|---|\n")
        summary.write(f"| Commit | `{commit['commit_id']}` |\n")
        summary.write(f"| Risk Score | **{prediction['final_failure_risk_score']}%** |\n")
        summary.write(f"| Risk Level | **{prediction['risk_level']}** |\n")
        summary.write(f"| Prediction | **{prediction['prediction']}** |\n\n")

        summary.write("## ⚠️ Risk Reasons\n\n")
        for reason in prediction["reasons"]:
            summary.write(f"- {reason}\n")

        summary.write("\n## 🛠 Suggested Fixes\n\n")
        for suggestion in prediction["suggestions"]:
            summary.write(f"- {suggestion}\n")

        summary.write("\n## 📂 Risky Files\n\n")
        risky_files = prediction.get("risky_files", [])

        if risky_files:
            for file in risky_files:
                summary.write(f"- `{file}`\n")
        else:
            summary.write("- No risky files detected\n")


if prediction["final_failure_risk_score"] >= 90:
    print()
    print("Build blocked because risk is too high")
    sys.exit(1)
else:
    print()
    print("Build allowed")
    sys.exit(0)