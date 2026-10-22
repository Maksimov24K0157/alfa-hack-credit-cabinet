from pathlib import Path

import pandas as pd
from catboost import CatBoostClassifier

MODEL_PATH = (
    Path(__file__).resolve().parent.parent
    / "models"
    / "catboost_model.cbm"
)

model = CatBoostClassifier()
model.load_model(str(MODEL_PATH))

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


def predict_risk(company_data: dict) -> dict:
    """
    Принимает параметры компании и возвращает класс риска
    и вероятности, рассчитанные моделью.
    """

    missing = [key for key in FEATURES if key not in company_data]
    if missing:
        raise ValueError(f"Missing features: {missing}")

    row = {key: company_data[key] for key in FEATURES}

    for key in CATEGORICAL_FEATURES:
        if row[key] is None:
            row[key] = "unknown"
        else:
            row[key] = str(row[key])

    X = pd.DataFrame([row], columns=FEATURES)

    prediction = str(model.predict(X)[0][0])
    probabilities = model.predict_proba(X)[0]

    probability_by_class = {
        str(label): round(float(prob), 4)
        for label, prob in zip(model.classes_, probabilities)
    }

    return {
        "risk_class": prediction,
        "class_probabilities": probability_by_class,
    }