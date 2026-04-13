import httpx
import typer
from rich.align import Align
from rich.console import Console, Group
from rich.panel import Panel
from rich.progress import (
    Progress,
    SpinnerColumn,
    TaskProgressColumn,
    TextColumn,
)
from rich.table import Table
from rich.text import Text

app = typer.Typer(
    name="spite",
    help="Automated job hunting. Because optimism is for people with trust funds.",
    add_completion=False,
    rich_markup_mode="rich",
)

console = Console()
API_BASE = "http://127.0.0.1:8000"


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context) -> None:
    if ctx.invoked_subcommand is None:
        title = Text.assemble(
            ("\n", ""),
            (" S P I T E ", "bold white on red"),
            ("\n", ""),
        )
        banner = Panel(
            Align.center(
                Group(
                    title,
                    Text(
                        "\nAutomated job hunting for the cynical developer.",
                        style="dim italic",
                    ),
                    Text("The market is broken. This is the patch.\n", style="red"),
                )
            ),
            border_style="red",
            padding=(1, 2),
        )
        console.print(banner)
        console.print(
            Align.center("Run [bold]spite --help[/bold] to see available commands.\n")
        )


@app.command()
def version() -> None:
    """Print version and exit. At least something works as expected."""
    from spite import __version__

    console.print(
        f"spite [bold]{__version__}[/bold] — still less broken than the job market."
    )


@app.command()
def search(
    query: str = typer.Argument(..., help="Job title or keywords"),
    location: str = typer.Option(
        "Argentina", "--location", "-l", help="Location to search"
    ),
    hours: int = typer.Option(24, "--hours", "-h", help="Jobs from the last N hours"),
    no_score: bool = typer.Option(False, "--no-score", help="Skip Gemini scoring"),
    visible: bool = typer.Option(False, "--visible", help="Show browser window"),
    max_jobs: int = typer.Option(50, "--max-jobs", "-m", help="Max jobs to scrape"),
):
    """Scrape jobs and score them. The part that actually does something."""
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
            # Step 1: Search and Scrape
            task = progress.add_task("[dim]Scraping LinkedIn...", total=None)
            response = httpx.post(
                f"{API_BASE}/search/",
                json={
                    "query": query,
                    "location": location,
                    "hours": hours,
                    "score": not no_score,
                    "headless": not visible,
                    "max_jobs": max_jobs,
                },
                timeout=300.0,
            )
            response.raise_for_status()
            result = response.json()
            progress.update(task, completed=100, description="[green]Done![/green]")

    except httpx.ConnectError:
        console.print(
            "[red]API is not running. Start it with: uv run uvicorn spite.main:app[/red]"
        )
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error during search: {e}[/red]")
        raise typer.Exit(1)

    # Success Summary
    summary = Table.grid(padding=(0, 2))
    summary.add_column(style="bold green")
    summary.add_column()

    summary.add_row("FOUND", f"{result['found']} jobs")
    summary.add_row("SAVED", f"[bold cyan]{result['saved']}[/bold cyan] new")
    summary.add_row("SKIP", f"[dim]{result['duplicates']} duplicates[/dim]")
    summary.add_row(
        "SCORE", f"[bold yellow]{result['scored']}[/bold yellow] analyzed by AI"
    )

    console.print(
        Panel(summary, title="Search Results", border_style="green", expand=False)
    )


@app.command()
def list_jobs(
    min_score: float = typer.Option(
        0.0, "--min-score", "-s", help="Minimum Gemini score"
    ),
    platform: str = typer.Option(None, "--platform", "-p", help="Filter by platform"),
    limit: int = typer.Option(50, "--limit", "-n", help="Max results"),
):
    """List saved jobs. Sorted by score, best first."""
    try:
        params: dict = {"limit": limit}
        if min_score > 0.0:
            params["min_score"] = min_score
        if platform:
            params["platform"] = platform
        response = httpx.get(f"{API_BASE}/jobs/", params=params)
        response.raise_for_status()
        jobs = response.json()
    except httpx.ConnectError:
        console.print("[red]API is not running.[/red]")
        raise typer.Exit(1)

    if not jobs:
        console.print("[dim]No jobs found.[/dim]")
        return

    console.print(f"\n[dim]{len(jobs)} jobs[/dim]\n")

    for job in jobs:
        summary = (job.get("score_summary") or "No summary available.")[:120]
        content = Text()
        content.append(f"{job['company']}", style="dim")
        content.append(f"\n\n{summary}\n\n", style="white")
        content.append(job["url"], style="dim underline")

        console.print(
            Panel(
                content,
                title=f"[bold]#{job['id']}  {job['title']}[/bold]",
                title_align="left",
                border_style="dim",
                padding=(1, 2),
            )
        )
        console.print()


