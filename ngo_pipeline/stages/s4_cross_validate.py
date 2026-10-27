"""Stage 4: Cross-Validation Engine (The Core of the Pipeline).

Strict verification rules:
1. Treat a story as 'Verified' ONLY if at least 2 independent registered domains report it.
2. Extract atomic claims (who, what, when, numbers, raw quotes) from each article.
3. Compare claims across sources to detect numerical, entity, and timeline discrepancies.
4. Flag conflicts explicitly with source details rather than smoothing them over.
5. Classify every cluster & claim: Verified, Conflicting, Single-source, Rejected: Satire, Rejected: Outdated.
6. Keep source URLs attached to every claim for auditability.
"""

from __future__ import annotations

import logging
import re
from typing import Dict, List, Optional, Set, Tuple
from ngo_pipeline.config import DEFAULT_CONFIG, PipelineConfig
from ngo_pipeline.llm.client import BaseLLMClient, get_llm_client
from ngo_pipeline.llm.prompts import (
    CLAIM_EXTRACTION_SYSTEM,
    CLAIM_EXTRACTION_USER,
    CONFLICT_DETECTION_SYSTEM,
    CONFLICT_DETECTION_USER,
)
from ngo_pipeline.models import (
    Article,
    ArticleCluster,
    CrossValidatedClaim,
    ExtractedClaim,
    VerificationStatus,
)

logger = logging.getLogger(__name__)

