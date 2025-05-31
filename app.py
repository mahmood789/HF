# app.py  – Heart‐Failure Odyssey API (Python 3.10+)
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import random, datetime

app = FastAPI(title="HF-Odyssey API")

# ─── CORS so any front‐end (including ChatGPT Actions) can call us ─────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── 1. /lab ─────────────────────────────────────────────────────────
@app.get("/lab")
def get_lab_result(test: str = Query(..., enum=[
    "ntprobnp", "creatinine", "potassium",
    "egfr", "hemoglobin", "ferritin"
])):
    values = {
        "ntprobnp":  f"{random.randint(900, 2400)} pg/mL",
        "creatinine": f"{round(random.uniform(0.9, 1.6), 2)} mg/dL",
        "potassium":  f"{round(random.uniform(3.8, 5.8), 1)} mmol/L",
        "egfr":       f"{random.randint(55, 90)} mL/min",
        "hemoglobin": f"{random.randint(100, 130)} g/L",
        "ferritin":   f"{random.randint(30, 80)} µg/L",
    }
    interp = {
        "ntprobnp": "Markedly elevated → suspect decompensated HF",
        "creatinine": "Monitor renal function with ACE-I",
        "potassium": "Check before MRA/ACE-I titration",
        "egfr": "eGFR acceptable for GDMT",
        "hemoglobin": "Mild anaemia",
        "ferritin": "Borderline low → consider IV iron",
    }
    return {
        "test": test,
        "value": values.get(test, "?"),
        "interpretation": interp.get(test, "")
    }

# ─── 2. /image ───────────────────────────────────────────────────────
@app.get("/image")
def get_imaging_result(
    type: str = Query(..., enum=["CXR", "Echo", "ECG"]),
    stage: str = Query(..., enum=["initial", "decompensated", "post_treatment"])
):
    base = "https://raw.githubusercontent.com/openai-images/hf-assets/main"
    fname = f"{type.lower()}_{stage}.png"
    return {
        "url": f"{base}/{fname}",
        "caption": f"{type} image ({stage})"
    }

# ─── 3. /diary ───────────────────────────────────────────────────────
diary_bank = {
    "after_echo": {
        "diary": "I saw my heart on the grey screen today. It thumped slower than I felt.",
        "mood": "⛅",
    },
    "after_medications": {
        "diary": "New pills make me pee more, but ankles look slimmer.",
        "mood": "🌞",
    },
    "post_decompensation": {
        "diary": "Oxygen mask tasted like metal. Kareem’s eyes were red.",
        "mood": "🌧",
    },
    "final": {
        "diary": "I can smell cardamom from the kitchen. Bilal hums softly.",
        "mood": "🕯️",
    },
}

@app.get("/diary")
def get_patient_diary(
    stage: str = Query(..., enum=list(diary_bank.keys()) + ["initial"])
):
    return diary_bank.get(stage, {"diary": "No entry yet", "mood": "🌥"})

# ─── 4. /decision ────────────────────────────────────────────────────
log: list[dict] = []

@app.post("/decision")
def record_decision(action: str, outcome: str = Query(..., enum=["correct", "incorrect", "partial"])):
    log.append({
        "ts": datetime.datetime.utcnow().isoformat(),
        "action": action,
        "outcome": outcome
    })
    return {"message": f"Decision recorded: {action} ({outcome})"}

# ─── 5. /trend ───────────────────────────────────────────────────────
@app.get("/trend")
def get_trend_chart(metric: str = Query(..., enum=["weight", "ntprobnp", "potassium", "creatinine"])):
    demo = "https://raw.githubusercontent.com/openai-images/hf-assets/main/trend_weight.png"
    return {"url": demo, "caption": f"{metric} trend chart"}

# ─── 6. /summary ─────────────────────────────────────────────────────
@app.get("/summary")
def get_score_summary():
    xp = sum(2 for d in log if d["outcome"] == "correct")
    return {
        "xp": xp,
        "decisions": log,
        "summary": "Great job! Review potassium before up‐titration."
    }
