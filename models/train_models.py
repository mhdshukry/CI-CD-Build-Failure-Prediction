import pandas as pd

from sklearn.model_selection import train_test_split

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix
)

from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier

from xgboost import XGBClassifier

import joblib
import os


# ==========================
# Load Dataset
# ==========================

df = pd.read_csv(
    "data/processed/final_ml_dataset.csv"
)


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


X = df[features]


y = df["build_result"]



# ==========================
# Split Data
# ==========================


X_train, X_test, y_train, y_test = train_test_split(

    X,

    y,

    test_size=0.2,

    random_state=42,

    stratify=y

)



models = {


"Logistic Regression":

LogisticRegression(
max_iter=1000
),



"Decision Tree":

DecisionTreeClassifier(),



"Random Forest":

RandomForestClassifier(
n_estimators=200,
random_state=42,
class_weight="balanced"
),



"XGBoost":

XGBClassifier(
eval_metric="logloss"
)

}



results=[]



for name, model in models.items():

    print("\nTraining:", name)


    model.fit(
        X_train,
        y_train
    )


    prediction = model.predict(
        X_test
    )


    results.append({

        "Model":name,

        "Accuracy":
        accuracy_score(
            y_test,
            prediction
        ),


        "Precision":
        precision_score(
            y_test,
            prediction
        ),


        "Recall":
        recall_score(
            y_test,
            prediction
        ),


        "F1":
        f1_score(
            y_test,
            prediction
        )

    })


    print(
        confusion_matrix(
            y_test,
            prediction
        )
    )



result_df = pd.DataFrame(results)


print("\n========== RESULTS ==========")

print(result_df)



os.makedirs(
"models/saved",
exist_ok=True
)



best_model=models[
"Random Forest"
]


joblib.dump(

best_model,

"models/saved/build_failure_model.pkl"

)


print("\nModel saved successfully")