@app.command()
def inspect(
    job_id: int = typer.Argument(..., help="Job ID to inspect"),
):
    """Show full details of a job, including Gemini's verdict."""
    try:
        response = httpx.get(f"{API_BASE}/jobs/{job_id}")
        if response.status_code == 404:
            console.print(f"[red]Job {job_id} not found.[/red]")
            raise typer.Exit(1)
        response.raise_for_status()
        job = response.json()
    except httpx.ConnectError:
        console.print("[red]API is not running.[/red]")
        raise typer.Exit(1)

    score = job.get("score")
    score_color = (
        "green" if score and score >= 7 else "yellow" if score and score >= 4 else "red"
    )

    # Header Info
    header = Panel(
        Group(
            Text(job["title"], style="bold white"),
            Text(f"{job['company']} • {job.get('location') or 'N/A'}", style="dim"),
            Text(job["url"], style="cyan underline"),
        ),
        title=f"Detailed Report #{job_id}",
        border_style=score_color,
    )
    console.print(header)

    # Scoring Info
    if score is not None:
        summary_text = job.get("score_summary") or "No summary available."
        reasoning = job.get("score_reasoning") or "No detailed reasoning."

        score_panel = Panel(
            Group(
                Text(f"Score: {score:.1f}/10", style=f"bold {score_color}"),
                Text(f"\n[italic]{summary_text}[/italic]\n"),
                Text(reasoning, style="dim"),
            ),
            title="AI Verdict",
            border_style=score_color,
        )

        # Flags
        red_flags = job.get("red_flags") or []
        green_flags = job.get("green_flags") or []

        flags_table = Table.grid(expand=True, padding=(0, 2))
        flags_table.add_column()
        flags_table.add_column()

        red_text = Text()
        for flag in red_flags:
            red_text.append(f"🚩 {flag}\n", style="red")

        green_text = Text()
        for flag in green_flags:
            green_text.append(f"✅ {flag}\n", style="green")

        flags_table.add_row(
            Panel(
                red_text or "[dim]None detected[/dim]",
                title="Red Flags",
                border_style="red",
            ),
            Panel(
                green_text or "[dim]None detected[/dim]",
                title="Green Flags",
                border_style="green",
            ),
        )

        console.print(score_panel)
        console.print(flags_table)
    else:
        console.print("\n[yellow]This job hasn't been scored by Gemini yet.[/yellow]\n")

    console.print()


@app.command()
def apply(
    job_id: int = typer.Argument(..., help="Job ID to mark as applied"),
):
    """Mark a job as applied. Optimistic of you."""
    try:
        response = httpx.patch(
            f"{API_BASE}/jobs/{job_id}/status", json={"status": "applied"}
        )
        response.raise_for_status()
        console.print(
            f"[green]Job {job_id} marked as applied. Good luck. You'll need it.[/green]"
        )
    except httpx.ConnectError:
        console.print("[red]API is not running.[/red]")
        raise typer.Exit(1)


@app.command()
def ignore(
    job_id: int = typer.Argument(..., help="Job ID to ignore"),
):
    """Mark a job as ignored. Sometimes that's the right call."""
    try:
        response = httpx.patch(
            f"{API_BASE}/jobs/{job_id}/status", json={"status": "ignored"}
        )
        response.raise_for_status()
        console.print(f"[yellow]Job {job_id} ignored. Probably for the best.[/yellow]")
    except httpx.ConnectError:
        console.print("[red]API is not running.[/red]")
        raise typer.Exit(1)


@app.command()
def clear(
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation"),
):
    """Delete all saved jobs. Nuclear option."""
    if not force:
        confirm = typer.confirm("This will delete ALL jobs. Are you sure?")
        if not confirm:
            console.print("[yellow]Aborted. Smart choice.[/yellow]")
            raise typer.Exit(0)

    try:
        response = httpx.delete(f"{API_BASE}/jobs/")
        response.raise_for_status()
        result = response.json()
        console.print(f"[red]{result['message']}[/red]")
    except httpx.ConnectError:
        console.print("[red]API is not running.[/red]")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
