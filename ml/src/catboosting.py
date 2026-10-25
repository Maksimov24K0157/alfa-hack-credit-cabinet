
from pathlib import Path

import pandas as pd
from catboost import CatBoostClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix


BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "synthetic_data.csv"
MODEL_PATH = BASE_DIR / "catboost_model.cbm"

NUMERIC_FEATURES = [
    "company_age",
    "revenue_last_year",
    "net_profit",
    "existing_debt",
    "requested_amount",
]

CATEGORICAL_FEATURES = [
    "industry_okved",
    "credit_history_status",
    "loan_purpose",
]

FEATURES = NUMERIC_FEATURES + CATEGORICAL_FEATURES


def train_model():
    dff = pd.read_csv(DATA_PATH)
    df = dff.drop(columns=["company_id"])
    X = df[FEATURES].copy()
    y = df["target_risk_class"]

    for col in CATEGORICAL_FEATURES:
        X[col] = X[col].fillna("unknown").astype(str)

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y,
    )

    model = CatBoostClassifier(
        iterations=500,
        learning_rate=0.05,
        depth=6,
        loss_function="MultiClass",
        auto_class_weights="Balanced",
        random_seed=42,
        verbose=100,
    )

    model.fit(
        X_train,
        y_train,
        cat_features=CATEGORICAL_FEATURES,
    )

    y_pred = model.predict(X_test).ravel()

    print("\nAccuracy:", round(accuracy_score(y_test, y_pred), 4))
    print(classification_report(y_test, y_pred, zero_division=0))
    print("Class order:", model.classes_)
    print(confusion_matrix(y_test, y_pred, labels=model.classes_))

    model.save_model(str(MODEL_PATH))
    print(f"\nМодель сохранена: {MODEL_PATH}")

    return model


def predict_risk(company_data: dict) -> dict:
    missing = [key for key in FEATURES if key not in company_data]
    if missing:
        raise ValueError(f"Missing features: {missing}")

    row = {key: company_data[key] for key in FEATURES}

    for col in CATEGORICAL_FEATURES:
        row[col] = (
            "unknown" if row[col] is None else str(row[col])
        )

    X_new = pd.DataFrame([row], columns=FEATURES)

    model = CatBoostClassifier()
    model.load_model(str(MODEL_PATH))

    prediction = str(model.predict(X_new)[0][0])
    probabilities = model.predict_proba(X_new)[0]

    return {
        "risk_class": prediction,
        "class_probabilities": {
            str(label): round(float(prob), 4)
            for label, prob in zip(model.classes_, probabilities)
        },
    }


if __name__ == "__main__":
    train_model()

    example_company = {
        "company_age": 5,
        "revenue_last_year": 10000000,
        "net_profit": 1000000,
        "existing_debt": 2000000,
        "requested_amount": 3000000,
        "industry_okved": "IT",
        "credit_history_status": "good",
        "loan_purpose": "working_capital",
    }

    print(predict_risk(example_company))