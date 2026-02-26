"""
Rehab Recommendation Engine
Rule-based logic adjusted dynamically by surgery type and recovery data
"""

REHAB_PLANS = {
    "Minor Surgery": {
        "Low": {
            "exercises": [
                "Deep breathing exercises — 10 reps × 3 sets",
                "Gentle ankle circles — 15 reps each side",
                "Seated leg raises — 10 reps × 2 sets",
                "Short walks (5-10 minutes) twice daily"
            ],
            "restrictions": ["Avoid heavy lifting > 5kg", "No strenuous activity"],
            "goals": "Regain baseline mobility within 1–2 weeks"
        },
        "Moderate": {
            "exercises": [
                "Bed-based breathing exercises only",
                "Gentle foot pumps — 20 reps hourly",
                "Passive range of motion with assistance"
            ],
            "restrictions": ["Rest primarily", "Elevate affected area", "Ice packs 20min every 2hrs"],
            "goals": "Reduce inflammation before progressing"
        },
        "High": {
            "exercises": ["Rest only — consult physiotherapist before any exercise"],
            "restrictions": ["Strict rest", "No movement of affected area without guidance"],
            "goals": "Stabilize condition — contact your doctor"
        },
        "Critical": {
            "exercises": ["STOP all exercise — seek emergency medical attention"],
            "restrictions": ["Immediate medical consultation required"],
            "goals": "Emergency evaluation needed"
        }
    },
    "Orthopedic Surgery": {
        "Low": {
            "exercises": [
                "Quadriceps sets — 10 reps × 3 sets",
                "Straight leg raises — 10 reps × 3 sets",
                "Heel slides — 15 reps × 2 sets",
                "Standing balance (with support) — 30 sec × 3",
                "Stair climbing practice with railing"
            ],
            "restrictions": ["Weight bear as tolerated", "No deep bending > 90°", "Use walker/crutches as prescribed"],
            "goals": "Restore joint range of motion and strength"
        },
        "Moderate": {
            "exercises": [
                "Isometric quad contractions only",
                "Ankle pumps — 20 reps every hour",
                "Gentle ROM within pain-free range only"
            ],
            "restrictions": ["Elevate limb", "Ice 20min/2hrs", "Limit weight bearing"],
            "goals": "Control pain and swelling before progressing"
        },
        "High": {
            "exercises": ["Pause exercise program — reassess with physiotherapist"],
            "restrictions": ["Non-weight bearing", "Splint/brace if available"],
            "goals": "Medical review required within 24 hours"
        },
        "Critical": {
            "exercises": ["IMMEDIATE medical attention required"],
            "restrictions": ["Call emergency services or go to ER"],
            "goals": "Possible complication — do not delay"
        }
    },
    "General Discharge": {
        "Low": {
            "exercises": [
                "Breathing exercises — 5 min, 3× daily",
                "Gentle walks increasing by 5 min each day",
                "Light stretching of major muscle groups",
                "Posture correction exercises"
            ],
            "restrictions": ["Avoid fatigue", "Stay hydrated", "Follow dietary guidelines"],
            "goals": "Gradual return to daily activities over 2–4 weeks"
        },
        "Moderate": {
            "exercises": [
                "Seated breathing exercises only",
                "Gentle range of motion while seated"
            ],
            "restrictions": ["Rest primarily", "Monitor vitals", "Increase fluids"],
            "goals": "Stabilize and monitor closely"
        },
        "High": {
            "exercises": ["Bed rest — no exercise"],
            "restrictions": ["Contact primary care physician today"],
            "goals": "Urgent medical review"
        },
        "Critical": {
            "exercises": ["Seek emergency care immediately"],
            "restrictions": ["Call ambulance or go to nearest ER"],
            "goals": "Emergency evaluation"
        }
    },
    "Injury Recovery": {
        "Low": {
            "exercises": [
                "RICE protocol (Rest, Ice, Compression, Elevation)",
                "Gentle ROM exercises within pain-free range",
                "Progressive strengthening — resistance band exercises",
                "Proprioception training — balance board (week 2+)"
            ],
            "restrictions": ["Avoid re-injury", "Tape/brace support", "Gradual return to sport"],
            "goals": "Full functional recovery in 3–8 weeks"
        },
        "Moderate": {
            "exercises": [
                "Continue RICE protocol",
                "Gentle stretching only",
                "No strengthening until pain reduces"
            ],
            "restrictions": ["Complete rest from activity", "Ice every 2 hours"],
            "goals": "Reduce acute inflammation"
        },
        "High": {
            "exercises": ["Rest — possible re-injury or complication"],
            "restrictions": ["Imaging may be required — visit clinic"],
            "goals": "Rule out fracture or tendon damage"
        },
        "Critical": {
            "exercises": ["Immediate medical evaluation"],
            "restrictions": ["Do not move injury — immobilize and seek ER"],
            "goals": "Emergency assessment required"
        }
    },
    "Stroke Rehab": {
        "Low": {
            "exercises": [
                "Mirror therapy — 15 min daily",
                "Hand grip exercises with therapy putty",
                "Seated marching — 2 min × 3 sets",
                "Speech and word recall exercises",
                "Fine motor tasks — buttoning, picking objects"
            ],
            "restrictions": ["Supervision required for all exercises", "Avoid fatigue", "Fall prevention protocol"],
            "goals": "Neuroplasticity training — rebuild motor pathways"
        },
        "Moderate": {
            "exercises": [
                "Passive ROM only with caregiver assistance",
                "Breathing exercises",
                "Visual tracking exercises"
            ],
            "restrictions": ["Bed rest", "Supervision at all times"],
            "goals": "Stabilize before progressing rehab"
        },
        "High": {
            "exercises": ["Pause rehab program"],
            "restrictions": ["Neurologist review required urgently"],
            "goals": "Reassess neurological status"
        },
        "Critical": {
            "exercises": ["Emergency services — possible secondary stroke"],
            "restrictions": ["FAST protocol: Face drooping, Arm weakness, Speech difficulty, Time to call emergency"],
            "goals": "Immediate emergency evaluation"
        }
    }
}


