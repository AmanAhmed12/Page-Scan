
from pydantic import BaseModel, Field


class SEOAnalysis(BaseModel):
    reasoning: str = Field(description="Step-by-step logical explanation of the analysis based strictly on the metrics provided")
    score: int = Field(description="SEO health score 0-100")
    summary: str = Field(description="2-3 sentence SEO structure assessment referencing actual metrics")
    issues: list[str] = Field(description="Specific SEO problems found, each referencing a metric")


class MessagingAnalysis(BaseModel):
    reasoning: str = Field(description="Step-by-step logical explanation of the analysis based strictly on the metrics provided")
    score: int = Field(description="Messaging clarity score 0-100")
    summary: str = Field(description="2-3 sentence assessment of value proposition and clarity")
    issues: list[str] = Field(description="Specific messaging gaps or inconsistencies")


class CTAAnalysis(BaseModel):
    reasoning: str = Field(description="Step-by-step logical explanation of the analysis based strictly on the metrics provided")
    score: int = Field(description="CTA effectiveness score 0-100")
    summary: str = Field(description="2-3 sentence assessment of CTA usage and placement")
    issues: list[str] = Field(description="Specific CTA problems referencing count and text found")


class ContentAnalysis(BaseModel):
    reasoning: str = Field(description="Step-by-step logical explanation of the analysis based strictly on the metrics provided")
    score: int = Field(description="Content depth score 0-100")
    summary: str = Field(description="2-3 sentence assessment of content depth and quality")
    issues: list[str] = Field(description="Specific content depth gaps referencing word count and headings")


class UXAnalysis(BaseModel):
    reasoning: str = Field(description="Step-by-step logical explanation of the analysis based strictly on the metrics provided")
    score: int = Field(description="UX/structural health score 0-100")
    summary: str = Field(description="2-3 sentence assessment of UX and structural concerns")
    issues: list[str] = Field(description="Specific UX or structural problems found")


class Recommendation(BaseModel):
    priority: int = Field(description="Priority rank 1 (highest) to 5 (lowest)")
    title: str = Field(description="Short action-oriented title")
    reasoning: str = Field(description="Why this matters, explicitly referencing the metric that drove it")
    action: str = Field(description="Concrete step to implement this recommendation")


class AuditInsights(BaseModel):
    overall_score: int = Field(description="Overall page health score 0-100, weighted average of all dimensions")
    executive_summary: str = Field(description="3-4 sentence plain-English summary of the page's biggest strengths and weaknesses")
    seo: SEOAnalysis
    messaging: MessagingAnalysis
    cta: CTAAnalysis
    content: ContentAnalysis
    ux: UXAnalysis
    recommendations: list[Recommendation] = Field(
        description="3 to 5 prioritized recommendations, most impactful first"
    )