class CrossValidationEngine:
    """Enforces multi-source cross-verification and conflict detection."""

    def __init__(self, config: Optional[PipelineConfig] = None, llm: Optional[BaseLLMClient] = None):
        self.config = config or DEFAULT_CONFIG
        self.llm = llm or get_llm_client(self.config)
        self.min_domains = self.config.min_independent_domains
        self.recency_window_hours = self.config.recency_window_hours

    def validate_cluster(self, cluster: ArticleCluster) -> ArticleCluster:
        """Execute complete cross-validation across all articles in a cluster."""
        articles = cluster.articles
        if not articles:
            cluster.status = VerificationStatus.SINGLE_SOURCE
            return cluster

        # Step 1: Satire filtering
        if any(a.is_satire for a in articles) or any(
            any(s in a.domain for s in self.config.satire_domains) for a in articles
        ):
            cluster.status = VerificationStatus.REJECTED_SATIRE
            cluster.rejection_reason = "Identified satire publication domain. Excluded from NGO reporting."
            return cluster

        # Step 2: Recency filtering
        ages = [a.age_hours for a in articles if a.age_hours is not None]
        if ages and all(age > self.recency_window_hours for age in ages):
            cluster.status = VerificationStatus.REJECTED_OUTDATED
            cluster.rejection_reason = f"Articles published {max(ages):.1f}h ago, exceeding {self.recency_window_hours}h recency limit."
            return cluster

        # Step 3: Count independent domains (ignore subdomains and duplicates)
        distinct_domains = sorted(list(set(a.domain for a in articles if a.domain)))
        cluster.independent_domains = distinct_domains
        cluster.independent_domain_count = len(distinct_domains)

        # Step 4: Extract atomic claims from each article
        all_extracted_claims: List[ExtractedClaim] = []
        for article in articles:
            extracted = self._extract_article_claims(article)
            all_extracted_claims.extend(extracted)

        # Step 5: Check single-source status
        if len(distinct_domains) < self.min_domains:
            cluster.status = VerificationStatus.SINGLE_SOURCE
            cluster.conflict_summary = f"Reported by only {len(distinct_domains)} independent domain ({', '.join(distinct_domains)}). Requires 2+ independent domains."
            for ec in all_extracted_claims:
                claim = CrossValidatedClaim(
                    normalized_claim=ec.what,
                    category="general",
                    status=VerificationStatus.SINGLE_SOURCE,
                    source_urls=[ec.source_url],
                    source_domains=[ec.source_domain],
                    supporting_quotes={ec.source_url: ec.raw_quote},
                    conflict_details="Single-source unverified report.",
                )
                cluster.claims.append(claim)
            return cluster

        # Step 6: Multi-source claim comparison and conflict detection
        cross_claims, conflicts, agreed = self._compare_claims(all_extracted_claims, distinct_domains)
        cluster.claims = cross_claims
        cluster.verified_claims = agreed
        cluster.conflicting_claims = conflicts

        if conflicts:
            cluster.status = VerificationStatus.CONFLICTING
            conflict_descriptions = [c.conflict_details for c in conflicts if c.conflict_details]
            cluster.conflict_summary = " | ".join(conflict_descriptions)
        else:
            cluster.status = VerificationStatus.VERIFIED

        return cluster

    def _extract_article_claims(self, article: Article) -> List[ExtractedClaim]:
        """Call LLM or deterministic rule-extractor to parse atomic claims from an article."""
        user_prompt = CLAIM_EXTRACTION_USER.format(
            title=article.title,
            domain=article.domain,
            published_at=article.published_at or "Unknown",
            text=article.raw_text[:2500],
        )

        try:
            res = self.llm.generate_json(CLAIM_EXTRACTION_SYSTEM, user_prompt)
            raw_claims = res.get("claims", [])
            claims: List[ExtractedClaim] = []

            for c in raw_claims:
                claim = ExtractedClaim(
                    article_id=article.id,
                    source_url=article.url,
                    source_domain=article.domain,
                    who=c.get("who", []),
                    what=c.get("what", ""),
                    when=c.get("when"),
                    numbers=[str(n) for n in c.get("numbers", [])],
                    raw_quote=c.get("raw_quote", article.raw_text[:150]),
                )
                claims.append(claim)
            return claims
        except Exception as e:
            logger.error(f"Error extracting claims for {article.url}: {e}")
            return [
                ExtractedClaim(
                    article_id=article.id,
                    source_url=article.url,
                    source_domain=article.domain,
                    who=["Authorities"],
                    what=article.title,
                    numbers=[],
                    raw_quote=article.title,
                )
            ]

    def _compare_claims(
        self, extracted_claims: List[ExtractedClaim], distinct_domains: List[str]
    ) -> Tuple[List[CrossValidatedClaim], List[CrossValidatedClaim], List[CrossValidatedClaim]]:
        """Compare numbers, dates, and claims across sources using dynamic unit extraction."""
        cross_claims: List[CrossValidatedClaim] = []
        conflicts: List[CrossValidatedClaim] = []
        agreed: List[CrossValidatedClaim] = []

        # Dynamic number & unit extraction supporting floats, decimals, and commas
        # Matches patterns like "42 dead", "118 dead", "500 crore", "2500 crore", "1,200 beds", "8,500 beds", "15,000 tonnes", "90,000 tonnes", "1.2 million"
        metric_pattern = re.compile(
            r"\b(\d+(?:,\d+)*(?:\.\d+)?)\s*([a-zA-Z]{3,15})\b",
            re.IGNORECASE,
        )

        # Map: metric_unit -> { domain: set of values }
        metric_domain_values: Dict[str, Dict[str, Set[float]]] = {}

        # Units that represent significant humanitarian measurements
        tracked_units = {
            "dead", "killed", "casualt", "casualties", "injured", "displaced",
            "crore", "million", "billion", "lakh", "fund", "funds", "damage",
            "bed", "beds", "shelter", "shelters", "tonne", "tonnes", "tons",
            "kit", "kits", "family", "families", "people"
        }

        for ec in extracted_claims:
            domain = ec.source_domain
            full_context = f"{ec.what} {ec.raw_quote}"

            for match in metric_pattern.finditer(full_context):
                num_str = match.group(1).replace(",", "")
                try:
                    val = float(num_str)
                except ValueError:
                    continue

                raw_unit = match.group(2).lower()
                
                # Normalize unit plural forms
                norm_unit = raw_unit
                for tu in tracked_units:
                    if tu in raw_unit or raw_unit in tu:
                        norm_unit = tu
                        break

                if norm_unit in tracked_units:
                    metric_domain_values.setdefault(norm_unit, {}).setdefault(domain, set()).add(val)

        # Check for discrepancies across independent domains for each tracked metric
        for unit, domain_map in metric_domain_values.items():
            if len(domain_map) >= 2:
                # Get representative number for each domain
                domain_summaries = []
                distinct_values = set()
                for dom, vals in domain_map.items():
                    max_v = max(vals)
                    distinct_values.add(max_v)
                    # Format float cleanly if integer
                    v_str = f"{int(max_v)}" if max_v.is_integer() else f"{max_v}"
                    domain_summaries.append(f"{dom} reports {v_str} {unit}")

                # If values differ across domains, register explicit conflict
                if len(distinct_values) > 1:
                    conflicting_urls = [ec.source_url for ec in extracted_claims if ec.source_domain in domain_map]
                    conflicting_quotes = {
                        ec.source_url: ec.raw_quote for ec in extracted_claims if ec.source_domain in domain_map
                    }

                    conflict_claim = CrossValidatedClaim(
                        normalized_claim=f"Conflicting statistics on {unit}",
                        category="numbers",
                        status=VerificationStatus.CONFLICTING,
                        source_urls=list(set(conflicting_urls)),
                        source_domains=list(domain_map.keys()),
                        supporting_quotes=conflicting_quotes,
                        conflict_details=f"Numerical discrepancy: {'; '.join(domain_summaries)}",
                    )
                    conflicts.append(conflict_claim)
                    cross_claims.append(conflict_claim)

        # Check LLM / auditor for semantic conflict signals
        claims_summary_text = "\n".join(
            [
                f"- Domain: {ec.source_domain} | URL: {ec.source_url} | What: {ec.what} | Numbers: {', '.join(ec.numbers)} | Quote: {ec.raw_quote}"
                for ec in extracted_claims[:12]
            ]
        )
        user_prompt = CONFLICT_DETECTION_USER.format(
            domain_count=len(distinct_domains),
            claims_block=claims_summary_text,
        )

        res = self.llm.generate_json(CONFLICT_DETECTION_SYSTEM, user_prompt)
        llm_conflicts = res.get("conflicts", [])
        for c in llm_conflicts:
            issue_title = c.get("issue", "Factual Discrepancy")
            # If not already flagged by numerical auditor
            if not any(issue_title.lower() in existing.normalized_claim.lower() for existing in conflicts):
                c_domains = c.get("domains_involved", distinct_domains)
                c_urls = [ec.source_url for ec in extracted_claims if ec.source_domain in c_domains]
                c_quotes = {ec.source_url: ec.raw_quote for ec in extracted_claims if ec.source_domain in c_domains}
                conflict_claim = CrossValidatedClaim(
                    normalized_claim=issue_title,
                    category="general",
                    status=VerificationStatus.CONFLICTING,
                    source_urls=list(set(c_urls)),
                    source_domains=c_domains,
                    supporting_quotes=c_quotes,
                    conflict_details=c.get("details", "Conflicting assertions across sources."),
                )
                conflicts.append(conflict_claim)
                cross_claims.append(conflict_claim)

        # If no conflicts detected, establish verified claims
        if not conflicts:
            llm_agreed = res.get("agreed_facts", [])
            for af in llm_agreed:
                supp_domains = af.get("supporting_domains", distinct_domains)
                if len(supp_domains) >= self.min_domains:
                    supp_urls = [ec.source_url for ec in extracted_claims if ec.source_domain in supp_domains]
                    supp_quotes = {ec.source_url: ec.raw_quote for ec in extracted_claims if ec.source_domain in supp_domains}
                    agreed_claim = CrossValidatedClaim(
                        normalized_claim=af.get("claim", ""),
                        category=af.get("category", "general"),
                        status=VerificationStatus.VERIFIED,
                        source_urls=list(set(supp_urls)),
                        source_domains=supp_domains,
                        supporting_quotes=supp_quotes,
                        conflict_details=None,
                    )
                    agreed.append(agreed_claim)
                    cross_claims.append(agreed_claim)

            # Ensure at least one verified claim for agreed multi-source event
            if not agreed and len(distinct_domains) >= self.min_domains:
                first_claim = extracted_claims[0]
                all_urls = list(set(ec.source_url for ec in extracted_claims))
                all_quotes = {ec.source_url: ec.raw_quote for ec in extracted_claims}
                fallback_verified = CrossValidatedClaim(
                    normalized_claim=f"Event independently confirmed by {', '.join(distinct_domains)}: {first_claim.what}",
                    category="general",
                    status=VerificationStatus.VERIFIED,
                    source_urls=all_urls,
                    source_domains=distinct_domains,
                    supporting_quotes=all_quotes,
                    conflict_details=None,
                )
                agreed.append(fallback_verified)
                cross_claims.append(fallback_verified)

        return cross_claims, conflicts, agreed
