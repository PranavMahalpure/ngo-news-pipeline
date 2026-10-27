"""Deterministic Pipeline Orchestrator for NGO Verification and Social Digest.

Executes the 7-stage fixed pipeline:
Collect → Extract → Cluster → Cross-validate → Digest → Social posts → Human approval
"""

from __future__ import annotations

import logging
import time
from typing import Any, Dict, List, Optional
from ngo_pipeline.config import DEFAULT_CONFIG, PipelineConfig
from ngo_pipeline.db import Database
from ngo_pipeline.llm.client import BaseLLMClient, get_llm_client
from ngo_pipeline.models import (
    Article,
    ArticleCluster,
    NewsDigest,
    SocialPostDraft,
)
from ngo_pipeline.stages.s1_collect import NewsCollector
from ngo_pipeline.stages.s2_extract import ArticleExtractor
from ngo_pipeline.stages.s3_cluster import SemanticClusterer
from ngo_pipeline.stages.s4_cross_validate import CrossValidationEngine
from ngo_pipeline.stages.s5_digest import DigestGenerator
from ngo_pipeline.stages.s6_social_posts import SocialPostGenerator
from ngo_pipeline.stages.s7_human_approval import HumanApprovalManager

logger = logging.getLogger(__name__)

class VerificationPipeline:
    """Fixed deterministic pipeline orchestrator."""

    def __init__(
        self,
        config: Optional[PipelineConfig] = None,
        db: Optional[Database] = None,
        llm: Optional[BaseLLMClient] = None,
    ):
        self.config = config or DEFAULT_CONFIG
        self.db = db or Database(self.config.db_path)
        self.llm = llm or get_llm_client(self.config)

        # Initialize the 7 stages
        self.collector = NewsCollector(self.config)
        self.extractor = ArticleExtractor(self.config)
        self.clusterer = SemanticClusterer(self.config)
        self.validator = CrossValidationEngine(self.config, self.llm)
        self.digest_gen = DigestGenerator(self.config, self.llm)
        self.social_gen = SocialPostGenerator(self.config, self.llm)
        self.approval_mgr = HumanApprovalManager(self.db)

    def run(
        self,
        articles: Optional[List[Article]] = None,
        search_query: Optional[str] = None,
        fetch_online: bool = True,
    ) -> Dict[str, Any]:
        """Execute all 7 pipeline stages sequentially and deterministically."""
        start_time = time.time()
        stage_latencies: Dict[str, float] = {}

        # ---------------- Stage 1: Collect ----------------
        t0 = time.time()
        if articles is not None:
            raw_articles = articles
            logger.info(f"Stage 1: Ingested {len(raw_articles)} supplied candidate articles.")
        elif search_query:
            raw_articles = self.collector.search_news(search_query)
        else:
            raw_articles = self.collector.collect_from_rss()
        stage_latencies["s1_collect_ms"] = round((time.time() - t0) * 1000, 2)

        # ---------------- Stage 2: Extract ----------------
        t0 = time.time()
        extracted_articles = self.extractor.extract_batch(raw_articles, fetch_online=fetch_online)
        for article in extracted_articles:
            self.db.save_article(article)
        stage_latencies["s2_extract_ms"] = round((time.time() - t0) * 1000, 2)

        # ---------------- Stage 3: Cluster ----------------
        t0 = time.time()
        raw_clusters = self.clusterer.cluster_articles(extracted_articles)
        stage_latencies["s3_cluster_ms"] = round((time.time() - t0) * 1000, 2)

        # ---------------- Stage 4: Cross-validate ----------------
        t0 = time.time()
        validated_clusters: List[ArticleCluster] = []
        for cluster in raw_clusters:
            validated = self.validator.validate_cluster(cluster)
            self.db.save_cluster(validated)
            validated_clusters.append(validated)
        stage_latencies["s4_cross_validate_ms"] = round((time.time() - t0) * 1000, 2)

        # ---------------- Stage 5: Digest ----------------
        t0 = time.time()
        digests: List[NewsDigest] = []
        for cluster in validated_clusters:
            digest = self.digest_gen.generate_digest(cluster)
            self.db.save_digest(digest)
            digests.append(digest)
        stage_latencies["s5_digest_ms"] = round((time.time() - t0) * 1000, 2)

        # ---------------- Stage 6: Social posts ----------------
        t0 = time.time()
        all_drafts: List[SocialPostDraft] = []
        for cluster in validated_clusters:
            drafts = self.social_gen.generate_drafts(cluster)
            all_drafts.extend(drafts)
        stage_latencies["s6_social_posts_ms"] = round((time.time() - t0) * 1000, 2)

        # ---------------- Stage 7: Human approval ----------------
        t0 = time.time()
        self.approval_mgr.enqueue_drafts(all_drafts)
        stage_latencies["s7_human_approval_ms"] = round((time.time() - t0) * 1000, 2)

        total_latency_ms = round((time.time() - start_time) * 1000, 2)

        return {
            "articles_count": len(extracted_articles),
            "clusters_count": len(validated_clusters),
            "digests_count": len(digests),
            "drafts_created": len(all_drafts),
            "clusters": validated_clusters,
            "digests": digests,
            "drafts": all_drafts,
            "stage_latencies_ms": stage_latencies,
            "total_latency_ms": total_latency_ms,
        }
