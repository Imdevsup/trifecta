"""
Cognitive Triad Simulation — Entry Point
Runs the multi-day simulation of three AI cognitive units: Alpha, Beta, Gamma.
Topics are generated dynamically per day, rotating across eight PhD-level
domains that LLMs demonstrably struggle with (mathematics, theoretical physics,
formal methods, theoretical CS & cryptography, molecular biology, analytic
philosophy, quantitative finance, theoretical linguistics). Runs can go for
arbitrarily many days.
"""

import argparse
import logging
import os
import random
import sys
from pathlib import Path

os.environ.setdefault("PYTHONIOENCODING", "utf-8")

from dotenv import load_dotenv
from rich.console import Console

import config
from knowledge.store import create_stores_for_agent
from agents.alpha import AlphaAgent
from agents.beta import BetaAgent
from agents.gamma import GammaAgent
from sim_logging.db import DatabaseLogger
from simulation.environment import SimulationEnvironment
from sim_logging.export import export_all

console = Console()
logger = logging.getLogger(__name__)


def parse_args():
    parser = argparse.ArgumentParser(description="Cognitive Triad Simulation (CTS)")
    parser.add_argument("--days", type=int, default=config.DEFAULT_DAYS, help=f"Number of days to simulate (default {config.DEFAULT_DAYS})")
    parser.add_argument("--start-day", type=int, default=1, help="Day to start/resume from (default 1)")
    parser.add_argument("--speed", choices=["normal", "fast"], default="normal", help="Speed mode: 'fast' reduces exchanges")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducibility")
    parser.add_argument("--model-override", type=str, default=None, help="Override all agent models with this model string")
    parser.add_argument("--dry-run", action="store_true", help="Run without making LLM calls (placeholder responses)")
    parser.add_argument("--no-export", action="store_true", help="Skip exporting analysis files after simulation")
    parser.add_argument("--data-dir", type=str, default=None, help="Override data directory path")
    parser.add_argument("--log-level", choices=["DEBUG", "INFO", "WARNING", "ERROR"], default="WARNING", help="Logging level")
    # Ablation flags — disable individual components for testing
    parser.add_argument("--ablation-no-knowledge", action="store_true", help="Ablation: disable knowledge injection")
    parser.add_argument("--ablation-no-peers", action="store_true", help="Ablation: disable peer conversations")
    parser.add_argument("--ablation-no-axioms", action="store_true", help="Ablation: disable axiom validation")
    parser.add_argument("--ablation-no-consolidation", action="store_true", help="Ablation: disable knowledge consolidation")
    parser.add_argument("--ablation-no-sharing", action="store_true", help="Ablation: disable knowledge sharing")
    return parser.parse_args()


def setup_logging(level: str):
    logging.basicConfig(
        level=getattr(logging, level),
        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
        handlers=[
            logging.StreamHandler(sys.stderr),
        ],
    )


def main():
    args = parse_args()
    setup_logging(args.log_level)

    # Load .env file if present
    load_dotenv()

    # Apply configuration overrides
    if args.dry_run:
        config.DRY_RUN = True

    if args.data_dir:
        config.DATA_DIR = Path(args.data_dir)
        config.LOG_DB_PATH = config.DATA_DIR / "simulation.db"
        config.ANALYSIS_DIR = config.DATA_DIR / "analysis"

    # Apply ablation flags
    if args.ablation_no_knowledge:
        config.ABLATION_NO_KNOWLEDGE = True
    if args.ablation_no_peers:
        config.ABLATION_NO_PEER_CONVERSATION = True
    if args.ablation_no_axioms:
        config.ABLATION_NO_AXIOM_VALIDATION = True
    if args.ablation_no_consolidation:
        config.ABLATION_NO_CONSOLIDATION = True
    if args.ablation_no_sharing:
        config.ABLATION_NO_KNOWLEDGE_SHARING = True

    # API keys loaded from .env
    if not config.DRY_RUN:
        # Quick validation that keys are present
        for name, cfg in config.AGENT_CONFIG.items():
            if not cfg.get("api_key"):
                console.print(f"[bold red]Error: No API key configured for {name} in config.py[/bold red]")
                sys.exit(1)

    # Seed RNG
    rng = random.Random(args.seed)

    # Create data directories
    for agent_name in ["alpha", "beta", "gamma"]:
        (config.DATA_DIR / agent_name).mkdir(parents=True, exist_ok=True)
    config.ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)

    # Initialize database logger
    db_logger = DatabaseLogger(config.LOG_DB_PATH)

    # Build agent config (model + api_key per agent)
    agent_configs = {}
    for name, cfg in config.AGENT_CONFIG.items():
        agent_configs[name] = {
            "model": args.model_override if args.model_override else cfg["model"],
            "api_key": cfg["api_key"],
        }

    # Create knowledge stores and agents
    agents = {}
    agent_classes = {
        "alpha": AlphaAgent,
        "beta": BetaAgent,
        "gamma": GammaAgent,
    }

    for agent_name, agent_cls in agent_classes.items():
        stores = create_stores_for_agent(agent_name, rng, db_logger)
        acfg = agent_configs[agent_name]
        agent = agent_cls(
            name=agent_name,
            model=acfg["model"],
            api_key=acfg["api_key"],
            stores=stores,
            rng=rng,
            db_logger=db_logger,
        )
        if args.start_day > 1:
            agent.load()
        agents[agent_name] = agent

    # Initialize simulation environment
    env = SimulationEnvironment(
        agents=agents,
        rng=rng,
        db_logger=db_logger,
    )

    # Run
    model_display = {n: c["model"] for n, c in agent_configs.items()}
    console.print(f"\n[bold]Configuration:[/bold]")
    console.print(f"  Days: {args.days}")
    console.print(f"  Speed: {args.speed}")
    console.print(f"  Seed: {args.seed}")
    console.print(f"  Models: {model_display}")
    console.print(f"  Dry run: {config.DRY_RUN}")
    console.print(f"  Data dir: {config.DATA_DIR}")
    console.print(f"  Max retries per call: {config.MAX_RETRIES}")
    console.print()

    try:
        env.run_simulation(
            num_days=args.days,
            speed_fast=(args.speed == "fast"),
            start_day=args.start_day,
        )
    except KeyboardInterrupt:
        console.print("\n[yellow]Simulation interrupted by user.[/yellow]")
    finally:
        # Always persist and export
        for agent in agents.values():
            agent.persist()

        if not args.no_export:
            try:
                export_all(db_logger, config.ANALYSIS_DIR, agents)
                console.print(f"\n[green]Analysis exported to {config.ANALYSIS_DIR}/[/green]")
            except Exception as e:
                console.print(f"[yellow]Warning: Export failed: {e}[/yellow]")

        db_logger.close()
        console.print(f"[dim]Database saved to {config.LOG_DB_PATH}[/dim]")


if __name__ == "__main__":
    main()
