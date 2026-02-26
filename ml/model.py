"""
AI Risk Prediction Model
Uses RandomForest with simulated dataset for post-discharge recovery risk classification
Risk Levels: 0=Low, 1=Moderate, 2=High, 3=Critical
"""

import numpy as np
import pickle
import os
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

# ─────────────────────────────────────────
# 1. SIMULATE DATASET
# ─────────────────────────────────────────
def generate_dataset(n=2000):
    np.random.seed(42)
    data = []

    for _ in range(n):
        pain_score = np.random.randint(0, 11)          # 0-10
        swelling = np.random.randint(0, 4)              # 0=none,1=mild,2=mod,3=severe
        fever = round(np.random.uniform(97.0, 104.5), 1)
        mobility = np.random.randint(0, 11)             # 0=bedridden, 10=full
        wound_status = np.random.randint(0, 3)         # 0=clean,1=redness,2=discharge
        medication_adherence = np.random.randint(0, 11) # 0-10
        days_post_surgery = np.random.randint(1, 60)
        surgery_type = np.random.randint(0, 5)         # 0-4 types
        pain_trend = np.random.choice([-1, 0, 1, 1])  # -1=improving,0=stable,1=worsening

        # ── Risk Label Logic ──
        risk = 0  # Low

        if fever >= 101.5 or wound_status == 2:
            risk = 3  # Critical
        elif pain_score >= 8 or swelling == 3:
            risk = 2  # High
        elif pain_score >= 6 or swelling == 2 or fever >= 100.4:
            risk = 1  # Moderate
        elif pain_trend == 1 and pain_score >= 5:
            risk = 1
        elif mobility <= 2 and days_post_surgery > 14:
            risk = 2

        data.append([
            pain_score, swelling, fever, mobility,
            wound_status, medication_adherence,
            days_post_surgery, surgery_type, pain_trend, risk
        ])

    return np.array(data)


# ─────────────────────────────────────────
# 2. TRAIN & SAVE MODEL
# ─────────────────────────────────────────
def train_and_save():
    dataset = generate_dataset(2000)
    X = dataset[:, :-1]
    y = dataset[:, -1].astype(int)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = RandomForestClassifier(n_estimators=100, random_state=42, class_weight='balanced')
    model.fit(X_train, y_train)

    print("Model Accuracy Report:")
    print(classification_report(y_test, model.predict(X_test),
          target_names=["Low", "Moderate", "High", "Critical"]))

    # Save model
    model_path = os.path.join(os.path.dirname(__file__), "risk_model.pkl")
    with open(model_path, "wb") as f:
        pickle.dump(model, f)
    print(f"✅ Model saved to {model_path}")
    return model


# ─────────────────────────────────────────
# 3. LOAD MODEL & PREDICT
# ─────────────────────────────────────────
def load_model():
    model_path = os.path.join(os.path.dirname(__file__), "risk_model.pkl")
    if not os.path.exists(model_path):
        return train_and_save()
    with open(model_path, "rb") as f:
        return pickle.load(f)


RISK_LABELS = {0: "Low", 1: "Moderate", 2: "High", 3: "Critical"}
RISK_COLORS = {0: "#22c55e", 1: "#f59e0b", 2: "#f97316", 3: "#ef4444"}


def predict_risk(features: dict) -> dict:
    """
    features: dict with keys:
      pain_score, swelling, fever, mobility, wound_status,
      medication_adherence, days_post_surgery, surgery_type, pain_trend
    """
    model = load_model()

    surgery_map = {
        "Minor Surgery": 0, "Orthopedic Surgery": 1,
        "General Discharge": 2, "Injury Recovery": 3, "Stroke Rehab": 4
    }
    swelling_map = {"None": 0, "Mild": 1, "Moderate": 2, "Severe": 3}
    wound_map = {"Clean/Healing": 0, "Redness": 1, "Discharge/Open": 2}
    trend_map = {"Improving": -1, "Stable": 0, "Worsening": 1}

    X = np.array([[
        features["pain_score"],
        swelling_map.get(features["swelling"], 0),
        features["fever"],
        features["mobility"],
        wound_map.get(features["wound_status"], 0),
        features["medication_adherence"],
        features["days_post_surgery"],
        surgery_map.get(features["surgery_type"], 2),
        trend_map.get(features["pain_trend"], 0)
    ]])

    risk_idx = int(model.predict(X)[0])
    probabilities = model.predict_proba(X)[0]
    confidence = round(float(probabilities[risk_idx]) * 100, 1)

    return {
        "risk_level": RISK_LABELS[risk_idx],
        "risk_index": risk_idx,
        "confidence": confidence,
        "color": RISK_COLORS[risk_idx],
        "probabilities": {RISK_LABELS[i]: round(float(p)*100,1) for i,p in enumerate(probabilities)}
    }


if __name__ == "__main__":
    train_and_save()