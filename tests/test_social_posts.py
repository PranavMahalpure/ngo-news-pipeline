"""Tests for Social Post Drafting and Human Editorial Approval Queue."""

import pytest
from ngo_pipeline.db import Database
from ngo_pipeline.models import (
    ApprovalStatus,
    Article,
    ArticleCluster,
    CrossValidatedClaim,
    VerificationStatus,
)
from ngo_pipeline.stages.s6_social_posts import SocialPostGenerator
from ngo_pipeline.stages.s7_human_approval import HumanApprovalManager

def test_social_post_character_limit_and_url():
    social_gen = SocialPostGenerator()
    verified_claim = CrossValidatedClaim(
        normalized_claim="100,000 oral cholera vaccines distributed in Assam",
        status=VerificationStatus.VERIFIED,
        source_urls=["https://pib.gov.in/assam-drive"],
        source_domains=["pib.gov.in", "thehindu.com"],
    )
    cluster = ArticleCluster(
        topic="Assam Inoculation Campaign Following Floods",
        status=VerificationStatus.VERIFIED,
        articles=[Article(url="https://pib.gov.in/assam-drive", domain="pib.gov.in", title="Assam Drive", raw_text="100,000 doses distributed.")],
        verified_claims=[verified_claim],
    )

    drafts = social_gen.generate_drafts(cluster)
    x_draft = next(d for d in drafts if d.platform == "x")
    
    # Assert X post length strictly <= 280
    assert len(x_draft.content) <= 280
    # Assert source URL included
    assert "https://pib.gov.in/assam-drive" in x_draft.content
    assert x_draft.status == ApprovalStatus.PENDING_REVIEW

def test_human_approval_queue_lifecycle(tmp_path):
    db = Database(tmp_path / "queue_test.db")
    mgr = HumanApprovalManager(db)
    social_gen = SocialPostGenerator()

    cluster = ArticleCluster(
        topic="Clean Water for 50,000 Children",
        status=VerificationStatus.VERIFIED,
        articles=[Article(url="https://reuters.com/water", domain="reuters.com", title="Water Drive", raw_text="Potable water supplied.")],
        verified_claims=[CrossValidatedClaim(normalized_claim="Water delivered", status=VerificationStatus.VERIFIED)],
    )

    drafts = social_gen.generate_drafts(cluster)
    mgr.enqueue_drafts(drafts)

    pending = mgr.list_pending()
    assert len(pending) == 3

    # Test Approval
    target_draft = pending[0]
    draft_id = target_draft["draft_id"]
    mgr.approve_draft(draft_id, reviewer="senior_editor", notes="Verified with UN field report")

    approved = mgr.list_approved()
    assert len(approved) == 1
    assert approved[0]["draft_id"] == draft_id
    assert approved[0]["reviewer_notes"] == "Verified with UN field report"

    # Test Rejection
    second_draft_id = pending[1]["draft_id"]
    mgr.reject_draft(second_draft_id, reviewer="senior_editor", reason="Sensational wording")
    remaining_pending = mgr.list_pending()
    assert len(remaining_pending) == 1
