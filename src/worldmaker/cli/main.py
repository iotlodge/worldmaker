"""WorldMaker CLI — command-line interface for ecosystem management."""
from __future__ import annotations
import json
import sys
import logging

try:
    import click
    HAS_CLICK = True
except ImportError:
    HAS_CLICK = False


if HAS_CLICK:

    @click.group()
    @click.option("--verbose", "-v", is_flag=True, help="Enable verbose logging")
    def cli(verbose: bool) -> None:
        """WorldMaker — Sustained Enterprise Digital Lifecycle Management"""
        level = logging.DEBUG if verbose else logging.INFO
        logging.basicConfig(
            level=level,
            format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        )

    @cli.command()
    @click.option("--seed", default=42, help="Random seed for reproducibility")
    @click.option(
        "--size",
        default="small",
        type=click.Choice(["small", "medium", "large"]),
        help="Ecosystem size"
    )
    @click.option("--output", "-o", default=None, help="Output file path (default: stdout)")
    @click.option(
        "--format",
        "fmt",
        default="json",
        type=click.Choice(["json", "summary"]),
        help="Output format"
    )
    def generate(seed: int, size: str, output: str | None, fmt: str) -> None:
        """Generate a synthetic enterprise ecosystem."""
        try:
            from ..generators.ecosystem import generate_ecosystem
        except ImportError:
            click.echo("Error: ecosystem generator not available")
            sys.exit(1)

        click.echo(f"Generating {size} ecosystem with seed={seed}...")
        ecosystem = generate_ecosystem(seed=seed, size=size)

        if fmt == "summary":
            summary = ecosystem.get("summary", {})
            click.echo("\n=== Ecosystem Summary ===")
            for key, value in summary.items():
                click.echo(f"  {key}: {value}")
            total = sum(summary.values()) if summary else 0
            click.echo(f"\n  Total entities: {total}")
        else:
            result = json.dumps(ecosystem, indent=2, default=str)
            if output:
                with open(output, "w") as f:
                    f.write(result)
                click.echo(f"Ecosystem written to {output}")
            else:
                click.echo(result)

    @cli.command()
    @click.option("--host", default="0.0.0.0", help="API host")
    @click.option("--port", default=8000, help="API port")
    @click.option("--reload", "do_reload", is_flag=True, help="Enable auto-reload")
    def serve(host: str, port: int, do_reload: bool) -> None:
        """Start the WorldMaker API server."""
        try:
            import uvicorn
        except ImportError:
            click.echo("Error: uvicorn not installed")
            click.echo("Install with: pip install uvicorn")
            sys.exit(1)

        try:
            from ..api.app import create_app
        except ImportError:
            click.echo("Error: fastapi not installed")
            click.echo("Install with: pip install fastapi")
            sys.exit(1)

        click.echo(f"Starting WorldMaker API on {host}:{port}...")
        if do_reload:
            # IMPORTANT: Only watch the src/ tree for reloads.
            # The default watches the entire cwd, which includes repos/
            # and logs/. When code scaffolding writes files to repos/,
            # uvicorn detects the change and restarts — wiping the
            # in-memory store and all generated data.
            import pathlib
            src_dir = str(pathlib.Path(__file__).resolve().parents[2])  # src/worldmaker/../../ => src/
            uvicorn.run(
                "worldmaker.api.app:app",
                host=host,
                port=port,
                reload=True,
                reload_dirs=[src_dir],
            )
        else:
            from ..api.app import create_app
            app = create_app()
            uvicorn.run(app, host=host, port=port)

    @cli.command()
    def info() -> None:
        """Show WorldMaker system information."""
        from .. import __version__

        click.echo(f"WorldMaker v{__version__}")
        click.echo(f"Python: {sys.version}")

        # Check available backends
        backends = {}
        for pkg in ["fastapi", "sqlalchemy", "motor", "neo4j", "celery", "aiokafka", "click"]:
            try:
                __import__(pkg)
                backends[pkg] = "installed"
            except ImportError:
                backends[pkg] = "not installed"

        click.echo("\nBackends:")
        for pkg, status in sorted(backends.items()):
            icon = "✓" if status == "installed" else "✗"
            click.echo(f"  {icon} {pkg}: {status}")

else:
    # Fallback if click is not installed

    def cli() -> None:
        """Fallback CLI when click is not installed."""
        print("WorldMaker CLI requires 'click' package.")
        print("Install with: pip install click")
        sys.exit(1)


if __name__ == "__main__":
    cli()
