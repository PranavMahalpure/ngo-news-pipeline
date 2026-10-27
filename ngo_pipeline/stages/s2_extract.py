"""Stage 2: Article Text and Metadata Extraction.

Uses trafilatura to extract clean body text, metadata, authors, and publication dates.
Normalizes domains and flags satire outlets or outdated publication dates.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import List, Optional
from urllib.parse import urlparse
import dateparser
import trafilatura

from ngo_pipeline.config import DEFAULT_CONFIG, PipelineConfig
from ngo_pipeline.models import Article

logger = logging.getLogger(__name__)

class ArticleExtractor:
    """Extracts article content via trafilatura and calculates age and credibility flags."""

    def __init__(self, config: Optional[PipelineConfig] = None):
        self.config = config or DEFAULT_CONFIG
        self.satire_domains = set(self.config.satire_domains)

    def extract(self, article: Article, fetch_online: bool = True) -> Article:
        """Enrich an Article with clean text, domain, publication age, and satire flag."""
        # Clean domain
        parsed_url = urlparse(article.url)
        clean_domain = parsed_url.netloc.lower().replace("www.", "")
        if clean_domain:
            article.domain = clean_domain

        # Satire check
        if any(satire_d in article.domain for satire_d in self.satire_domains):
            article.is_satire = True

        # Fetch and extract body text if online fetching is requested and text is sparse
        if fetch_online and (not article.raw_text or len(article.raw_text.split()) < 30):
            try:
                downloaded = trafilatura.fetch_url(article.url)
                if downloaded:
                    extracted_text = trafilatura.extract(
                        downloaded,
                        include_comments=False,
                        include_tables=True,
                        no_fallback=False,
                    )
                    if extracted_text:
                        article.raw_text = extracted_text.strip()
                    metadata = trafilatura.extract_metadata(downloaded)
                    if metadata:
                        if metadata.date and not article.published_at:
                            article.published_at = metadata.date
                        if metadata.author and not article.author:
                            article.author = metadata.author
                        if metadata.title and (not article.title or len(article.title) < 10):
                            article.title = metadata.title
            except Exception as e:
                logger.warning(f"Trafilatura extraction failed for {article.url}: {e}")

        # Compute age in hours
        if article.published_at:
            try:
                parsed_date = dateparser.parse(article.published_at)
                if parsed_date:
                    if parsed_date.tzinfo is None:
                        parsed_date = parsed_date.replace(tzinfo=timezone.utc)
                    now = datetime.now(timezone.utc)
                    diff = (now - parsed_date).total_seconds() / 3600.0
                    article.age_hours = max(0.0, diff)
            except Exception:
                pass

        return article

    def extract_batch(self, articles: List[Article], fetch_online: bool = False) -> List[Article]:
        """Extract and clean a list of articles."""
        return [self.extract(a, fetch_online=fetch_online) for a in articles]
