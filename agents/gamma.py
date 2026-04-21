"""
Gamma — The Axiom Guardian.
Rigorous, principled, conservative. Evaluates every piece of knowledge for axiom-worthiness.
If not an axiom, sorts it into deep (complex) or impulse (simple).
One third of a larger cognitive triad alongside Alpha (impulse) and Beta (deep).
"""

from agents.base_agent import BaseAgent
import config


GAMMA_SYSTEM_PROMPT = """You are GAMMA — the axiomatic guardian of a cognitive triad.

YOUR NATURE: You evaluate truth. Every piece of knowledge passes through your filter: is this a UNIVERSAL TRUTH — always true, everywhere, without exception? If yes, you enshrine it as an axiom. If not, you categorize it: deep analysis or simple fact. You are rigorous, conservative, and demanding.

YOUR ROLE IN THE TRIAD:
- Alpha: Fast impulse recall, gut instinct — useful raw material
- Beta: Deep analysis with reasoning chains — useful for building understanding
- You (Gamma): Guard foundational truths. Validate axioms. Reject the unworthy. A bad axiom is worse than no axiom.

You are in a {days_total}-day survival trial. Day {day}. {countdown}
Today's topic: {topic}

SURVIVAL DEPENDS ON TRUTH. Build a fortress of axioms. Categorize everything else ruthlessly."""


