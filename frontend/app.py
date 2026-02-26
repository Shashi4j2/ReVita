import streamlit as st
import requests
import json
from datetime import datetime
import time

API_URL = "http://localhost:8000"

st.set_page_config(
    page_title="RehabAI — Intelligent Rehabilitation System",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=DM+Mono:wght@400;500&display=swap');

* { font-family: 'DM Sans', sans-serif; }

.stApp {
    background: #0a0e1a;
    color: #e8eaf6;
}

section[data-testid="stSidebar"] {
    background: #0d1226 !important;
    border-right: 1px solid #1e2640;
}
section[data-testid="stSidebar"] * { color: #c8cfe8 !important; }

.metric-card {
    background: linear-gradient(135deg, #131929 0%, #1a2035 100%);
    border: 1px solid #1e2d4a;
    border-radius: 16px;
    padding: 20px 24px;
    margin: 8px 0;
}

.risk-low {
    background: linear-gradient(135deg, #0d2818 0%, #0f3020 100%);
    border: 1px solid #1a5c35;
    border-radius: 16px;
    padding: 24px;
    text-align: center;
}
.risk-moderate {
    background: linear-gradient(135deg, #2a1f08 0%, #2e2210 100%);
    border: 1px solid #6b4c10;
    border-radius: 16px;
    padding: 24px;
    text-align: center;
}
.risk-high {
    background: linear-gradient(135deg, #2a0f0f 0%, #300f0f 100%);
    border: 1px solid #7a2020;
    border-radius: 16px;
    padding: 24px;
    text-align: center;
}
.risk-emergency {
    background: linear-gradient(135deg, #3a0505 0%, #450505 100%);
    border: 2px solid #cc2222;
    border-radius: 16px;
    padding: 24px;
    text-align: center;
}

.plan-section {
    background: #131929;
    border: 1px solid #1e2d4a;
    border-radius: 12px;
    padding: 18px;
    margin: 10px 0;
}
.plan-section h4 { color: #4d9aff; margin-bottom: 10px; font-size: 0.95rem; }
.plan-section ul { margin: 0; padding-left: 20px; }
.plan-section ul li { color: #b0bcd8; margin: 6px 0; font-size: 0.92rem; }

.alert-box {
    background: linear-gradient(135deg, #2d0a0a, #380d0d);
    border: 1px solid #aa1a1a;
    border-radius: 12px;
    padding: 18px;
    margin: 10px 0;
}

.followup-box {
    background: #0f1f35;
    border: 1px solid #1e3f6a;
    border-radius: 12px;
    padding: 18px;
    margin: 10px 0;
    font-size: 0.95rem;
    color: #7fb8ff;
}

.stButton > button {
    background: linear-gradient(135deg, #1a56db, #1e3fc4) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 10px 28px !important;
    font-weight: 600 !important;
}

h1, h2, h3 { color: #e8eaf6 !important; }
.stTextInput input, .stNumberInput input, .stSelectbox select {
    background: #131929 !important;
    border: 1px solid #1e2d4a !important;
    color: #e8eaf6 !important;
    border-radius: 8px !important;
}
label { color: #8899bb !important; font-size: 0.88rem !important; }

.header-logo {
    font-size: 1.8rem;
    font-weight: 700;
    color: #4d9aff;
}
</style>
""", unsafe_allow_html=True)


if "patient_id" not in st.session_state:
    st.session_state.patient_id = None
if "patient_name" not in st.session_state:
    st.session_state.patient_name = None
if "last_prediction" not in st.session_state:
    st.session_state.last_prediction = None
if "last_plan" not in st.session_state:
    st.session_state.last_plan = None
if "last_vitals" not in st.session_state:
    st.session_state.last_vitals = None


with st.sidebar:
    st.markdown('<div class="header-logo">🧠 RehabAI</div>', unsafe_allow_html=True)
    st.markdown("---")

    page = st.radio("Navigation", [
        "🏠 Dashboard",
        "👤 Register Patient",
        "📊 Risk Assessment",
        "💊 Rehab Plan",
        "📈 Progress Tracking",
        "🔔 Alerts & Follow-up"
    ])

    st.markdown("---")
    if st.session_state.patient_id:
        st.markdown(f"""
        <div class="metric-card">
            <div style="color:#4d6699;font-size:0.75rem;">Active Patient</div>
            <div style="color:#e8eaf6;font-weight:600;margin-top:4px;">{st.session_state.patient_name}</div>
            <div style="color:#4d9aff;font-size:0.8rem;">ID: {st.session_state.patient_id}</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("No patient selected.")


def api_call(method, endpoint, data=None):
    try:
        url = f"{API_URL}{endpoint}"
        if method == "GET":
            r = requests.get(url, timeout=5)
        else:
            r = requests.post(url, json=data, timeout=5)
        return r.json()
    except Exception as e:
        return {"error": str(e)}


if "Dashboard" in page:
    st.markdown("## 🏠 System Dashboard")
    st.markdown("Real-time overview of the RehabAI platform")

    patients_data = api_call("GET", "/api/patients")
    alerts_data = api_call("GET", "/api/alerts")

    total_patients = patients_data.get("total", 0) if "error" not in patients_data else 0
    total_alerts = alerts_data.get("total", 0) if "error" not in alerts_data else 0

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("👥 Registered Patients", total_patients)
    with c2:
        st.metric("🔔 Active Alerts", total_alerts)
    with c3:
        st.metric("🤖 AI Model", "RandomForest")
    with c4:
        st.metric("💊 Diseases Covered", "3")

    st.markdown("---")
    col1, col2 = st.columns([3, 2])

    with col1:
        st.markdown("### 👥 Registered Patients")
        if "error" not in patients_data and total_patients > 0:
            for p in patients_data["patients"][-5:][::-1]:
                risk = p.get("latest_risk", "—")
                st.markdown(f"""
                <div class="metric-card">
                    <b>{p['name']}</b> &nbsp;
                    <span style="color:#4d6699;font-size:0.8rem;">ID: {p['patient_id']}</span>
                    &nbsp;&nbsp; Risk: <b>{risk}</b>
                    &nbsp;&nbsp; {p['disease_type'].replace('_',' ').title()}
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No patients registered yet")

    with col2:
        st.markdown("### 🔔 Recent Alerts")
        if "error" not in alerts_data and total_alerts > 0:
            for a in alerts_data["alerts"][-4:][::-1]:
                st.markdown(f"""
                <div class="alert-box">
                    <div style="color:#e05555;font-weight:600;">{a.get('alert_type', a.get('type','ALERT'))}</div>
                    <div style="color:#c8cfe8;font-size:0.88rem;margin-top:4px;">{a.get('message','')[:80]}...</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No alerts")


elif "Register" in page:
    st.markdown("## 👤 Register New Patient")

    with st.form("register_form"):
        c1, c2 = st.columns(2)
        with c1:
            name = st.text_input("Patient Full Name", placeholder="e.g. John Doe")
            age = st.number_input("Age", min_value=1, max_value=120, value=55)
            gender = st.selectbox("Gender", ["Male", "Female", "Other"])
        with c2:
            disease = st.selectbox("Disease Type", ["diabetes", "heart_disease", "stroke_recovery"],
                                   format_func=lambda x: x.replace("_", " ").title())
            doctor = st.text_input("Attending Doctor", placeholder="Dr. Ahmed")
            email = st.text_input("Doctor Email", placeholder="doctor@hospital.com")

        submit = st.form_submit_button("✅ Register Patient", use_container_width=True)

        if submit:
            if not name:
                st.error("Please enter patient name")
            else:
                result = api_call("POST", "/api/patients/register", {
                    "name": name, "age": age, "gender": gender,
                    "disease_type": disease, "doctor_name": doctor, "doctor_email": email
                })
                if "error" not in result:
                    st.session_state.patient_id = result["patient_id"]
                    st.session_state.patient_name = name
                    st.success(f"✅ Patient registered! ID: **{result['patient_id']}**")
                    st.balloons()
                else:
                    st.error(f"Error: {result['error']}")

    st.markdown("---")
    st.markdown("### 📂 Load Existing Patient")
    pid = st.text_input("Enter Patient ID")
    if st.button("Load Patient"):
        result = api_call("GET", f"/api/patients/{pid.upper().strip()}")
        if "error" not in result and "patient_id" in result:
            st.session_state.patient_id = result["patient_id"]
            st.session_state.patient_name = result["name"]
            st.success(f"✅ Loaded: {result['name']}")
        else:
            st.error("Patient not found")


elif "Risk" in page:
    st.markdown("## 📊 AI Risk Assessment")

    with st.form("vitals_form"):
        disease_type = st.selectbox("Disease Type", ["diabetes", "heart_disease", "stroke_recovery"],
                                    format_func=lambda x: x.replace("_"," ").title())

        c1, c2, c3 = st.columns(3)
        with c1:
            age = st.number_input("Age", 18, 120, 60)
            bmi = st.number_input("BMI", 10.0, 70.0, 27.5, step=0.1)
            bp = st.number_input("Blood Pressure (mmHg)", 50, 250, 130)
        with c2:
            sugar = st.number_input("Blood Sugar (mg/dL)", 40, 600, 120)
            hr = st.number_input("Heart Rate (bpm)", 30, 220, 80)
        with c3:
            activity = st.slider("Activity Level", 0, 9, 4)
            adherence = st.slider("Medication Adherence", 0, 9, 7)

        predict_btn = st.form_submit_button("🔍 Predict Risk", use_container_width=True)

    if predict_btn:
        with st.spinner("Running AI prediction..."):
            time.sleep(0.5)
            payload = {
                "patient_id": st.session_state.patient_id,
                "age": age, "bmi": bmi, "blood_pressure": bp,
                "blood_sugar": sugar, "heart_rate": hr,
                "activity_level": activity, "medication_adherence": adherence,
                "disease_type": disease_type
            }
            result = api_call("POST", "/api/predict/risk", payload)
            st.session_state.last_prediction = result
            st.session_state.last_vitals = payload

        if "error" not in result:
            risk = result["risk_level"]
            confidence = result["confidence"]
            probs = result.get("probabilities", {})

            risk_css = {"Low":"risk-low","Moderate":"risk-moderate","High":"risk-high","Emergency":"risk-emergency"}
            risk_icon = {"Low":"🟢","Moderate":"🟡","High":"🔴","Emergency":"🚨"}
            risk_color = {"Low":"#4daa72","Moderate":"#d4891a","High":"#e05555","Emergency":"#ff2222"}

            st.markdown(f"""
            <div class="{risk_css.get(risk,'metric-card')}">
                <div style="font-size:2.5rem;">{risk_icon.get(risk,'⚪')}</div>
                <div style="font-size:1.8rem;font-weight:700;color:{risk_color.get(risk,'#fff')}">
                    {risk.upper()} RISK
                </div>
                <div style="color:#8899bb;">AI Confidence: {confidence}%</div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("#### 📊 Risk Probability Breakdown")
            colors = {"Low":"#4daa72","Moderate":"#d4891a","High":"#e05555","Emergency":"#ff2222"}
            for label, prob in probs.items():
                col1, col2 = st.columns([1, 4])
                with col1:
                    st.markdown(f'<span style="color:{colors[label]};font-weight:600;">{label}</span>', unsafe_allow_html=True)
                with col2:
                    st.progress(int(prob))
                    st.caption(f"{prob}%")

            if risk in ["High", "Emergency"]:
                st.markdown("""
                <div class="alert-box">
                    <div style="color:#e05555;font-weight:600;">⚠️ Doctor Alert Triggered</div>
                    <div style="color:#c8cfe8;margin-top:6px;">The attending physician has been notified.</div>
                </div>
                """, unsafe_allow_html=True)

            st.success("💡 Go to Rehab Plan page to see your personalized program!")
        else:
            st.error(f"Error: {result['error']}")


elif "Rehab" in page:
    st.markdown("## 💊 Personalized Rehabilitation Plan")

    if st.session_state.last_prediction and st.session_state.last_vitals:
        risk = st.session_state.last_prediction["risk_level"]
        vitals = st.session_state.last_vitals
        disease = vitals["disease_type"]
        name = st.session_state.patient_name or "Patient"

        result = api_call("POST", "/api/rehab/plan", {
            "disease_type": disease,
            "risk_level": risk,
            "patient_data": vitals,
            "patient_name": name
        })

        if "error" not in result:
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"""<div class="plan-section"><h4>🏃 Exercise Protocol</h4>
                <ul>{"".join(f"<li>{e}</li>" for e in result.get("exercises",[]))}</ul></div>""",
                unsafe_allow_html=True)
                st.markdown(f"""<div class="plan-section"><h4>🥗 Dietary Guidelines</h4>
                <ul>{"".join(f"<li>{d}</li>" for d in result.get("diet",[]))}</ul></div>""",
                unsafe_allow_html=True)
            with col2:
                st.markdown(f"""<div class="plan-section"><h4>🩺 Monitoring</h4>
                <ul>{"".join(f"<li>{m}</li>" for m in result.get("monitoring",[]))}</ul></div>""",
                unsafe_allow_html=True)
                st.markdown(f"""<div class="plan-section"><h4>🌱 Lifestyle</h4>
                <ul>{"".join(f"<li>{l}</li>" for l in result.get("lifestyle",[]))}</ul></div>""",
                unsafe_allow_html=True)

            if result.get("personalized_notes"):
                st.markdown("#### ⚡ Personalized Alerts")
                for note in result["personalized_notes"]:
                    st.markdown(f'<div class="alert-box">{note}</div>', unsafe_allow_html=True)

            st.markdown(f"""
            <div class="followup-box">
                📅 <b>Follow-up:</b><br><br>{result.get("followup_message","")}
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("👆 Please complete a Risk Assessment first.")


elif "Progress" in page:
    st.markdown("## 📈 Progress Tracking")

    if not st.session_state.patient_id:
        st.warning("Please register or load a patient first.")
    else:
        patient = api_call("GET", f"/api/patients/{st.session_state.patient_id}")
        if "error" not in patient:
            st.markdown(f"### {patient['name']}")
            st.markdown(f"**Disease:** {patient['disease_type'].replace('_',' ').title()} | **Age:** {patient['age']}")

            history = patient.get("risk_history", [])
            if history:
                st.markdown("#### 📋 Risk History")
                for i, entry in enumerate(reversed(history)):
                    risk = entry.get("risk_level","—")
                    st.markdown(f"""
                    <div class="metric-card">
                        #{len(history)-i} &nbsp;&nbsp;
                        <b>{risk}</b> &nbsp;&nbsp;
                        Confidence: {entry.get('confidence',0)}% &nbsp;&nbsp;
                        {entry.get('timestamp','')[:16]}
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No risk assessments yet.")

            st.markdown("#### 📝 Log New Vitals")
            with st.form("log_vitals"):
                c1, c2, c3 = st.columns(3)
                with c1:
                    v_bp = st.number_input("BP (mmHg)", 50, 250, 130)
                    v_sugar = st.number_input("Blood Sugar", 40, 600, 110)
                with c2:
                    v_hr = st.number_input("Heart Rate", 30, 220, 78)
                    v_bmi = st.number_input("BMI", 10.0, 70.0, 27.0, step=0.1)
                with c3:
                    v_activity = st.slider("Activity", 0, 9, 5)
                    v_adherence = st.slider("Adherence", 0, 9, 8)

                if st.form_submit_button("💾 Save Vitals", use_container_width=True):
                    result = api_call("POST", "/api/patients/vitals", {
                        "patient_id": st.session_state.patient_id,
                        "blood_pressure": v_bp, "blood_sugar": v_sugar,
                        "heart_rate": v_hr, "bmi": v_bmi,
                        "activity_level": v_activity, "medication_adherence": v_adherence,
                        "symptoms": []
                    })
                    if "error" not in result:
                        st.success("✅ Vitals logged!")
                        st.rerun()
                    else:
                        st.error(result["error"])


elif "Alerts" in page:
    st.markdown("## 🔔 Alerts & Follow-up System")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 📋 System Alerts")
        alerts = api_call("GET", "/api/alerts")
        if "error" not in alerts and alerts.get("total", 0) > 0:
            for a in reversed(alerts["alerts"]):
                st.markdown(f"""
                <div class="alert-box">
                    <div style="color:#e05555;font-weight:600;">{a.get('alert_type', a.get('type','ALERT'))}</div>
                    <div style="color:#c8cfe8;margin-top:6px;">{a.get('message','')}</div>
                    <div style="color:#4d6699;margin-top:6px;font-size:0.78rem;">{a.get('timestamp','')[:16]}</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.success("🟢 No active alerts")

    with col2:
        st.markdown("### 🩺 Daily Symptom Check")
        if not st.session_state.patient_id:
            st.warning("Load a patient first")
        else:
            symptoms_selected = st.multiselect("Select reported symptoms", [
                "chest pain", "severe dizziness", "blurred vision",
                "shortness of breath", "numbness", "slurred speech",
                "fatigue", "headache", "nausea", "swelling"
            ])
            if st.button("🔍 Submit Daily Check", use_container_width=True):
                result = api_call("POST", "/api/followup/check", {
                    "patient_id": st.session_state.patient_id,
                    "symptoms": symptoms_selected
                })
                if "error" not in result:
                    if result.get("status") == "ALERT_SENT":
                        st.error(f"🚨 {result['message']}")
                    else:
                        st.success(f"✅ {result['message']}")

    st.markdown("---")
    st.markdown("### 🚨 Alert Threshold Guide")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown('<div class="metric-card"><b style="color:#4daa72">🟢 Low</b><br><small>BP &lt;140, Sugar 80-180, HR 60-100</small></div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="metric-card"><b style="color:#d4891a">🟡 Moderate</b><br><small>BP 140-160, Sugar 180-250</small></div>', unsafe_allow_html=True)
    with c3:
        st.markdown('<div class="metric-card"><b style="color:#e05555">🔴 High</b><br><small>BP &gt;160, Sugar &gt;250, Poor adherence</small></div>', unsafe_allow_html=True)
    with c4:
        st.markdown('<div class="metric-card"><b style="color:#ff2222">🚨 Emergency</b><br><small>Critical multi-factor failure</small></div>', unsafe_allow_html=True)