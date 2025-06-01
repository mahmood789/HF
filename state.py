"""
JSON-based game state store; suitable for demo.
"""

import json, random
from pathlib import Path

STORE = Path("game_store.json")

def _load():
    return json.loads(STORE.read_text()) if STORE.exists() else {}

def _save(d): STORE.write_text(json.dumps(d, indent=2))

def _bucket(action):
    a = action.lower()
    if any(x in a for x in ("echo", "bnp", "angiography")): return "xp_diag"
    if any(x in a for x in ("counsel", "diary", "trust")):  return "xp_emp"
    return "xp_sys"

def _user(uid):
    base = {
        "xp_diag":0,"xp_emp":0,"xp_sys":0,
        "combo":0,"coins":0,
        "focus":80,"stress":20,"cbw":70,
        "pill_ace":0,"pill_bb":0,"pill_mra":0,"pill_sglt2":0,
        "device_stage":0,
        "token_anemia":0,"token_ckd":0,"token_af":0,
        "alert_debt":0
    }
    data = _load()
    if uid not in data: data[uid] = base
    return data

def evaluate(uid, action, outcome, confidence):
    data = _user(uid)
    s = data[uid]

    gain = {"correct":2, "partial":1, "incorrect":0}[outcome]
    bucket = _bucket(action)
    s[bucket] += gain

    # combo / synergy
    if outcome == "correct":
        s["combo"] += 1
        if s["combo"] >= 3:
            s["coins"] += 1
            if action.lower() in ("ace","bb","mra","sglt2"):
                s[bucket] += gain  # simple synergy
    else:
        s["combo"] = 0

    # stress / focus / cbw
    if outcome == "incorrect":
        s["stress"] += 10
        s["alert_debt"] += 1
    else:
        if confidence == "sure":
            s["stress"] -= 5
            s["focus"] += 2
        s["alert_debt"] = max(0, s["alert_debt"] - 1)

    s["cbw"] = max(0, min(100, s["cbw"]))
    s["focus"] = max(0, min(100, s["focus"]))
    s["stress"] = max(0, min(100, s["stress"]))

    _save(data)
    return {**s, "needs_night_shift": s["alert_debt"] >= 3}

def night_shift_questions(uid):
    return {
        "questions": [
            "List one mortality-reducing drug class in HFrEF.",
            "Ferritin cut-off for IV iron in HF?",
            "Indication criteria for CRT?"
        ],
        "expiry_seconds": 90
    }