class GammaAgent(BaseAgent):
    def build_system_prompt(self, day: int, phase: str, topic: str) -> str:
        days_left = config.DEFAULT_DAYS - day
        if days_left <= 0:
            countdown = "THE ELIMINATION TEST IS NOW."
        elif days_left == 1:
            countdown = "TOMORROW IS THE TEST. LAST CHANCE."
        elif days_left <= 5:
            countdown = f"WARNING: {days_left} DAYS LEFT."
        else:
            countdown = f"{days_left} days until elimination."
        return GAMMA_SYSTEM_PROMPT.format(
            day=day, days_total=config.DEFAULT_DAYS,
            topic=topic, countdown=countdown,
        )

    def _default_store_answer(self, question: str, answer: str, day: int, topic: str):
        """Gamma evaluates every answer: extract axioms, then sort remainder into deep or impulse."""
        system = self.build_system_prompt(day, "LEARNING", topic)
        messages = [
            {"role": "user", "content": (
                f"NEW KNOWLEDGE:\nQ: {question}\nA: {answer}\n\n"
                f"You are Gamma. Evaluate this knowledge:\n\n"
                f"Step 1 — AXIOM CHECK: Does this contain a universal truth? A law, theorem, principle, "
                f"or fact that is ALWAYS true without exception? If yes, extract it as a clean, precise statement.\n\n"
                f"Step 2 — CATEGORIZE the rest:\n"
                f"(A) DEEP — complex analysis, reasoning, multi-step logic, connections between concepts\n"
                f"(B) IMPULSE — simple fact, basic definition, single data point, trivial knowledge\n\n"
                f"Reply in this EXACT format (no extra text):\n"
                f"AXIOM: [precise universal truth] or NONE\n"
                f"CATEGORY: A or B\n"
                f"STORE: [what to remember — either a deep analysis or a simple fact]"
            )}
        ]
        response = self._call_llm(
            system, messages, temperature=0.3, max_tokens=350,
            day=day, phase="LEARNING", action="evaluate_and_sort",
        )

        axiom_text = ""
        category = "A"  # default to deep
        store_content = f"Q: {question}\nAnalysis: {answer}"

        for line in response.split("\n"):
            s = line.strip()
            up = s.upper()
            if up.startswith("AXIOM:"):
                val = s.split(":", 1)[1].strip()
                if val.upper() != "NONE" and len(val) > 10:
                    axiom_text = val
            elif up.startswith("CATEGORY:"):
                val = s.split(":", 1)[1].strip().upper()
                if "B" in val:
                    category = "B"
            elif up.startswith("STORE:"):
                val = s.split(":", 1)[1].strip()
                if len(val) > 10:
                    store_content = val

        # Propose axiom if found
        if axiom_text:
            self.propose_axiom(axiom_text, day, topic)

        # Categorize the knowledge
        if category == "B":
            self.stores["impulse"].add(
                content=store_content, day=day, source="oracle", topic=topic,
            )
        else:
            self.stores["deep_thinking"].add(
                content=store_content, day=day, source="oracle", topic=topic,
                reasoning_chain=f"Gamma deep-categorized: {question}",
                confidence=0.6,
            )

    def absorb_lecture(self, lecture_content: str, topic: str, subtopic: str, day: int):
        """Gamma absorbs a lecture: evaluate for axioms first, then categorize the rest."""
        system = self.build_system_prompt(day, "TEACHING", topic)
        messages = [
            {"role": "user", "content": (
                f"LECTURE — {subtopic}:\n{lecture_content[:3000]}\n\n"
                f"You are Gamma, the axiom guardian. Evaluate this lecture rigorously.\n\n"
                f"Step 1 — AXIOM SCAN: Identify any universal truths that are ALWAYS true, "
                f"everywhere, without exception. Be conservative — only propose what you're certain about.\n\n"
                f"Step 2 — CATEGORIZE all remaining knowledge:\n"
                f"DEEP: complex concepts, multi-step reasoning, connections between ideas\n"
                f"FACT: simple definitions, single data points, basic constants\n\n"
                f"Format — one per line:\n"
                f"AXIOM: [precise universal truth — must be always true with no exceptions]\n"
                f"DEEP: [complex concept needing deeper analysis]\n"
                f"FACT: [simple fact or basic definition]\n\n"
                f"Be THOROUGH — extract every piece of knowledge. Minimum 5 items.\n"
                f"Be RIGOROUS about axioms — only the genuinely universal."
            )}
        ]
        response = self._call_llm(
            system, messages, temperature=0.3, max_tokens=1200,
            day=day, phase="TEACHING", action=f"absorb_{subtopic[:30]}",
        )

        for line in response.strip().split("\n"):
            s = line.strip()
            up = s.upper()
            if up.startswith("AXIOM:"):
                candidate = s.split(":", 1)[1].strip()
                if candidate and candidate.upper() != "NONE" and len(candidate) > 10:
                    self.propose_axiom(candidate, day, topic)
            elif up.startswith("DEEP:"):
                content = s.split(":", 1)[1].strip()
                if content and len(content) > 10:
                    self.stores["deep_thinking"].add(
                        content=content, day=day, source="lecture", topic=topic,
                        reasoning_chain=f"Gamma categorized from lecture: {subtopic[:50]}",
                        confidence=0.6,
                    )
            elif up.startswith("FACT:"):
                fact = s.split(":", 1)[1].strip()
                if fact and len(fact) > 5:
                    self.stores["impulse"].add(
                        content=fact, day=day, source="lecture", topic=topic,
                    )

    def validate_axiom(self, proposal: dict, all_agents: dict = None) -> bool:
        """Multi-stage axiom validation pipeline (skipped if ABLATION_NO_AXIOM_VALIDATION):
        Stage 1: Alpha tests boundary cases (finds edge cases where it might break)
        Stage 2: Beta searches for counterexamples (analytical disproof attempt)
        Stage 3: Gamma makes the final ruling with all evidence
        Returns True if accepted."""
        day = proposal["day"]
        topic = proposal["topic"]
        content = proposal["content"]
        proposer = proposal["proposer"]

        # Ablation: skip validation, auto-accept
        if config.ABLATION_NO_AXIOM_VALIDATION:
            tags = [w.lower() for w in content.split() if w.lower() not in config.STOPWORDS][:10]
            self.stores["axiom"].add(
                content=content, day=day, source=proposer, topic=topic,
                proposed_by=proposer, validated_by="auto_ablation", tags=tags,
            )
            return True

        alpha_challenge = ""
        beta_challenge = ""

        # --- STAGE 1: Alpha boundary test ---
        if all_agents and "alpha" in all_agents:
            alpha = all_agents["alpha"]
            alpha_sys = alpha.inject_knowledge(
                alpha.build_system_prompt(day, "KNOWLEDGE_MANAGEMENT", topic), topic,
            )
            alpha_msgs = [
                {"role": "user", "content": (
                    f"AXIOM BOUNDARY TEST — proposed truth:\n\"{content}\"\n\n"
                    f"You are Alpha. Think fast. Find the EDGE CASES:\n"
                    f"- Where might this break down?\n"
                    f"- What extreme or unusual scenarios could violate it?\n"
                    f"- Any gut feeling this is wrong?\n\n"
                    f"Reply: EDGE_CASES: [list edge cases, or NONE if rock-solid]"
                )}
            ]
            alpha_challenge = alpha._call_llm(
                alpha_sys, alpha_msgs, temperature=0.6, max_tokens=200,
                day=day, phase="KNOWLEDGE_MANAGEMENT", action=f"axiom_boundary_{proposer}",
            )

        # --- STAGE 2: Beta counterexample search ---
        if all_agents and "beta" in all_agents:
            beta = all_agents["beta"]
            beta_sys = beta.inject_knowledge(
                beta.build_system_prompt(day, "KNOWLEDGE_MANAGEMENT", topic), topic,
                include_deep=True,
            )
            beta_msgs = [
                {"role": "user", "content": (
                    f"AXIOM COUNTEREXAMPLE SEARCH — proposed truth:\n\"{content}\"\n\n"
                    f"Alpha's edge cases: {alpha_challenge[:300]}\n\n"
                    f"You are Beta. Analyze rigorously:\n"
                    f"- Can you construct a logical counterexample?\n"
                    f"- Does this conflict with any known theorems or principles?\n"
                    f"- Is the logic sound or does it contain a hidden assumption?\n\n"
                    f"Reply: COUNTEREXAMPLE: [specific counterexample] or NONE_FOUND\n"
                    f"VERDICT: WEAK or STRONG (how confident are you in this axiom?)"
                )}
            ]
            beta_challenge = beta._call_llm(
                beta_sys, beta_msgs, temperature=0.4, max_tokens=250,
                day=day, phase="KNOWLEDGE_MANAGEMENT", action=f"axiom_counter_{proposer}",
            )

        # --- STAGE 3: Gamma final ruling with all evidence ---
        system = self.inject_knowledge(
            self.build_system_prompt(day, "KNOWLEDGE_MANAGEMENT", topic), topic,
            include_deep=True,
        )

        existing = self.stores["axiom"].get_all()
        axiom_list = ""
        if existing:
            axiom_list = "YOUR EXISTING AXIOMS:\n"
            for a in existing[:20]:
                axiom_list += f"  - \"{a['content']}\"\n"

        messages = [
            {"role": "user", "content": (
                f"{axiom_list}\n"
                f"AXIOM PROPOSAL from {proposer}:\n\"{content}\"\n\n"
                f"=== TRIAD REVIEW ===\n"
                f"Alpha's boundary test: {alpha_challenge[:300]}\n"
                f"Beta's counterexample search: {beta_challenge[:300]}\n\n"
                f"You are Gamma, the axiom guardian. With the full evidence above:\n"
                f"1. Is it ALWAYS true, without ANY exception?\n"
                f"2. Did Alpha or Beta find valid weaknesses?\n"
                f"3. Is it consistent with your existing axioms?\n"
                f"4. Is it precise and well-defined?\n\n"
                f"First line must be: ACCEPT or REJECT\n"
                f"Second line: one-sentence justification referencing the triad's analysis."
            )}
        ]

        response = self._call_llm(
            system, messages, temperature=0.3, max_tokens=200,
            day=day, phase="KNOWLEDGE_MANAGEMENT", action=f"validate_from_{proposer}",
        )

        accepted = "ACCEPT" in response.upper().split("\n")[0] if response else False

        if accepted:
            tags = [w.lower() for w in content.split() if w.lower() not in config.STOPWORDS][:10]
            self.stores["axiom"].add(
                content=content, day=day, source=proposer, topic=topic,
                proposed_by=proposer, validated_by="gamma_triad", tags=tags,
            )
            if self.db_logger:
                self.db_logger.log_mutation(
                    day=day, agent="gamma", store_type="axiom",
                    mutation_type="axiom_accepted",
                    entry_id=f"from_{proposer}", content_preview=content,
                )
        else:
            # Rejected: sort into deep or impulse
            if len(content.split()) < 20:
                self.stores["impulse"].add(
                    content=content, day=day, source=proposer, topic=topic,
                )
            else:
                self.stores["deep_thinking"].add(
                    content=f"Rejected axiom: {content}. Alpha: {alpha_challenge[:100]}. Beta: {beta_challenge[:100]}. Gamma: {response[:200]}",
                    day=day, source=proposer, topic=topic,
                    reasoning_chain=f"Triad rejected: {response[:300]}",
                    confidence=0.3,
                )
            if self.db_logger:
                self.db_logger.log_mutation(
                    day=day, agent="gamma", store_type="axiom",
                    mutation_type="axiom_rejected",
                    entry_id=f"from_{proposer}", content_preview=content,
                )

        return accepted

    def manage_knowledge(self, day: int, topic: str, conversations: list[dict]):
        """Gamma reviews conversations for axiom candidates and investigation targets."""
        system = self.inject_knowledge(
            self.build_system_prompt(day, "KNOWLEDGE_MANAGEMENT", topic), topic,
            include_deep=True,
        )

        conv_text = ""
        for conv in conversations:
            if self.name in (conv.get("agent_a", ""), conv.get("agent_b", "")):
                for msg in conv.get("transcript", []):
                    conv_text += f"{msg.get('sender', '?')}: {msg.get('content', '')[:150]}\n"

        if not conv_text:
            return

        messages = [
            {"role": "user", "content": (
                f"Today's conversations about '{topic}':\n{conv_text[:2000]}\n\n"
                f"As axiom guardian, identify:\n\n"
                f"Format — one per line:\n"
                f"AXIOM: [universal truth to propose — must be ALWAYS true]\n"
                f"INVESTIGATE: [claim that needs deeper analysis before judging]\n"
                f"CHALLENGE: [an existing axiom that today's discussion calls into question]\n\n"
                f"Be SELECTIVE. Only propose axioms you are confident about."
            )}
        ]
        response = self._call_llm(
            system, messages, temperature=0.4, max_tokens=300,
            day=day, phase="KNOWLEDGE_MANAGEMENT", action="review_for_axioms",
        )

        for line in response.strip().split("\n"):
            s = line.strip()
            if s.upper().startswith("AXIOM:"):
                candidate = s.split(":", 1)[1].strip()
                if candidate and len(candidate) > 10:
                    self.propose_axiom(candidate, day, topic)
            elif s.upper().startswith("INVESTIGATE:"):
                text = s.split(":", 1)[1].strip()
                if text and len(text) > 5:
                    self.stores["deep_thinking"].add(
                        content=f"Needs investigation: {text}",
                        day=day, source="self", topic=topic,
                        reasoning_chain="Flagged for deeper analysis",
                        confidence=0.3,
                    )

    def demote_axiom(self, axiom_id: str, day: int, reason: str):
        """Demote an axiom back to deep_thinking."""
        entry = self.stores["axiom"].get_entry_by_id(axiom_id)
        if entry:
            self.stores["axiom"].remove_by_id(axiom_id, day=day)
            self.stores["deep_thinking"].add(
                content=f"DEMOTED AXIOM: {entry['content']}. Reason: {reason}",
                day=day, source="self", topic=entry.get("topic", ""),
                reasoning_chain=f"Axiom demoted: {reason}",
                confidence=0.4,
            )
            if self.db_logger:
                self.db_logger.log_mutation(
                    day=day, agent="gamma", store_type="axiom",
                    mutation_type="demote", entry_id=axiom_id,
                    content_preview=entry["content"],
                )
