import json
import os
from datetime import datetime
from pathlib import Path

from openai import OpenAI
from page_scraper import PageData
from schemas import AuditInsights


LOGS_DIR = Path(__file__).parent / "prompt_logs"
LOGS_DIR.mkdir(exist_ok=True)

MODEL = "gpt-4.1"

from prompts.system_prompt import SYSTEM_PROMPT


def _build_user_prompt(page: PageData) -> str:
    metrics_block = f"""
=== FACTUAL METRICS ===
URL: {page.url}
Meta Title: {page.meta_title or '(missing)'}
Meta Description: {page.meta_description or '(missing)'}

Word Count: {page.word_count}
H1 Count: {page.h1_count}
H2 Count: {page.h2_count}
H3 Count: {page.h3_count}

CTA Count: {page.cta_count}
CTA Texts (sample): {json.dumps(page.cta_texts)}

Internal Links: {page.internal_links}
External Links: {page.external_links}

Images: {page.image_count}
Images Missing Alt Text: {page.images_missing_alt} ({page.images_missing_alt_pct}%)

=== HEADING STRUCTURE (first 20) ===
{chr(10).join(page.headings) if page.headings else '(none found)'}

=== PAGE TEXT EXCERPT (first ~1500 words) ===
{page.text_content[:3000]}
"""
    return metrics_block.strip()


def analyze(page: PageData) -> tuple[AuditInsights, dict]:
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

    user_prompt = _build_user_prompt(page)

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt},
    ]

    completion = client.beta.chat.completions.parse(
        model=MODEL,
        messages=messages,
        response_format=AuditInsights,
        temperature=0.3,
    )

    insights: AuditInsights = completion.choices[0].message.parsed
    raw_output = completion.choices[0].message.content

    log = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "url": page.url,
        "model": MODEL,
        "system_prompt": SYSTEM_PROMPT,
        "user_prompt": user_prompt,
        "raw_model_output": raw_output,
        "parsed_output": insights.model_dump(),
        "usage": {
            "prompt_tokens": completion.usage.prompt_tokens,
            "completion_tokens": completion.usage.completion_tokens,
            "total_tokens": completion.usage.total_tokens,
        },
    }

    safe_url = page.url.replace("https://", "").replace("http://", "").replace("/", "_")[:60]
    log_filename = LOGS_DIR / f"{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{safe_url}.json"
    with open(log_filename, "w") as f:
        json.dump(log, f, indent=2)

    return insights, log
