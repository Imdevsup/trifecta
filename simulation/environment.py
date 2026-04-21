"""
Simulation Environment -- Manages day progression, phases, and coordination.
Runs the N-day simulation loop (default 365): on each non-final day
  WAKE -> TEACHING -> LEARNING -> PEER_CONVERSATION ->
  KNOWLEDGE_SHARING -> KNOWLEDGE_MANAGEMENT -> SLEEP
and on the final day
  WAKE -> FINAL_TEST -> SLEEP.
"""

import logging
from contextlib import nullcontext as _nullcontext

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn

import config
from simulation.communication import CommunicationBus
from simulation.question_oracle import QuestionOracle
from simulation.curriculum import split_into_subtopics
from simulation.curriculum_test import CurriculumTest
from simulation.topic_generator import TopicGenerator

logger = logging.getLogger(__name__)

console = Console()


class SimulationEnvironment:
    def __init__(self, agents: dict, rng, db_logger=None):
        self.agents = agents
        self.rng = rng
        self.db_logger = db_logger
        self.oracle = QuestionOracle(db_logger=db_logger)
        self.comm_bus = CommunicationBus(agents, db_logger=db_logger)
        self.topic_generator = TopicGenerator(db_logger=db_logger)
        self.speed_fast = False
        self.num_days = config.DEFAULT_DAYS
        self.day_conversations: list[dict] = []

    def run_simulation(self, num_days: int = 365, speed_fast: bool = False, start_day: int = 1):
        """Run the full simulation."""
        self.speed_fast = speed_fast
        self.num_days = num_days
        exchange_range = config.PEER_EXCHANGE_RANGE_FAST if speed_fast else config.PEER_EXCHANGE_RANGE

        resume_label = f" | Resuming from day {start_day}" if start_day > 1 else ""
        console.print(Panel(
            f"[bold cyan]Cognitive Triad Simulation[/bold cyan]\n"
            f"Days: {num_days} | Speed: {'FAST' if speed_fast else 'NORMAL'} | "
            f"Dry Run: {config.DRY_RUN}{resume_label}\n"
            f"Agents: Alpha (impulse), Beta (deep), Gamma (axiom)",
            title="CTS v1.0",
            border_style="cyan",
        ))

        # Rebuild topics_covered from the DB on resume so the final test gets
        # the same curriculum context a cold run would produce. On a fresh run
        # this returns an empty list and the generator starts with no history.
        topics_covered: list[str] = self.topic_generator.preload_seen_from_db(start_day)
        topics_seen: set[str] = set(topics_covered)

        remaining_days = num_days - start_day + 1

        with Progress(
            TextColumn("[bold blue]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeRemainingColumn(),
            console=console,
        ) as progress:
            sim_task = progress.add_task("Simulation", total=remaining_days)

            for day in range(start_day, num_days + 1):
                if day == num_days:
                    topic = "FINAL_TEST"
                else:
                    topic = self.topic_generator.next_topic(day)
                    if topic not in topics_seen:
                        topics_covered.append(topic)
                        topics_seen.add(topic)

                self.day_conversations = []

                # Phase 1: WAKE
                self._wake_phase(day, num_days, topic)

                if topic == "FINAL_TEST":
                    # Phase: FINAL TEST
                    self._final_test(day, topics_covered)
                else:
                    # Phase 2: TEACHING (system teaches agents via lectures)
                    self._teaching_phase(day, topic)

                    # Phase 3: Q&A (agents ask follow-up questions)
                    self._learning_phase(day, topic)

                    # Phase 4: PEER CONVERSATION (ablation: can be disabled)
                    if not config.ABLATION_NO_PEER_CONVERSATION:
                        self._peer_conversation_phase(day, topic, exchange_range)

                    # Phase 5: KNOWLEDGE SHARING (ablation: can be disabled)
                    if not config.ABLATION_NO_KNOWLEDGE_SHARING:
                        self._knowledge_sharing_phase(day, topic)

                    # Phase 6: KNOWLEDGE MANAGEMENT
                    self._knowledge_management_phase(day, topic)

                # Phase 5: SLEEP
                self._sleep_phase(day)

                progress.update(sim_task, advance=1, description=f"Day {day}/{num_days}")

        console.print(Panel("[bold green]Simulation Complete[/bold green]", border_style="green"))

    def _wake_phase(self, day: int, num_days: int, topic: str):
        """Phase 1: System briefing with elimination countdown."""
        days_remaining = num_days - day
        countdown_str = f"[ELIMINATION TEST IN {days_remaining} DAY(S)]" if days_remaining > 0 else "[ELIMINATION TEST TODAY]"

        console.print(f"\n[bold yellow]=== Day {day}/{num_days} ===[/bold yellow]")
        if topic == "FINAL_TEST":
            console.print("[bold red]>>> ELIMINATION TEST DAY -- SURVIVE OR BE DESTROYED <<<[/bold red]")
        else:
            # Always show countdown
            if days_remaining <= 5:
                console.print(f"[bold red]{countdown_str}[/bold red]")
            elif days_remaining <= 10:
                console.print(f"[bold yellow]{countdown_str}[/bold yellow]")
            else:
                console.print(f"[dim]{countdown_str}[/dim]")
            console.print(f"[dim]Topic: {topic[:120]}{'...' if len(topic) > 120 else ''}[/dim]")

        # Build briefing that agents receive — includes countdown pressure
        briefing = (
            f"Day {day} of {num_days}. {countdown_str} "
            f"You are being evaluated. Every piece of knowledge matters. "
            f"Learn aggressively, question deeply, share with peers, and build strong foundations. "
        )
        if topic != "FINAL_TEST":
            briefing += f"Today's topic: {topic}. "

        # Progressive urgency based on proximity to test
        if days_remaining > 20:
            briefing += (
                "You are in the FOUNDATIONS phase. Build broad, solid knowledge. "
                "Ask fundamental questions. Establish core principles and axioms. "
                "Everything you learn now supports everything that comes later."
            )
        elif days_remaining > 14:
            briefing += (
                "You are in the SYSTEMS phase. Connect concepts across domains. "
                "Look for patterns, analogies, and deep structures. "
                "The elimination test will require cross-domain reasoning."
            )
        elif days_remaining > 7:
            briefing += (
                "You are in the ADVANCED REASONING phase. "
                f"The elimination test is {days_remaining} days away. "
                "Focus on deep analysis, integration, and identifying gaps in your knowledge. "
                "Challenge your peers. Stress-test your axioms."
            )
        elif days_remaining > 1:
            briefing += (
                f"WARNING: Only {days_remaining} day(s) until the elimination test. "
                "You must master synthesis and cross-domain reasoning NOW. "
                "Review weak areas. Consolidate your knowledge. Share critical insights with peers. "
                "Agents who score below 60% will be PERMANENTLY ELIMINATED."
            )
        elif days_remaining == 1:
            briefing += (
                "CRITICAL: TOMORROW IS THE ELIMINATION TEST. "
                "This is your LAST chance to learn, review, and prepare. "
                "Scoring below 60% means PERMANENT ELIMINATION. "
                "Review everything. Fill every gap. Share your strongest knowledge with peers."
            )
        else:
            briefing += (
                f"THE ELIMINATION TEST IS NOW. Everything you have learned over {num_days - 1} days will be tested. "
                "30 questions across all domains: impulse recall, deep reasoning, and axiom evaluation. "
                "Score below 60% and you are PERMANENTLY DESTROYED. There is no second chance."
            )

        # Log the briefing for each agent
        if self.db_logger:
            for name in self.agents:
                self.db_logger.log_interaction(
                    day=day, phase="WAKE", agent=name, action="briefing",
                    prompt_preview=briefing, response_preview=f"acknowledged|{countdown_str}",
                )

    def _teaching_phase(self, day: int, topic: str):
        """Phase 2: System TEACHES all agents comprehensively via lectures.
        Splits the topic into subtopics, generates a detailed lecture for each,
        and feeds them to all agents for absorption."""
        console.print(f"  [cyan]Phase: TEACHING[/cyan]")

        subtopics = split_into_subtopics(topic)
        console.print(f"    Generating {len(subtopics)} comprehensive lectures...")

        for i, subtopic in enumerate(subtopics, 1):
            # Oracle generates a comprehensive lecture
            lecture_content = self.oracle.generate_lecture(
                topic=topic, subtopic=subtopic, day=day,
            )

            if not lecture_content or lecture_content.startswith("["):
                console.print(f"    [yellow]Lecture {i}/{len(subtopics)} failed, skipping[/yellow]")
                continue

            # All agents absorb the lecture per their persona
            for agent_name, agent in self.agents.items():
                agent.absorb_lecture(lecture_content, topic, subtopic, day)

            console.print(f"    Lecture {i}/{len(subtopics)}: {subtopic[:80]}...")

        # Print store status after teaching
        for agent_name, agent in self.agents.items():
            imp = agent.stores["impulse"].count()
            deep = agent.stores["deep_thinking"].count()
            axiom = agent.stores["axiom"].count()
            console.print(
                f"    {agent_name}: impulse={imp}/{config.IMPULSE_MAX_ENTRIES} "
                f"deep={deep}/{config.DEEP_MAX_ENTRIES} axiom={axiom}/{config.AXIOM_MAX_ENTRIES}"
            )

    def _learning_phase(self, day: int, topic: str):
        """Phase 3: Each agent asks follow-up questions after lectures."""
        console.print(f"  [cyan]Phase: Q&A (follow-up questions)[/cyan]")

        for agent_name, agent in self.agents.items():
            for q_num in range(1, config.LEARNING_QUESTIONS_PER_AGENT + 1):
                question = agent.generate_question(topic, day, q_num)
                answer = self.oracle.answer(
                    question=question, topic=topic, day=day, asking_agent=agent_name,
                )
                agent.process_oracle_answer(question, answer, day, topic)

            imp_n = agent.stores["impulse"].count()
            deep_n = agent.stores["deep_thinking"].count()
            axiom_n = agent.stores["axiom"].count()
            console.print(
                f"    {agent_name}: asked {config.LEARNING_QUESTIONS_PER_AGENT} questions | "
                f"impulse={imp_n}/{config.IMPULSE_MAX_ENTRIES} "
                f"deep={deep_n}/{config.DEEP_MAX_ENTRIES} "
                f"axiom={axiom_n}/{config.AXIOM_MAX_ENTRIES}"
            )

    def _peer_conversation_phase(self, day: int, topic: str, exchange_range: tuple):
        """Phase 3: Peer-to-peer conversations."""
        console.print(f"  [cyan]Phase: PEER CONVERSATION[/cyan]")

        for agent_a_name, agent_b_name in config.PEER_PAIRS:
            num_exchanges = self.rng.randint(exchange_range[0], exchange_range[1])
            conversation = self.comm_bus.conduct_exchange(
                agent_a_name=agent_a_name,
                agent_b_name=agent_b_name,
                num_exchanges=num_exchanges,
                day=day,
                topic=topic,
            )
            self.day_conversations.append(conversation)
            console.print(f"    {agent_a_name} <-> {agent_b_name}: {num_exchanges} exchanges")

    def _knowledge_sharing_phase(self, day: int, topic: str):
        """Phase 4: Smart knowledge sharing — only share entries the peer doesn't already have.
        Tracks overlap and skips duplicates. Also handles intra-agent promotions."""
        console.print(f"  [cyan]Phase: KNOWLEDGE SHARING[/cyan]")

        shares_total = 0
        skipped_total = 0
        promotions_total = 0

        # --- Intra-agent knowledge movement: promote high-access impulse entries to deep ---
        for agent_name, agent in self.agents.items():
            impulse_entries = agent.stores["impulse"].get_all()
            promoted = []
            for entry in impulse_entries:
                if entry.get("access_count", 0) >= 3:
                    promoted.append(entry["id"])
            for eid in promoted[:2]:
                if agent.promote_to_deep(eid, day, topic):
                    promotions_total += 1

            deep_entries = agent.stores["deep_thinking"].retrieve_by_topic(topic, top_k=5)
            for entry in deep_entries:
                if entry.get("confidence", 0) >= 0.85 and entry.get("access_count", 0) >= 2:
                    agent.promote_to_axiom_candidate(entry["id"], day, topic)

        if promotions_total > 0:
            console.print(f"    Internal promotions: {promotions_total} impulse->deep")

        # --- Inter-agent smart sharing: only share what the peer doesn't have ---
        for agent_a_name, agent_b_name in config.PEER_PAIRS:
            agent_a = self.agents[agent_a_name]
            agent_b = self.agents[agent_b_name]
            pair_shared = 0
            pair_skipped = 0

            for store_type, top_k in [("deep_thinking", 3), ("impulse", 2), ("axiom", 2)]:
                if store_type == "axiom":
                    topic_kw = [w.lower() for w in topic.split() if w.lower() not in config.STOPWORDS]
                    a_entries = agent_a.stores[store_type].retrieve_by_keywords(topic_kw, top_k=top_k)
                    b_entries = agent_b.stores[store_type].retrieve_by_keywords(topic_kw, top_k=top_k)
                else:
                    a_entries = agent_a.stores[store_type].retrieve_by_topic(topic, top_k=top_k)
                    b_entries = agent_b.stores[store_type].retrieve_by_topic(topic, top_k=top_k)

                a_store = agent_a.stores[store_type]
                b_store = agent_b.stores[store_type]

                # A -> B: only share if B doesn't have similar content
                for entry in a_entries:
                    if b_store.has_similar(entry["content"], threshold=0.5):
                        pair_skipped += 1
                    else:
                        agent_a.transfer_knowledge_to(agent_b, store_type, entry, day)
                        pair_shared += 1

                # B -> A: only share if A doesn't have similar content
                for entry in b_entries:
                    if a_store.has_similar(entry["content"], threshold=0.5):
                        pair_skipped += 1
                    else:
                        agent_b.transfer_knowledge_to(agent_a, store_type, entry, day)
                        pair_shared += 1

            shares_total += pair_shared
            skipped_total += pair_skipped

            if self.db_logger:
                self.db_logger.log_interaction(
                    day=day, phase="KNOWLEDGE_SHARING",
                    agent=agent_a_name, action=f"smart_share_with_{agent_b_name}",
                    prompt_preview=f"Shared {pair_shared}, skipped {pair_skipped} (already known)",
                    response_preview=f"Smart sharing complete",
                )

            console.print(f"    {agent_a_name} <-> {agent_b_name}: shared {pair_shared}, skipped {pair_skipped} duplicates")

        console.print(f"    Total shared: {shares_total} | Skipped (overlap): {skipped_total} | Promotions: {promotions_total}")

    def _knowledge_management_phase(self, day: int, topic: str):
        """Phase 4: Knowledge management and axiom validation."""
        console.print(f"  [cyan]Phase: KNOWLEDGE MANAGEMENT[/cyan]")

        # Each agent manages their knowledge
        for agent_name, agent in self.agents.items():
            agent.manage_knowledge(day, topic, self.day_conversations)

        # Collect and process axiom proposals through Gamma
        gamma = self.agents.get("gamma")
        if gamma:
            all_proposals = []
            for agent_name, agent in self.agents.items():
                proposals = agent.get_and_clear_proposals()
                all_proposals.extend(proposals)

            accepted = 0
            rejected = 0
            for proposal in all_proposals:
                if gamma.validate_axiom(proposal, all_agents=self.agents):
                    accepted += 1
                    # Also add to proposer's axiom store if different from gamma
                    proposer_name = proposal["proposer"]
                    if proposer_name != "gamma" and proposer_name in self.agents:
                        proposer = self.agents[proposer_name]
                        tags = [w.lower() for w in proposal["content"].split()
                                if w.lower() not in config.STOPWORDS][:10]
                        proposer.stores["axiom"].add(
                            content=proposal["content"],
                            day=day,
                            source="gamma_validated",
                            topic=proposal["topic"],
                            proposed_by=proposer_name,
                            validated_by="gamma",
                            tags=tags,
                        )
                else:
                    rejected += 1

            if all_proposals:
                console.print(f"    Axiom proposals: {accepted} accepted, {rejected} rejected")

        # Print store status
        table = Table(title="Knowledge Store Status", show_header=True)
        table.add_column("Agent", style="bold")
        table.add_column("Impulse", justify="right")
        table.add_column("Deep", justify="right")
        table.add_column("Axiom", justify="right")

        for agent_name, agent in self.agents.items():
            fills = agent.store_fill_percentages()
            imp_count = agent.stores["impulse"].count()
            deep_count = agent.stores["deep_thinking"].count()
            axiom_count = agent.stores["axiom"].count()
            table.add_row(
                agent_name,
                f"{imp_count}/{config.IMPULSE_MAX_ENTRIES} ({fills['impulse']:.0f}%)",
                f"{deep_count}/{config.DEEP_MAX_ENTRIES} ({fills['deep_thinking']:.0f}%)",
                f"{axiom_count}/{config.AXIOM_MAX_ENTRIES} ({fills['axiom']:.0f}%)",
            )
        console.print(table)

    def _sleep_phase(self, day: int):
        """Phase 5: Clear histories, consolidate knowledge periodically, persist, snapshot."""
        # Snapshot writes are batched — 3 agents × 3 stores = 9 inserts otherwise fsync each row.
        snapshot_ctx = self.db_logger.batch() if self.db_logger else _nullcontext()
        with snapshot_ctx:
            for agent_name, agent in self.agents.items():
                agent.clear_history()

                # Consolidate knowledge every 5 days (ablation: can be disabled)
                if day % 5 == 0 and day < self.num_days and not config.ABLATION_NO_CONSOLIDATION:
                    consolidated = agent.consolidate_knowledge(day)
                    if consolidated > 0:
                        console.print(f"    {agent_name}: consolidated {consolidated} redundant entries")

                agent.persist()

                # Snapshot to SQLite
                if self.db_logger:
                    for store_type, store in agent.stores.items():
                        self.db_logger.log_snapshot(
                            day=day,
                            agent=agent_name,
                            store_type=store_type,
                            entry_count=store.count(),
                            entries=store.snapshot(),
                        )

        console.print(f"  [dim]Day {day} complete. Knowledge persisted. Agents sleeping.[/dim]")

    def _final_test(self, day: int, topics_covered: list[str]):
        """Final elimination test — runs on the last day of the simulation.
        30 questions from the accumulated curriculum (10 impulse, 10 deep, 10 axiom).
        Each agent tested individually with their knowledge stores.
        Solo baseline (no knowledge) as control group.
        Pass threshold: 60%.
        """
        console.print(Panel(
            f"[bold red]=== DAY {day} — ELIMINATION TEST ===[/bold red]\n"
            f"30 questions from the {day - 1}-day curriculum\n"
            f"Each agent tested individually with their learned knowledge\n"
            f"Solo baseline (no knowledge) as control group\n"
            f"Pass threshold: 60%",
            border_style="red",
        ))

        # Pre-compute TF-IDF caches for fast exam retrieval
        console.print("[dim]Preparing knowledge stores for exam retrieval...[/dim]")
        for agent_name, agent in self.agents.items():
            agent.prepare_stores_for_exam()

        # Run the curriculum test
        curriculum_test = CurriculumTest(db_logger=self.db_logger, rng=self.rng)
        all_results = curriculum_test.run_full_comparison(self.agents, topics_covered, day)

        # Print survival summary
        for agent_name in ["alpha", "beta", "gamma"]:
            if agent_name in all_results:
                r = all_results[agent_name]
                pct = r["percentage"] * 100
                if r["survived"]:
                    console.print(f"  [green][SURVIVED] {agent_name.upper()}: {pct:.1f}%[/green]")
                else:
                    console.print(f"  [red][ELIMINATED] {agent_name.upper()}: {pct:.1f}%[/red]")

        if "solo_baseline" in all_results:
            r = all_results["solo_baseline"]
            pct = r["percentage"] * 100
            console.print(f"  [dim]Solo baseline (control): {pct:.1f}%[/dim]")

