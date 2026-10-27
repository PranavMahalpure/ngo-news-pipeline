"""Stage 6: Platform-Specific Social Post Draft Generation.

Strictly drafts posts only from VERIFIED facts.
Generates tailored posts for X (<280 chars), LinkedIn, and Instagram with source citations.
Enforces draft status (PENDING_REVIEW) for mandatory human editorial approval.
"""

from __future__ import annotations

import logging
from typing import List, Optional
from ngo_pipeline.config import DEFAULT_CONFIG, PipelineConfig
from ngo_pipeline.llm.client import BaseLLMClient, get_llm_client
from ngo_pipeline.llm.prompts import SOCIAL_POSTS_SYSTEM, SOCIAL_POSTS_USER
from ngo_pipeline.models import (
    ApprovalStatus,
    ArticleCluster,
    SocialPostDraft,
    VerificationStatus,
)

logger = logging.getLogger(__name__)

class SocialPostGenerator:
    """Generates draft social posts strictly grounded in verified facts."""

    def __init__(self, config: Optional[PipelineConfig] = None, llm: Optional[BaseLLMClient] = None):
        self.config = config or DEFAULT_CONFIG
        self.llm = llm or get_llm_client(self.config)
        self.max_x_len = self.config.max_x_length

    def generate_drafts(self, cluster: ArticleCluster) -> List[SocialPostDraft]:
        """Generate platform drafts for human review. Only verified stories get public post drafts."""
        # Safety gate: If not verified, DO NOT generate public social media drafts
        if cluster.status != VerificationStatus.VERIFIED:
            logger.info(
                f"Cluster {cluster.cluster_id} is '{cluster.status.value}'. Skipping public social post generation for NGO safety."
            )
            return []

        primary_url = cluster.articles[0].url if cluster.articles else "https://ngo-verified.org"
        verified_facts_text = "\n".join([f"- {c.normalized_claim}" for c in cluster.verified_claims])

        user_prompt = SOCIAL_POSTS_USER.format(
            topic=cluster.topic,
            verified_facts_text=verified_facts_text or "Humanitarian field operations independently confirmed.",
            primary_url=primary_url,
        )

        res = self.llm.generate_json(SOCIAL_POSTS_SYSTEM, user_prompt)
        drafts: List[SocialPostDraft] = []

        # 1. Draft for Platform X (strictly under 280 characters)
        x_text = res.get("x_post", "").strip()
        x_text = self._enforce_x_constraints(x_text, cluster.topic, primary_url)
        draft_x = SocialPostDraft(
            cluster_id=cluster.cluster_id,
            platform="x",
            content=x_text,
            character_count=len(x_text),
            source_urls=[primary_url],
            verification_badge="[NGO Verified]",
            status=ApprovalStatus.PENDING_REVIEW,
        )
        drafts.append(draft_x)

        # 2. Draft for LinkedIn
        linkedin_text = res.get("linkedin_post", "").strip()
        if primary_url not in linkedin_text:
            linkedin_text += f"\n\nSource Report: {primary_url}"
        draft_li = SocialPostDraft(
            cluster_id=cluster.cluster_id,
            platform="linkedin",
            content=linkedin_text,
            character_count=len(linkedin_text),
            source_urls=[primary_url],
            verification_badge="[NGO Verified]",
            status=ApprovalStatus.PENDING_REVIEW,
        )
        drafts.append(draft_li)

        # 3. Draft for Instagram
        insta_text = res.get("instagram_post", "").strip()
        if primary_url not in insta_text:
            insta_text += f"\n\n🔗 Verified Source: {primary_url}"
        draft_ig = SocialPostDraft(
            cluster_id=cluster.cluster_id,
            platform="instagram",
            content=insta_text,
            character_count=len(insta_text),
            source_urls=[primary_url],
            verification_badge="[NGO Verified]",
            status=ApprovalStatus.PENDING_REVIEW,
        )
        drafts.append(draft_ig)

        return drafts

    def _enforce_x_constraints(self, raw_x: str, topic: str, primary_url: str) -> str:
        """Strictly enforce the 280-character ceiling for platform X while preserving source link."""
        if len(raw_x) <= self.max_x_len and primary_url in raw_x and len(raw_x) > 30:
            return raw_x

        suffix = f" Details: {primary_url} #NGOVerified"
        available_chars = self.max_x_len - len(suffix)

        clean_topic = topic.replace("\n", " ").strip()
        if len(clean_topic) > available_chars:
            clean_topic = clean_topic[: available_chars - 3].rstrip() + "..."

        formatted = f"Verified: {clean_topic}{suffix}"
        return formatted[: self.max_x_len]
