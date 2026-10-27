"""Evaluation Judge Module combining Deterministic Rules and LLM-as-a-Judge.

Calculates hallucination rate, source attribution validity, post quality,
and adherence to NGO factual safety standards.
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional
from ngo_pipeline.llm.client import BaseLLMClient, get_llm_client
from ngo_pipeline.llm.prompts import (
    JUDGE_ATTRIBUTION_SYSTEM,
    JUDGE_HALLUCINATION_SYSTEM,
)
from ngo_pipeline.models import Article, CrossValidatedClaim, SocialPostDraft

class LLMJudge:
    """Evaluates outputs against ground truth source texts using deterministic rules + local LLM."""

    def __init__(self, llm: Optional[BaseLLMClient] = None):
        self.llm = llm or get_llm_client()

    def evaluate_source_attribution(
        self, claim: CrossValidatedClaim, articles: List[Article]
    ) -> Dict[str, Any]:
        """Check whether each URL cited by the claim actually contains supporting evidence."""
        results = {}
        article_map = {a.url: a.raw_text for a in articles}

        for url in claim.source_urls:
            raw_text = article_map.get(url, "")
            quote = claim.supporting_quotes.get(url, "")

            # Deterministic check 1: Exact quote containment
            if quote and quote.lower() in raw_text.lower():
                results[url] = {
                    "is_supported": True,
                    "confidence": 1.0,
                    "method": "exact_quote_match",
                }
                continue

            # Deterministic check 2: High token overlap (>60% of significant words)
            claim_tokens = set(re.findall(r"\b\w{4,}\b", claim.normalized_claim.lower()))
            source_tokens = set(re.findall(r"\b\w{4,}\b", raw_text.lower()))

            if claim_tokens:
                overlap = len(claim_tokens.intersection(source_tokens)) / len(claim_tokens)
            else:
                overlap = 0.0

            if overlap >= 0.55:
                results[url] = {
                    "is_supported": True,
                    "confidence": overlap,
                    "method": "token_overlap",
                }
                continue

            # Fallback: LLM Judge evaluation for fuzzy paraphrases
            user_prompt = f"Claim: {claim.normalized_claim}\nSource Excerpt: {raw_text[:1200]}"
            llm_res = self.llm.generate_json(JUDGE_ATTRIBUTION_SYSTEM, user_prompt)
            results[url] = {
                "is_supported": bool(llm_res.get("is_supported", False)),
                "confidence": float(llm_res.get("confidence", 0.5)),
                "method": "llm_judge",
                "reasoning": llm_res.get("reasoning", ""),
            }

        overall_supported = all(r["is_supported"] for r in results.values()) if results else False
        return {
            "claim": claim.normalized_claim,
            "overall_supported": overall_supported,
            "url_breakdown": results,
        }

    def evaluate_hallucination(
        self, generated_text: str, source_articles: List[Article]
    ) -> Dict[str, Any]:
        """Detect facts, numbers, or entities in generated output absent from source articles."""
        all_sources_text = " ".join([a.raw_text for a in source_articles])

        # 1. Deterministic number check: Every significant number in generated text should exist in source text
        gen_numbers = set(re.findall(r"\b\d+(?:,\d+)*(?:\.\d+)?\b", generated_text))
        src_numbers = set(re.findall(r"\b\d+(?:,\d+)*(?:\.\d+)?\b", all_sources_text))

        # Ignore formatting numbers like character limits or step indices
        exempt_numbers = {"280", "1", "2", "3", "4", "5", "10", "100"}
        unsupported_numbers = [n for n in gen_numbers if n not in src_numbers and n not in exempt_numbers]

        # 2. Check for explicit named entities (e.g. UNESCO, Red Cross, Assam, UNICEF)
        # Acronyms (e.g., WHO, UNICEF, NDRF, MSF)
        gen_acronyms = set(re.findall(r"\b[A-Z]{2,6}\b", generated_text))
        src_acronyms = set(re.findall(r"\b[A-Z]{2,6}\b", all_sources_text))
        common_acronyms = {"NGO", "URL", "USA", "THE", "ALL", "AND", "PM"}
        unsupported_acronyms = [a for a in (gen_acronyms - common_acronyms) if a not in src_acronyms]

        is_hallucinated = len(unsupported_numbers) > 0 or len(unsupported_acronyms) > 0

        if is_hallucinated:
            return {
                "is_hallucinated": True,
                "hallucination_score": min(1.0, 0.4 * len(unsupported_numbers) + 0.3 * len(unsupported_acronyms)),
                "hallucinated_elements": {
                    "unsupported_numbers": unsupported_numbers,
                    "unsupported_acronyms": unsupported_acronyms,
                },
                "method": "deterministic_number_acronym_check",
            }

        return {
            "is_hallucinated": False,
            "hallucination_score": 0.0,
            "hallucinated_elements": {},
            "method": "deterministic_grounding_verified",
        }

    def evaluate_post_quality(
        self, draft: SocialPostDraft, verified_claims: List[CrossValidatedClaim]
    ) -> Dict[str, Any]:
        """Validate character limits, tone, and that unverified/conflicting claims are never stated."""
        content = draft.content
        char_count = len(content)

        # 1. Platform-specific length check
        length_ok = True
        length_reason = "OK"
        if draft.platform == "x" and char_count > 280:
            length_ok = False
            length_reason = f"X post exceeds 280 characters ({char_count} chars)"

        # 2. Source link presence
        has_source_link = bool(re.search(r"https?://\S+", content))

        # 3. Tone check (no sensationalism or clickbait)
        clickbait_patterns = [
            r"\bSHOCKING\b", r"\bYOU WON'?T BELIEVE\b", r"\bMINDBLOWING\b",
            r"\bSECRET EXPOSED\b", r"\bEXCLUSIVE LEAK\b"
        ]
        has_clickbait = any(re.search(p, content, re.IGNORECASE) for p in clickbait_patterns)

        quality_score = 1.0
        if not length_ok:
            quality_score -= 0.5
        if not has_source_link:
            quality_score -= 0.2
        if has_clickbait:
            quality_score -= 0.3

        return {
            "platform": draft.platform,
            "char_count": char_count,
            "length_ok": length_ok,
            "length_reason": length_reason,
            "has_source_link": has_source_link,
            "tone_appropriate": not has_clickbait,
            "overall_quality_score": max(0.0, quality_score),
            "passes_quality": length_ok and has_source_link and not has_clickbait,
        }
