from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import json, os, sys, uuid
from datetime import datetime, date

sys.path.append(os.path.join(os.path.dirname(__file__), "../ml"))
from model import predict_risk
from rehab_engine import get_rehab_plan, get_recovery_score

app = FastAPI(title="RehabAI API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

DB_FILE = os.path.join(os.path.dirname(__file__), "../data/db.json")

def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE) as f:
            return json.load(f)
    return {"patients": {}, "logs": {}, "alerts": []}

def save_db(db):
    os.makedirs(os.path.dirname(DB_FILE), exist_ok=True)
    with open(DB_FILE, "w") as f:
        json.dump(db, f, indent=2, default=str)

class Patient(BaseModel):
    name: str
    age: int
    surgery_type: str
    surgery_date: str
    doctor_name: str
    doctor_email: Optional[str] = ""
    weight_kg: Optional[float] = 70
    height_cm: Optional[float] = 170

class DailyLog(BaseModel):
    patient_id: str
    pain_score: int
    swelling: str
    fever: float
    mobility: int
    wound_status: str
    medication_adherence: int
    pain_trend: str
    notes: Optional[str] = ""

@app.get("/")
def root():
    return {"message": "RehabAI Backend Running", "version": "1.0.0"}

@app.post("/patient/register")
def register_patient(patient: Patient):
    db = load_db()
    pid = str(uuid.uuid4())[:8]
    db["patients"][pid] = {**patient.dict(), "id": pid, "created_at": str(datetime.now())}
    db["logs"][pid] = []
    save_db(db)
    return {"patient_id": pid, "message": "Patient registered successfully"}

@app.get("/patient/{patient_id}")
def get_patient(patient_id: str):
    db = load_db()
    if patient_id not in db["patients"]:
        raise HTTPException(404, "Patient not found")
    return db["patients"][patient_id]

@app.get("/patients")
def list_patients():
    db = load_db()
    return list(db["patients"].values())

@app.post("/log/daily")
def submit_daily_log(log: DailyLog):
    db = load_db()
    if log.patient_id not in db["patients"]:
        raise HTTPException(404, "Patient not found")
    patient = db["patients"][log.patient_id]
    surgery_date = datetime.strptime(patient["surgery_date"], "%Y-%m-%d")
    days_post = (datetime.now() - surgery_date).days
    risk_result = predict_risk({
        "pain_score": log.pain_score,
        "swelling": log.swelling,
        "fever": log.fever,
        "mobility": log.mobility,
        "wound_status": log.wound_status,
        "medication_adherence": log.medication_adherence,
        "days_post_surgery": days_post,
        "surgery_type": patient["surgery_type"],
        "pain_trend": log.pain_trend
    })
    rehab = get_rehab_plan(patient["surgery_type"], risk_result["risk_level"], days_post)
    log_entry = {
        **log.dict(),
        "date": str(date.today()),
        "days_post_surgery": days_post,
        "risk_level": risk_result["risk_level"],
        "risk_index": risk_result["risk_index"],
        "timestamp": str(datetime.now())
    }
    db["logs"][log.patient_id].append(log_entry)
    alerts = check_alerts(db["logs"][log.patient_id], patient, risk_result)
    if alerts:
        for a in alerts:
            db["alerts"].append(a)
    save_db(db)
    recovery_score = get_recovery_score(db["logs"][log.patient_id])
    return {
        "risk": risk_result,
        "rehab_plan": rehab,
        "recovery_score": recovery_score,
        "days_post_surgery": days_post,
        "alerts_triggered": alerts
    }

@app.get("/logs/{patient_id}")
def get_logs(patient_id: str):
    db = load_db()
    if patient_id not in db["logs"]:
        raise HTTPException(404, "No logs found")
    logs = db["logs"][patient_id]
    recovery_score = get_recovery_score(logs)
    return {"logs": logs, "recovery_score": recovery_score}

@app.get("/alerts")
def get_alerts():
    db = load_db()
    return db.get("alerts", [])

