"""Stage 1: News Collection.

Harvests candidate articles from credible RSS feeds (Google News, The Hindu, PIB, BBC)
and web search fallback for broad humanitarian coverage.
"""

from __future__ import annotations

import logging
from typing import List, Optional
from urllib.parse import urlparse
import feedparser

from ngo_pipeline.config import DEFAULT_CONFIG, PipelineConfig
from ngo_pipeline.models import Article

logger = logging.getLogger(__name__)

class NewsCollector:
    """Collects raw article entries from RSS feeds and search APIs."""

    def __init__(self, config: Optional[PipelineConfig] = None):
        self.config = config or DEFAULT_CONFIG

    def collect_from_rss(self, feeds: Optional[List[str]] = None, max_per_feed: int = 5) -> List[Article]:
        """Fetch news entries from configured RSS feeds."""
        target_feeds = feeds or self.config.rss_feeds
        collected_articles: List[Article] = []
        seen_urls = set()

        for feed_url in target_feeds:
            try:
                parsed = feedparser.parse(feed_url)
                feed_title = parsed.feed.get("title", "RSS Feed")

                for entry in parsed.entries[:max_per_feed]:
                    link = entry.get("link", "").strip()
                    title = entry.get("title", "").strip()
                    published = entry.get("published", "") or entry.get("updated", "")
                    summary = entry.get("summary", "")

                    if not link or link in seen_urls:
                        continue
                    seen_urls.add(link)

                    domain = urlparse(link).netloc.replace("www.", "")

                    article = Article(
                        url=link,
                        domain=domain,
                        title=title,
                        raw_text=summary,  # Will be enriched by trafilatura in Stage 2
                        published_at=published,
                        source_name=feed_title,
                    )
                    collected_articles.append(article)

            except Exception as e:
                logger.error(f"Failed to fetch RSS feed {feed_url}: {e}")

        logger.info(f"Collected {len(collected_articles)} articles from RSS feeds.")
        return collected_articles

    def search_news(self, query: str, max_results: int = 5) -> List[Article]:
        """Query Google News RSS for humanitarian keywords."""
        encoded_query = query.replace(" ", "+")
        rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-IN&gl=IN&ceid=IN:en"
        return self.collect_from_rss(feeds=[rss_url], max_per_feed=max_results)
