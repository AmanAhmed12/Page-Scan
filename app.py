import json
import os
from pathlib import Path
import sys

import streamlit as st
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

sys.path.insert(0, str(Path(__file__).parent.resolve()))

from page_scraper import scrape
from ai_analyzer import analyze

st.set_page_config(page_title="PageScan — AI Website Audit Tool", page_icon="⬡", layout="wide")

LOGS_DIR = Path(__file__).parent / "prompt_logs"

def render_score(overall_score, executive_summary):
    st.markdown("---")
    col1, col2 = st.columns([1, 4])
    with col1:
        st.metric(label="Overall Score", value=f"{overall_score}/100")
    with col2:
        st.subheader("Executive Summary")
        st.write(executive_summary)

def render_metrics(metrics):
    st.markdown("### 01 Factual Metrics")
    st.write("Raw data extracted from the page — no AI involved.")
    
    st.markdown(f"**Meta Title**: {metrics.get('meta_title') or '(missing)'}")
    st.markdown(f"**Meta Description**: {metrics.get('meta_description') or '(missing)'}")
    
    cols = st.columns(4)
    cols[0].metric("Word Count", metrics.get("word_count"))
    cols[1].metric("H1 Tags", metrics.get("h1_count"))
    cols[2].metric("H2 Tags", metrics.get("h2_count"))
    cols[3].metric("H3 Tags", metrics.get("h3_count"))
    
    cols2 = st.columns(4)
    cols2[0].metric("CTAs", metrics.get("cta_count"))
    cols2[1].metric("Internal Links", metrics.get("internal_links"))
    cols2[2].metric("External Links", metrics.get("external_links"))
    cols2[3].metric("Images", metrics.get("image_count"))
    
    st.metric("Missing Alt Text", f"{metrics.get('images_missing_alt_pct')}%", delta=f"{metrics.get('images_missing_alt')} images", delta_color="inverse")
    
    if metrics.get("headings"):
        with st.expander("Heading Structure"):
            for h in metrics["headings"]:
                st.text(h)
                
    if metrics.get("cta_texts"):
        with st.expander("CTA Texts Found"):
            for cta in metrics["cta_texts"]:
                st.text(cta)

def render_insights(insights):
    st.markdown("### 02 AI Insights")
    st.write("Generated from the metrics above. Every claim references factual data.")
    
    dims = [
        ("SEO Structure", insights.seo),
        ("Messaging Clarity", insights.messaging),
        ("CTA Usage", insights.cta),
        ("Content Depth", insights.content),
        ("UX & Structure", insights.ux),
    ]
    
    for label, d in dims:
        with st.expander(f"{label} - Score: {d.score}/100"):
            st.markdown(f"> **Reasoning:** {d.reasoning}")
            st.write(d.summary)
            for issue in d.issues:
                st.markdown(f"- {issue}")

def render_recommendations(recs):
    st.markdown("### 03 Recommendations")
    st.write("Prioritized by impact. Each tied to a specific metric.")
    for i, r in enumerate(recs, 1):
        with st.container():
            st.markdown(f"**{i}. {r.title}**")
            st.write(r.reasoning)
            st.info(f"→ {r.action}")

def main():
    st.title("⬡ PageScan")
    st.subheader("AI-powered website audit. Metrics first. Insights second.")
    st.markdown("Paste any public URL to get a full SEO & UX audit")
    
    with st.form("audit_form"):
        url_input = st.text_input("URL", placeholder="https://example.com", label_visibility="collapsed")
        submitted = st.form_submit_button("Audit →")
        
    if submitted:
        if not url_input.strip():
            st.error("URL is required")
            return
            
        url = url_input.strip()
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
            
        with st.spinner("Analyzing page... (Scraping metrics, then running AI analysis)"):
            try:
                page = scrape(url)
            except Exception as exc:
                st.error(f"Scraping failed: {exc}")
                return
                
            try:
                insights, log = analyze(page)
            except Exception as exc:
                st.error(f"AI analysis failed: {exc}")
                return
                
        metrics = {
            "url": page.url,
            "meta_title": page.meta_title,
            "meta_description": page.meta_description,
            "word_count": page.word_count,
            "h1_count": page.h1_count,
            "h2_count": page.h2_count,
            "h3_count": page.h3_count,
            "cta_count": page.cta_count,
            "cta_texts": page.cta_texts,
            "internal_links": page.internal_links,
            "external_links": page.external_links,
            "image_count": page.image_count,
            "images_missing_alt": page.images_missing_alt,
            "images_missing_alt_pct": page.images_missing_alt_pct,
            "headings": page.headings,
        }
        
        st.success(f"Audit complete for {url}")
        
        render_score(insights.overall_score, insights.executive_summary)
        render_metrics(metrics)
        st.markdown("---")
        render_insights(insights)
        st.markdown("---")
        render_recommendations(insights.recommendations)
        
        st.markdown("---")
        st.markdown("### Prompt Log")
        st.write("Full system prompt, user prompt, and raw model output saved for transparency.")
        
        prompt_log_file = sorted(LOGS_DIR.glob("*.json"))[-1] if list(LOGS_DIR.glob("*.json")) else None
        if prompt_log_file:
            with open(prompt_log_file, "r") as f:
                log_data = json.load(f)
            st.download_button(
                label="Download Prompt Log JSON",
                data=json.dumps(log_data, indent=2),
                file_name=prompt_log_file.name,
                mime="application/json"
            )

if __name__ == "__main__":
    main()