@app.get("/dashboard/{patient_id}")
def get_dashboard(patient_id: str):
    db = load_db()
    if patient_id not in db["patients"]:
        raise HTTPException(404, "Patient not found")
    patient = db["patients"][patient_id]
    logs = db["logs"].get(patient_id, [])
    recovery_score = get_recovery_score(logs)
    latest_risk = logs[-1]["risk_level"] if logs else "Unknown"
    latest_risk_idx = logs[-1]["risk_index"] if logs else 0
    return {
        "patient": patient,
        "total_logs": len(logs),
        "recovery_score": recovery_score,
        "latest_risk": latest_risk,
        "latest_risk_index": latest_risk_idx,
        "logs": logs[-7:]
    }

def check_alerts(logs, patient, risk_result):
    alerts = []
    now = str(datetime.now())
    if risk_result["risk_index"] >= 3:
        alerts.append({
            "type": "CRITICAL",
            "message": f"CRITICAL risk for {patient['name']}. Immediate attention required.",
            "patient": patient["name"],
            "timestamp": now
        })
    if len(logs) >= 3:
        last3_pain = [l["pain_score"] for l in logs[-3:]]
        if last3_pain[0] < last3_pain[1] < last3_pain[2]:
            alerts.append({
                "type": "ESCALATION",
                "message": f"Pain increasing 3 days in a row for {patient['name']}.",
                "patient": patient["name"],
                "timestamp": now
            })
    latest = logs[-1] if logs else {}
    if latest.get("fever", 98.6) >= 100.4 and latest.get("swelling") in ["Moderate", "Severe"]:
        alerts.append({
            "type": "FEVER_SWELLING",
            "message": f"Fever + Swelling detected for {patient['name']}. Possible infection.",
            "patient": patient["name"],
            "timestamp": now
        })
    return alerts

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

