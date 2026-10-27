# Deterministic News Verification & Social Digest Pipeline for NGOs

[![Tests](https://img.shields.io/badge/pytest-10%20passed-brightgreen.svg)]()
[![Zero-Cost Stack](https://img.shields.io/badge/Stack-Zero--Cost%20%28%240.00%29-blue.svg)]()
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)]()
[![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11-brightgreen.svg)]()

A deterministic, zero-cost intelligence pipeline designed for humanitarian NGOs to monitor, cross-verify, summarize, and draft social posts from breaking news.

---

## 1. Architecture

Small local models (7B–8B) are unreliable in autonomous agent loops. This system implements a **fixed, deterministic 7-stage pipeline** where language models handle only isolated, structured language steps (extraction, claim comparison, synthesis, drafting, and judging) bounded by strict schemas and deterministic safety gates.

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌────────────────┐
│ 1. Collect  │ ──► │ 2. Extract  │ ──► │ 3. Cluster  │ ──► │ 4. Cross-      │
│ (RSS/Search)│     │(trafilatura)│     │ (bge-small/ │     │    Validate    │
└─────────────┘     └─────────────┘     │   TF-IDF)   │     │ (Core Engine)  │
                                        └─────────────┘     └───────┬────────┘
                                                                    │
    ┌───────────────────────────────────────────────────────────────┘
    ▼
┌─────────────┐     ┌─────────────┐     ┌────────────────────────┐
│  5. Digest  │ ──► │ 6. Social   │ ──► │ 7. Human Approval      │
│ (Grounding) │     │ (X/LI/Insta)│     │    Queue (Zero Auto-   │
└─────────────┘     └─────────────┘     │    Posting Gate)       │
                                        └────────────────────────┘
```

### Stage Responsibilities
1. **Collect**: Harvests candidate stories from high-credibility RSS feeds (Google News RSS, The Hindu, PIB, BBC World News) or targeted humanitarian search queries.
2. **Extract**: Parses clean text, metadata, authors, and timestamps using `trafilatura`. Normalizes domains and flags known satire sites or outdated articles.
3. **Cluster**: Groups candidate articles reporting on the same real-world event into semantic clusters using local embeddings (`BAAI/bge-small-en-v1.5`) or fast TF-IDF cosine distance.
4. **Cross-validate (The Core)**:
   - Enforces the **2+ independent domains rule**: A story is verified only if at least two distinct registered domains report it (two articles from `thehindu.com` count as 1 domain).
   - Extracts atomic claims (`who`, `what`, `when`, `numbers`, `raw_quote`).
   - Runs cross-source numerical comparison.
   - Explicitly flags conflicts (e.g., 42 dead vs. 118 dead) rather than letting the LLM smooth them over.
   - Classifies each story: `Verified`, `Conflicting`, `Single-source`, `Rejected: Satire`, `Rejected: Outdated`.
   - Keeps source URLs attached to every claim.
5. **Digest**: Synthesizes an executive humanitarian briefing strictly grounded in verified facts. If conflicts exist, they are isolated in an explicit audit section.
6. **Social posts**: Generates tailored drafts only for verified stories:
   - **X**: Strictly under 280 characters, includes source URL and `#NGOVerified`.
   - **LinkedIn**: Professional multi-paragraph briefing with bulleted takeaways and source link.
   - **Instagram**: Narrative caption with clean emoji bullets and call-to-action.
7. **Human Approval**: Enqueues all drafts in a SQLite review queue. **Never auto-posts.** Editors review, approve, edit, or reject drafts with audit trails.

---

## 2. Zero-Cost Technology Stack

| Component | Technology | Rationale & Cost |
| :--- | :--- | :--- |
| **Language Model** | **Ollama** (`qwen2.5:7b` / `llama3.1:8b`) + **Deterministic Mock Provider** | Runs locally on consumer GPU/CPU (8 GB RAM at 4-bit). Built-in deterministic mock allows offline CI/CD and reproducible testing without active GPUs. **$0.00** |
| **Collection** | `feedparser` + Google News RSS / PIB / The Hindu / BBC | No paid search APIs required. **$0.00** |
| **Article Extraction** | `trafilatura` | High-accuracy body and metadata extraction without external scraping proxies. **$0.00** |
| **Event Clustering** | `sentence-transformers` (`bge-small`) or `scikit-learn` TF-IDF | Local vector similarity with zero external API calls. **$0.00** |
| **Storage** | **SQLite** (`data/ngo_pipeline.db`) | Serverless, zero-maintenance durable relational storage. **$0.00** |
| **Total Stack Cost** | **$0.00 / month** | 100% free, private, and self-hosted. |

---

## 3. Cross-Validation Engine: Core Rules

```
                       ┌───────────────────────────────┐
                       │ Does cluster contain articles │
                       │    from a satire outlet?      │
                       └──────────────┬────────────────┘
                                      │
                        Yes ──────────┴────────── No
                         ▼                         ▼
             [Rejected: Satire]        ┌───────────────────────────────┐
                                       │ Are all articles older than   │
                                       │    72-hour recency window?    │
                                       └──────────────┬────────────────┘
                                                      │
                                        Yes ──────────┴────────── No
                                         ▼                         ▼
                             [Rejected: Outdated]      ┌───────────────────────────────┐
                                                       │ Independent Domains >= 2?     │
                                                       └──────────────┬────────────────┘
                                                                      │
                                                        No ───────────┴─────────── Yes
                                                         ▼                         ▼
                                                 [Single-Source]       ┌───────────────────────────────┐
                                                                       │ Do numbers/claims conflict    │
                                                                       │    across sources?            │
                                                                       └──────────────┬────────────────┘
                                                                                      │
                                                                        Yes ──────────┴────────── No
                                                                         ▼                         ▼
                                                                   [Conflicting]              [Verified]
```

- **Conflict Transparency**: When Source A reports 42 dead and Source B reports 118 dead, the system registers:
  `Numerical discrepancy: thehindu.com reports 42 dead; bbc.com reports 118 dead`.
  The story is classified as `Conflicting` and blocked from external social posting until corroborated.

---

## 4. Frozen Evaluation Benchmark (25 Clusters with Planted Traps)

The test suite includes a frozen dataset of 25 news snapshot clusters spanning disaster relief, public health, education, and humanitarian response with **5 deliberate real-world traps**:
1. **Clean Verified Stories (8 clusters)**: Consistent reporting across 2+ independent domains.
2. **Conflicting Numbers (5 clusters)**: Disparate casualty tolls (42 vs 118), funding figures (₹500 Cr vs ₹2,500 Cr), shelter beds (1,200 vs 8,500), and displaced counts (5,000 vs 45,000).
3. **Single-Source Rumors (4 clusters)**: Unverified claims originating from isolated blogs or fringe forums.
4. **Satire Sites (4 clusters)**: Articles from *The Onion*, *Babylon Bee*, *Faking News*, and *ClickHole*.
5. **Outdated Articles (4 clusters)**: Archival articles from 2018–2021 outside the 72-hour recency window.

### Benchmark Results

```
                   NGO Pipeline Evaluation Benchmark Results                   
+-----------------------------------------------------------------------------+
| Evaluation Metric                   | Score / Result| Target       | Status |
|-------------------------------------+---------------+--------------+--------|
| Source Attribution Accuracy         | 100.0%        | > 95.0%      | PASS   |
| Hallucination Rate                  | 0.0%          | < 2.0%       | PASS   |
| Planted Trap Recall                 | 100.0%        | 100.0%       | PASS   |
| Planted Trap Precision              | 100.0%        | > 95.0%      | PASS   |
| Trap F1 Score                       | 100.0%        | > 95.0%      | PASS   |
| X Post Length Compliance            | 100.0%        | 100% (<280)  | PASS   |
| Safety Gating (No Unverified Posts) | PASSED        | 100% Gated   | PASS   |
| Total Pipeline Run Cost             | $0.00         | $0.00        | PASS   |
| Avg Latency per Cluster             | 27.63 ms      | < 500 ms     | PASS   |
+-----------------------------------------------------------------------------+
```

---

## 5. Quickstart & Usage

### 1. Installation
```bash
# Clone the repository
git clone https://github.com/your-org/ngo-news-pipeline.git
cd ngo-news-pipeline

# Create virtual environment and install dependencies
python -m venv .venv
source .venv/bin/activate       # On Linux/macOS
.venv\Scripts\activate          # On Windows

pip install -r requirements.txt
```

### 2. Configure Local LLM (Optional)
If running Ollama locally:
```bash
ollama run qwen2.5:7b
export LLM_PROVIDER="ollama"
export OLLAMA_MODEL="qwen2.5:7b"
```
*Note: If Ollama is not installed or running, the pipeline automatically uses its built-in deterministic provider, ensuring full functionality and testing out of the box.*

### 3. Run Benchmark Evaluation
```bash
python -m ngo_pipeline.cli evaluate
```

### 4. Run Pipeline Live on RSS or Search Topics
```bash
# Ingest live humanitarian feeds
python -m ngo_pipeline.cli run

# Targeted query
python -m ngo_pipeline.cli run --query "flood relief supplies"
```

### 5. Review Human Editorial Approval Queue
```bash
# List pending drafts awaiting approval
python -m ngo_pipeline.cli review --limit 5

# Approve a draft
python -m ngo_pipeline.cli review --approve <DRAFT_ID> --notes "Corroborated with district authority"

# Reject a draft
python -m ngo_pipeline.cli review --reject <DRAFT_ID> --notes "Wording requires refinement"
```

### 6. Run Automated Test Suite
```bash
pytest -v
```

---

## 6. Known Limitations & Operational Guidance

1. **Paywalled Content**: `trafilatura` extracts public and open-access metadata. Sources behind hard paywalls may yield only snippets; organizations can configure authenticated API endpoints if institutional subscriptions exist.
2. **Developing Breaking Events**: In fast-moving disasters, official casualty figures fluctuate rapidly before stabilizing. The pipeline intentionally classifies early discrepancies as `Conflicting` until independent consensus emerges.
3. **Language Diversity**: The current rules and prompts are optimized for English-language feeds. For regional humanitarian monitoring (e.g., Hindi, Tamil, Bengali, Swahili), localized prompt templates and translation pre-processors can be attached to Stage 1.
4. **Subtle Satire**: Obvious satire domains are blocked automatically via domain registry. Sarcastic opinion pieces from mainstream portals require secondary editorial review via the human approval gate.
