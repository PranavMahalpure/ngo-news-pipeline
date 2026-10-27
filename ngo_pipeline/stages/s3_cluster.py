"""Stage 3: Event-Based Semantic Clustering.

Groups candidate articles about the same real-world event into clusters using
local embeddings (bge-small) or fast TF-IDF cosine distance.
"""

from __future__ import annotations

import logging
from typing import List, Optional
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from ngo_pipeline.config import DEFAULT_CONFIG, PipelineConfig
from ngo_pipeline.models import Article, ArticleCluster

logger = logging.getLogger(__name__)

class SemanticClusterer:
    """Clusters articles by semantic event similarity."""

    def __init__(self, config: Optional[PipelineConfig] = None):
        self.config = config or DEFAULT_CONFIG
        self.similarity_threshold = self.config.cluster_similarity_threshold
        self._st_model = None

    def _get_sentence_transformer(self):
        """Lazy load local sentence-transformers model if installed."""
        if self._st_model is None:
            try:
                from sentence_transformers import SentenceTransformer
                self._st_model = SentenceTransformer("BAAI/bge-small-en-v1.5")
                logger.info("Loaded local BAAI/bge-small-en-v1.5 embedding model.")
            except Exception:
                self._st_model = False
        return self._st_model if self._st_model is not False else None

    def cluster_articles(self, articles: List[Article]) -> List[ArticleCluster]:
        """Cluster a collection of articles into event groups."""
        if not articles:
            return []
        if len(articles) == 1:
            return [self._build_cluster([articles[0]])]

        # Combine title and lead paragraphs for clustering representation
        texts = [f"{a.title}. {a.raw_text[:400]}" for a in articles]

        st_model = self._get_sentence_transformer()
        if st_model is not None:
            embeddings = st_model.encode(texts, normalize_embeddings=True)
            sim_matrix = np.dot(embeddings, embeddings.T)
        else:
            # High-performance TF-IDF + Cosine similarity fallback
            vectorizer = TfidfVectorizer(
                stop_words="english",
                ngram_range=(1, 2),
                max_features=5000,
            )
            tfidf_mat = vectorizer.fit_transform(texts)
            sim_matrix = cosine_similarity(tfidf_mat)

        # Graph-based connected components / threshold clustering
        n = len(articles)
        visited = [False] * n
        clusters: List[ArticleCluster] = []

        for i in range(n):
            if visited[i]:
                continue
            component = [articles[i]]
            visited[i] = True

            for j in range(i + 1, n):
                if not visited[j] and sim_matrix[i, j] >= self.similarity_threshold:
                    component.append(articles[j])
                    visited[j] = True

            clusters.append(self._build_cluster(component))

        logger.info(f"Formed {len(clusters)} clusters from {len(articles)} articles.")
        return clusters

    def _build_cluster(self, cluster_articles: List[Article]) -> ArticleCluster:
        """Construct an ArticleCluster from grouped articles."""
        # Find best title as cluster topic
        topic = cluster_articles[0].title if cluster_articles else "Humanitarian Event"
        # Independent domains
        domains = list(set([a.domain for a in cluster_articles if a.domain]))

        return ArticleCluster(
            topic=topic,
            articles=cluster_articles,
            independent_domain_count=len(domains),
            independent_domains=domains,
        )
