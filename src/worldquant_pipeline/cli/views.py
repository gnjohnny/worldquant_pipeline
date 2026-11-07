"""Rich terminal UI views and screen rendering for worldquant_pipeline."""
from typing import Any

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from worldquant_pipeline.brain.manual_adapter import SimulationCard
from worldquant_pipeline.evaluation.gates import GateEvaluationResult
from worldquant_pipeline.hypotheses.importer import IngestionReport

console = Console()


def render_dashboard(
    hypotheses_count: int,
    status_counts: dict[str, int],
    recent_candidates: list[Any],
) -> None:
    """Render research status dashboard."""
    console.print()
    console.print("[bold cyan]===============================================================[/bold cyan]")
    console.print("[bold cyan]            worldquant_pipeline Research Dashboard            [/bold cyan]")
    console.print("[bold cyan]===============================================================[/bold cyan]\n")

    # Status summary table
    summary_table = Table(title="Candidate Alpha Pipeline Status", show_header=True, header_style="bold white")
    summary_table.add_column("Status", style="bold")
    summary_table.add_column("Count", justify="right")

    status_styles = {
        "PROPOSED": "dim white",
        "VALIDATED": "bold cyan",
        "SIMULATION_QUEUED": "yellow",
        "SIMULATED": "blue",
        "APPROVED": "bold green",
        "REJECTED": "bold red",
        "NEEDS_REVISION": "magenta",
    }

    total_candidates = sum(status_counts.values())
    summary_table.add_row("Total Hypotheses", str(hypotheses_count))
    summary_table.add_row("Total Candidates", str(total_candidates))
    summary_table.add_section()

    for st, count in status_counts.items():
        style = status_styles.get(st, "white")
        summary_table.add_row(f"[{style}]{st}[/{style}]", str(count))

    console.print(summary_table)
    console.print()

    # Recent candidates table
    if recent_candidates:
        cand_table = Table(title="Recent Candidates", show_header=True, header_style="bold white")
        cand_table.add_column("ID", style="cyan", max_width=12, overflow="ellipsis")
        cand_table.add_column("Status", justify="center")
        cand_table.add_column("Complexity", justify="right")
        cand_table.add_column("Expression", style="green")

        for c in recent_candidates:
            st = c.status
            style = status_styles.get(st, "white")
            cand_table.add_row(
                c.id[:8],
                f"[{style}]{st}[/{style}]",
                str(c.complexity_score),
                c.expression_raw[:60] + ("..." if len(c.expression_raw) > 60 else ""),
            )
        console.print(cand_table)
    else:
        console.print("[dim]No candidates recorded yet. Run `prompt` and `ingest` to start research.[/dim]")
    console.print()


def render_prompt_export(prompt_text: str) -> None:
    """Render copilot brainstorming prompt."""
    console.print("\n[bold green]Copilot Research Prompt Ready![/bold green]")
    console.print("[dim]Copy the prompt below and paste it into your chat with Antigravity:[/dim]\n")
    console.print(Panel(prompt_text, title="Research Prompt", border_style="cyan"))


def render_ingestion_report(report: IngestionReport) -> None:
    """Render candidate batch ingestion and validation results."""
    console.print("\n[bold cyan]Candidate Batch Ingestion Report[/bold cyan]")
    table = Table(show_header=True, header_style="bold white")
    table.add_column("Metric", style="bold")
    table.add_column("Value", justify="right")

    table.add_row("Hypotheses Ingested", str(report.total_hypotheses))
    table.add_row("Candidates Evaluated", str(report.total_candidates))
    table.add_row("[bold green]Valid & Registered (G1 Passed)[/bold green]", str(report.valid_candidates))
    table.add_row("[yellow]Duplicates Skipped (G3)[/yellow]", str(report.duplicates))
    table.add_row("[bold red]Syntax / Whitelist Errors[/bold red]", str(report.syntax_errors))

    console.print(table)
    console.print()

    if report.registered_candidates:
        cand_table = Table(title="Registered Candidates", show_header=True, header_style="bold white")
        cand_table.add_column("ID", style="cyan")
        cand_table.add_column("Complexity", justify="right")
        cand_table.add_column("Turnover Est.", justify="right")
        cand_table.add_column("Corr Risk", justify="center")
        cand_table.add_column("Canonical Expression", style="green")

        for c in report.registered_candidates:
            risk = c.get("correlation_risk", "LOW")
            risk_style = "green" if risk == "LOW" else "yellow" if risk == "MEDIUM" else "bold red"
            turnover_str = f"{c.get('estimated_turnover', 0.12):.1%}" if "estimated_turnover" in c else "N/A"
            cand_table.add_row(
                c["id"][:8],
                str(c["complexity"]),
                turnover_str,
                f"[{risk_style}]{risk}[/{risk_style}]",
                c["canonical"][:60] + ("..." if len(c["canonical"]) > 60 else ""),
            )
        console.print(cand_table)
        console.print()

    if report.errors:
        console.print("[bold red]Rejections / Errors:[/bold red]")
        for err in report.errors:
            console.print(f"  - [yellow]{err['expression']}[/yellow]: [red]{err['reason']}[/red]")
        console.print()


