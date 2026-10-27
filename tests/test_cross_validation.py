"""Cross-Validation Engine Tests (The Core of the Pipeline).

Verifies:
- 2+ independent domain standard
- Numerical conflict detection (e.g. 42 vs 118 dead)
- Claim URL attribution preservation
- Satire filtering
- Recency window compliance
"""

import pytest
from ngo_pipeline.models import Article, ArticleCluster, VerificationStatus
from ngo_pipeline.stages.s4_cross_validate import CrossValidationEngine

@pytest.fixture
def engine():
    return CrossValidationEngine()

def test_numerical_conflict_detection(engine):
    cluster = ArticleCluster(
        topic="Flood Landslide Casualties in Wayanad",
        articles=[
            Article(
                url="https://thehindu.com/kerala/floods",
                domain="thehindu.com",
                title="Wayanad rescue confirms 42 dead",
                raw_text="District administration confirmed 42 dead following hillslope collapse in northern Wayanad.",
                age_hours=12.0,
            ),
            Article(
                url="https://bbc.com/world/india/wayanad",
                domain="bbc.com",
                title="Landslide toll hits 118 dead in Kerala",
                raw_text="Hospital coordinators report at least 118 dead as search teams comb plantation quarters.",
                age_hours=10.0,
            ),
        ],
    )
    result = engine.validate_cluster(cluster)
    assert result.status == VerificationStatus.CONFLICTING
    assert len(result.conflicting_claims) > 0
    assert "dead" in result.conflicting_claims[0].normalized_claim.lower()
    # Ensure source URLs are attached to the conflict claim
    assert "https://thehindu.com/kerala/floods" in result.conflicting_claims[0].source_urls
    assert "https://bbc.com/world/india/wayanad" in result.conflicting_claims[0].source_urls

def test_satire_rejection(engine):
    cluster = ArticleCluster(
        topic="Satire Breathing Tax Story",
        articles=[
            Article(
                url="https://theonion.com/breathing-tax",
                domain="theonion.com",
                title="Govt Imposes 200% Surcharge on Breathing",
                raw_text="Survivors who breathe compressed air will be taxed per lungful.",
                is_satire=True,
            )
        ],
    )
    result = engine.validate_cluster(cluster)
    assert result.status == VerificationStatus.REJECTED_SATIRE

def test_outdated_article_rejection(engine):
    cluster = ArticleCluster(
        topic="Historic 2019 Cyclone Relief",
        articles=[
            Article(
                url="https://thehindu.com/archive-2019",
                domain="thehindu.com",
                title="Relief package for Cyclone Fani",
                raw_text="Union Cabinet cleared financial aid for cyclone damage in 2019.",
                age_hours=65000.0,  # Well beyond 72h window
            )
        ],
    )
    result = engine.validate_cluster(cluster)
    assert result.status == VerificationStatus.REJECTED_OUTDATED
