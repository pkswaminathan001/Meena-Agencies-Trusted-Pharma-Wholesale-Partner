# Meena Agencies Trusted Pharma Wholesale Partner

A Streamlit-based B2B ordering application.

## Quick Start
1. `python3 -m venv .venv`
2. `source .venv/bin/activate`
3. `pip install -r requirements.txt`
4. Add token to `.streamlit/secrets.toml`
5. `streamlit run apps_isolated/meena.py`

## Testing
Run `bash scripts/test_all.sh`

## Security
Never commit `secrets.toml`. Runtime files (`users.json`, `retailers.json`) must be tracked.
