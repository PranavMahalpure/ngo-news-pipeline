"""SQLite Database Storage Module for NGO News Verification Pipeline.

Provides durable, zero-cost, serverless storage for articles, clusters,
cross-validated claims, executive digests, social post drafts, and human audit logs.
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime

from ngo_pipeline.config import DEFAULT_CONFIG
from ngo_pipeline.models import (
    ApprovalStatus,
    Article,
    ArticleCluster,
    CrossValidatedClaim,
    NewsDigest,
    SocialPostDraft,
    VerificationStatus,
)

class Database:
    """Manages SQLite tables and atomic transactions."""

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or DEFAULT_CONFIG.db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def _init_schema(self) -> None:
        """Create tables if they do not exist."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.executescript("""
                CREATE TABLE IF NOT EXISTS articles (
                    id TEXT PRIMARY KEY,
                    url TEXT UNIQUE,
                    domain TEXT,
                    title TEXT,
                    raw_text TEXT,
                    published_at TEXT,
                    source_name TEXT,
                    author TEXT,
                    is_satire INTEGER DEFAULT 0,
                    age_hours REAL,
                    created_at TEXT
                );

                CREATE TABLE IF NOT EXISTS clusters (
                    cluster_id TEXT PRIMARY KEY,
                    topic TEXT,
                    status TEXT,
                    independent_domain_count INTEGER,
                    domains_json TEXT,
                    conflict_summary TEXT,
                    rejection_reason TEXT,
                    created_at TEXT
                );

                CREATE TABLE IF NOT EXISTS claims (
                    claim_id TEXT PRIMARY KEY,
                    cluster_id TEXT,
                    normalized_claim TEXT,
                    category TEXT,
                    status TEXT,
                    source_urls_json TEXT,
                    source_domains_json TEXT,
                    supporting_quotes_json TEXT,
                    conflict_details TEXT,
                    created_at TEXT,
                    FOREIGN KEY(cluster_id) REFERENCES clusters(cluster_id)
                );

                CREATE TABLE IF NOT EXISTS digests (
                    digest_id TEXT PRIMARY KEY,
                    cluster_id TEXT UNIQUE,
                    headline TEXT,
                    executive_summary TEXT,
                    verified_facts_json TEXT,
                    flagged_conflicts_json TEXT,
                    source_citations_json TEXT,
                    status TEXT,
                    generated_at TEXT,
                    FOREIGN KEY(cluster_id) REFERENCES clusters(cluster_id)
                );

                CREATE TABLE IF NOT EXISTS social_drafts (
                    draft_id TEXT PRIMARY KEY,
                    cluster_id TEXT,
                    platform TEXT,
                    content TEXT,
                    character_count INTEGER,
                    source_urls_json TEXT,
                    verification_badge TEXT,
                    status TEXT,
                    reviewer_notes TEXT,
                    created_at TEXT,
                    reviewed_at TEXT,
                    FOREIGN KEY(cluster_id) REFERENCES clusters(cluster_id)
                );

                CREATE TABLE IF NOT EXISTS audit_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    draft_id TEXT,
                    action TEXT,
                    actor TEXT,
                    timestamp TEXT,
                    comment TEXT
                );
            """)
            conn.commit()

    def save_article(self, article: Article) -> None:
        """Insert or replace an article."""
        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO articles 
                (id, url, domain, title, raw_text, published_at, source_name, author, is_satire, age_hours, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    article.id,
                    article.url,
                    article.domain,
                    article.title,
                    article.raw_text,
                    article.published_at,
                    article.source_name,
                    article.author,
                    1 if article.is_satire else 0,
                    article.age_hours,
                    datetime.utcnow().isoformat(),
                ),
            )
            conn.commit()

    def save_cluster(self, cluster: ArticleCluster) -> None:
        """Save a cluster and its cross-validated claims."""
        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO clusters
                (cluster_id, topic, status, independent_domain_count, domains_json, conflict_summary, rejection_reason, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    cluster.cluster_id,
                    cluster.topic,
                    cluster.status.value,
                    cluster.independent_domain_count,
                    json.dumps(cluster.independent_domains),
                    cluster.conflict_summary,
                    cluster.rejection_reason,
                    datetime.utcnow().isoformat(),
                ),
            )

            # Save claims
            for claim in cluster.claims:
                conn.execute(
                    """
                    INSERT OR REPLACE INTO claims
                    (claim_id, cluster_id, normalized_claim, category, status, source_urls_json, source_domains_json, supporting_quotes_json, conflict_details, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        claim.claim_id,
                        cluster.cluster_id,
                        claim.normalized_claim,
                        claim.category,
                        claim.status.value,
                        json.dumps(claim.source_urls),
                        json.dumps(claim.source_domains),
                        json.dumps(claim.supporting_quotes),
                        claim.conflict_details,
                        datetime.utcnow().isoformat(),
                    ),
                )
            conn.commit()

    def save_digest(self, digest: NewsDigest) -> None:
        """Save an executive news digest."""
        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO digests
                (digest_id, cluster_id, headline, executive_summary, verified_facts_json, flagged_conflicts_json, source_citations_json, status, generated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    digest.digest_id,
                    digest.cluster_id,
                    digest.headline,
                    digest.executive_summary,
                    json.dumps(digest.verified_facts),
                    json.dumps(digest.flagged_conflicts),
                    json.dumps(digest.source_citations),
                    digest.status.value,
                    digest.generated_at,
                ),
            )
            conn.commit()

    def save_social_draft(self, draft: SocialPostDraft) -> None:
        """Save or update a social post draft."""
        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO social_drafts
                (draft_id, cluster_id, platform, content, character_count, source_urls_json, verification_badge, status, reviewer_notes, created_at, reviewed_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    draft.draft_id,
                    draft.cluster_id,
                    draft.platform,
                    draft.content,
                    len(draft.content),
                    json.dumps(draft.source_urls),
                    draft.verification_badge,
                    draft.status.value,
                    draft.reviewer_notes,
                    draft.created_at,
                    draft.reviewed_at,
                ),
            )
            conn.commit()

    def update_draft_status(
        self, draft_id: str, status: ApprovalStatus, reviewer_notes: Optional[str] = None, actor: str = "human_editor"
    ) -> bool:
        """Update draft approval status and write to audit log."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            now = datetime.utcnow().isoformat()
            cursor.execute(
                """
                UPDATE social_drafts
                SET status = ?, reviewer_notes = ?, reviewed_at = ?
                WHERE draft_id = ?
                """,
                (status.value, reviewer_notes, now, draft_id),
            )
            if cursor.rowcount == 0:
                return False

            cursor.execute(
                """
                INSERT INTO audit_logs (draft_id, action, actor, timestamp, comment)
                VALUES (?, ?, ?, ?, ?)
                """,
                (draft_id, status.value, actor, now, reviewer_notes or ""),
            )
            conn.commit()
            return True

    def get_pending_drafts(self) -> List[Dict[str, Any]]:
        """Fetch all drafts pending human editorial approval."""
        with self._get_connection() as conn:
            rows = conn.execute(
                """
                SELECT d.*, c.topic, c.status as cluster_status
                FROM social_drafts d
                LEFT JOIN clusters c ON d.cluster_id = c.cluster_id
                WHERE d.status = ?
                ORDER BY d.created_at DESC
                """,
                (ApprovalStatus.PENDING_REVIEW.value,),
            ).fetchall()
            return [dict(r) for r in rows]

    def get_approved_drafts(self) -> List[Dict[str, Any]]:
        """Fetch all approved drafts ready for publishing."""
        with self._get_connection() as conn:
            rows = conn.execute(
                """
                SELECT * FROM social_drafts
                WHERE status = ?
                ORDER BY reviewed_at DESC
                """,
                (ApprovalStatus.APPROVED.value,),
            ).fetchall()
            return [dict(r) for r in rows]
