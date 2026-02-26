"""
RehabAI — Advanced AI Features Module
1. Recovery Days Prediction
2. Complication Probability %
3. Pain Pattern Analyzer
4. Daily AI Health Tip
"""

import random
from datetime import datetime

# ─────────────────────────────────────────
# 1. RECOVERY DAYS PREDICTION
# ─────────────────────────────────────────
RECOVERY_BASE_DAYS = {
    "Minor Surgery": 14,
    "Orthopedic Surgery": 60,
    "General Discharge": 21,
    "Injury Recovery": 30,
    "Stroke Rehab": 90
}

def predict_recovery_days(surgery_type: str, risk_level: str, days_post: int,
                           pain_score: int, mobility: int) -> dict:
    """
    Predicts estimated remaining recovery days
    Based on surgery type, current risk, and symptom scores
    """
    base = RECOVERY_BASE_DAYS.get(surgery_type, 30)

    # Risk multiplier
    risk_multiplier = {"Low": 1.0, "Moderate": 1.3, "High": 1.6, "Critical": 2.0}
    multiplier = risk_multiplier.get(risk_level, 1.0)

    # Pain penalty — high pain = longer recovery
    pain_factor = 1 + (pain_score / 10) * 0.5

    # Mobility bonus — good mobility = faster recovery
    mobility_factor = 1 - (mobility / 10) * 0.3

    # Estimated total days
    estimated_total = int(base * multiplier * pain_factor * mobility_factor)

    # Remaining days
    remaining = max(0, estimated_total - days_post)

    # Progress percentage
    progress_pct = min(100, round((days_post / estimated_total) * 100, 1)) if estimated_total > 0 else 100

    # Milestone
    if progress_pct >= 90:
        milestone = "🎉 Almost fully recovered!"
    elif progress_pct >= 70:
        milestone = "💪 Great progress — final stretch!"
    elif progress_pct >= 50:
        milestone = "📈 Halfway there — keep going!"
    elif progress_pct >= 25:
        milestone = "🌱 Early recovery — stay consistent!"
    else:
        milestone = "🏥 Just started — follow your plan carefully."

    return {
        "estimated_total_days": estimated_total,
        "days_completed": days_post,
        "days_remaining": remaining,
        "progress_pct": progress_pct,
        "milestone": milestone,
        "expected_recovery_date": _add_days(remaining)
    }


def _add_days(days: int) -> str:
    from datetime import date, timedelta
    target = date.today() + timedelta(days=days)
    return target.strftime("%B %d, %Y")


# ─────────────────────────────────────────
# 2. COMPLICATION PROBABILITY %
# ─────────────────────────────────────────
def calculate_complication_probability(features: dict) -> dict:
    """
    Calculates probability of complication in next 48 hours
    Based on combination of risk factors
    """
    score = 0  # 0-100

    pain = features.get("pain_score", 0)
    fever = features.get("fever", 98.6)
    swelling = features.get("swelling", "None")
    wound = features.get("wound_status", "Clean/Healing")
    trend = features.get("pain_trend", "Stable")
    mobility = features.get("mobility", 5)
    adherence = features.get("medication_adherence", 10)

    # Pain contribution (0-25)
    score += (pain / 10) * 25

    # Fever contribution (0-25)
    if fever >= 103:    score += 25
    elif fever >= 101.5: score += 20
    elif fever >= 100.4: score += 12
    elif fever >= 99.5:  score += 5

    # Swelling contribution (0-15)
    sw = {"None": 0, "Mild": 5, "Moderate": 10, "Severe": 15}
    score += sw.get(swelling, 0)

    # Wound contribution (0-15)
    wnd = {"Clean/Healing": 0, "Redness": 8, "Discharge/Open": 15}
    score += wnd.get(wound, 0)

    # Pain trend (0-10)
    if trend == "Worsening": score += 10
    elif trend == "Stable":  score += 2

    # Mobility penalty (0-5)
    if mobility <= 2: score += 5

    # Medication adherence bonus (reduce score)
    score -= (adherence / 10) * 8

    score = max(0, min(100, round(score, 1)))

    # Risk category
    if score < 20:
        category = "Very Low"
        color = "#22c55e"
        advice = "Your recovery is on track. Maintain your current routine."
    elif score < 40:
        category = "Low"
        color = "#86efac"
        advice = "Minor concerns detected. Follow your rehab plan carefully."
    elif score < 60:
        category = "Moderate"
        color = "#f59e0b"
        advice = "Some risk factors present. Contact your doctor if symptoms worsen."
    elif score < 80:
        category = "High"
        color = "#f97316"
        advice = "Multiple risk factors detected. Schedule a doctor visit today."
    else:
        category = "Critical"
        color = "#ef4444"
        advice = "URGENT: High complication risk. Contact doctor immediately."

    return {
        "probability": score,
        "category": category,
        "color": color,
        "advice": advice,
        "next_48hr_risk": f"{score}% chance of complication in next 48 hours"
    }


