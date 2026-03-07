"""CLI for marpx converter."""

from __future__ import annotations

import logging
import sys

import click
from rich.console import Console
from rich.logging import RichHandler

from marpx import __version__
from marpx.converter import convert, ConversionError

console = Console()


@click.command()
@click.argument("input_file", type=click.Path(exists=True))
@click.option(
    "-o",
    "--output",
    "output_file",
    type=click.Path(),
    default=None,
    help="Output PPTX file path. Defaults to input name with .pptx extension.",
)
@click.option("--theme", default=None, help="Marp theme name or CSS file path.")
@click.option(
    "--fallback-mode",
    type=click.Choice(["subtree", "slide"]),
    default="subtree",
    help="Fallback mode for unsupported content.",
)
@click.option(
    "--prefer-editable",
    is_flag=True,
    default=False,
    help="Maximize editable shapes even for complex content.",
)
@click.option(
    "--keep-temp",
    is_flag=True,
    default=False,
    help="Keep temporary files after conversion.",
)
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    default=False,
    help="Enable verbose logging.",
)
@click.version_option(version=__version__)
def main(
    input_file: str,
    output_file: str | None,
    theme: str | None,
    fallback_mode: str,
    prefer_editable: bool,
    keep_temp: bool,
    verbose: bool,
) -> None:
    """Convert Marp Markdown to editable PPTX.

    INPUT_FILE is the path to a Marp Markdown file.
    """
    # Configure logging
    if verbose:
        logging.basicConfig(
            level=logging.DEBUG,
            format="%(message)s",
            handlers=[RichHandler(console=console, rich_tracebacks=True)],
        )
    else:
        logging.basicConfig(level=logging.WARNING)

    # Default output path
    if output_file is None:
        from pathlib import Path

        output_file = str(Path(input_file).with_suffix(".pptx"))

    # Header
    console.print()
    console.print("[bold blue]marpx[/bold blue]", f"[dim]v{__version__}[/dim]")
    console.print()
    console.print(f"  [dim]Input:[/dim]  [cyan]{input_file}[/cyan]")
    console.print(f"  [dim]Output:[/dim] [cyan]{output_file}[/cyan]")
    console.print()

    try:
        with console.status("[bold blue]Converting...[/bold blue]", spinner="dots"):
            result = convert(
                markdown_path=input_file,
                output_path=output_file,
                theme=theme,
                fallback_mode=fallback_mode,
                prefer_editable=prefer_editable,
                keep_temp=keep_temp,
                verbose=verbose,
            )
        console.print(f"[bold green]✓[/bold green] Done: [cyan]{result}[/cyan]")
        console.print()
    except ConversionError as e:
        console.print(f"[bold red]✗ Error:[/bold red] {e}")
        sys.exit(1)
    except Exception as e:
        console.print(f"[bold red]✗ Unexpected error:[/bold red] {e}")
        if verbose:
            console.print_exception()
        sys.exit(1)
