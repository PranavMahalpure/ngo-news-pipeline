"""End-to-End Frozen Benchmark Test Suite."""

import pytest
from ngo_pipeline.eval.runner import BenchmarkRunner

def test_full_frozen_benchmark(tmp_path):
    runner = BenchmarkRunner(output_dir=tmp_path / "bench_out")
    results = runner.run_benchmark()

    # Core Metric Assertions
    assert results["total_clusters_evaluated"] == 25
    assert results["source_attribution"]["attribution_accuracy_pct"] >= 95.0
    assert results["hallucination"]["hallucination_rate_pct"] <= 2.0
    assert results["planted_traps"]["overall_trap_recall_pct"] == 100.0
    assert results["planted_traps"]["overall_trap_precision_pct"] >= 95.0
    assert results["social_post_quality"]["x_length_compliance_pct"] == 100.0
    assert results["social_post_quality"]["safety_gating_status"] == "PASSED"
    assert results["estimated_api_cost_usd"] == 0.00
