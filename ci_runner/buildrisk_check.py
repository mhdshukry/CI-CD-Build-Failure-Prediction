import sys
import os


sys.path.append(
    os.getcwd()
)


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



prediction = predict_build_risk(commit)



print()

print("Commit:")
print(commit["commit_id"])


print()

print("Risk Score:")

print(
    prediction["final_failure_risk_score"],
    "%"
)


print()

print("Risk Level:")

print(
    prediction["risk_level"]
)



print()

print("Reasons:")


for reason in prediction["reasons"]:

    print(
        "-",
        reason
    )


print()

print("Suggestions:")


for suggestion in prediction["suggestions"]:

    print(
        "-",
        suggestion
    )



# block very dangerous builds

if prediction["final_failure_risk_score"] >= 90:


    print()
    print(
        "Build blocked because risk is too high"
    )


    sys.exit(1)


else:

    print()
    print(
        "Build allowed"
    )


    sys.exit(0)