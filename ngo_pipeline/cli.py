"""Command-Line Interface (CLI) for NGO Verification Pipeline.

Provides commands to:
1. Run pipeline live on RSS feeds or search topics
2. Evaluate frozen benchmark suite (25 clusters with planted traps)
3. Review and manage the Human Editorial Approval Queue (Approve / Reject drafts)
4. Export approved social posts
"""

from __future__ import annotations

import argparse
import sys
from typing import Optional

# Ensure UTF-8 output on Windows consoles
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from ngo_pipeline.eval.runner import BenchmarkRunner
from ngo_pipeline.pipeline import VerificationPipeline
from ngo_pipeline.stages.s7_human_approval import HumanApprovalManager

console = Console(force_terminal=True)

def cmd_run(args):
    """Run pipeline live on RSS feeds or a search topic."""
    pipeline = VerificationPipeline()
    console.print(f"\n[bold green]Running NGO News Verification Pipeline...[/bold green]")
    if args.query:
        console.print(f"Target Search Query: [cyan]{args.query}[/cyan]")
    else:
        console.print("Target Sources: Configured High-Credibility RSS Feeds")

    results = pipeline.run(search_query=args.query, fetch_online=not args.offline)

    console.print(f"\n[bold]Ingestion Summary:[/bold]")
    console.print(f"• Articles Ingested: {results['articles_count']}")
    console.print(f"• Event Clusters Formed: {results['clusters_count']}")
    console.print(f"• Executive Digests Synthesized: {results['digests_count']}")
    console.print(f"• Social Drafts Enqueued: {results['drafts_created']}")
    console.print(f"• Total Pipeline Latency: {results['total_latency_ms']} ms")

    table = Table(title="Processed Event Clusters", show_lines=True)
    table.add_column("Cluster Topic", style="cyan", max_width=45)
    table.add_column("Status", style="bold")
    table.add_column("Domains", style="green")
    table.add_column("Notes / Conflict", style="yellow", max_width=40)

    for c in results["clusters"]:
        table.add_row(
            c.topic,
            c.status.value,
            ", ".join(c.independent_domains) or "N/A",
            c.conflict_summary or c.rejection_reason or "Verified consensus",
        )
    console.print(table)

def cmd_evaluate(args):
    """Execute the frozen benchmark suite."""
    runner = BenchmarkRunner()
    runner.run_benchmark()

def cmd_review(args):
    """Review drafts awaiting human editorial approval."""
    mgr = HumanApprovalManager()

    if args.approve:
        success = mgr.approve_draft(args.approve, notes=args.notes or "Approved via CLI")
        if success:
            console.print(f"[bold green]Draft '{args.approve}' has been APPROVED.[/bold green]")
        else:
            console.print(f"[bold red]Draft '{args.approve}' not found.[/bold red]")
        return

    if args.reject:
        success = mgr.reject_draft(args.reject, reason=args.notes or "Rejected via CLI")
        if success:
            console.print(f"[bold yellow]Draft '{args.reject}' has been REJECTED.[/bold yellow]")
        else:
            console.print(f"[bold red]Draft '{args.reject}' not found.[/bold red]")
        return

    # List pending drafts
    pending = mgr.list_pending()
    if not pending:
        console.print("\n[green]No social drafts are currently awaiting human review. Queue is clear![/green]\n")
        return

    limit = getattr(args, "limit", 5) or 5
    console.print(f"\n[bold yellow]Pending Human Approval Queue ({len(pending)} Drafts - Showing first {min(limit, len(pending))}):[/bold yellow]\n")
    for d in pending[:limit]:
        char_badge = f"{d['character_count']} chars"
        if d['platform'] == 'x':
            char_badge += " (Max: 280)"

        panel_content = (
            f"[bold]Platform:[/bold] {d['platform'].upper()} | [bold]Length:[/bold] {char_badge}\n"
            f"[bold]Associated Topic:[/bold] {d.get('topic', 'N/A')}\n"
            f"[bold]Cluster Status:[/bold] [green]{d.get('cluster_status', 'VERIFIED')}[/green]\n\n"
            f"[bold cyan]Draft Content:[/bold cyan]\n{d['content']}\n\n"
            f"[dim]To approve: python -m ngo_pipeline.cli review --approve {d['draft_id']}[/dim]\n"
            f"[dim]To reject:  python -m ngo_pipeline.cli review --reject {d['draft_id']} --notes 'reason'[/dim]"
        )
        console.print(Panel(panel_content, title=f"Draft ID: {d['draft_id']}", border_style="cyan"))

def main():
    parser = argparse.ArgumentParser(description="NGO Intelligence Verification & Social Digest CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available pipeline commands")

    # Command: run
    p_run = subparsers.add_parser("run", help="Run the pipeline on live RSS feeds or query")
    p_run.add_argument("--query", "-q", type=str, help="Search query for targeted humanitarian news")
    p_run.add_argument("--offline", action="store_true", help="Do not fetch external web pages via HTTP")

    # Command: evaluate
    subparsers.add_parser("evaluate", help="Execute frozen 25-cluster benchmark suite with planted traps")

    # Command: review
    p_rev = subparsers.add_parser("review", help="Human editorial queue review and approval")
    p_rev.add_argument("--approve", type=str, help="Approve draft ID")
    p_rev.add_argument("--reject", type=str, help="Reject draft ID")
    p_rev.add_argument("--notes", type=str, help="Reviewer notes or rejection reason")
    p_rev.add_argument("--limit", type=int, default=5, help="Number of drafts to display")

    args = parser.parse_args()

    if args.command == "run":
        cmd_run(args)
    elif args.command == "evaluate":
        cmd_evaluate(args)
    elif args.command == "review":
        cmd_review(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
