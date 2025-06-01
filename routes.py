from fastapi import APIRouter, Query, Response, HTTPException
from pathlib import Path
import state

router = APIRouter()

# ---------- gameplay ----------
@router.post("/record_decision", tags=["Gameplay"])
def record_decision(
    user_id: str = Query(...),
    action: str = Query(...),
    outcome: str = Query(..., pattern="^(correct|partial|incorrect)$"),
    confidence: str = Query(..., pattern="^(sure|unsure)$")
):
    try:
        return state.evaluate(user_id, action, outcome, confidence)
    except ValueError as err:
        raise HTTPException(status_code=400, detail=str(err))

@router.get("/night_shift_page", tags=["Gameplay"])
def night_shift_page(user_id: str):
    return state.night_shift_questions(user_id)

# ---------- banner ----------
@router.get("/generate_banner_svg", tags=["Assets"])
def banner_svg(**params):
    """
    Fills banner_template.svg placeholders with query params.
    XP bars are scaled: 1 XP point → 4 px width; min width 1 px so bar is visible.
    """
    tpl = Path("banner_template.svg").read_text()

    keys = [
        "xp_diag","xp_sys","xp_emp","combo","coins",
        "focus","stress","cbw",
        "pill_ace","pill_bb","pill_mra","pill_sglt2",
        "device_stage",
        "token_anemia","token_ckd","token_af"
    ]
    payload = {k: int(params.get(k, 0)) for k in keys}

    # scale XP
    for xp in ("xp_diag", "xp_sys", "xp_emp"):
        payload[xp] = max(1, payload[xp] * 4)  # 1-px minimum

    svg = tpl.format(**payload)
    return Response(svg, media_type="image/svg+xml",
                    headers={"Cache-Control": "no-store"})
