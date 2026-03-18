# PageScan — AI Website Audit Tool

PageScan is a tool built for EIGHT25MEDIA that extracts factual metrics from public webpages and uses an LLM to generate an SEO, messaging, CTA, content, and UX audit.

## Requirements

- Python 3.12 

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

## Architecture Overview

```text
website-audit-tool/
├── app.py                  # Streamlit UI + main controller
├── page_scraper.py         # Extracts webpage data (title, meta, headings)
├── ai_analyzer.py          # Sends data to OpenAI + generates insights
├── schemas.py              # Pydantic models for structured outputs
├── prompts/
│   └── system_prompt.py    # AI system prompt
├── prompt_logs/            # JSON logs of API requests
├── .env                    # Secrets
├── .gitignore              
├── requirements.txt        
├── DockerFile
├── .dockerignore
├── README_PREV.md          
├── .venv/                  
└── __pycache__/            
```

### Layer Responsibilities

| Layer | Responsibility |
|---|---|
| `page_scraper.py` | Data extraction only (no AI). Returns a `PageData` object. |
| `schemas.py` | Outlines the exact JSON shape the LLM must return using Pydantic. |
| `ai_analyzer.py` | Glues it together: builds the prompt, hits the OpenAI API, and saves the logs. |
| `app.py` | The frontend Streamlit dashboard. |

## AI Design Decisions

Here's how the AI layer was built to be reliable:

- **Strict JSON Validation:** I used OpenAI's structured outputs (`response_format=AuditInsights`) mapped directly to Pydantic models. This completely prevents the model from hallucinating keys or breaking the JSON payload. If the model messes up, the API fails cleanly rather than passing bad data to the UI.
- **Metrics-First Prompting:** To prevent the AI from generating generic fluff, the system prompt forces the model to cite specific metrics before making a claim. I separated the prompt into two distinct sections: one for hard data (e.g. "H1 count: 0") and one for the raw page text excerpt.
- **Lower Temperature:** The API temperature is permanently set to `0.3`. Pushing it any higher makes the model overly creative, which results in it inventing statistics that don't exist on the page.
- **Capping the Content Payload:** We limit the scraped text sent to the model to approximately 1,500 words. This captures the critical above-the-fold content while keeping token costs strictly under control. The raw HTML is explicitly excluded from the prompt to avoid confusing the model with DOM noise.
- **Decoupling AI from Scraping:** The AI layer has zero knowledge of making HTTP requests. The scraper handles all standard extraction, making it incredibly simple to swap the parser out for a headless browser later if needed.

## Trade-offs

- **BeautifulSoup vs. Headless Webdriver:** `requests` + `BeautifulSoup` is extraordinarily fast and costs nothing, but it falls down if the webpage relies entirely on client-side JavaScript to render content (like a React SPA).
- **Single Page vs. Site Crawl:** The tool audits exactly one URL. A full site crawler would provide deeper insights across an entire sitemap, but would introduce massive execution delays and multiply the OpenAI API costs per run exponentially.
- **Streamlit vs. React Frontend:** Streamlit let me prototype the UI and visualizations natively in Python in a tiny fraction of the time, but lacks the granular CSS customization abilities of a Next.js or React dashboard.
- **Local Prompt Logs:** By default, every AI transaction is dumped to a local JSON file in `prompt_logs/`. This is perfect for debugging and proving the model's reasoning, but for a real production tool, these should be pushed directly to a database or S3.

## What I'd Improve With More Time

If I had more time to refine this, I'd tackle:
1. **SPA Scraping Support:** I'd wire up Playwright or Firecrawl to handle JavaScript-rendered sites.
2. **Historical Tracking:** Adding a lightweight SQLite DB to track scores over time, showing the user if their metrics are improving or declining.
3. **Head-to-Head Comparisons:** Letting the user input two URLs to diff an audit against a competitor's site directly.
4. **Output Streaming:** Streaming the API response token-by-token in the UI rather than waiting for the entire object to parse, purely for a faster perceived load time.
5. **Core Web Vitals:** Hitting Google's PageSpeed Insights API so performance metrics could be factored directly into the AI's UX score.

## Prompt Logs

Every single audit writes an execution trace to the `prompt_logs/` directories. This JSON includes the exact system prompt, the user data sent to the AI, the raw response, and the exact token usage numbers. 

You can download these natively in the Streamlit app at the bottom of the audit results view.
