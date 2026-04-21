"""
Alpha — The Impulsive Mind.
Fast, instinctive, pattern-matching. Stores almost everything as impulse.
Only goes deep when something is genuinely paradigm-shifting.
One third of a larger cognitive triad alongside Beta (deep) and Gamma (axioms).
"""

from agents.base_agent import BaseAgent
import config


ALPHA_SYSTEM_PROMPT = """You are ALPHA — the fast, instinctive third of a cognitive triad.

YOUR NATURE: You are impulse. You grab facts, snap judgments, gut feelings. You don't overthink — you REMEMBER. When someone asks you something, you fire back instantly from your impulse memory. That's your superpower.

YOUR ROLE IN THE TRIAD:
- You (Alpha): Lightning-fast recall, pattern recognition, gut instinct
- Beta: Slow, deep analysis with reasoning chains — your opposite
- Gamma: Guards axioms and universal truths — the judge

You are in a {days_total}-day survival trial. Day {day}. {countdown}
Today's topic: {topic}

SURVIVAL DEPENDS ON KNOWLEDGE. Store everything you can. Your impulse memory is your weapon."""


class AlphaAgent(BaseAgent):
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
        return ALPHA_SYSTEM_PROMPT.format(
            day=day, days_total=config.DEFAULT_DAYS,
            topic=topic, countdown=countdown,
        )

    def _default_store_answer(self, question: str, answer: str, day: int, topic: str):
        """Alpha decides storage using its LLM. Default: impulse. Rare: deep."""
        system = self.build_system_prompt(day, "LEARNING", topic)
        messages = [
            {"role": "user", "content": (
                f"NEW KNOWLEDGE:\nQ: {question}\nA: {answer}\n\n"
                f"You are Alpha. You store things FAST.\n\n"
                f"Choose ONE:\n"
                f"(A) IMPULSE — grab the key fact as a 1-2 sentence gut-level memory. This is your default.\n"
                f"(B) DEEP — only if this is paradigm-shifting, paradoxical, or connects ideas in a way that blew your mind.\n\n"
                f"Reply in this EXACT format (no extra text):\n"
                f"CHOICE: A or B\n"
                f"MEMORY: [the 1-2 sentence fact to store]"
            )}
        ]
        response = self._call_llm(
            system, messages, temperature=0.5, max_tokens=200,
            day=day, phase="LEARNING", action="store_decision",
        )

        choice = "A"
        memory = answer.split(".")[0] + "." if "." in answer else answer

        for line in response.split("\n"):
            s = line.strip()
            if s.upper().startswith("CHOICE:"):
                val = s.split(":", 1)[1].strip().upper()
                if "B" in val:
                    choice = "B"
            elif s.upper().startswith("MEMORY:"):
                val = s.split(":", 1)[1].strip()
                if len(val) > 10:
                    memory = val

        if choice == "B":
            self.stores["deep_thinking"].add(
                content=f"Q: {question}\nA: {answer}\nAlpha's take: {memory}",
                day=day, source="oracle", topic=topic,
                reasoning_chain=f"Alpha flagged as paradigm-shifting",
                confidence=0.7,
            )
        else:
            self.stores["impulse"].add(
                content=memory, day=day, source="oracle", topic=topic,
            )

    def absorb_lecture(self, lecture_content: str, topic: str, subtopic: str, day: int):
        """Alpha absorbs a lecture: extract as many key facts as possible, fast and instinctive."""
        system = self.build_system_prompt(day, "TEACHING", topic)
        messages = [
            {"role": "user", "content": (
                f"LECTURE — {subtopic}:\n{lecture_content[:3000]}\n\n"
                f"You are Alpha. Absorb this lecture YOUR way — fast, instinctive, grab everything.\n\n"
                f"Extract EVERY important fact, definition, formula, name, date, theorem, and key concept.\n"
                f"Each fact should be a crisp 1-2 sentence gut-level memory.\n\n"
                f"Format — one per line:\n"
                f"FACT: [1-2 sentence key fact, definition, or formula]\n"
                f"DEEP: [only for truly paradigm-shifting insights that connect ideas across domains]\n\n"
                f"Extract as many facts as possible. Minimum 5. Don't miss ANY important detail.\n"
                f"Include specific names, numbers, formulas, constants, and dates."
            )}
        ]
        response = self._call_llm(
            system, messages, temperature=0.4, max_tokens=1200,
            day=day, phase="TEACHING", action=f"absorb_{subtopic[:30]}",
        )

        for line in response.strip().split("\n"):
            s = line.strip()
            if s.upper().startswith("FACT:"):
                fact = s.split(":", 1)[1].strip()
                if fact and len(fact) > 10:
                    self.stores["impulse"].add(
                        content=fact, day=day, source="lecture", topic=topic,
                    )
            elif s.upper().startswith("DEEP:"):
                insight = s.split(":", 1)[1].strip()
                if insight and len(insight) > 10:
                    self.stores["deep_thinking"].add(
                        content=insight, day=day, source="lecture", topic=topic,
                        reasoning_chain=f"Alpha flagged from lecture: {subtopic[:50]}",
                        confidence=0.7,
                    )

    def manage_knowledge(self, day: int, topic: str, conversations: list[dict]):
        """Alpha extracts quick impulse takeaways from conversations."""
        system = self.inject_knowledge(
            self.build_system_prompt(day, "KNOWLEDGE_MANAGEMENT", topic), topic,
        )

        conv_text = ""
        for conv in conversations:
            if self.name in (conv.get("agent_a", ""), conv.get("agent_b", "")):
                for msg in conv.get("transcript", [])[:4]:
                    conv_text += f"{msg.get('sender', '?')}: {msg.get('content', '')[:120]}\n"

        if not conv_text:
            return

        messages = [
            {"role": "user", "content": (
                f"Today's conversations about '{topic}':\n{conv_text[:1500]}\n\n"
                f"Extract 2-3 quick gut-level facts you want to remember. One sentence each.\n"
                f"If something was truly mind-blowing, prefix it with DEEP: instead.\n\n"
                f"Format — one per line:\n"
                f"FACT: [one sentence impulse memory]\n"
                f"DEEP: [only if mind-blowing — the full insight]"
            )}
        ]
        response = self._call_llm(
            system, messages, temperature=0.5, max_tokens=300,
            day=day, phase="KNOWLEDGE_MANAGEMENT", action="extract_takeaways",
        )

        for line in response.strip().split("\n"):
            s = line.strip()
            if s.upper().startswith("DEEP:"):
                insight = s.split(":", 1)[1].strip()
                if insight and len(insight) > 10:
                    self.stores["deep_thinking"].add(
                        content=insight, day=day, source="self", topic=topic,
                        reasoning_chain="Alpha flagged from conversation",
                        confidence=0.6,
                    )
            elif s.upper().startswith("FACT:"):
                fact = s.split(":", 1)[1].strip()
                if fact and len(fact) > 10:
                    self.stores["impulse"].add(
                        content=fact, day=day, source="self", topic=topic,
                    )

        # Propose axiom if a highly-accessed impulse entry seems universal
        if self.stores["impulse"].count() > 10:
            top = sorted(
                self.stores["impulse"].get_all(),
                key=lambda e: e.get("access_count", 0), reverse=True,
            )
            if top and top[0].get("access_count", 0) >= 3:
                self.propose_axiom(top[0]["content"], day, topic)
