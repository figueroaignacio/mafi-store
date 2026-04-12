"""
spite cli — your personal weapon against the broken job market.
"""

import typer
from rich.console import Console
from rich.panel import Panel

app = typer.Typer(
    name="spite",
    help="Automated job hunting. Because optimism is for people with trust funds.",
    add_completion=False,
    rich_markup_mode="rich",
)

console = Console()


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context) -> None:
    if ctx.invoked_subcommand is None:
        console.print(
            Panel.fit(
                "[bold red]spite[/bold red] [dim]v0.1.0[/dim]\n"
                "[italic]The job market is broken. This is the patch.[/italic]",
                border_style="red",
            )
        )
        console.print("\nRun [bold]spite --help[/bold] to see available commands.\n")


@app.command()
def version() -> None:
    """Print version and exit. At least something works as expected."""
    from spite import __version__

    console.print(
        f"spite [bold]{__version__}[/bold] — still less broken than the job market."
    )


if __name__ == "__main__":
    app()
