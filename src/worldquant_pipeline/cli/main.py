"""Typer CLI application for worldquant_pipeline."""
import json
from pathlib import Path
from typing import Annotated

import typer
from rich.prompt import Confirm, FloatPrompt, Prompt
from rich.table import Table

from worldquant_pipeline.brain.manual_adapter import ManualBrainAdapter
from worldquant_pipeline.cli.views import (
    console,
    render_dashboard,
    render_gate_results,
    render_ingestion_report,
    render_prompt_export,
    render_simulation_card,
)
from worldquant_pipeline.config.settings import get_settings
from worldquant_pipeline.evaluation.gates import QualityGateRunner
from worldquant_pipeline.hypotheses.importer import HypothesisImporter
from worldquant_pipeline.hypotheses.prompts import generate_copilot_prompt
from worldquant_pipeline.storage.database import get_session
from worldquant_pipeline.storage.models import (
    AlphaCandidate,
    Decision,
    Experiment,
    ExperimentMetric,
    ResearchHypothesis,
)

app = typer.Typer(
    name="worldquant",
    help="WorldQuant BRAIN Alpha Research & Experiment Tracking Pipeline",
    add_completion=False,
)


@app.command()
def status() -> None:
    """View overall research workbench status, candidate counts, and recent alphas."""
    try:
        with get_session() as session:
            hypo_count = session.query(ResearchHypothesis).count()
            candidates = session.query(AlphaCandidate).all()

            status_counts: dict[str, int] = {}
            for c in candidates:
                status_counts[c.status] = status_counts.get(c.status, 0) + 1

            recent = (
                session.query(AlphaCandidate)
                .order_by(AlphaCandidate.created_at.desc())
                .limit(5)
                .all()
            )
            render_dashboard(hypo_count, status_counts, recent)
    except Exception as e:  # noqa: BLE001
        console.print(f"[bold red]Could not connect to database:[/bold red] {e}")
        console.print("[yellow]Tip:[/yellow] Run `python scripts/init_db.py` to create tables.")


@app.command()
def prompt(
    domain: Annotated[
        str | None,
        typer.Option("--domain", "-d", help="Research domain (e.g. price_volume, momentum, analyst)"),
    ] = None,
) -> None:
    """Export structured copilot brainstorming prompt with data fields and negative knowledge."""
    settings = get_settings()
    active_domain = domain or settings.research_domain

    session = None
    try:
        session = get_session()
    except Exception:  # noqa: BLE001
        session = None

    try:
        prompt_text = generate_copilot_prompt(active_domain, session=session)
        render_prompt_export(prompt_text)
    finally:
        if session:
            session.close()


@app.command()
def ingest(
    file_path: Annotated[
        Path,
        typer.Argument(help="Path to JSON file containing hypotheses & candidate expressions"),
    ],
) -> None:
    """Ingest, validate against Gate G1 (AST check), and register a JSON candidate batch."""
    if not file_path.exists():
        console.print(f"[bold red]File not found:[/bold red] {file_path}")
        raise typer.Exit(code=1)

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    with get_session() as session:
        importer = HypothesisImporter(session)
        report = importer.ingest_data(data)
        render_ingestion_report(report)


@app.command()
def show(
    candidate_id: Annotated[
        str,
        typer.Argument(help="Candidate ID (or first 8 characters of UUID)"),
    ],
) -> None:
    """Display a candidate expression formatted with recommended BRAIN simulation parameters."""
    with get_session() as session:
        candidate = (
            session.query(AlphaCandidate)
            .filter(AlphaCandidate.id.startswith(candidate_id))
            .first()
        )
        if not candidate:
            console.print(f"[bold red]Candidate with ID prefix '{candidate_id}' not found.[/bold red]")
            raise typer.Exit(code=1)

        adapter = ManualBrainAdapter()
        card = adapter.format_candidate(candidate)
        render_simulation_card(card)


