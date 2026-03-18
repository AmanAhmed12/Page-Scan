# PageScan — AI Website Audit Tool

> A lightweight AI-powered website auditor built for EIGHT25MEDIA.  
> Extracts factual metrics from any public page, then uses structured AI analysis to surface SEO, messaging, CTA, content, and UX insights — with prioritised recommendations.

---
## Requirements

- Python 3.12 (recommended)

## Quick Start

### Option 1: Using Docker

```bash
# 1. Build the image
docker build -t page-scan .

# 2. Run the container
docker run -p 8501:8501 -e OPENAI_API_KEY=<your-open-api-key> page-scan
```

Open **http://localhost:8501** in your browser.

### Option 2: Local Setup

```bash
# 1. Clone & enter
git clone https://github.com/AmanAhmed12/Page-Scan.git
cd Page-Scan

# 2. Create virtual environment
python -m venv .venv
# Mac/Linux
source .venv/bin/activate

# Windows
.venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set your OpenAI API key
# Edit .env 
#OPENAI_API_KEY=your_api_key_here

# 5. Run Streamlit App
streamlit run app.py
```

Open **http://localhost:8501** in your browser.

---

## Architecture Overview

```
website-audit-tool/
├── app.py                  # Streamlit UI + main controller
├── page_scraper.py         # Extracts webpage data (title, meta, headings)
├── ai_analyzer.py          # Sends data to OpenAI + generates insights
├── schemas.py              # Pydantic models for structured data
│
├── prompts/
│   └── system_prompt.py    # Stores reusable AI system prompt
│
├── prompt_logs/            # Stores JSON logs of AI requests/responses
│
├── .env                    # Environment variables (API keys, configs)
├── .gitignore              # Ignore venv, logs, secrets
├── requirements.txt        # Project dependencies
├── README_PREV.md          # Older documentation (optional/backup)
│
├── .venv/                  # Virtual environment (not committed)
└── __pycache__/            # Python cache files
```

### Layer responsibilities

| Layer | Responsibility |
|---|---|
| `page_scraper.py` | Pure data extraction — no AI. Returns a `PageData` dataclass. |
| `schemas.py` | Defines the exact JSON shape the AI must return via Pydantic. |
| `ai_analyzer.py` | Builds prompts from `PageData`, calls OpenAI structured output, writes log. |
| `app.py` | The main Streamlit file. Mounts the UI, wires scraper → analyzer, and displays visualizations. |

---

## AI Design Decisions

### Structured Output with Pydantic
`openai.beta.chat.completions.parse()` is used with `response_format=AuditInsights`. This guarantees the model returns a valid object that matches the Pydantic schema — no fragile JSON parsing or hallucinated keys. If the model deviates, OpenAI raises a `LengthFinishReasonError` or validation error rather than silently returning garbage.

### Metrics-first prompting
The system prompt explicitly instructs the model: **every claim must reference a specific metric**. The user prompt is structured in two clearly labelled blocks (`=== FACTUAL METRICS ===` and `=== PAGE TEXT EXCERPT ===`), so the model has both quantitative context and qualitative page content without conflating the two.

### Temperature 0.3
Low temperature keeps recommendations consistent and grounded. Higher temperature introduced hallucinated statistics in testing.

### Text truncation
`text_content` is capped at ~1,500 words sent to the model to stay within token budget while covering above-the-fold content. `html` is stored but not sent — HTML noise degrades insight quality.

### Separated concerns
The scraper and analyzer are decoupled. To swap the scraper for Firecrawl, you only change `page_scraper.py` and map its output to `PageData`. The AI layer never touches HTTP.

---

## Replacing the Scraper (Firecrawl)

1. `pip install firecrawl-py`
2. Open `page_scraper.py`
3. Replace the body of `scrape(url)` with:

```python
from firecrawl import FirecrawlApp

def scrape(url: str) -> PageData:
    app = FirecrawlApp(api_key=os.environ["FIRECRAWL_API_KEY"])
    result = app.scrape_url(url, params={"formats": ["markdown", "html"]})
    # map result fields to PageData(...)
```

No other files need changing.

---

## Prompt Logs

Every audit run writes a JSON file to `prompt_logs/` containing:

```json
{
  "timestamp": "...",
  "url": "...",
  "model": "gpt-4o-mini",
  "system_prompt": "...",
  "user_prompt": "...",
  "raw_model_output": "...",
  "parsed_output": { ... },
  "usage": { "prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0 }
}
```

These are accessible natively within the Streamlit UI via the download button at the bottom of each audit results page.

---

## Trade-offs

| Decision | Trade-off |
|---|---|
| `gpt-4o-mini` default | Much cheaper per run; swap to `gpt-4.1` in `ai_analyzer.py` for richer insights |
| BeautifulSoup scraper | Fast, zero cost, works on 80% of sites; fails on JS-heavy SPAs — Firecrawl solves this |
| Single-page only | Keeps scope tight and fast; multi-page would need a crawl queue and cost much more per run |
| Streamlit UI | Extremely fast to develop Python-native data visualizations, albeit less customizable than Vanilla JS/React. |
| In-file prompt logs | Easy to inspect; in production, push to a DB or S3 |

---

## What I'd Improve With More Time

1. **JavaScript-rendered pages** — Use Playwright or Firecrawl to handle SPAs (React, Next.js, etc.)
2. **Competitor comparison** — Accept 2 URLs and diff their scores
3. **Historical tracking** — Store audits in SQLite, show score trends over time
4. **Streaming responses** — Stream AI insights token-by-token for a faster perceived UX
5. **Webhook / scheduled audits** — Re-audit a URL on a schedule and alert on score drops
6. **Richer CTA detection** — Use CSS selector heuristics to identify above-the-fold vs below-the-fold CTAs
7. **Core Web Vitals** — Integrate PageSpeed Insights API for performance data alongside content metrics
