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
def banner_svg(
    xp_diag: int = Query(default=0),
    xp_sys: int = Query(default=0),
    xp_emp: int = Query(default=0),
    combo: int = Query(default=0),
    coins: int = Query(default=0),
    focus: int = Query(default=80),
    stress: int = Query(default=20),
    cbw: int = Query(default=70),
    pill_ace: int = Query(default=0),
    pill_bb: int = Query(default=0),
    pill_mra: int = Query(default=0),
    pill_sglt2: int = Query(default=0),
    device_stage: int = Query(default=0),
    token_anemia: int = Query(default=0),
    token_ckd: int = Query(default=0),
    token_af: int = Query(default=0)
):
    """
    Fills banner_template.svg placeholders with query params.
    XP bars are scaled: 1 XP point → 4 px width; min width 1 px so bar is visible.
    """
    tpl = Path("banner_template.svg").read_text()

    # Scale XP (1 XP point → 4 px width; min width 1 px so bar is visible)
    scaled_xp_diag = max(1, xp_diag * 4)
    scaled_xp_sys = max(1, xp_sys * 4) 
    scaled_xp_emp = max(1, xp_emp * 4)

    # Calculate device stage positioning
    device_height = 22 * device_stage
    device_y = 66 - device_height

    # First, replace the complex expressions manually
    tpl = tpl.replace("{66 - 22*device_stage}", str(device_y))
    tpl = tpl.replace("{22*device_stage}", str(device_height))

    # Now format with all the simple placeholders
    payload = {
        "xp_diag": scaled_xp_diag,
        "xp_sys": scaled_xp_sys,
        "xp_emp": scaled_xp_emp,
        "combo": combo,
        "coins": coins,
        "focus": focus,
        "stress": stress,
        "cbw": cbw,
        "pill_ace": pill_ace,
        "pill_bb": pill_bb,
        "pill_mra": pill_mra,
        "pill_sglt2": pill_sglt2,
        "device_stage": device_stage,
        "token_anemia": token_anemia,
        "token_ckd": token_ckd,
        "token_af": token_af
    }

    svg = tpl.format(**payload)

    return Response(svg, media_type="image/svg+xml",
                    headers={"Cache-Control": "no-store"})