@app.command()
def record(
    candidate_id: Annotated[
        str,
        typer.Argument(help="Candidate ID (or first 8 characters of UUID)"),
    ],
) -> None:
    """Record platform simulation metrics (Sharpe, turnover, fitness) and log an explicit decision."""
    with get_session() as session:
        candidate = (
            session.query(AlphaCandidate)
            .filter(AlphaCandidate.id.startswith(candidate_id))
            .first()
        )
        if not candidate:
            console.print(f"[bold red]Candidate with ID prefix '{candidate_id}' not found.[/bold red]")
            raise typer.Exit(code=1)

        console.print(f"\n[bold cyan]Recording Simulation for Candidate:[/bold cyan] {candidate.id[:8]}")
        console.print(f"[bold]Expression:[/bold] [green]{candidate.expression_raw}[/green]\n")

        # Interactive metric prompt
        sharpe = FloatPrompt.ask("Enter Sharpe Ratio")
        turnover = FloatPrompt.ask("Enter Turnover (e.g. 0.25 for 25%)")
        fitness_str = Prompt.ask("Enter Fitness Score (press Enter to skip)", default="")
        drawdown_str = Prompt.ask("Enter Max Drawdown (e.g. 0.15 for 15%, press Enter to skip)", default="")

        metrics: dict[str, float] = {"sharpe": sharpe, "turnover": turnover}
        if fitness_str:
            metrics["fitness"] = float(fitness_str)
        if drawdown_str:
            metrics["drawdown"] = float(drawdown_str)

        # Gate G5 evaluation
        gate_runner = QualityGateRunner()
        gate_res = gate_runner.evaluate_metrics(metrics)
        render_gate_results(gate_res)

        # Prompt for decision
        default_decision = "APPROVED" if gate_res.passed else "REJECTED"
        decision = Prompt.ask(
            "Enter Decision ([green]APPROVED[/green] / [red]REJECTED[/red] / [magenta]NEEDS_REVISION[/magenta])",
            choices=["APPROVED", "REJECTED", "NEEDS_REVISION"],
            default=default_decision,
        )

        reason = Prompt.ask("Enter detailed reason / research notes")

        if not Confirm.ask("Save this experiment and decision to PostgreSQL?"):
            console.print("[yellow]Aborted. No records were saved.[/yellow]")
            return

        # Create experiment and metrics
        exp = Experiment(
            candidate_id=candidate.id,
            status="COMPLETED",
        )
        session.add(exp)
        session.flush()

        for m_name, m_val in metrics.items():
            session.add(
                ExperimentMetric(
                    experiment_id=exp.id,
                    metric_name=m_name,
                    metric_value=m_val,
                    source="BRAIN_PLATFORM",
                )
            )

        # Create decision
        dec = Decision(
            candidate_id=candidate.id,
            decision=decision,
            reason=reason,
            reviewer="HUMAN_RESEARCHER",
        )
        session.add(dec)

        # Update candidate status
        candidate.status = decision
        session.commit()

        console.print(f"\n[bold green][SUCCESS] Successfully recorded experiment and decision ({decision})![/bold green]\n")


@app.command()
def audit(
    expression_or_id: Annotated[
        str,
        typer.Argument(help="Alpha expression string or candidate ID prefix to audit"),
    ],
    decay: Annotated[int, typer.Option("--decay", "-d", help="Simulation decay horizon")] = 4,
    neutralization: Annotated[
        str,
        typer.Option("--neutralization", "-n", help="Group neutralization (subindustry/sector)"),
    ] = "subindustry",
) -> None:
    """Run pre-simulation Gate G1 (AST/Event), Gate G2 (Turnover Proxy), and Gate G3+ (Collision Audit)."""
    with get_session() as session:
        cand = (
            session.query(AlphaCandidate)
            .filter(AlphaCandidate.id.startswith(expression_or_id))
            .first()
        )
        expr = cand.expression_raw if cand else expression_or_id

        console.print("\n[bold cyan]=== Pre-Simulation Alpha Audit (Gates G1, G2, G3+) ===[/bold cyan]")
        console.print(f"[bold]Expression:[/bold] [green]{expr}[/green]")
        console.print(f"[bold]Settings:[/bold] Decay = {decay}, Neutralization = {neutralization}\n")

        gate_runner = QualityGateRunner()
        res = gate_runner.evaluate_pre_simulation(
            expr, session=session, decay=decay, target_grouping=neutralization
        )

        # Gate details table
        table = Table(show_header=True, header_style="bold white")
        table.add_column("Gate", style="bold")
        table.add_column("Status", justify="center")
        table.add_column("Details")

        g1_ok = res.gate_details.get("G1_ast_validity", True)
        table.add_row(
            "Gate G1: AST & Event Typing",
            "[green]PASS[/green]" if g1_ok else "[bold red]FAIL[/bold red]",
            "Valid syntax & operator types" if g1_ok else "; ".join(res.failures),
        )

        g2_ok = res.gate_details.get("G2_turnover_proxy", True)
        table.add_row(
            "Gate G2: Turnover Proxy",
            "[green]PASS[/green]" if g2_ok else "[bold red]FAIL[/bold red]",
            "Turnover in acceptable bounds" if g2_ok else "Turnover risk outside bounds",
        )

        g3_ok = res.gate_details.get("G3_correlation_risk", True)
        table.add_row(
            "Gate G3+: Factor Overlap",
            "[green]LOW RISK[/green]" if g3_ok else "[bold red]HIGH RISK[/bold red]",
            "No dangerous overlap with approved alphas" if g3_ok else "Self-correlation collision risk",
        )

        console.print(table)
        console.print()

        if res.warnings:
            console.print("[bold yellow]Audit Warnings & Advisories:[/bold yellow]")
            for w in res.warnings:
                console.print(f"  • [yellow]{w}[/yellow]")
            console.print()

        if res.failures:
            console.print("[bold red]Audit Blocking Failures:[/bold red]")
            for f in res.failures:
                console.print(f"  • [red]{f}[/red]")
            console.print()
        else:
            console.print("[bold green]Pre-simulation checks passed! Candidate is safe for BRAIN simulation.[/bold green]\n")


def main() -> None:
    app()


if __name__ == "__main__":
    main()
