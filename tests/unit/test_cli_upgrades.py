"""Tests for new CLI workflow upgrades: metric_parser and submission generator."""
import pytest

from worldquant_pipeline.cli.metric_parser import (
    evaluate_consultant_track_decision,
    parse_brain_paste,
)
from worldquant_pipeline.cli.submission import generate_submission_metadata
from worldquant_pipeline.storage.models import AlphaCandidate


def test_parse_brain_paste_standard_pass():
    raw_text = """
    Candidate 1:
    8 PASS
    Sharpe of 1.60 is above cutoff of 1.25.
    Fitness of 1.50 is above cutoff of 1.
    Turnover of 14.76% is above cutoff of 1%.
    Turnover of 14.76% is below cutoff of 70%.
    Weight is well distributed over instruments.
    Sub-universe Sharpe of 1.23 is above cutoff of 0.85.
    Self-correlation is 0.6246, which is above cutoff of 0.7, or Sharpe is better by 10.0% or more.
    Competition Challenge matches.
    """
    metrics = parse_brain_paste(raw_text)
    assert metrics.pass_count == 8
    assert metrics.sharpe == 1.60
    assert metrics.fitness == 1.50
    assert pytest.approx(metrics.turnover, 0.0001) == 0.1476
    assert metrics.sub_universe_sharpe == 1.23
    assert metrics.self_correlation == 0.6246
    assert metrics.weight_well_distributed is True

    decision, reason = evaluate_consultant_track_decision(metrics)
    assert decision == "APPROVED"
    assert "GOLD LEVEL CONSULTANT QUALIFIED" in reason


def test_parse_brain_paste_rejection_low_fitness():
    raw_text = """
    6 PASS
    Fitness of 1.19 is above cutoff of 1.
    Turnover of 12.26% is above cutoff of 1%.
    Turnover of 12.26% is below cutoff of 70%.
    Weight is well distributed over instruments.
    Sub-universe Sharpe of 0.99 is above cutoff of 0.66.
    Competition Challenge matches.
    1 FAIL
    Sharpe of 1.24 is below cutoff of 1.25.
    """
    metrics = parse_brain_paste(raw_text)
    assert metrics.pass_count == 6
    assert metrics.fail_count == 1
    assert metrics.sharpe == 1.24
    assert metrics.fitness == 1.19
    assert pytest.approx(metrics.turnover, 0.0001) == 0.1226

    decision, reason = evaluate_consultant_track_decision(metrics)
    assert decision == "REJECTED"
    assert "Sharpe 1.24 < 1.25 cutoff" in reason


def test_parse_brain_paste_self_correlation_fail():
    raw_text = """
    7 PASS
    Sharpe of 1.77 is above cutoff of 1.25.
    Fitness of 1.36 is above cutoff of 1.
    Turnover of 26.85% is above cutoff of 1%.
    Turnover of 26.85% is below cutoff of 70%.
    Weight is well distributed over instruments.
    Sub-universe Sharpe of 1.27 is above cutoff of 0.94.
    Competition Challenge matches.
    1 FAIL
    Self-correlation 0.8953 is above cutoff of 0.7 and Sharpe not better by 10.0% or more.
    """
    metrics = parse_brain_paste(raw_text)
    assert metrics.sharpe == 1.77
    assert metrics.fitness == 1.36
    assert metrics.self_correlation == 0.8953

    decision, reason = evaluate_consultant_track_decision(metrics)
    assert decision == "REJECTED"
    assert "Self-correlation 0.8953 >= 0.70" in reason


def test_submission_metadata_generation():
    cand = AlphaCandidate(
        id="990116d5-test-uuid",
        expression_raw="0.60 * signed_power(group_rank(ts_rank(ts_backfill(anl4_afv4_median_eps, 60) / close, 180), market) - 0.5, 2) + 0.30 * group_rank(ts_mean(ts_backfill(anl4_capex_value, 252), 252) / (ts_backfill(assets, 60) + 1000), market) - 0.10 * group_rank(ts_delta(close, 5) / close, market)",
        status="APPROVED",
    )
    meta = generate_submission_metadata(cand, neutralization="Market")
    assert "Consensus_Median_EPS_Yield" in meta.name
    assert "Market_Neutral" in meta.name
    assert meta.category in ["price momentum", "price reversion", "none"]
    assert len(meta.tags) == 3
    assert len(meta.description) > 30


def test_submission_metadata_defaults():
    cand = AlphaCandidate(
        id="a1b2c3d4-test",
        expression_raw="group_rank(close, subindustry)",
        status="APPROVED",
    )
    meta = generate_submission_metadata(cand)
    assert meta.universe == "TOP3000"
    assert meta.neutralization == "SUBINDUSTRY"
    assert meta.decay == 4
    assert meta.delay == 1
    assert meta.truncation == 0.0100
