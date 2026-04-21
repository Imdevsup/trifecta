"""
Curriculum Test — final elimination exam (runs on the last day of the simulation).
Generates 30 questions (10 impulse, 10 deep, 10 axiom) from the accumulated curriculum.
Tests each agent SEPARATELY with their learned knowledge, then runs a solo baseline
(same model, no knowledge, no persona) as the control group.
"""

import logging
import time

from rich.console import Console
from rich.table import Table
from rich.panel import Panel

import config
from simulation.evaluator import Evaluator

logger = logging.getLogger(__name__)
console = Console()


class CurriculumTest:
    """Runs the final curriculum test: each agent individually + solo baseline."""

    def __init__(self, db_logger=None, rng=None):
        self.db_logger = db_logger
        self.rng = rng
        self.evaluator = Evaluator(db_logger=db_logger)

    def run_full_comparison(self, agents: dict, topics_covered: list[str], day: int) -> dict:
        """
        Generate 30 curriculum questions, test each agent individually with knowledge,
        then test a solo baseline (no knowledge, no persona).
        Returns results dict with per-agent scores and baseline.
        """
        # Step 1: Generate 30 questions
        console.print("[dim]Generating 30 curriculum-aligned test questions...[/dim]")
        questions = self.evaluator.generate_questions(topics_covered, rng=self.rng)
        console.print(f"[green]Generated {len(questions)} questions "
                      f"(10 impulse, 10 deep, 10 axiom)[/green]")

        for q in questions[:3]:
            console.print(f"  [dim]Q{q['number']} ({q['type']}): {q['question'][:100]}...[/dim]")
        if len(questions) > 3:
            console.print(f"  [dim]... and {len(questions) - 3} more[/dim]")

        all_results = {}

        # Step 2: Test each agent individually WITH their learned knowledge
        console.print(Panel(
            "[bold cyan]PHASE 1: Individual Agent Tests (with knowledge)[/bold cyan]\n"
            "Each agent answers all 30 questions using their own knowledge stores",
            border_style="cyan",
        ))

        for agent_name, agent in agents.items():
            console.print(f"\n  [bold]Testing {agent_name.upper()}...[/bold]")
            result = self._test_agent(agent, questions, day, use_knowledge=True)
            all_results[agent_name] = result
            self._print_agent_result(agent_name, result)

        # Step 3: Solo baseline — same model, no knowledge, no persona
        console.print(Panel(
            "[bold yellow]PHASE 2: Solo Baseline (control group)[/bold yellow]\n"
            "Same model, same questions, NO knowledge stores, NO agent persona",
            border_style="yellow",
        ))
        baseline_result = self._run_solo_baseline(agents, questions, day)
        all_results["solo_baseline"] = baseline_result
        self._print_agent_result("solo_baseline", baseline_result)

        # Step 4: Print comparison table
        self._print_comparison(all_results, day)

        return all_results

    def _test_agent(self, agent, questions: list[dict], day: int,
                    use_knowledge: bool = True) -> dict:
        """Test a single agent on all questions. Returns scores breakdown."""
        scores = []
        by_type = {"impulse": [], "deep": [], "axiom": []}

        for i, q in enumerate(questions):
            answer = agent.answer_test_question(
                question=q["question"], question_type=q["type"],
                day=day, use_knowledge=use_knowledge,
            )

            score, reasoning = self.evaluator.score_answer(
                question=q["question"], answer=answer,
                q_type=q["type"], topic=q["topic"],
            )

            entry = {
                "question_number": q["number"],
                "question_type": q["type"],
                "topic": q["topic"],
                "question": q["question"],
                "answer": answer,
                "score": score,
                "reasoning": reasoning,
            }
            scores.append(entry)
            by_type[q["type"]].append(score)

            if self.db_logger:
                self.db_logger.log_test_result(
                    agent=agent.name,
                    question_number=q["number"],
                    question_type=q["type"],
                    question=q["question"],
                    answer=answer,
                    score=score,
                    score_reasoning=reasoning,
                )

            console.print(f"    Q{q['number']} ({q['type']}): {score:.0f}/10")

        total = sum(s["score"] for s in scores)
        max_score = len(questions) * 10
        pct = total / max_score if max_score > 0 else 0

        type_avgs = {}
        for qtype, type_scores in by_type.items():
            type_avgs[qtype] = sum(type_scores) / len(type_scores) if type_scores else 0

        return {
            "scores": scores,
            "total_score": total,
            "max_score": max_score,
            "percentage": pct,
            "survived": pct >= config.PASS_THRESHOLD,
            "by_type": type_avgs,
        }

    def _run_solo_baseline(self, agents: dict, questions: list[dict], day: int) -> dict:
        """Solo baseline: use any agent's model but strip all knowledge and persona."""
        solo_agent = list(agents.values())[0]

        scores = []
        by_type = {"impulse": [], "deep": [], "axiom": []}

        for i, q in enumerate(questions):
            # Answer with NO knowledge injection
            answer = solo_agent.answer_test_question(
                question=q["question"], question_type=q["type"],
                day=day, use_knowledge=False,
            )

            score, reasoning = self.evaluator.score_answer(
                question=q["question"], answer=answer,
                q_type=q["type"], topic=q["topic"],
            )

            entry = {
                "question_number": q["number"],
                "question_type": q["type"],
                "topic": q["topic"],
                "question": q["question"],
                "answer": answer,
                "score": score,
                "reasoning": reasoning,
            }
            scores.append(entry)
            by_type[q["type"]].append(score)

            if self.db_logger:
                self.db_logger.log_test_result(
                    agent="solo_baseline",
                    question_number=q["number"],
                    question_type=q["type"],
                    question=q["question"],
                    answer=answer,
                    score=score,
                    score_reasoning=reasoning,
                )

            console.print(f"    Q{q['number']} ({q['type']}): {score:.0f}/10")

        total = sum(s["score"] for s in scores)
        max_score = len(questions) * 10
        pct = total / max_score if max_score > 0 else 0

        type_avgs = {}
        for qtype, type_scores in by_type.items():
            type_avgs[qtype] = sum(type_scores) / len(type_scores) if type_scores else 0

        return {
            "scores": scores,
            "total_score": total,
            "max_score": max_score,
            "percentage": pct,
            "survived": pct >= config.PASS_THRESHOLD,
            "by_type": type_avgs,
        }

    def _print_agent_result(self, name: str, result: dict):
        pct = result["percentage"] * 100
        status = "[green]SURVIVED[/green]" if result["survived"] else "[red]ELIMINATED[/red]"
        type_str = " | ".join(
            f"{t}={avg:.1f}/10" for t, avg in result.get("by_type", {}).items()
        )
        console.print(
            f"  {name.upper()}: {result['total_score']:.0f}/{result['max_score']} "
            f"({pct:.1f}%) [{status}] | {type_str}"
        )

    def _print_comparison(self, all_results: dict, day: int):
        """Print the final comparison table."""
        console.print("\n")

        table = Table(title=f"DAY {day} FINAL TEST RESULTS", show_header=True)
        table.add_column("Agent", style="bold")
        table.add_column("Total", justify="right")
        table.add_column("%", justify="right")
        table.add_column("Impulse", justify="right")
        table.add_column("Deep", justify="right")
        table.add_column("Axiom", justify="right")
        table.add_column("Status", justify="center")

        baseline_pct = 0
        for agent_name in all_results:
            r = all_results[agent_name]
            pct = r["percentage"] * 100
            status = "[green]PASS[/green]" if r["survived"] else "[red]FAIL[/red]"
            types = r.get("by_type", {})
            if agent_name == "solo_baseline":
                baseline_pct = pct
            table.add_row(
                agent_name.upper(),
                f"{r['total_score']:.0f}/{r['max_score']}",
                f"{pct:.1f}%",
                f"{types.get('impulse', 0):.1f}",
                f"{types.get('deep', 0):.1f}",
                f"{types.get('axiom', 0):.1f}",
                status,
            )

        console.print(table)

        # Print deltas vs baseline
        if baseline_pct > 0:
            console.print("\n[bold]Delta vs Solo Baseline:[/bold]")
            for agent_name in all_results:
                if agent_name == "solo_baseline":
                    continue
                r = all_results[agent_name]
                agent_pct = r["percentage"] * 100
                diff = agent_pct - baseline_pct
                color = "green" if diff > 0 else ("red" if diff < 0 else "white")
                console.print(f"  {agent_name.upper()}: [{color}]{diff:+.1f}%[/{color}]")
