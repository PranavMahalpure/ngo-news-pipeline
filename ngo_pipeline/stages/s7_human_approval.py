"""Stage 7: Human Editorial Approval Queue.

Enforces zero-auto-posting safety. All social drafts enter a durable approval queue
where human editors inspect verified claims, source URLs, character counts, and approve or reject.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional
from ngo_pipeline.db import Database
from ngo_pipeline.models import ApprovalStatus, SocialPostDraft

logger = logging.getLogger(__name__)

class HumanApprovalManager:
    """Manages the editorial review and approval lifecycle for NGO social drafts."""

    def __init__(self, db: Optional[Database] = None):
        self.db = db or Database()

    def enqueue_drafts(self, drafts: List[SocialPostDraft]) -> None:
        """Add new drafts into the pending review database queue."""
        for draft in drafts:
            self.db.save_social_draft(draft)
        logger.info(f"Enqueued {len(drafts)} drafts for human review.")

    def list_pending(self) -> List[Dict[str, Any]]:
        """Retrieve all drafts currently awaiting human approval."""
        return self.db.get_pending_drafts()

    def list_approved(self) -> List[Dict[str, Any]]:
        """Retrieve all approved drafts ready for dissemination."""
        return self.db.get_approved_drafts()

    def approve_draft(self, draft_id: str, reviewer: str = "editor", notes: str = "") -> bool:
        """Approve a draft for publication."""
        success = self.db.update_draft_status(
            draft_id=draft_id,
            status=ApprovalStatus.APPROVED,
            reviewer_notes=notes or "Approved by human editor.",
            actor=reviewer,
        )
        if success:
            logger.info(f"Draft {draft_id} APPROVED by {reviewer}.")
        return success

    def reject_draft(self, draft_id: str, reviewer: str = "editor", reason: str = "") -> bool:
        """Reject a draft with an editorial reason."""
        success = self.db.update_draft_status(
            draft_id=draft_id,
            status=ApprovalStatus.REJECTED,
            reviewer_notes=reason or "Rejected by human editor.",
            actor=reviewer,
        )
        if success:
            logger.info(f"Draft {draft_id} REJECTED by {reviewer}. Reason: {reason}")
        return success

    def edit_draft(
        self, draft_id: str, new_content: str, reviewer: str = "editor", notes: str = ""
    ) -> bool:
        """Update draft content with editor adjustments."""
        with self.db._get_connection() as conn:
            conn.execute(
                """
                UPDATE social_drafts 
                SET content = ?, character_count = ?, status = ?
                WHERE draft_id = ?
                """,
                (new_content, len(new_content), ApprovalStatus.EDITED.value, draft_id),
            )
            conn.commit()
        return self.approve_draft(draft_id, reviewer=reviewer, notes=f"Edited and approved: {notes}")