def render_simulation_card(card: SimulationCard) -> None:
    """Render simulation parameters ready for WorldQuant BRAIN web platform."""
    console.print()
    console.print(f"[bold cyan]WorldQuant BRAIN Simulation Card -- Candidate `{card.candidate_id}`[/bold cyan]\n")

    # Formula display panel
    expr_panel = Panel(
        Text(card.expression, style="bold green on black"),
        title="Formula (Copy & Paste to Platform)",
        border_style="green",
    )
    console.print(expr_panel)
    console.print()

    # Settings table
    table = Table(title="Platform Settings", show_header=True, header_style="bold white")
    table.add_column("Parameter", style="bold cyan")
    table.add_column("Recommended Setting", style="bold yellow")

    table.add_row("Region", card.region)
    table.add_row("Universe", card.universe)
    table.add_row("Delay", str(card.delay))
    table.add_row("Decay", str(card.decay))
    table.add_row("Neutralization", card.neutralization)
    table.add_row("Truncation", f"{card.truncation:.4f}")

    console.print(table)
    console.print()

    # Hypothesis context
    console.print(f"[bold]Hypothesis:[/bold] {card.hypothesis_title}")
    console.print(f"[bold]Rationale:[/bold] {card.economic_rationale}")
    console.print(f"[bold]Expected Horizon:[/bold] {card.intended_horizon}\n")


def render_gate_results(result: GateEvaluationResult) -> None:
    """Render evaluation gate results for recorded simulation metrics."""
    if result.passed:
        console.print("[bold green][PASS] Quality Gates Passed (G5 Robustness Check)[/bold green]")
    else:
        console.print("[bold red][FAIL] Quality Gate Failures Detected:[/bold red]")
        for fail in result.failures:
            console.print(f"  - [red]{fail}[/red]")

    if result.warnings:
        console.print("[bold yellow]Warnings:[/bold yellow]")
        for warn in result.warnings:
            console.print(f"  - [yellow]{warn}[/yellow]")
    console.print()


def render_parsed_metrics(
    candidate_id: str,
    metrics: Any,
    decision: str,
    reason: str,
) -> None:
    """Render summary table of metrics parsed from raw BRAIN text."""
    console.print()
    console.print(f"[bold cyan]Simulation Metrics Recorded for Candidate `{candidate_id}`[/bold cyan]\n")

    table = Table(show_header=True, header_style="bold white")
    table.add_column("Metric", style="bold")
    table.add_column("Value", justify="right")
    table.add_column("Benchmark Cutoff", justify="right")
    table.add_column("Status", justify="center")

    def add_row(name: str, val: float | None, cutoff: str, passed: bool | None, fmt: str = "{:.2f}") -> None:
        val_str = fmt.format(val) if val is not None else "N/A"
        st_str = "[green]PASS[/green]" if passed else "[red]FAIL[/red]" if passed is False else "[dim]INFO[/dim]"
        table.add_row(name, val_str, cutoff, st_str)

    add_row("Sharpe Ratio", metrics.sharpe, ">= 1.25", metrics.sharpe >= 1.25 if metrics.sharpe is not None else None)
    add_row("Fitness Score", metrics.fitness, ">= 1.50 (GOOD)", metrics.fitness >= 1.50 if metrics.fitness is not None else None)
    add_row(
        "Turnover",
        metrics.turnover,
        "1.0% - 70.0%",
        (0.01 <= metrics.turnover <= 0.70) if metrics.turnover is not None else None,
        fmt="{:.2%}",
    )
    add_row(
        "Sub-Universe Sharpe",
        metrics.sub_universe_sharpe,
        ">= 0.00",
        metrics.sub_universe_sharpe >= 0.0 if metrics.sub_universe_sharpe is not None else None,
    )
    if metrics.self_correlation is not None:
        add_row(
            "Self-Correlation",
            metrics.self_correlation,
            "< 0.70",
            metrics.self_correlation < 0.70,
        )

    console.print(table)
    console.print()

    dec_color = "green" if decision == "APPROVED" else "yellow" if decision == "NEEDS_REVIEW" else "red"
    console.print(f"[bold]Decision:[/bold] [{dec_color}]{decision}[/{dec_color}]")
    console.print(f"[bold]Reason:[/bold] {reason}\n")


