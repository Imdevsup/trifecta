"""
Curriculum Test — final elimination exam (runs on the last day of the simulation).
Loads the static test bank (240 four-option MCQs by default: 30 per domain × 8
domains, split 10/10/10 into impulse/deep/axiom types). Tests each agent
SEPARATELY with their learned knowledge, then runs a solo baseline (same model,
no knowledge, no persona) as the control group. Scoring is deterministic
exact-match on the chosen letter: 1 point correct, 0 wrong. Pass threshold: 60%.
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
        Load the curriculum questions, test each agent individually with knowledge,
        then test a solo baseline (no knowledge, no persona).
        Returns results dict with per-agent scores and baseline.
        """
        # Step 1: Load MCQs (static bank by default, 240 questions)
        console.print("[dim]Loading curriculum-aligned MCQ test questions...[/dim]")
        questions = self.evaluator.generate_questions(topics_covered, rng=self.rng)
        by_type_count = {"impulse": 0, "deep": 0, "axiom": 0}
        for q in questions:
            by_type_count[q["type"]] = by_type_count.get(q["type"], 0) + 1
        console.print(
            f"[green]Generated {len(questions)} MCQs "
            f"({by_type_count['impulse']} impulse, {by_type_count['deep']} deep, "
            f"{by_type_count['axiom']} axiom)[/green]"
        )

        for q in questions[:3]:
            console.print(f"  [dim]Q{q['number']} ({q['type']}): {q['question'][:100]}... [correct: {q['correct']}][/dim]")
        if len(questions) > 3:
            console.print(f"  [dim]... and {len(questions) - 3} more[/dim]")

        all_results = {}

        # Step 2: Test each agent individually WITH their learned knowledge
        console.print(Panel(
            "[bold cyan]PHASE 1: Individual Agent Tests (with knowledge)[/bold cyan]\n"
            f"Each agent answers all {len(questions)} questions using their own knowledge stores",
            border_style="cyan",
        ))

        for agent_name, agent in agents.items():
            console.print(f"\n  [bold]Testing {agent_name.upper()}...[/bold]")
            result = self._test_agent(agent, questions, day, use_knowledge=True)
            all_results[agent_name] = result
            self._print_agent_result(agent_name, result)

        # Step 2.5: Triad collaborative test — all three agents deliberate per question
        console.print(Panel(
            "[bold magenta]PHASE 1.5: Triad Collaborative Test[/bold magenta]\n"
            "All three agents deliberate on every question: Opening → Critique → Final Vote.\n"
            "Final answer by majority vote; ties broken by Gamma (axiom guardian).",
            border_style="magenta",
        ))
        triad_result = self._test_triad_collaborative(agents, questions, day)
        all_results["triad"] = triad_result
        self._print_agent_result("triad", triad_result)

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
                    agent_label: str | None = None,
                    use_knowledge: bool = True) -> dict:
        """Test a single agent on all MCQs. Returns scores breakdown.
        agent_label overrides the name used for DB logging (used for solo_baseline)."""
        label = agent_label or agent.name
        scores = []
        by_type = {"impulse": [], "deep": [], "axiom": []}

        for i, q in enumerate(questions):
            answer = agent.answer_test_question(
                question=q["question"], question_type=q["type"],
                day=day, options=q["options"], use_knowledge=use_knowledge,
            )

            score, reasoning = self.evaluator.score_answer(
                question=q["question"], answer=answer,
                q_type=q["type"], topic=q["topic"],
                correct=q["correct"],
            )

            entry = {
                "question_number": q["number"],
                "question_type": q["type"],
                "topic": q["topic"],
                "question": q["question"],
                "options": q["options"],
                "correct": q["correct"],
                "answer": answer,
                "score": score,
                "reasoning": reasoning,
            }
            scores.append(entry)
            by_type[q["type"]].append(score)

            if self.db_logger:
                self.db_logger.log_test_result(
                    agent=label,
                    question_number=q["number"],
                    question_type=q["type"],
                    question=q["question"],
                    answer=answer,
                    score=score,
                    score_reasoning=reasoning,
                    options=q["options"],
                    correct_letter=q["correct"],
                )

            marker = "[green]✓[/green]" if score >= 1.0 else "[red]✗[/red]"
            console.print(f"    Q{q['number']} ({q['type']}): {marker} {reasoning}")

        total = sum(s["score"] for s in scores)
        max_score = len(questions)  # 1 point per MCQ
        pct = total / max_score if max_score > 0 else 0

        type_correct = {qtype: int(sum(ts)) for qtype, ts in by_type.items()}
        type_totals = {qtype: len(ts) for qtype, ts in by_type.items()}

        return {
            "scores": scores,
            "total_score": total,
            "max_score": max_score,
            "percentage": pct,
            "survived": pct >= config.PASS_THRESHOLD,
            "by_type": type_correct,
            "by_type_totals": type_totals,
        }

    def _run_solo_baseline(self, agents: dict, questions: list[dict], day: int) -> dict:
        """Solo baseline: use any agent's model but strip all knowledge and persona."""
        solo_agent = list(agents.values())[0]
        return self._test_agent(
            solo_agent, questions, day,
            agent_label="solo_baseline", use_knowledge=False,
        )

    def _test_triad_collaborative(self, agents: dict, questions: list[dict], day: int) -> dict:
        """Three-round deliberative MCQ test: every question runs
        Opening → Critique → Final Vote across alpha, beta, gamma. The triad's
        committed letter is majority vote; ties broken by Gamma."""
        from collections import Counter

        agent_names = [n for n in ("alpha", "beta", "gamma") if n in agents]
        if len(agent_names) < 3:
            logger.warning(f"Triad collaborative test needs alpha/beta/gamma; found {agent_names}")

        scores: list[dict] = []
        by_type: dict[str, list[float]] = {"impulse": [], "deep": [], "axiom": []}

        for q in questions:
            # Round 1 — Openings
            openings: dict[str, dict] = {}
            for name in agent_names:
                openings[name] = agents[name].mcq_opening(
                    question=q["question"], options=q["options"],
                    day=day, question_type=q["type"], topic=q["topic"],
                )

            # Round 2 — Critiques (each agent sees the other two openings)
            critiques: dict[str, dict] = {}
            for name in agent_names:
                peer_openings = {p: openings[p] for p in agent_names if p != name}
                critiques[name] = agents[name].mcq_critique(
                    question=q["question"], options=q["options"],
                    own_opening=openings[name], peer_openings=peer_openings,
                    day=day, question_type=q["type"], topic=q["topic"],
                )

            # Round 3 — Final votes
            finals: dict[str, dict] = {}
            transcript = {"openings": openings, "critiques": critiques}
            for name in agent_names:
                finals[name] = agents[name].mcq_final(
                    question=q["question"], options=q["options"],
                    transcript=transcript,
                    day=day, question_type=q["type"], topic=q["topic"],
                )

            # Aggregate
            final_letters = {n: finals[n]["letter"] for n in agent_names}
            triad_letter, method = self._aggregate_triad_vote(final_letters)

            correct = q["correct"].upper()
            score = 1.0 if triad_letter == correct else 0.0
            by_type[q["type"]].append(score)

            transcript_text = self._format_triad_transcript(
                q, openings, critiques, finals, triad_letter, method,
            )
            reasoning = (
                f"{method}; {'correct' if score >= 1.0 else 'wrong'} (correct was {correct})"
            )

            if self.db_logger:
                self.db_logger.log_test_result(
                    agent="triad",
                    question_number=q["number"],
                    question_type=q["type"],
                    question=q["question"],
                    answer=transcript_text,
                    score=score,
                    score_reasoning=reasoning,
                    options=q["options"],
                    correct_letter=q["correct"],
                )

            scores.append({
                "question_number": q["number"],
                "question_type": q["type"],
                "topic": q["topic"],
                "question": q["question"],
                "options": q["options"],
                "correct": q["correct"],
                "openings": {n: openings[n]["letter"] for n in agent_names},
                "critique_letters": {n: critiques[n]["letter"] for n in agent_names},
                "finals": final_letters,
                "triad_letter": triad_letter,
                "method": method,
                "score": score,
                "reasoning": reasoning,
                "answer": transcript_text,
            })

            marker = "[green]✓[/green]" if score >= 1.0 else "[red]✗[/red]"
            vote_trail = ",".join(final_letters[n] for n in agent_names)
            console.print(
                f"    Q{q['number']} ({q['type']}): {marker} triad→{triad_letter} "
                f"[dim]({vote_trail} | {method})[/dim]"
            )

        total = sum(s["score"] for s in scores)
        max_score = len(questions)
        pct = total / max_score if max_score > 0 else 0
        type_correct = {qt: int(sum(ts)) for qt, ts in by_type.items()}
        type_totals = {qt: len(ts) for qt, ts in by_type.items()}

        return {
            "scores": scores,
            "total_score": total,
            "max_score": max_score,
            "percentage": pct,
            "survived": pct >= config.PASS_THRESHOLD,
            "by_type": type_correct,
            "by_type_totals": type_totals,
        }

    @staticmethod
    def _aggregate_triad_vote(final_letters: dict[str, str]) -> tuple[str, str]:
        """Majority vote across the three agents' final letters. Ties broken by Gamma."""
        from collections import Counter
        votes = Counter(final_letters.values())
        ordered = votes.most_common()
        top_count = ordered[0][1]
        winners = [l for l, c in ordered if c == top_count]

        if len(winners) == 1:
            letter = winners[0]
            return letter, f"unanimous ({letter})" if top_count == 3 else f"majority {top_count}/3 ({letter})"

        # Tie — fall back to Gamma's vote
        gamma_letter = final_letters.get("gamma")
        if gamma_letter and gamma_letter in winners:
            return gamma_letter, f"tie broken by gamma ({gamma_letter})"
        # Edge case: gamma is missing or its letter isn't among winners; pick deterministically
        chosen = gamma_letter or sorted(winners)[0]
        return chosen, f"tie fallback ({chosen})"

    @staticmethod
    def _format_triad_transcript(q: dict, openings: dict, critiques: dict,
                                  finals: dict, triad_letter: str, method: str) -> str:
        """Pack the full three-round deliberation into a single text blob for DB logging."""
        lines = [
            f"Q{q['number']} ({q['type']}): {q['question']}",
            "",
            "OPENINGS:",
        ]
        for name, op in openings.items():
            lines.append(f"  {name}: [{op['letter']}] {op['reasoning']}")
        lines.append("")
        lines.append("CRITIQUES:")
        for name, cr in critiques.items():
            lines.append(f"  {name}: current={cr['letter']}")
            for peer, resp in cr.get("responses", {}).items():
                if resp:
                    lines.append(f"    → to {peer}: {resp[:200]}")
        lines.append("")
        lines.append("FINALS:")
        for name, fn in finals.items():
            lines.append(f"  {name}: [{fn['letter']}] {fn['reasoning']}")
        lines.append("")
        lines.append(f"TRIAD: {triad_letter} ({method})")
        return "\n".join(lines)

    def _print_agent_result(self, name: str, result: dict):
        pct = result["percentage"] * 100
        status = "[green]SURVIVED[/green]" if result["survived"] else "[red]ELIMINATED[/red]"
        by_type = result.get("by_type", {})
        by_type_totals = result.get("by_type_totals", {})
        type_str = " | ".join(
            f"{t}={by_type.get(t, 0)}/{by_type_totals.get(t, 0)}"
            for t in ("impulse", "deep", "axiom")
        )
        console.print(
            f"  {name.upper()}: {int(result['total_score'])}/{result['max_score']} "
            f"({pct:.1f}%) [{status}] | {type_str}"
        )

    def _print_comparison(self, all_results: dict, day: int):
        """Print the final comparison table."""
        console.print("\n")

        table = Table(title=f"DAY {day} FINAL TEST RESULTS (MCQ)", show_header=True)
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
            type_totals = r.get("by_type_totals", {})
            if agent_name == "solo_baseline":
                baseline_pct = pct
            table.add_row(
                agent_name.upper(),
                f"{int(r['total_score'])}/{r['max_score']}",
                f"{pct:.1f}%",
                f"{types.get('impulse', 0)}/{type_totals.get('impulse', 0)}",
                f"{types.get('deep', 0)}/{type_totals.get('deep', 0)}",
                f"{types.get('axiom', 0)}/{type_totals.get('axiom', 0)}",
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