def get_rehab_plan(surgery_type: str, risk_level: str, days_post_surgery: int) -> dict:
    """Get rehab plan with dynamic adjustments based on recovery day"""
    plans = REHAB_PLANS.get(surgery_type, REHAB_PLANS["General Discharge"])
    base_plan = plans.get(risk_level, plans["Low"]).copy()

    # Dynamic adjustment by recovery phase
    phase = "Acute (Days 1-7)"
    if days_post_surgery <= 7:
        phase = "Acute Phase (Days 1–7)"
        note = "Focus on rest, pain management, and basic mobility."
    elif days_post_surgery <= 21:
        phase = "Sub-Acute Phase (Days 8–21)"
        note = "Begin progressive strengthening. Gentle exercises allowed."
    elif days_post_surgery <= 42:
        phase = "Functional Recovery (Days 22–42)"
        note = "Increase activity gradually. Focus on functional tasks."
    else:
        phase = "Return to Activity (Day 42+)"
        note = "Progressive loading. Prepare for full daily activities."

    base_plan["recovery_phase"] = phase
    base_plan["phase_note"] = note
    return base_plan


def get_recovery_score(logs: list) -> float:
    """
    Calculate recovery progress score (0-100)
    Based on: pain reduction, mobility increase, symptom trend
    """
    if not logs:
        return 0.0
    
    if len(logs) == 1:
        entry = logs[0]
        score = 50.0  # baseline
        score += (10 - entry.get("pain_score", 5)) * 3
        score += entry.get("mobility", 5) * 2
        return min(max(round(score, 1), 0), 100)

    # Compare first and latest
    first = logs[0]
    latest = logs[-1]

    pain_improvement = first.get("pain_score", 5) - latest.get("pain_score", 5)
    mobility_improvement = latest.get("mobility", 5) - first.get("mobility", 5)

    score = 40  # base
    score += pain_improvement * 5       # each point reduction = +5
    score += mobility_improvement * 3   # each point increase = +3

    # Penalize for fever/swelling
    if latest.get("fever", 98.6) >= 100.4:
        score -= 15
    if latest.get("swelling") in ["Moderate", "Severe"]:
        score -= 10

    return min(max(round(score, 1), 0), 100)