# ─────────────────────────────────────────
# 3. PAIN PATTERN ANALYZER
# ─────────────────────────────────────────
def analyze_pain_pattern(logs: list) -> dict:
    """
    Analyzes pain score history to detect patterns
    Returns pattern type, trend, and recommendation
    """
    if len(logs) < 2:
        return {
            "pattern": "Insufficient Data",
            "trend": "unknown",
            "description": "Log at least 2 days of data to see pain pattern analysis.",
            "recommendation": "Continue logging daily symptoms.",
            "color": "#8BAFC8",
            "icon": "📊"
        }

    pain_scores = [l.get("pain_score", 0) for l in logs[-7:]]  # last 7 days

    # Trend calculation
    if len(pain_scores) >= 3:
        recent_avg = sum(pain_scores[-3:]) / 3
        earlier_avg = sum(pain_scores[:3]) / 3
        trend_diff = recent_avg - earlier_avg
    else:
        trend_diff = pain_scores[-1] - pain_scores[0]

    # Pattern detection
    diffs = [pain_scores[i+1] - pain_scores[i] for i in range(len(pain_scores)-1)]
    increasing = sum(1 for d in diffs if d > 0)
    decreasing = sum(1 for d in diffs if d < 0)
    stable = sum(1 for d in diffs if d == 0)

    if trend_diff <= -2 and decreasing >= increasing:
        pattern = "Steady Improvement"
        trend = "improving"
        icon = "📉"
        color = "#22c55e"
        desc = f"Your pain has decreased by {abs(round(trend_diff, 1))} points. Excellent recovery progress!"
        rec = "Continue your current rehab plan. You're on the right track."

    elif trend_diff >= 2 and increasing >= decreasing:
        pattern = "Worsening Trend"
        trend = "worsening"
        icon = "📈"
        color = "#ef4444"
        desc = f"Pain has increased by {round(trend_diff, 1)} points over recent days. This needs attention."
        rec = "Contact your doctor. Reduce activity intensity immediately."

    elif abs(trend_diff) <= 1 and stable >= 2:
        pattern = "Plateau"
        trend = "stable"
        icon = "➡️"
        color = "#f59e0b"
        desc = "Pain score has been stable. Recovery may have reached a plateau."
        rec = "Discuss with your physiotherapist about progressing your exercises."

    elif increasing > 0 and decreasing > 0:
        pattern = "Fluctuating"
        trend = "fluctuating"
        icon = "〰️"
        color = "#f97316"
        desc = "Pain is going up and down inconsistently. Possible over-exertion."
        rec = "Rest more between exercise sessions. Avoid pushing through pain."

    else:
        pattern = "Early Recovery"
        trend = "early"
        icon = "🌱"
        color = "#00b4ff"
        desc = "Not enough data yet for full pattern analysis."
        rec = "Keep logging daily. Pattern will emerge in 3-5 days."

    # Peak and minimum
    peak_day = pain_scores.index(max(pain_scores)) + 1
    best_day = pain_scores.index(min(pain_scores)) + 1

    return {
        "pattern": pattern,
        "trend": trend,
        "icon": icon,
        "color": color,
        "description": desc,
        "recommendation": rec,
        "scores": pain_scores,
        "average": round(sum(pain_scores) / len(pain_scores), 1),
        "peak_score": max(pain_scores),
        "best_score": min(pain_scores),
        "trend_change": round(trend_diff, 1)
    }


