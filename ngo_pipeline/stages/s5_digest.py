"""Stage 5: News Digest Generation.

Generates structured NGO briefings strictly grounded in verified facts.
Flagged conflicts are isolated in an explicit audit section rather than smoothed over.
"""

from __future__ import annotations

import logging
from typing import Optional
from ngo_pipeline.config import DEFAULT_CONFIG, PipelineConfig
from ngo_pipeline.llm.client import BaseLLMClient, get_llm_client
from ngo_pipeline.llm.prompts import DIGEST_SYSTEM, DIGEST_USER
from ngo_pipeline.models import ArticleCluster, NewsDigest, VerificationStatus

logger = logging.getLogger(__name__)

class DigestGenerator:
    """Produces objective, factual NGO executive digests."""

    def __init__(self, config: Optional[PipelineConfig] = None, llm: Optional[BaseLLMClient] = None):
        self.config = config or DEFAULT_CONFIG
        self.llm = llm or get_llm_client(self.config)

    def generate_digest(self, cluster: ArticleCluster) -> NewsDigest:
        """Create an executive briefing from cross-validated cluster facts."""
        verified_facts_texts = [f"- {c.normalized_claim}" for c in cluster.verified_claims]
        conflicts_texts = [f"- {c.conflict_details}" for c in cluster.conflicting_claims if c.conflict_details]

        if cluster.status == VerificationStatus.VERIFIED:
            user_prompt = DIGEST_USER.format(
                topic=cluster.topic,
                verified_facts_text="\n".join(verified_facts_texts) or "Independent reporting verified.",
                conflicts_text="None. Reporting across independent domains is consistent.",
                domains=", ".join(cluster.independent_domains),
            )
            res = self.llm.generate_json(DIGEST_SYSTEM, user_prompt)

            citations = list(set([a.url for a in cluster.articles if a.url]))
            return NewsDigest(
                cluster_id=cluster.cluster_id,
                headline=res.get("headline", f"Verified Field Report: {cluster.topic}"),
                executive_summary=res.get(
                    "executive_summary",
                    "Independent multi-source reporting confirms current humanitarian situation and relief deployment.",
                ),
                verified_facts=res.get("verified_facts", [c.normalized_claim for c in cluster.verified_claims]),
                flagged_conflicts=[],
                source_citations=citations,
                status=VerificationStatus.VERIFIED,
            )

        elif cluster.status == VerificationStatus.CONFLICTING:
            user_prompt = DIGEST_USER.format(
                topic=cluster.topic,
                verified_facts_text="Certain baseline events reported, but major statistical/factual discrepancies exist.",
                conflicts_text="\n".join(conflicts_texts) or cluster.conflict_summary or "Contradictory claims reported.",
                domains=", ".join(cluster.independent_domains),
            )
            res = self.llm.generate_json(DIGEST_SYSTEM, user_prompt)

            citations = list(set([a.url for a in cluster.articles if a.url]))
            return NewsDigest(
                cluster_id=cluster.cluster_id,
                headline=f"[CONFLICT DETECTED] Reporting Discrepancy: {cluster.topic}",
                executive_summary=res.get(
                    "executive_summary",
                    "Discrepant figures and contradictory claims were identified across independent news sources. The NGO verification desk has placed this briefing on hold pending primary corroboration.",
                ),
                verified_facts=[],
                flagged_conflicts=conflicts_texts or [cluster.conflict_summary or "Unresolved source discrepancies."],
                source_citations=citations,
                status=VerificationStatus.CONFLICTING,
            )

        else:
            # Single-source, satire, or outdated
            citations = list(set([a.url for a in cluster.articles if a.url]))
            return NewsDigest(
                cluster_id=cluster.cluster_id,
                headline=f"[{cluster.status.value.upper()}] {cluster.topic}",
                executive_summary=f"This story is classified as {cluster.status.value}. {cluster.rejection_reason or cluster.conflict_summary or 'Does not satisfy NGO verification standards.'}",
                verified_facts=[],
                flagged_conflicts=[cluster.conflict_summary or cluster.rejection_reason or "Unverified."],
                source_citations=citations,
                status=cluster.status,
            )
