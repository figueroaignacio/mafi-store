import httpx
import typer
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TaskProgressColumn, TextColumn
from rich.table import Table

from spite.cli.commands import API_BASE, console


def search(
    query: str = typer.Argument(..., help="Job title or keywords"),
    location: str = typer.Option(
        "Argentina", "--location", "-l", help="Location to search"
    ),
    hours: int = typer.Option(24, "--hours", "-h", help="Jobs from the last N hours"),
    no_analyze: bool = typer.Option(False, "--no-score", help="Skip Groq analysis"),
    visible: bool = typer.Option(False, "--visible", help="Show browser window"),
    max_jobs: int = typer.Option(50, "--max-jobs", "-m", help="Max jobs to scrape"),
) -> None:
    """Scrape jobs and analyze them. The part that actually does something."""
    console.print(
        f"\n[bold red]▶[/bold red] [bold]Searching:[/bold] {query} in {location} (last {hours}h)\n"
    )

    try:
        with Progress(
            SpinnerColumn(spinner_name="dots2", style="red"),
            TextColumn("[progress.description]{task.description}"),
            TaskProgressColumn(),
            console=console,
            transient=True,
        ) as progress:
            task = progress.add_task("[dim]Scraping LinkedIn...", total=None)
            response = httpx.post(
                f"{API_BASE}/search/",
                json={
                    "query": query,
                    "location": location,
                    "hours": hours,
                    "analyze": not no_analyze,
                    "headless": not visible,
                    "max_jobs": max_jobs,
                },
                timeout=300.0,
            )
            response.raise_for_status()
            result = response.json()
            progress.update(task, completed=100, description="[green]Done![/green]")
    except httpx.ConnectError:
        console.print("[red]API is not running. Start it with: ./run.sh[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error during search: {e}[/red]")
        raise typer.Exit(1)

    summary = Table.grid(padding=(0, 2))
    summary.add_column(style="bold green")
    summary.add_column()
    summary.add_row("FOUND", f"{result['found']} jobs")
    summary.add_row("SAVED", f"[bold cyan]{result['saved']}[/bold cyan] new")
    summary.add_row("SKIP", f"[dim]{result['duplicates']} duplicates[/dim]")
    summary.add_row(
        "ANALYZE", f"[bold yellow]{result['analyzed']}[/bold yellow] analyzed by AI"
    )
    console.print(
        Panel(summary, title="Search Results", border_style="green", expand=False)
    )