def render_submission_card(meta: Any) -> None:
    """Render standardized Invariant 6 submission card for approved alphas."""
    console.print()
    console.print("[bold green]===============================================================[/bold green]")
    console.print("[bold green]   WORLDQUANT BRAIN STANDARDIZED SUBMISSION METADATA (INV-6)   [/bold green]")
    console.print("[bold green]===============================================================[/bold green]\n")

    info_table = Table(show_header=True, header_style="bold white")
    info_table.add_column("Field", style="bold cyan")
    info_table.add_column("Submission Value", style="bold yellow")

    info_table.add_row("Candidate ID", meta.candidate_id)
    info_table.add_row("Name", meta.name)
    info_table.add_row("Category", meta.category)
    info_table.add_row("3 Tags", ", ".join(meta.tags))
    info_table.add_row("Universe", meta.universe)
    info_table.add_row("Neutralization", meta.neutralization)
    info_table.add_row("Decay", str(meta.decay))
    info_table.add_row("Delay", str(meta.delay))
    info_table.add_row("Truncation", f"{meta.truncation:.4f}")

    console.print(info_table)
    console.print()

    desc_panel = Panel(
        Text(meta.description, style="white"),
        title="Short Precise Description (1-2 sentences)",
        border_style="cyan",
    )
    console.print(desc_panel)
    console.print()

    expr_panel = Panel(
        Text(meta.expression, style="bold green on black"),
        title="Formula Expression",
        border_style="green",
    )
    console.print(expr_panel)
    console.print()


def render_discovered_fields(fields: list[dict[str, Any]], title: str) -> None:
    """Render table of discovered data fields."""
    console.print(f"\n[bold cyan]{title}[/bold cyan]\n")
    table = Table(show_header=True, header_style="bold white")
    table.add_column("Field Key", style="bold cyan")
    table.add_column("Category", style="yellow")
    table.add_column("Timing Delay", justify="center")
    table.add_column("Approved Overlap", justify="center")
    table.add_column("Description")

    for f in fields:
        overlap_str = "[red]USED[/red]" if f.get("used_in_approved") else "[bold green]UNMINED (0)[/bold green]"
        table.add_row(
            f["field_key"],
            f.get("category", "N/A"),
            f"{f.get('timing_delay', 1)}d",
            overlap_str,
            f.get("description", "")[:60],
        )

    console.print(table)
    console.print()



