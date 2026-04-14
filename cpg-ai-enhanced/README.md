# CPG Strategic Sourcing Suite Plus

An upgraded Flask SaaS demo for CPG supplier risk, outsourcing, RFQ tracking, qualification workflow, and executive dashboards.

## Added in this version
- Dashboard and sourcing filters
- Cleaner information hierarchy
- Better CPG-specific insight cards
- Country and qualification-stage filtering
- Commercially stronger executive summary
- UX notes for future app-store-ready improvements

## Run in GitHub Codespaces

```bash
unzip -o cpg-strategic-sourcing-suite-plus.zip
cd cpg-strategic-sourcing-suite-plus
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Open port 5000 in the browser.


## This version specifically fixes
- oversized sourcing page sections
- duplicated-feeling charts between views
- missing filters on sourcing and executive pages
- more logical top-to-bottom information flow
