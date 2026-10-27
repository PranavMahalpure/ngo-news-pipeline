"""Pipeline Configuration Module.

Defines all constants, thresholds, feed endpoints, and LLM runtime settings.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import List
from pydantic import BaseModel, Field

# Base directories
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

class PipelineConfig(BaseModel):
    """Configuration settings for the NGO verification & digest pipeline."""

    # Storage
    db_path: Path = Field(default=DATA_DIR / "ngo_pipeline.db")
    frozen_dataset_path: Path = Field(default=DATA_DIR / "benchmark" / "frozen_benchmark_25.json")

    # LLM settings
    llm_provider: str = Field(
        default_factory=lambda: os.getenv("LLM_PROVIDER", "auto")
    )  # 'auto', 'ollama', or 'mock'
    ollama_host: str = Field(
        default_factory=lambda: os.getenv("OLLAMA_HOST", "http://localhost:11434")
    )
    ollama_model: str = Field(
        default_factory=lambda: os.getenv("OLLAMA_MODEL", "qwen2.5:7b")
    )
    llm_temperature: float = 0.0  # Deterministic language steps
    llm_timeout_seconds: int = 45

    # Verification rules
    min_independent_domains: int = 2  # Strict 2+ independent domains rule
    recency_window_hours: int = 72    # Articles older than this are flagged as outdated
    satire_domains: List[str] = Field(
        default_factory=lambda: [
            "theonion.com",
            "babylonbee.com",
            "fakingnews.com",
            "thebeaverton.com",
            "clickhole.com",
            "duffelblog.com",
            "waterfordwhispersnews.com",
        ]
    )

    # Social Posts limits
    max_x_length: int = 280
    social_platforms: List[str] = Field(default_factory=lambda: ["x", "linkedin", "instagram"])

    # Clustering
    cluster_similarity_threshold: float = 0.28  # Cosine similarity cutoff for event grouping

    # Default RSS Sources for NGO Monitoring
    rss_feeds: List[str] = Field(
        default_factory=lambda: [
            # High-credibility Indian & Global feeds for humanitarian/public interest
            "https://news.google.com/rss/search?q=humanitarian+OR+disaster+relief+OR+education+welfare&hl=en-IN&gl=IN&ceid=IN:en",
            "https://www.thehindu.com/news/national/feeder/default.rss",
            "https://pib.gov.in/RssMain.aspx?ModId=6&Lang=1",
            "http://feeds.bbci.co.uk/news/world/rss.xml",
        ]
    )

# Global default config instance
DEFAULT_CONFIG = PipelineConfig()
