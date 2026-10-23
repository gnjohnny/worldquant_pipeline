"""Database initialization and seed script for worldquant_pipeline."""
import sys
from pathlib import Path

# Add src to pythonpath
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from rich.console import Console
from sqlalchemy.orm import Session

from worldquant_pipeline.config.settings import get_settings
from worldquant_pipeline.storage.database import get_engine, get_session, init_db
from worldquant_pipeline.storage.models import DataField

console = Console()


def seed_data_fields(session: Session, settings) -> int:
    """Seed default fields from data_sources.yaml into the database."""
    fields_catalog = settings.data_sources_config.get("fields", [])
    seeded_count = 0

    for item in fields_catalog:
        key = item["field_key"]
        existing = session.query(DataField).filter_by(field_key=key).first()
        if not existing:
            field = DataField(
                field_key=key,
                category=item.get("category", "price_volume"),
                description=item.get("description", ""),
                timing_delay=item.get("timing_delay", 1),
                unit=item.get("unit"),
                region=item.get("region", "USA"),
                permitted_use=item.get("permitted_use", True),
            )
            session.add(field)
            seeded_count += 1

    session.commit()
    return seeded_count


def main() -> None:
    settings = get_settings()
    console.print(f"[bold cyan]Connecting to database:[/bold cyan] {settings.database_url}")

    try:
        engine = get_engine()
        with engine.connect():
            console.print("[bold green]Connection successful![/bold green]")

        console.print("[cyan]Creating database tables...[/cyan]")
        init_db(engine)
        console.print("[bold green]Tables created successfully.[/bold green]")

        console.print("[cyan]Seeding data fields from catalog...[/cyan]")
        with get_session() as session:
            count = seed_data_fields(session, settings)
            console.print(f"[bold green]Seeded {count} new data fields.[/bold green]")

    except Exception as e:  # noqa: BLE001
        console.print(f"[bold red]Database initialization failed:[/bold red] {e}")
        console.print(
            "\n[yellow]Tip:[/yellow] Ensure PostgreSQL is running locally and the database exists:\n"
            "  createdb worldquant_brain\n"
            "Or update DATABASE_URL in your .env file."
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
