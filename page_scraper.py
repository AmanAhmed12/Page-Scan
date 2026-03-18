import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
from dataclasses import dataclass, field
from typing import Optional


TIMEOUT = 15


@dataclass
class PageData:
    url: str
    html: str
    text_content: str

    meta_title: str
    meta_description: str

    word_count: int
    h1_count: int
    h2_count: int
    h3_count: int
    cta_count: int
    internal_links: int
    external_links: int
    image_count: int
    images_missing_alt: int
    images_missing_alt_pct: float

    headings: list[str] = field(default_factory=list)
    cta_texts: list[str] = field(default_factory=list)
    page_title: str = ""


def scrape(url: str) -> PageData:
    response = requests.get(url,timeout=TIMEOUT)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "lxml")
    parsed_base = urlparse(url)

    meta_title = (soup.find("title") or soup.new_tag("x")).get_text(strip=True)

    desc_tag = soup.find("meta", attrs={"name": re.compile(r"description", re.I)})
    meta_description = desc_tag.get("content", "").strip() if desc_tag else ""

    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    text_content = soup.get_text(separator=" ", strip=True)
    words = text_content.split()
    word_count = len(words)

    h1_tags = soup.find_all("h1")
    h2_tags = soup.find_all("h2")
    h3_tags = soup.find_all("h3")

    headings = []
    for tag in (h1_tags + h2_tags + h3_tags)[:20]:
        headings.append(f"[{tag.name.upper()}] {tag.get_text(strip=True)}")

    cta_keywords = re.compile(
        r"\b(get|start|try|buy|sign up|sign-up|signup|subscribe|download|"
        r"learn more|contact|book|schedule|request|demo|free|order|shop|"
        r"join|apply|register|access|claim|unlock)\b",
        re.I,
    )
    cta_elements = soup.find_all(["button", "a"])
    cta_matches = []
    for el in cta_elements:
        text = el.get_text(strip=True)
        if el.name == "button" or (el.name == "a" and cta_keywords.search(text)):
            if text:
                cta_matches.append(text)

    cta_texts = cta_matches[:10]
    cta_count = len(cta_matches)

    internal_links = 0
    external_links = 0
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        if not href or href.startswith("#") or href.startswith("mailto:") or href.startswith("tel:"):
            continue
        full = urljoin(url, href)
        parsed_link = urlparse(full)
        if parsed_link.netloc == parsed_base.netloc:
            internal_links += 1
        else:
            external_links += 1

    images = soup.find_all("img")
    image_count = len(images)
    missing_alt = sum(
        1 for img in images
        if not img.get("alt", "").strip()
    )
    missing_alt_pct = round((missing_alt / image_count * 100) if image_count else 0, 1)

    return PageData(
        url=url,
        html=response.text[:5000],
        text_content=" ".join(words[:1500]),
        meta_title=meta_title,
        meta_description=meta_description,
        word_count=word_count,
        h1_count=len(h1_tags),
        h2_count=len(h2_tags),
        h3_count=len(h3_tags),
        cta_count=cta_count,
        internal_links=internal_links,
        external_links=external_links,
        image_count=image_count,
        images_missing_alt=missing_alt,
        images_missing_alt_pct=missing_alt_pct,
        headings=headings,
        cta_texts=cta_texts,
        page_title=meta_title,
    )
