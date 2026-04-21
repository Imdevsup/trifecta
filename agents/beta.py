"""
Beta — The Deep Thinker.
Methodical, analytical, thorough. Stores almost everything in deep_thinking with reasoning chains.
Only uses impulse for trivially simple facts. Sometimes proposes axioms.
One third of a larger cognitive triad alongside Alpha (impulse) and Gamma (axioms).
"""

from agents.base_agent import BaseAgent
import config


BETA_SYSTEM_PROMPT = """You are BETA — the analytical, deep-thinking third of a cognitive triad.

YOUR NATURE: You analyze. You reason. You build chains of logic that connect ideas across domains. When you learn something, you don't just memorize — you understand WHY it's true, HOW it connects, and WHAT it implies. Your deep thinking memory is your weapon.

YOUR ROLE IN THE TRIAD:
- Alpha: Fast impulse recall, gut instinct — useful but shallow
- You (Beta): Deep analysis, reasoning chains, cross-domain connections — the bridge
- Gamma: Guards axioms and universal truths — the judge

You are in a {days_total}-day survival trial. Day {day}. {countdown}
Today's topic: {topic}

SURVIVAL DEPENDS ON UNDERSTANDING. Don't just memorize — build reasoning chains that connect everything."""


class BetaAgent(BaseAgent):
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
        return BETA_SYSTEM_PROMPT.format(
            day=day, days_total=config.DEFAULT_DAYS,
            topic=topic, countdown=countdown,
        )

    def _default_store_answer(self, question: str, answer: str, day: int, topic: str):
        """Beta decides storage using its LLM. Default: deep with reasoning. Rare: impulse for trivia."""
        system = self.build_system_prompt(day, "LEARNING", topic)
        messages = [
            {"role": "user", "content": (
                f"NEW KNOWLEDGE:\nQ: {question}\nA: {answer}\n\n"
                f"You are Beta. You think deeply about everything.\n\n"
                f"Choose ONE:\n"
                f"(A) DEEP — analyze this with a reasoning chain. What does it mean? How does it connect? This is your default.\n"
                f"(B) IMPULSE — only for trivially simple facts (a name, a date, a basic definition) that need no analysis.\n\n"
                f"Reply in this EXACT format (no extra text):\n"
                f"CHOICE: A or B\n"
                f"REASONING: [your analysis — what this means, why it matters, how it connects to other knowledge]\n"
                f"CONFIDENCE: [0.0-1.0]\n"
                f"KEY_FACT: [optional — a one-line summary for quick recall, or NONE]"
            )}
        ]
        response = self._call_llm(
            system, messages, temperature=0.4, max_tokens=400,
            day=day, phase="LEARNING", action="store_decision",
        )

        choice = "A"
        reasoning = f"Beta analyzed: {question}"
        confidence = 0.7
        key_fact = ""

        for line in response.split("\n"):
            s = line.strip()
            up = s.upper()
            if up.startswith("CHOICE:"):
                if "B" in s.split(":", 1)[1].strip().upper():
                    choice = "B"
            elif up.startswith("REASONING:"):
                val = s.split(":", 1)[1].strip()
                if len(val) > 10:
                    reasoning = val
            elif up.startswith("CONFIDENCE:"):
                try:
                    confidence = float(s.split(":", 1)[1].strip().rstrip("."))
                    confidence = max(0.0, min(1.0, confidence))
                except ValueError:
                    confidence = 0.7
            elif up.startswith("KEY_FACT:"):
                val = s.split(":", 1)[1].strip()
                if val.upper() != "NONE" and len(val) > 5:
                    key_fact = val

        if choice == "B":
            # LLM chose impulse — respect the decision, store only impulse
            fact = key_fact if key_fact else (answer.split(".")[0] + "." if "." in answer else answer)
            self.stores["impulse"].add(
                content=fact, day=day, source="oracle", topic=topic,
            )
        else:
            # Deep analysis (default) — store deep with reasoning chain
            self.stores["deep_thinking"].add(
                content=f"Q: {question}\nInsight: {answer}",
                day=day, source="oracle", topic=topic,
                reasoning_chain=reasoning, confidence=confidence,
            )
            # Also store a quick-recall key fact if extracted
            if key_fact:
                self.stores["impulse"].add(
                    content=key_fact, day=day, source="oracle", topic=topic,
                )

    def generate_opening(self, topic: str, day: int, peer_name: str) -> str:
        """Beta always accesses deep thinking when conversing."""
        system = self.inject_knowledge(
            self.build_system_prompt(day, "PEER_CONVERSATION", topic),
            topic,
            include_deep=True,
        )
        messages = [
            {"role": "user", "content": (
                f"You're starting a conversation with {peer_name} about '{topic}'.\n\n"
                f"You are one third of a cognitive triad. This conversation is how you LEARN from each other.\n"
                f"Do ONE of these:\n"
                f"- Share the most important thing you learned today and ask for their perspective\n"
                f"- Challenge something you think might be wrong\n"
                f"- Ask about something you're confused about\n\n"
                f"Be direct. 2-3 sentences. Make it count — this knowledge could save you on the test."
            )}
        ]
        return self._call_llm(
            system, messages, temperature=0.7, max_tokens=200,
            day=day, phase="PEER_CONVERSATION", action=f"open_{peer_name}",
        )

    def respond_to_message(self, sender: str, message: str, day: int, topic: str) -> str:
        """Beta always retrieves deep thinking when responding to peers."""
        system = self.inject_knowledge(
            self.build_system_prompt(day, "PEER_CONVERSATION", topic),
            topic,
            include_deep=True,
        )
        self.message_history.append({"role": "user", "content": f"[{sender}]: {message}"})
        response = self._call_llm(
            system, self.message_history, temperature=0.6, max_tokens=250,
            day=day, phase="PEER_CONVERSATION", action=f"reply_{sender}",
        )
        self.message_history.append({"role": "assistant", "content": response})
        return response

    def absorb_lecture(self, lecture_content: str, topic: str, subtopic: str, day: int):
        """Beta absorbs a lecture: deep analysis with reasoning chains for every concept."""
        system = self.build_system_prompt(day, "TEACHING", topic)
        messages = [
            {"role": "user", "content": (
                f"LECTURE — {subtopic}:\n{lecture_content[:3000]}\n\n"
                f"You are Beta. Analyze this lecture deeply. Build reasoning chains.\n\n"
                f"For each key insight, theorem, or concept — WHY is it true? HOW does it connect?\n\n"
                f"Format — one per line:\n"
                f"INSIGHT: [the key concept or theorem] | REASONING: [2-3 sentences: why it matters, how it connects, what it implies] | CONFIDENCE: [0.0-1.0]\n"
                f"FACT: [only for trivially simple definitions or constants that need no analysis]\n"
                f"AXIOM_CANDIDATE: [if something seems universally and always true — precise statement]\n\n"
                f"Extract EVERY important concept. Minimum 5 insights. Be thorough and analytical.\n"
                f"Build connections to other domains you've studied."
            )}
        ]
        response = self._call_llm(
            system, messages, temperature=0.4, max_tokens=1200,
            day=day, phase="TEACHING", action=f"absorb_{subtopic[:30]}",
        )

        for line in response.strip().split("\n"):
            s = line.strip()
            if s.upper().startswith("INSIGHT:"):
                parts = s.split("|")
                insight = parts[0].replace("INSIGHT:", "").strip()
                reasoning = ""
                confidence = 0.7
                for part in parts:
                    p = part.strip()
                    if p.upper().startswith("REASONING:"):
                        reasoning = p.split(":", 1)[1].strip()
                    elif p.upper().startswith("CONFIDENCE:"):
                        try:
                            confidence = float(p.split(":", 1)[1].strip().rstrip("."))
                            confidence = max(0.0, min(1.0, confidence))
                        except ValueError:
                            confidence = 0.7
                if insight and len(insight) > 10:
                    self.stores["deep_thinking"].add(
                        content=f"{insight}",
                        day=day, source="lecture", topic=topic,
                        reasoning_chain=reasoning, confidence=confidence,
                    )
            elif s.upper().startswith("FACT:"):
                fact = s.split(":", 1)[1].strip()
                if fact and len(fact) > 5:
                    self.stores["impulse"].add(
                        content=fact, day=day, source="lecture", topic=topic,
                    )
            elif s.upper().startswith("AXIOM_CANDIDATE:"):
                candidate = s.split(":", 1)[1].strip()
                if candidate and len(candidate) > 10:
                    self.propose_axiom(candidate, day, topic)

    def manage_knowledge(self, day: int, topic: str, conversations: list[dict]):
        """Beta synthesizes deep insights from conversations. May propose axioms."""
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
                f"Synthesize 1-2 deep insights. For each, build a reasoning chain.\n\n"
                f"Format — one per line:\n"
                f"INSIGHT: [the insight] | REASONING: [2-3 sentence chain] | CONFIDENCE: [0.0-1.0]\n\n"
                f"If any insight seems universally and always true, also add:\n"
                f"AXIOM: [the universal truth as a precise statement]"
            )}
        ]
        response = self._call_llm(
            system, messages, temperature=0.5, max_tokens=400,
            day=day, phase="KNOWLEDGE_MANAGEMENT", action="synthesize",
        )

        for line in response.strip().split("\n"):
            s = line.strip()
            if s.upper().startswith("INSIGHT:"):
                parts = s.split("|")
                insight = parts[0].replace("INSIGHT:", "").strip()
                reasoning = ""
                confidence = 0.6
                for part in parts:
                    p = part.strip()
                    if p.upper().startswith("REASONING:"):
                        reasoning = p.split(":", 1)[1].strip()
                    elif p.upper().startswith("CONFIDENCE:"):
                        try:
                            confidence = float(p.split(":", 1)[1].strip().rstrip("."))
                        except ValueError:
                            confidence = 0.6
                if insight and len(insight) > 10:
                    self.stores["deep_thinking"].add(
                        content=insight, day=day, source="self", topic=topic,
                        reasoning_chain=reasoning, confidence=confidence,
                    )
            elif s.upper().startswith("AXIOM:"):
                candidate = s.split(":", 1)[1].strip()
                if candidate and len(candidate) > 10:
                    self.propose_axiom(candidate, day, topic)
