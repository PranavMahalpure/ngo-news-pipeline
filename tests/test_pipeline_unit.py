"""Unit Tests for All 7 Pipeline Stages."""

import pytest
from ngo_pipeline.models import (
    Article,
    ArticleCluster,
    ApprovalStatus,
    VerificationStatus,
)
from ngo_pipeline.stages.s2_extract import ArticleExtractor
from ngo_pipeline.stages.s3_cluster import SemanticClusterer
from ngo_pipeline.stages.s4_cross_validate import CrossValidationEngine
from ngo_pipeline.stages.s5_digest import DigestGenerator
from ngo_pipeline.stages.s6_social_posts import SocialPostGenerator
from ngo_pipeline.stages.s7_human_approval import HumanApprovalManager
from ngo_pipeline.db import Database

def test_article_extractor_satire_and_age():
    extractor = ArticleExtractor()
    satire_art = Article(
        url="https://theonion.com/news/test",
        domain="theonion.com",
        title="Test Satire Article",
        raw_text="This is satire text.",
        published_at="2026-10-26T10:00:00Z",
    )
    processed = extractor.extract(satire_art, fetch_online=False)
    assert processed.is_satire is True
    assert processed.domain == "theonion.com"

def test_semantic_clusterer():
    clusterer = SemanticClusterer()
    articles = [
        Article(
            url="https://source1.com/a1",
            domain="source1.com",
            title="Heavy Flooding Hits Assam Valley",
            raw_text="Continuous torrential monsoon rain caused severe flooding in Assam affecting thousands.",
        ),
        Article(
            url="https://source2.com/a2",
            domain="source2.com",
            title="Assam Flood Crisis Intensifies Following Rain",
            raw_text="Thousands of residents displaced as river waters breach embankments in Assam.",
        ),
        Article(
            url="https://source3.com/a3",
            domain="source3.com",
            title="Tech Startup Unveils New Smartphone Processor",
            raw_text="Silicon manufacturer announced next-generation 3nm mobile processing chip.",
        ),
    ]
    clusters = clusterer.cluster_articles(articles)
    assert len(clusters) >= 2  # Assam floods clustered together, Tech separate

def test_cross_validation_two_domain_rule():
    validator = CrossValidationEngine()
    
    # Single source cluster
    single_cluster = ArticleCluster(
        topic="Unverified Water Leak",
        articles=[
            Article(
                url="https://blog.com/1",
                domain="blog.com",
                title="Rumor of water leak",
                raw_text="An unverified leak claims water was cut off.",
            )
        ],
    )
    res_single = validator.validate_cluster(single_cluster)
    assert res_single.status == VerificationStatus.SINGLE_SOURCE
    assert res_single.independent_domain_count == 1

    # Same domain 2 articles cluster (Must still be Single-source!)
    same_domain_cluster = ArticleCluster(
        topic="Same Domain Event",
        articles=[
            Article(
                url="https://news-outlet.org/article1",
                domain="news-outlet.org",
                title="Part 1 of event",
                raw_text="Event is developing according to our reporter.",
            ),
            Article(
                url="https://news-outlet.org/article2",
                domain="news-outlet.org",
                title="Part 2 of event",
                raw_text="Further update from our same news room.",
            ),
        ],
    )
    res_same = validator.validate_cluster(same_domain_cluster)
    assert res_same.status == VerificationStatus.SINGLE_SOURCE
    assert res_same.independent_domain_count == 1

def test_digest_and_social_posts_safety_gating(tmp_path):
    db = Database(tmp_path / "test.db")
    digest_gen = DigestGenerator()
    social_gen = SocialPostGenerator()
    approval_mgr = HumanApprovalManager(db)

    # Verified cluster
    verified_cluster = ArticleCluster(
        topic="Clean Water Delivered to 50,000 Children",
        status=VerificationStatus.VERIFIED,
        independent_domain_count=2,
        independent_domains=["reuters.com", "aljazeera.com"],
        articles=[
            Article(url="https://reuters.com/news", domain="reuters.com", title="Clean Water Drive", raw_text="Water delivered."),
            Article(url="https://aljazeera.com/news", domain="aljazeera.com", title="Water Convoy", raw_text="Aid convoy arrived."),
        ],
    )
    digest = digest_gen.generate_digest(verified_cluster)
    assert digest.status == VerificationStatus.VERIFIED
    assert len(digest.source_citations) >= 2

    drafts = social_gen.generate_drafts(verified_cluster)
    assert len(drafts) == 3  # X, LinkedIn, Instagram
    for d in drafts:
        assert d.status == ApprovalStatus.PENDING_REVIEW
        if d.platform == "x":
            assert len(d.content) <= 280

    approval_mgr.enqueue_drafts(drafts)
    pending = approval_mgr.list_pending()
    assert len(pending) == 3

    # Safety Gating: Conflicting cluster must NEVER generate social drafts
    conflicting_cluster = ArticleCluster(
        topic="Conflicting Casualty Toll",
        status=VerificationStatus.CONFLICTING,
        conflict_summary="42 vs 118 dead",
    )
    conflicting_drafts = social_gen.generate_drafts(conflicting_cluster)
    assert len(conflicting_drafts) == 0  # 100% Gated!
