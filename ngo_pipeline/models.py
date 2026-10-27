"""Data Models for the NGO Verification and Social Digest Pipeline.

Strict Pydantic schemas enforce type safety, URL tracking on every claim,
conflict flagging, platform-specific social post drafts, and evaluation fixtures.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel, Field, field_validator

class VerificationStatus(str, Enum):
    """Verification classification for news stories and claims."""
    VERIFIED = "Verified"
    CONFLICTING = "Conflicting"
    SINGLE_SOURCE = "Single-source"
    REJECTED_SATIRE = "Rejected: Satire"
    REJECTED_OUTDATED = "Rejected: Outdated"

class PlantedTrapType(str, Enum):
    """Benchmark evaluation trap types planted in frozen test clusters."""
    NONE = "none"
    FALSE_CLAIM = "false_claim"
    CONFLICTING_NUMBERS = "conflicting_numbers"
    SINGLE_SOURCE_RUMOR = "single_source_rumor"
    SATIRE_SITE = "satire_site"
    OUTDATED_ARTICLE = "outdated_article"

class ApprovalStatus(str, Enum):
    """Human approval lifecycle states."""
    PENDING_REVIEW = "PENDING_REVIEW"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    EDITED = "EDITED"

class Article(BaseModel):
    """Ingested news article representation."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    url: str
    domain: str
    title: str
    raw_text: str
    published_at: Optional[str] = None
    source_name: str = ""
    author: Optional[str] = None
    is_satire: bool = False
    age_hours: Optional[float] = None

    @field_validator("domain", mode="before")
    @classmethod
    def clean_domain(cls, v: str) -> str:
        if not v:
            return ""
        v = v.lower().strip()
        if v.startswith("http://") or v.startswith("https://"):
            from urllib.parse import urlparse
            return urlparse(v).netloc.replace("www.", "")
        return v.replace("www.", "")

class ExtractedClaim(BaseModel):
    """Atomic claim extracted from a single article."""
    claim_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    article_id: str
    source_url: str
    source_domain: str
    who: List[str] = Field(default_factory=list, description="Entities involved")
    what: str = Field(..., description="Action or core assertion")
    when: Optional[str] = Field(None, description="Timeframe or date")
    numbers: List[str] = Field(default_factory=list, description="Quantitative claims, e.g., deaths, funds, counts")
    raw_quote: str = Field(..., description="Direct excerpt from source for URL attribution verification")
    confidence: float = 1.0

class CrossValidatedClaim(BaseModel):
    """Claim evaluated across multiple articles in a cluster."""
    claim_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    normalized_claim: str
    category: str = "general"  # 'numbers', 'who', 'what', 'timeline', 'general'
    status: VerificationStatus
    source_urls: List[str] = Field(default_factory=list)
    source_domains: List[str] = Field(default_factory=list)
    supporting_quotes: Dict[str, str] = Field(
        default_factory=dict, description="Mapping of source_url to exact source quote"
    )
    conflict_details: Optional[str] = None

class ArticleCluster(BaseModel):
    """Group of articles reporting on the same event."""
    cluster_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    topic: str
    articles: List[Article] = Field(default_factory=list)
    status: VerificationStatus = VerificationStatus.SINGLE_SOURCE
    independent_domain_count: int = 0
    independent_domains: List[str] = Field(default_factory=list)
    claims: List[CrossValidatedClaim] = Field(default_factory=list)
    verified_claims: List[CrossValidatedClaim] = Field(default_factory=list)
    conflicting_claims: List[CrossValidatedClaim] = Field(default_factory=list)
    conflict_summary: Optional[str] = None
    rejection_reason: Optional[str] = None

class NewsDigest(BaseModel):
    """Structured NGO briefing digest grounded strictly in verified claims."""
    digest_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    cluster_id: str
    headline: str
    executive_summary: str
    verified_facts: List[str] = Field(default_factory=list)
    flagged_conflicts: List[str] = Field(default_factory=list)
    source_citations: List[str] = Field(default_factory=list)
    status: VerificationStatus
    generated_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

class SocialPostDraft(BaseModel):
    """Draft social media post awaiting human editorial approval."""
    draft_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    cluster_id: str
    platform: str  # 'x', 'linkedin', 'instagram'
    content: str
    character_count: int = 0
    source_urls: List[str] = Field(default_factory=list)
    verification_badge: str = "[NGO Verified]"
    status: ApprovalStatus = ApprovalStatus.PENDING_REVIEW
    reviewer_notes: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    reviewed_at: Optional[str] = None

    @field_validator("character_count", mode="before")
    @classmethod
    def compute_len(cls, v: int, info) -> int:
        # Pydantic v2 validation fallback
        return v

class EvaluationCluster(BaseModel):
    """Frozen test fixture cluster with planted traps for reproducible benchmarking."""
    cluster_id: str
    topic: str
    planted_trap: PlantedTrapType = PlantedTrapType.NONE
    expected_status: VerificationStatus
    ground_truth_claims: List[str] = Field(default_factory=list)
    expected_conflict_details: Optional[str] = None
    articles: List[Article] = Field(default_factory=list)
    notes: Optional[str] = None