def render_cross_dataset_batch(candidates: list[Any], batch_path: str | None = None) -> None:
    """Render v2 Cross-Dataset Alpha Engine generated batch report and simulation cards."""
    console.print()
    console.print("[bold cyan]===============================================================[/bold cyan]")
    console.print("[bold cyan]       v2 CROSS-DATASET ALPHA ENGINE: TRI-CANDIDATE BATCH      [/bold cyan]")
    console.print("[bold cyan]===============================================================[/bold cyan]\n")

    if batch_path:
        console.print(f"[bold green]Saved batch file:[/bold green] [yellow]{batch_path}[/yellow]\n")

    summary_table = Table(title="Generated Cross-Dataset Candidates (Audited & Screened)", show_header=True, header_style="bold white")
    summary_table.add_column("#", justify="center", style="bold")
    summary_table.add_column("Archetype", style="bold cyan")
    summary_table.add_column("Datasets Paired", style="yellow")
    summary_table.add_column("Depth", justify="right")
    summary_table.add_column("Turnover Est.", justify="right")
    summary_table.add_column("Corr Risk", justify="center")

    for i, c in enumerate(candidates, 1):
        risk_style = "bold green" if c.correlation_risk_score <= 0.40 else "yellow" if c.correlation_risk_score <= 0.65 else "bold red"
        summary_table.add_row(
            str(i),
            c.title.split("(")[0].strip(),
            f"{c.primary_dataset} x {c.secondary_dataset}",
            str(c.ast_depth),
            f"{c.turnover_proxy_score:.1%}",
            f"[{risk_style}]{c.correlation_risk_score:.2f}[/{risk_style}]",
        )

    console.print(summary_table)
    console.print()

    # Render Simulation Cards
    for i, c in enumerate(candidates, 1):
        console.print(f"[bold white on blue] Candidate {i}: {c.title} [/bold white on blue]")
        console.print(f"[bold]Economic Rationale:[/bold] {c.economic_rationale}")
        console.print(f"[bold]Datasets:[/bold] {c.primary_dataset} (Primary) x {c.secondary_dataset} (Secondary)")
        console.print(f"[bold]Turnover Proxy:[/bold] {c.turnover_proxy_score:.1%} | [bold]Max Correlation Risk:[/bold] {c.correlation_risk_score:.2f}")

        expr_panel = Panel(
            Text(c.expression, style="bold green"),
            title="Formula Expression (Copy & Paste to Platform)",
            border_style="green",
        )
        console.print(expr_panel)

        settings_table = Table(show_header=True, header_style="bold white", box=None)
        settings_table.add_column("Region", style="cyan")
        settings_table.add_column("Universe", style="cyan")
        settings_table.add_column("Neutralization", style="cyan")
        settings_table.add_column("Decay", style="cyan")
        settings_table.add_column("Delay", style="cyan")
        settings_table.add_column("Truncation", style="cyan")
        settings_table.add_row(
            getattr(c, "recommended_region", "USA"),
            getattr(c, "recommended_universe", "TOP3000"),
            getattr(c, "recommended_neutralization", "SUBINDUSTRY"),
            str(getattr(c, "recommended_decay", 5)),
            "1",
            str(getattr(c, "recommended_truncation", 0.08)),
        )
        console.print(settings_table)
        console.print()