"""
RehabAI Backend — FastAPI
Endpoints: patient CRUD, daily logs, risk prediction, rehab plans, alerts
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import json, os, sys, uuid
from datetime import datetime, date

# Add ml to path
sys.path.append(os.path.join(os.path.dirname(__file__), "../ml"))
from model import predict_risk
from rehab_engine import get_rehab_plan, get_recovery_score
from ai_features import (predict_recovery_days, calculate_complication_probability,
                          analyze_pain_pattern, get_daily_tip)

app = FastAPI(title="RehabAI API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# ─────────────────────────────────────────
# In-memory store (replace with SQLite/Postgres in prod)
# ─────────────────────────────────────────
DB_FILE = os.path.join(os.path.dirname(__file__), "../data/db.json")

def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE) as f:
            return json.load(f)
    return {"patients": {}, "logs": {}, "alerts": []}

def save_db(db):
    os.makedirs(os.path.dirname(DB_FILE), exist_ok=True)
    with open(DB_FILE, "w") as f:
        json.dump(db, f, indent=2, default=str)

# ─────────────────────────────────────────
# MODELS
# ─────────────────────────────────────────
class Patient(BaseModel):
    name: str
    age: int
    surgery_type: str
    surgery_date: str
    doctor_name: str
    doctor_email: Optional[str] = ""
    weight_kg: Optional[float] = 70
    height_cm: Optional[float] = 170

class DailyLog(BaseModel):
    patient_id: str
    pain_score: int
    swelling: str
    fever: float
    mobility: int
    wound_status: str
    medication_adherence: int
    pain_trend: str
    notes: Optional[str] = ""

# ─────────────────────────────────────────
# ROUTES
# ─────────────────────────────────────────

@app.get("/")
def root():
    return {"message": "RehabAI Backend Running ✅", "version": "1.0.0"}


@app.post("/patient/register")
def register_patient(patient: Patient):
    db = load_db()
    pid = str(uuid.uuid4())[:8]
    db["patients"][pid] = {**patient.dict(), "id": pid, "created_at": str(datetime.now())}
    db["logs"][pid] = []
    save_db(db)
    return {"patient_id": pid, "message": "Patient registered successfully"}


@app.get("/patient/{patient_id}")
def get_patient(patient_id: str):
    db = load_db()
    if patient_id not in db["patients"]:
        raise HTTPException(404, "Patient not found")
    return db["patients"][patient_id]


@app.get("/patients")
def list_patients():
    db = load_db()
    return list(db["patients"].values())


@app.post("/log/daily")
def submit_daily_log(log: DailyLog):
    db = load_db()
    if log.patient_id not in db["patients"]:
        raise HTTPException(404, "Patient not found")

    patient = db["patients"][log.patient_id]
    surgery_date = datetime.strptime(patient["surgery_date"], "%Y-%m-%d")
    days_post = (datetime.now() - surgery_date).days

    # ── Risk Prediction ──
    risk_result = predict_risk({
        "pain_score": log.pain_score,
        "swelling": log.swelling,
        "fever": log.fever,
        "mobility": log.mobility,
        "wound_status": log.wound_status,
        "medication_adherence": log.medication_adherence,
        "days_post_surgery": days_post,
        "surgery_type": patient["surgery_type"],
        "pain_trend": log.pain_trend
    })

    # ── Rehab Plan ──
    rehab = get_rehab_plan(patient["surgery_type"], risk_result["risk_level"], days_post)

    # ── Save Log ──
    log_entry = {
        **log.dict(),
        "date": str(date.today()),
        "days_post_surgery": days_post,
        "risk_level": risk_result["risk_level"],
        "risk_index": risk_result["risk_index"],
        "timestamp": str(datetime.now())
    }
    db["logs"][log.patient_id].append(log_entry)

    # ── Intelligent Alert Logic ──
    alerts = check_alerts(db["logs"][log.patient_id], patient, risk_result)
    if alerts:
        for a in alerts:
            db["alerts"].append(a)

    save_db(db)

    # ── Recovery Score ──
    recovery_score = get_recovery_score(db["logs"][log.patient_id])

    return {
        "risk": risk_result,
        "rehab_plan": rehab,
        "recovery_score": recovery_score,
        "days_post_surgery": days_post,
        "alerts_triggered": alerts
    }


@app.get("/logs/{patient_id}")
def get_logs(patient_id: str):
    db = load_db()
    if patient_id not in db["logs"]:
        raise HTTPException(404, "No logs found")
    logs = db["logs"][patient_id]
    recovery_score = get_recovery_score(logs)
    return {"logs": logs, "recovery_score": recovery_score}


@app.get("/alerts")
def get_alerts():
    db = load_db()
    return db.get("alerts", [])


@app.get("/dashboard/{patient_id}")
def get_dashboard(patient_id: str):
    db = load_db()
    if patient_id not in db["patients"]:
        raise HTTPException(404, "Patient not found")
    
    patient = db["patients"][patient_id]
    logs = db["logs"].get(patient_id, [])
    recovery_score = get_recovery_score(logs)
    
    latest_risk = logs[-1]["risk_level"] if logs else "Unknown"
    latest_risk_idx = logs[-1]["risk_index"] if logs else 0

    return {
        "patient": patient,
        "total_logs": len(logs),
        "recovery_score": recovery_score,
        "latest_risk": latest_risk,
        "latest_risk_index": latest_risk_idx,
        "logs": logs[-7:]  # Last 7 days
    }


# ─────────────────────────────────────────
# ALERT LOGIC
# ─────────────────────────────────────────
def check_alerts(logs: list, patient: dict, risk_result: dict) -> list:
    alerts = []
    now = str(datetime.now())

    # Rule 1: Critical risk → immediate alert
    if risk_result["risk_index"] >= 3:
        alerts.append({
            "type": "CRITICAL",
            "message": f"🚨 CRITICAL risk detected for patient {patient['name']}. Immediate medical attention required.",
            "patient": patient["name"],
            "timestamp": now
        })

    # Rule 2: Pain worsening for 3+ consecutive days
    if len(logs) >= 3:
        last3_pain = [l["pain_score"] for l in logs[-3:]]
        if last3_pain[0] < last3_pain[1] < last3_pain[2]:
            alerts.append({
                "type": "ESCALATION",
                "message": f"⚠️ Pain has increased for 3 consecutive days for {patient['name']}. Doctor review needed.",
                "patient": patient["name"],
                "timestamp": now
            })

    # Rule 3: Fever + swelling combination
    latest = logs[-1] if logs else {}
    if latest.get("fever", 98.6) >= 100.4 and latest.get("swelling") in ["Moderate", "Severe"]:
        alerts.append({
            "type": "FEVER_SWELLING",
            "message": f"🌡️ Fever + Swelling combination detected for {patient['name']}. Possible infection — contact doctor.",
            "patient": patient["name"],
            "timestamp": now
        })

    return alerts



# ─────────────────────────────────────────
# NEW AI FEATURE ENDPOINTS
# ─────────────────────────────────────────

@app.get("/ai/recovery-prediction/{patient_id}")
def recovery_prediction(patient_id: str):
    """Predict remaining recovery days"""
    db = load_db()
    if patient_id not in db["patients"]:
        raise HTTPException(404, "Patient not found")
    patient = db["patients"][patient_id]
    logs = db["logs"].get(patient_id, [])
    surgery_date = datetime.strptime(patient["surgery_date"], "%Y-%m-%d")
    days_post = (datetime.now() - surgery_date).days
    latest = logs[-1] if logs else {}
    result = predict_recovery_days(
        surgery_type=patient["surgery_type"],
        risk_level=latest.get("risk_level", "Low"),
        days_post=days_post,
        pain_score=latest.get("pain_score", 5),
        mobility=latest.get("mobility", 5)
    )
    return result


@app.get("/ai/complication-risk/{patient_id}")
def complication_risk(patient_id: str):
    """Calculate complication probability %"""
    db = load_db()
    if patient_id not in db["patients"]:
        raise HTTPException(404, "Patient not found")
    logs = db["logs"].get(patient_id, [])
    if not logs:
        raise HTTPException(400, "No logs found — submit daily log first")
    latest = logs[-1]
    result = calculate_complication_probability(latest)
    return result


@app.get("/ai/pain-pattern/{patient_id}")
def pain_pattern(patient_id: str):
    """Analyze pain pattern from logs"""
    db = load_db()
    if patient_id not in db["patients"]:
        raise HTTPException(404, "Patient not found")
    logs = db["logs"].get(patient_id, [])
    result = analyze_pain_pattern(logs)
    return result


@app.get("/ai/daily-tip/{patient_id}")
def daily_tip(patient_id: str):
    """Get personalized daily health tip"""
    db = load_db()
    if patient_id not in db["patients"]:
        raise HTTPException(404, "Patient not found")
    patient = db["patients"][patient_id]
    logs = db["logs"].get(patient_id, [])
    surgery_date = datetime.strptime(patient["surgery_date"], "%Y-%m-%d")
    days_post = (datetime.now() - surgery_date).days
    latest = logs[-1] if logs else {}
    result = get_daily_tip(
        surgery_type=patient["surgery_type"],
        days_post=days_post,
        risk_level=latest.get("risk_level", "Low")
    )
    return result


@app.get("/ai/full-analysis/{patient_id}")
def full_ai_analysis(patient_id: str):
    """Get all AI features in one call"""
    db = load_db()
    if patient_id not in db["patients"]:
        raise HTTPException(404, "Patient not found")
    patient = db["patients"][patient_id]
    logs = db["logs"].get(patient_id, [])
    surgery_date = datetime.strptime(patient["surgery_date"], "%Y-%m-%d")
    days_post = (datetime.now() - surgery_date).days
    latest = logs[-1] if logs else {}
    risk_level = latest.get("risk_level", "Low")

    return {
        "recovery_prediction": predict_recovery_days(
            patient["surgery_type"], risk_level, days_post,
            latest.get("pain_score", 5), latest.get("mobility", 5)
        ),
        "complication_risk": calculate_complication_probability(latest) if latest else {"probability": 0, "category": "Unknown"},
        "pain_pattern": analyze_pain_pattern(logs),
        "daily_tip": get_daily_tip(patient["surgery_type"], days_post, risk_level)
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)