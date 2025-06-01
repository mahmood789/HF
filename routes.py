from fastapi import APIRouter, Query, Response, HTTPException
from pathlib import Path
import state

router = APIRouter()

@router.post("/record_decision", tags=["Gameplay"])
def record_decision(
    user_id: str = Query(...),
    action: str = Query(...),
    outcome: str = Query(..., regex="^(correct|partial|incorrect)$"),
    confidence: str = Query(..., regex="^(sure|unsure)$")
):
    try:
        return state.evaluate(user_id, action, outcome, confidence)
    except ValueError as err:
        raise HTTPException(status_code=400, detail=str(err))

@router.get("/night_shift_page", tags=["Gameplay"])
def night_shift_page(user_id: str):
    return state.night_shift_questions(user_id)

@router.get("/generate_banner_svg", tags=["Assets"])
def banner_svg(**params):
    """
    Fills banner_template.svg placeholders with query params.
    XP values are multiplied by 4 to convert points → pixel width.
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

    # scale XP to pixel width (1 XP = 4 px)
    for k in ("xp_diag", "xp_sys", "xp_emp"):
        payload[k] *= 4

    svg = tpl.format(**payload)
    return Response(svg, media_type="image/svg+xml")
