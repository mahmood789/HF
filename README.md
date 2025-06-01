# EchoSim (flat repo)

Minimal heart-failure narrative simulation with gamified learning.

## Run locally
```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
uvicorn app:app --reload
