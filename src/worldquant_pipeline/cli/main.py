"""Typer CLI application for worldquant_pipeline."""
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Annotated, Any

import typer
from rich.prompt import Confirm, FloatPrompt, Prompt
from rich.table import Table

from worldquant_pipeline.brain.manual_adapter import ManualBrainAdapter
from worldquant_pipeline.cli.metric_parser import (
    evaluate_consultant_track_decision,
    parse_brain_paste,
)
from worldquant_pipeline.cli.submission import generate_submission_metadata
from worldquant_pipeline.cli.views import (
    console,
    render_cross_dataset_batch,
    render_dashboard,
    render_discovered_fields,
    render_existence_check,
    render_gate_results,
    render_ingestion_report,
    render_parsed_metrics,
    render_prompt_export,
    render_simulation_card,
    render_submission_card,
)
from worldquant_pipeline.config.settings import get_settings
from worldquant_pipeline.evaluation.existence_checker import AlphaExistenceChecker
from worldquant_pipeline.evaluation.gates import QualityGateRunner
from worldquant_pipeline.hypotheses.cross_engine import CrossDatasetEngine
from worldquant_pipeline.hypotheses.importer import HypothesisImporter
from worldquant_pipeline.hypotheses.prompts import generate_copilot_prompt
from worldquant_pipeline.storage.database import get_session
from worldquant_pipeline.storage.models import (
    AlphaCandidate,
    DataField,
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


@app.command("record-paste")
def record_paste(
    candidate_id: Annotated[
        str,
        typer.Argument(help="Candidate ID (or first 8 characters of UUID)"),
    ],
    text: Annotated[
        str | None,
        typer.Option("--text", "-t", help="Raw backtest output pasted from WorldQuant BRAIN"),
    ] = None,
    universe: Annotated[str, typer.Option("--universe", "-u")] = "TOP3000",
    neutralization: Annotated[str, typer.Option("--neutralization", "-n")] = "SUBINDUSTRY",
    decay: Annotated[int, typer.Option("--decay", "-d")] = 5,
    truncation: Annotated[float, typer.Option("--truncation", "-t")] = 0.08,
) -> None:
    """Instantly parse raw text pasted from BRAIN platform, evaluate gates, and record to DB."""
    raw_content = text
    if not raw_content:
        console.print("[cyan]Paste raw text from WorldQuant BRAIN backtest card (end with empty line or EOF):[/cyan]")
        lines: list[str] = []
        try:
            while True:
                line = input()
                if not line and lines:
                    break
                lines.append(line)
        except EOFError:
            pass
        raw_content = "\n".join(lines)

    if not raw_content.strip():
        console.print("[red]No text provided. Aborting.[/red]")
        raise typer.Exit(code=1)

    with get_session() as session:
        candidate = (
            session.query(AlphaCandidate)
            .filter(AlphaCandidate.id.startswith(candidate_id))
            .first()
        )
        if not candidate:
            console.print(f"[bold red]Candidate with ID prefix '{candidate_id}' not found.[/bold red]")
            raise typer.Exit(code=1)

        metrics = parse_brain_paste(raw_content)
        decision, reason = evaluate_consultant_track_decision(metrics)

        exp = Experiment(
            candidate_id=candidate.id,
            universe=universe,
            neutralization=neutralization,
            decay=decay,
            truncation=truncation,
            status="COMPLETED",
        )
        session.add(exp)
        session.flush()

        for m_name, m_val in metrics.to_metric_dict().items():
            session.add(
                ExperimentMetric(
                    experiment_id=exp.id,
                    metric_name=m_name,
                    metric_value=m_val,
                    source="BRAIN_PLATFORM",
                )
            )

        session.add(
            Decision(
                candidate_id=candidate.id,
                decision=decision,
                reason=reason,
                reviewer="RECORD_PASTE_AUTO",
            )
        )
        candidate.status = decision
        session.commit()

        render_parsed_metrics(candidate.id[:8], metrics, decision, reason)

        if decision == "APPROVED":
            meta = generate_submission_metadata(
                candidate,
                universe=universe,
                neutralization=neutralization,
                decay=decay,
            )
            render_submission_card(meta)


@app.command("record-batch")
def record_batch(
    batch_source: Annotated[
        str,
        typer.Argument(help="Path to JSON batch file or comma-separated candidate ID prefixes (e.g. 'c1,c2,c3')"),
    ],
    paste_file: Annotated[
        str | None,
        typer.Option("--paste-file", "-f", help="Optional file containing raw backtest simulation pastes"),
    ] = None,
    universe: Annotated[str, typer.Option("--universe", "-u")] = "TOP3000",
    neutralization: Annotated[str, typer.Option("--neutralization", "-n")] = "SUBINDUSTRY",
    decay: Annotated[int, typer.Option("--decay", "-d")] = 5,
    truncation: Annotated[float, typer.Option("--truncation", "-t")] = 0.08,
) -> None:
    """Batch-record simulation metrics for all candidates in a batch (Tri-Candidate Protocol)."""
    with get_session() as session:
        candidates: list[AlphaCandidate] = []
        source_path = Path(batch_source)

        if source_path.exists():
            with open(source_path, "r", encoding="utf-8") as f:
                batch_data = json.load(f)

            # Auto-ingest if needed
            importer = HypothesisImporter(session=session)
            report = importer.ingest_data(batch_data)
            if report.valid_candidates > 0:
                console.print(f"[cyan]Ingested {report.valid_candidates} candidates from {source_path.name}[/cyan]")

            # Collect expressions from batch file
            expressions: list[str] = []
            for hypo in batch_data.get("hypotheses", []):
                for cand in hypo.get("candidates", []):
                    expressions.append(cand.get("expression", ""))

            # Fetch candidates from DB
            for expr in expressions:
                db_cand = (
                    session.query(AlphaCandidate)
                    .filter(AlphaCandidate.expression_raw == expr)
                    .order_by(AlphaCandidate.created_at.desc())
                    .first()
                )
                if db_cand and db_cand not in candidates:
                    candidates.append(db_cand)
        else:
            # Comma-separated prefixes
            prefixes = [p.strip() for p in batch_source.split(",") if p.strip()]
            for pfx in prefixes:
                db_cand = (
                    session.query(AlphaCandidate)
                    .filter(AlphaCandidate.id.startswith(pfx))
                    .first()
                )
                if db_cand and db_cand not in candidates:
                    candidates.append(db_cand)

        if not candidates:
            console.print(f"[bold red]No matching candidates found for source:[/bold red] {batch_source}")
            raise typer.Exit(code=1)

        console.print(f"\n[bold cyan]=== Starting Batch Simulation Recording ({len(candidates)} Candidates) ===[/bold cyan]")
        console.print(f"[bold]Platform Settings:[/bold] Universe={universe}, Neutralization={neutralization}, Decay={decay}, Truncation={truncation}\n")

        paste_blocks: list[str] = []
        if paste_file:
            pf = Path(paste_file)
            if pf.exists():
                with open(pf, "r", encoding="utf-8") as f:
                    content = f.read()
                # Split by delimiters like '---' or '===' or multiple blank lines or Candidate headers
                raw_splits = re.split(r"(?:\n\s*[-=]{3,}\s*\n|\n{3,}|\n+(?=Candidate\s+\d+.*?:))", content)
                paste_blocks = [s.strip() for s in raw_splits if s.strip()]

        batch_results: list[dict[str, Any]] = []

        for idx, cand in enumerate(candidates, start=1):
            console.print("\n[bold yellow]------------------------------------------------------------[/bold yellow]")
            console.print(f"[bold yellow]Candidate [{idx}/{len(candidates)}] ID:[/bold yellow] [bold white]{cand.id[:8]}[/bold white]")
            console.print(f"[bold]Expression:[/bold] [green]{cand.expression_raw}[/green]")
            console.print("[bold yellow]------------------------------------------------------------[/bold yellow]")

            raw_text = ""
            if paste_blocks and idx <= len(paste_blocks):
                raw_text = paste_blocks[idx - 1]
                console.print(f"[cyan]Using simulation text from paste file (block {idx}).[/cyan]")
            else:
                console.print("[cyan]Paste raw text from WorldQuant BRAIN backtest card (type 'skip' to skip, end with blank line):[/cyan]")
                lines: list[str] = []
                try:
                    while True:
                        line = input()
                        if line.strip().lower() == "skip":
                            raw_text = "skip"
                            break
                        if not line and lines:
                            break
                        lines.append(line)
                except EOFError:
                    pass
                if raw_text != "skip":
                    raw_text = "\n".join(lines).strip()

            if not raw_text or raw_text == "skip":
                console.print(f"[yellow]Skipping Candidate {cand.id[:8]}.[/yellow]")
                batch_results.append({
                    "id": cand.id[:8],
                    "expression": cand.expression_raw[:45] + "...",
                    "sharpe": "-",
                    "fitness": "-",
                    "turnover": "-",
                    "self_corr": "-",
                    "decision": "SKIPPED",
                    "reason": "User skipped manual paste.",
                })
                continue

            metrics = parse_brain_paste(raw_text)
            decision, reason = evaluate_consultant_track_decision(metrics)

            exp = Experiment(
                candidate_id=cand.id,
                universe=universe,
                neutralization=neutralization,
                decay=decay,
                truncation=truncation,
                status="COMPLETED",
            )
            session.add(exp)
            session.flush()

            for m_name, m_val in metrics.to_metric_dict().items():
                session.add(
                    ExperimentMetric(
                        experiment_id=exp.id,
                        metric_name=m_name,
                        metric_value=m_val,
                        source="BRAIN_PLATFORM",
                    )
                )

            session.add(
                Decision(
                    candidate_id=cand.id,
                    decision=decision,
                    reason=reason,
                    reviewer="RECORD_BATCH_AUTO",
                )
            )
            cand.status = decision
            session.commit()

            render_parsed_metrics(cand.id[:8], metrics, decision, reason)

            if decision == "APPROVED":
                meta = generate_submission_metadata(
                    cand,
                    universe=universe,
                    neutralization=neutralization,
                    decay=decay,
                )
                render_submission_card(meta)

            batch_results.append({
                "id": cand.id[:8],
                "expression": cand.expression_raw[:45] + "...",
                "sharpe": f"{metrics.sharpe:.2f}" if metrics.sharpe is not None else "-",
                "fitness": f"{metrics.fitness:.2f}" if metrics.fitness is not None else "-",
                "turnover": f"{metrics.turnover * 100:.1f}%" if metrics.turnover is not None else "-",
                "self_corr": f"{metrics.self_correlation:.4f}" if metrics.self_correlation is not None else "-",
                "decision": decision,
                "reason": reason[:60] + ("..." if len(reason) > 60 else ""),
            })

        # Render Batch Summary Table
        console.print("\n[bold cyan]=================== Batch Simulation Summary ===================[/bold cyan]")
        summary_table = Table(show_header=True, header_style="bold magenta")
        summary_table.add_column("Candidate ID", style="bold")
        summary_table.add_column("Expression")
        summary_table.add_column("Sharpe", justify="right")
        summary_table.add_column("Fitness", justify="right")
        summary_table.add_column("Turnover", justify="right")
        summary_table.add_column("Self-Corr", justify="right")
        summary_table.add_column("Decision", justify="center")
        summary_table.add_column("Audit Reason")

        for r in batch_results:
            dec_color = "green" if r["decision"] == "APPROVED" else ("red" if r["decision"] == "REJECTED" else "yellow")
            summary_table.add_row(
                r["id"],
                r["expression"],
                r["sharpe"],
                r["fitness"],
                r["turnover"],
                r["self_corr"],
                f"[{dec_color}]{r['decision']}[/{dec_color}]",
                r["reason"],
            )
        console.print(summary_table)
        console.print()


@app.command("prepare-submission")
def prepare_submission(
    candidate_id: Annotated[
        str,
        typer.Argument(help="Candidate ID (or first 8 characters of UUID)"),
    ],
    universe: Annotated[str, typer.Option("--universe", "-u")] = "TOP3000",
    neutralization: Annotated[str, typer.Option("--neutralization", "-n")] = "SUBINDUSTRY",
    decay: Annotated[int, typer.Option("--decay", "-d")] = 5,
) -> None:
    """Generate standardized Invariant 6 submission card for an alpha candidate."""
    with get_session() as session:
        candidate = (
            session.query(AlphaCandidate)
            .filter(AlphaCandidate.id.startswith(candidate_id))
            .first()
        )
        if not candidate:
            console.print(f"[bold red]Candidate with ID prefix '{candidate_id}' not found.[/bold red]")
            raise typer.Exit(code=1)

        meta = generate_submission_metadata(
            candidate,
            universe=universe,
            neutralization=neutralization,
            decay=decay,
        )
        render_submission_card(meta)


@app.command("discover-fields")
def discover_fields(
    category: Annotated[str | None, typer.Option("--category", "-c", help="Filter by category")] = None,
    keyword: Annotated[str | None, typer.Option("--keyword", "-k", help="Search keyword in name or description")] = None,
    unmined_only: Annotated[bool, typer.Option("--unmined-only/--all", help="Show only fields never used in approved alphas")] = True,
    limit: Annotated[int, typer.Option("--limit", "-l", help="Maximum fields to display")] = 25,
) -> None:
    """Discover unmined, high-coverage data fields across WorldQuant BRAIN datasets."""
    with get_session() as session:
        approved = session.query(AlphaCandidate).filter(AlphaCandidate.status == "APPROVED").all()
        used_fields: set[str] = set()
        for c in approved:
            expr_lower = c.expression_raw.lower()
            for token in re.findall(r"[a-z0-9_]+", expr_lower):
                used_fields.add(token)

        query = session.query(DataField)
        if category:
            query = query.filter(DataField.category.ilike(f"%{category}%"))
        fields = query.all()

        results: list[dict[str, Any]] = []
        for f in fields:
            is_used = f.field_key.lower() in used_fields
            if unmined_only and is_used:
                continue

            if keyword:
                kw = keyword.lower()
                if kw not in f.field_key.lower() and kw not in (f.description or "").lower():
                    continue

            results.append({
                "field_key": f.field_key,
                "category": f.category,
                "timing_delay": f.timing_delay,
                "used_in_approved": is_used,
                "description": f.description or "N/A",
            })

            if len(results) >= limit:
                break

        title = f"Discovered Data Fields (Category: {category or 'All'}, Unmined Only: {unmined_only})"
        render_discovered_fields(results, title=title)


@app.command("generate-v2")
def generate_v2(
    output: Annotated[
        str | None,
        typer.Option("--output", "-o", help="Custom JSON path to save the generated Tri-Candidate batch"),
    ] = None,
    max_risk: Annotated[
        float,
        typer.Option("--max-risk", "-r", help="Maximum allowable correlation risk against approved alphas"),
    ] = 0.40,
    auto_ingest: Annotated[
        bool,
        typer.Option("--ingest/--no-ingest", help="Automatically register candidates into PostgreSQL memory"),
    ] = True,
) -> None:
    """Generate a high-fitness, low-correlation Tri-Candidate Batch using the v2 Cross-Dataset Engine."""
    with get_session() as session:
        engine = CrossDatasetEngine(db_session=session)
        
        # Determine filepath
        if output:
            batch_path = Path(output)
        else:
            ts_str = datetime.now().strftime("%Y%m%d_%H%M%S")
            batch_path = Path("data") / f"batch_v2_{ts_str}.json"

        batch_path, candidates = engine.export_batch_json(
            filepath=batch_path,
            session=session,
            max_correlation_risk=max_risk,
        )

        render_cross_dataset_batch(candidates, batch_path=str(batch_path))

        if auto_ingest:
            console.print("[bold cyan]Auto-Ingesting batch into PostgreSQL research memory...[/bold cyan]")
            importer = HypothesisImporter(session=session)
            with open(batch_path, "r", encoding="utf-8") as f:
                batch_data = json.load(f)
            report = importer.ingest_data(batch_data)
            render_ingestion_report(report)


@app.command("check-exists")
def check_exists(
    expression: Annotated[
        str | None,
        typer.Argument(help="Alpha formula expression to check against research memory"),
    ] = None,
    file_path: Annotated[
        str | None,
        typer.Option("--file", "-f", help="JSON batch file to check all candidates"),
    ] = None,
    field_key: Annotated[
        str | None,
        typer.Option("--field", help="Search for all candidates using a specific data field"),
    ] = None,
    status_filter: Annotated[
        str | None,
        typer.Option("--status", "-s", help="Filter matching candidates by status (e.g. APPROVED, VALIDATED)"),
    ] = None,
) -> None:
    """Check if an alpha expression, driver factor, or data field already exists in PostgreSQL research memory."""
    with get_session() as session:
        if field_key:
            fk_clean = field_key.strip().lower()
            console.print(f"\n[bold cyan]Searching database for candidates using field:[/bold cyan] [bold yellow]{fk_clean}[/bold yellow]\n")
            cands = session.query(AlphaCandidate).all()
            matches = []
            for c in cands:
                all_f, _prim_f = AlphaExistenceChecker.extract_driver_fields(c.expression_raw)
                if (fk_clean in all_f or fk_clean in c.expression_raw.lower()) and (
                    not status_filter or c.status == status_filter.upper()
                ):
                    matches.append(c)

            if not matches:
                console.print(f"[bold green]No candidates found using field '{fk_clean}'. This field is 100% UNMINED & VIRGIN in your portfolio![/bold green]\n")
                return

            table = Table(title=f"Candidates Referencing Field '{fk_clean}' ({len(matches)} matches)", show_header=True, header_style="bold white")
            table.add_column("Candidate ID", style="bold magenta")
            table.add_column("Status", style="bold yellow")
            table.add_column("Expression")

            for m in matches[:25]:
                table.add_row(m.id[:8], m.status, m.expression_raw[:65] + ("..." if len(m.expression_raw) > 65 else ""))
            console.print(table)
            console.print()
            return

        expressions_to_check: list[str] = []
        if file_path:
            fp = Path(file_path)
            if not fp.exists():
                console.print(f"[bold red]File not found:[/bold red] {file_path}")
                raise typer.Exit(code=1)
            with open(fp, "r", encoding="utf-8") as f:
                bdata = json.load(f)
            for hypo in bdata.get("hypotheses", []):
                for cand in hypo.get("candidates", []):
                    expr = cand.get("expression")
                    if expr:
                        expressions_to_check.append(expr)
        elif expression:
            expressions_to_check.append(expression)
        else:
            console.print("[bold red]Please provide an expression string, a --file path, or a --field key.[/bold red]")
            raise typer.Exit(code=1)

        for expr in expressions_to_check:
            res = AlphaExistenceChecker.check_expression(expr, session)
            render_existence_check(res)


@app.command("companion")
def companion(
    batch_file: Annotated[
        Path | None,
        typer.Argument(help="Optional batch JSON file to inspect"),
    ] = None,
    show_bookmarklet: Annotated[
        bool,
        typer.Option("--bookmarklet", "-b", help="Print bookmarklet installation code"),
    ] = False,
) -> None:
    """WorldQuant BRAIN Simulator Companion (Browser HUD) helper."""
    bookmarklet_path = Path("tools/companion/bookmarklet.txt")
    if show_bookmarklet or not batch_file:
        console.print("[bold cyan]=========================================================================[/bold cyan]")
        console.print("[bold green]WorldQuant BRAIN Simulator Companion (Browser HUD)[/bold green]")
        console.print("[bold cyan]=========================================================================[/bold cyan]")
        console.print("A client-side browser helper that auto-fills simulator parameters and harvests results.")
        console.print("\n[bold yellow]Setup Instructions (10 seconds):[/bold yellow]")
        console.print("1. Open Chrome/Edge Bookmarks Manager ([bold white]Ctrl+Shift+O[/bold white])")
        console.print("2. Add a new bookmark named '[bold green]WQ Companion[/bold green]'")
        console.print("3. In the URL field, paste the bookmarklet code from [bold cyan]tools/companion/bookmarklet.txt[/bold cyan]")
        console.print("4. On [bold underline]platform.worldquantbrain.com/simulate[/bold underline], click the bookmark!")
        if bookmarklet_path.exists():
            bm_text = bookmarklet_path.read_text(encoding="utf-8").strip()
            console.print(f"\n[dim]Bookmarklet code ({len(bm_text)} chars ready in tools/companion/bookmarklet.txt)[/dim]")
        if not batch_file:
            return

    if batch_file and batch_file.exists():
        console.print(f"\n[bold green]Batch file ready: {batch_file.name}[/bold green]")
        console.print("Copy the batch content and click '[bold cyan]Load Batch from Clipboard[/bold cyan]' in the browser HUD.")


@app.command("import-fields")
def import_fields(
    file_path: Annotated[Path, typer.Argument(help="Path to CSV or JSON file containing field definitions")],
    category: Annotated[str | None, typer.Option("--category", "-c", help="Default category if missing in file")] = None,
) -> None:
    """Import new dataset fields from a CSV or JSON file into the database catalog."""
    if not file_path.exists():
        console.print(f"[bold red]File not found: {file_path}[/bold red]")
        raise typer.Exit(code=1)

    fields_to_add: list[dict[str, Any]] = []
    if file_path.suffix.lower() == ".json":
        with open(file_path, "r", encoding="utf-8") as f:
            raw_data = json.load(f)
            if isinstance(raw_data, list):
                fields_to_add = raw_data
            elif isinstance(raw_data, dict) and "fields" in raw_data:
                fields_to_add = raw_data["fields"]
    elif file_path.suffix.lower() == ".csv":
        import csv

        with open(file_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                fields_to_add.append(dict(row))

    if not fields_to_add:
        console.print("[yellow]No fields found in file.[/yellow]")
        return

    added_count = 0
    with get_session() as session:
        for item in fields_to_add:
            fkey = item.get("field_key") or item.get("name") or item.get("id")
            if not fkey:
                continue
            fkey = str(fkey).strip().lower()
            cat = item.get("category") or category or "custom"
            desc = item.get("description") or f"WorldQuant BRAIN data field {fkey}"
            unit = item.get("unit") or item.get("unit_type") or "dimensionless"
            delay = int(item.get("timing_delay") or item.get("delay") or 1)

            existing = session.query(DataField).filter_by(field_key=fkey).first()
            if not existing:
                df = DataField(
                    field_key=fkey,
                    category=cat,
                    description=desc,
                    timing_delay=delay,
                    unit=unit,
                    unit_type=unit,
                    permitted_use=True,
                )
                session.add(df)
                added_count += 1
            else:
                existing.category = cat
                existing.description = desc
                existing.unit = unit
                existing.unit_type = unit
        session.commit()

    console.print(f"[bold green]Successfully imported/updated {added_count} fields into data catalog![/bold green]")


def main() -> None:
    app()


if __name__ == "__main__":
    main()