# ─────────────────────────────────────────
# 4. DAILY AI HEALTH TIPS
# ─────────────────────────────────────────
HEALTH_TIPS = {
    "Minor Surgery": [
        ("💧", "Hydration Tip", "Drink at least 8 glasses of water daily. Proper hydration speeds up wound healing and tissue repair by up to 30%."),
        ("🛌", "Rest Position", "Elevate the operated area above heart level when resting. This reduces swelling and improves blood circulation."),
        ("🥗", "Nutrition", "Eat protein-rich foods like eggs, dal, and chicken. Protein is the building block for tissue healing."),
        ("🌬️", "Breathing", "Practice deep belly breathing 5 times every hour. This prevents lung complications common after surgery."),
        ("🚶", "Walking", "Short walks of 5-10 minutes, 2-3 times daily, prevent blood clots and improve circulation."),
        ("🧴", "Wound Care", "Keep your wound clean and dry. Change dressings as instructed. Never touch wound with unwashed hands."),
        ("😴", "Sleep", "Sleep 7-9 hours nightly. Growth hormone released during sleep accelerates tissue repair."),
    ],
    "Orthopedic Surgery": [
        ("🦵", "Leg Exercises", "Do ankle pumps every hour while resting — 20 pumps per session. This prevents dangerous blood clots (DVT)."),
        ("❄️", "Ice Therapy", "Apply ice pack for 20 minutes every 2 hours on swollen areas. Never apply directly on skin — use a cloth."),
        ("🔄", "Range of Motion", "Gently move your joint within pain-free range daily. Stiffness is the enemy of orthopedic recovery."),
        ("⚖️", "Weight Bearing", "Follow your doctor's weight-bearing instructions strictly. Premature loading can damage the repair."),
        ("💊", "Medication Timing", "Take anti-inflammatory medications with food, on schedule. Missing doses allows inflammation to return rapidly."),
        ("🪑", "Seating", "Avoid sitting in low chairs or soft sofas. Keep your hips at 90° or higher to protect joint repairs."),
        ("🧘", "Isometrics", "Tighten thigh muscles without moving the joint, hold 5 seconds, repeat 10 times. Maintains muscle tone safely."),
    ],
    "General Discharge": [
        ("📋", "Follow-up", "Attend all scheduled follow-up appointments. 80% of complications are caught at routine check-ups."),
        ("🩺", "Vital Signs", "Monitor temperature daily. Temperature above 100.4°F for 2+ days needs immediate medical attention."),
        ("💊", "Medications", "Set phone alarms for every medication. Stopping antibiotics early creates antibiotic-resistant bacteria."),
        ("🥦", "Diet", "Eat colorful fruits and vegetables rich in Vitamin C and zinc — essential minerals for immune function and healing."),
        ("🚿", "Hygiene", "Shower instead of bathing to keep wounds dry. Pat — don't rub — the area dry after washing."),
        ("📞", "Emergency Signs", "Call your doctor immediately for: high fever, increasing pain, unusual discharge, or difficulty breathing."),
        ("🧠", "Mental Health", "Recovery affects mood. Talk to family, maintain a daily routine, and celebrate small improvements."),
    ],
    "Injury Recovery": [
        ("🧊", "RICE Protocol", "Rest, Ice, Compression, Elevation — follow this for the first 48-72 hours after any activity-related pain spike."),
        ("🎽", "Compression", "Wear your compression bandage or brace as prescribed. It reduces swelling and provides joint stability."),
        ("⚡", "No Pain No Gain — MYTH", "During injury recovery, pain is a STOP signal, not motivation. Exercise within comfortable limits only."),
        ("🔥", "Heat vs Ice", "Use ice for first 72 hours (reduces swelling). Use heat after 72 hours (improves flexibility and blood flow)."),
        ("👟", "Footwear", "Wear supportive shoes even at home. Poor footwear puts extra stress on healing tendons and joints."),
        ("📐", "Posture", "Compensating for an injury changes your posture and creates new problems. Be conscious of how you move."),
        ("🏊", "Pool Therapy", "Swimming and water exercises are excellent for injury recovery — water reduces joint load by 90%."),
    ],
    "Stroke Rehab": [
        ("🧠", "Neuroplasticity", "Your brain can rewire itself. Repeat movements 300-400 times daily — repetition builds new neural pathways."),
        ("🖐️", "Hand Exercises", "Squeeze a soft ball 20 times every hour. Fine motor recovery requires consistent, frequent stimulation."),
        ("🗣️", "Speech Practice", "Read aloud for 10 minutes daily. Narrate what you're doing. Speech recovery requires daily practice."),
        ("👁️", "Visual Exercises", "Track a moving object with your eyes for 2 minutes. Visual field recovery responds well to targeted exercise."),
        ("🎵", "Music Therapy", "Listen to rhythmic music while doing exercises. Music activates multiple brain regions and aids motor recovery."),
        ("🤝", "Family Support", "Include family in your rehab sessions. Emotional support is proven to improve stroke recovery outcomes."),
        ("⏰", "Consistency", "Short sessions 3-4 times daily beat one long session. Frequency matters more than duration in neuro-rehab."),
    ]
}

def get_daily_tip(surgery_type: str, days_post: int, risk_level: str) -> dict:
    """
    Returns a personalized daily health tip based on surgery type and recovery day
    Rotates tips based on day number
    """
    tips = HEALTH_TIPS.get(surgery_type, HEALTH_TIPS["General Discharge"])
    tip_idx = days_post % len(tips)
    icon, title, content = tips[tip_idx]

    # Add urgency note for high/critical
    urgency_note = ""
    if risk_level == "Critical":
        urgency_note = "⚠️ Given your current critical status — please consult your doctor before attempting any activity."
    elif risk_level == "High":
        urgency_note = "⚠️ Due to high risk status — take extra caution and rest more than usual today."

    return {
        "icon": icon,
        "title": title,
        "content": content,
        "urgency_note": urgency_note,
        "day_number": days_post,
        "tip_category": surgery_type
    }