def render_existence_check(result: Any) -> None:
    """Render comprehensive existence check and portfolio collision report."""
    verdict = getattr(result, "verdict", None)
    v_val = verdict.value if hasattr(verdict, "value") else str(verdict)

    console.print()
    if v_val == "SAFE_VIRGIN_ALPHA":
        console.print(Panel(
            "[bold green]PASS: SAFE TO MINE (100% ORIGINAL VIRGIN ALPHA)[/bold green]\n"
            "Zero exact duplicates, no primary field overlap with approved/submitted portfolio.",
            title="Database Existence & Portfolio Collision Audit",
            border_style="bold green",
        ))
    elif v_val == "EXACT_DUPLICATE":
        console.print(Panel(
            "[bold red]FAIL: EXACT DUPLICATE DETECTED IN DATABASE[/bold red]\n"
            "This expression or its exact canonical hash already exists in PostgreSQL research memory.",
            title="Database Existence & Portfolio Collision Audit",
            border_style="bold red",
        ))
    elif v_val == "HIGH_PORTFOLIO_COLLISION":
        console.print(Panel(
            f"[bold red]FAIL: HIGH PORTFOLIO COLLISION ALERT (RISK: {result.max_risk_score:.1%})[/bold red]\n"
            "Shares core driver fields with active/submitted alphas in your portfolio. High self-correlation risk (>= 0.70).",
            title="Database Existence & Portfolio Collision Audit",
            border_style="bold red",
        ))
    else:
        console.print(Panel(
            "[bold yellow]WARNING: PREVIOUSLY TESTED & FAILED FACTOR[/bold yellow]\n"
            "Similar factor expressions were tested in past batches and repeatedly rejected.",
            title="Database Existence & Portfolio Collision Audit",
            border_style="bold yellow",
        ))

    # Details table
    detail_table = Table(show_header=False, box=None)
    detail_table.add_column("Field", style="bold white", width=22)
    detail_table.add_column("Value", style="cyan")

    detail_table.add_row("Expression", result.expression_raw)
    detail_table.add_row("Canonical Expression", result.canonical_expression)
    detail_table.add_row("Expression Hash", result.expression_hash)
    detail_table.add_row("Primary Drivers", ", ".join(sorted(result.primary_fields)) if result.primary_fields else "None (Price only)")
    detail_table.add_row("All Fields", ", ".join(sorted(result.all_fields)))
    detail_table.add_row("Max Collision Risk", f"{result.max_risk_score:.1%}")
    detail_table.add_row("Verdict", f"[bold]{v_val}[/bold]")
    console.print(detail_table)
    console.print()

    # Exact match details if present
    if result.exact_match:
        em = result.exact_match
        em_table = Table(title="Exact Duplicate Candidate in Database", show_header=True, header_style="bold white")
        em_table.add_column("Candidate ID", style="bold magenta")
        em_table.add_column("Status", style="bold yellow")
        em_table.add_column("Sharpe", justify="right")
        em_table.add_column("Fitness", justify="right")
        em_table.add_column("Turnover", justify="right")
        em_table.add_column("Sub-Univ Sharpe", justify="right")
        em_table.add_column("Decision Reason")

        em_table.add_row(
            em.candidate_id[:8],
            em.status,
            f"{em.sharpe:.2f}" if em.sharpe is not None else "-",
            f"{em.fitness:.2f}" if em.fitness is not None else "-",
            f"{em.turnover:.1%}" if em.turnover is not None else "-",
            f"{em.subuniverse_sharpe:.2f}" if em.subuniverse_sharpe is not None else "-",
            em.last_decision_reason or "N/A",
        )
        console.print(em_table)
        console.print()

    # Active portfolio collisions
    if result.portfolio_collisions:
        col_table = Table(title="Colliding Active / Submitted Portfolio Alphas", show_header=True, header_style="bold red")
        col_table.add_column("Candidate ID", style="bold magenta")
        col_table.add_column("Status", style="bold yellow")
        col_table.add_column("Similarity", justify="right", style="bold red")
        col_table.add_column("Sharpe", justify="right")
        col_table.add_column("Fitness", justify="right")
        col_table.add_column("Expression")

        for col in result.portfolio_collisions[:5]:
            col_table.add_row(
                col.candidate_id[:8],
                col.status,
                f"{col.similarity_score:.1%}",
                f"{col.sharpe:.2f}" if col.sharpe is not None else "-",
                f"{col.fitness:.2f}" if col.fitness is not None else "-",
                col.expression_raw[:45] + "...",
            )
        console.print(col_table)
        console.print()

    # Past failures
    if result.past_failures:
        fail_table = Table(title="Historical Negative Knowledge (Past Rejected Batches)", show_header=True, header_style="bold yellow")
        fail_table.add_column("Candidate ID", style="bold magenta")
        fail_table.add_column("Status", style="bold red")
        fail_table.add_column("Sharpe", justify="right")
        fail_table.add_column("Fitness", justify="right")
        fail_table.add_column("Turnover", justify="right")
        fail_table.add_column("Audit Reason")

        for f_cand in result.past_failures[:3]:
            fail_table.add_row(
                f_cand.candidate_id[:8],
                f_cand.status,
                f"{f_cand.sharpe:.2f}" if f_cand.sharpe is not None else "-",
                f"{f_cand.fitness:.2f}" if f_cand.fitness is not None else "-",
                f"{f_cand.turnover:.1%}" if f_cand.turnover is not None else "-",
                f_cand.last_decision_reason or "Rejected in past batch",
            )
        console.print(fail_table)
        console.print()

    # Recommendation
    rec_style = "bold green" if v_val == "SAFE_VIRGIN_ALPHA" else "bold red"
    console.print(Panel(f"[{rec_style}]{result.recommendation}[/{rec_style}]", title="Actionable Recommendation", border_style="cyan"))
    console.print()

