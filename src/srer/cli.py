import typer

cli = typer.Typer()

@cli.command()
def health() -> None:
    """Health check command."""

    typer.echo("ok")

@cli.command()
def download_repeat_photography() -> None:
    """Download Repeat Photography images."""

    typer.echo("Downloading Repeat Photography images...")

if __name__ == "__main__":
    cli()