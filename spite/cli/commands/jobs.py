import httpx
import typer
from rich.console import Group
from rich.panel import Panel
from rich.text import Text

from spite.cli.commands import API_BASE, console


def list_jobs(

    platform: str = typer.Option(None, "--platform", "-p", help="Filter by platform"),
    limit: int = typer.Option(50, "--limit", "-n", help="Max results"),
) -> None:
    """List saved jobs. Sorted by newest first."""
    try:
        params: dict = {"limit": limit}

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


def inspect(
    job_id: int = typer.Argument(..., help="Job ID to inspect"),
) -> None:
    """Show full details of a job, including Groq's verdict."""
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

    console.print(
        Panel(
            Group(
                Text(job["title"], style="bold white"),
                Text(f"{job['company']} • {job.get('location') or 'N/A'}", style="dim"),
                Text(job["url"], style="dim underline"),
            ),
            title=f"Detailed Report #{job_id}",
            border_style="cyan",
        )
    )

    summary_text = job.get("score_summary")
    if summary_text:
        reasoning = job.get("score_reasoning")
        
        info_group = []
        info_group.append(Text(f"{summary_text}\n", style="bold white"))
        
        if reasoning:
            info_group.append(Text(f"{reasoning}\n", style="dim"))
            
        red_flags = job.get("red_flags")
        if red_flags:
            info_group.append(Text("Red Flags:\n", style="bold red"))
            for flag in red_flags:
                info_group.append(Text(f"- {flag}\n", style="red"))
                
        green_flags = job.get("green_flags")
        if green_flags:
            info_group.append(Text("Green Flags:\n", style="bold green"))
            for flag in green_flags:
                info_group.append(Text(f"- {flag}\n", style="green"))

        console.print(
            Panel(
                Group(*info_group),
                title="AI Analysis",
                border_style="cyan",
            )
        )
    else:
        console.print("\n[dim]This job hasn't been analyzed yet.[/dim]\n")

    console.print()


def apply(
    job_id: int = typer.Argument(..., help="Job ID to mark as applied"),
) -> None:
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


def ignore(
    job_id: int = typer.Argument(..., help="Job ID to ignore"),
) -> None:
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


def clear(
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation"),
) -> None:
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
