"""
Evaluator — Final-test MCQ question generator and deterministic scorer.
Default path: load the hand-curated static test bank (240 four-option MCQs
spanning eight PhD-level domains — 30 per domain, 10 impulse / 10 deep /
10 axiom each). Scoring is exact-match on the chosen letter — no LLM grader
call. Orchestration lives in simulation.curriculum_test.CurriculumTest.
"""

import time
import logging
import re

import openai
import httpx

import config
from agents.base_agent import rate_limit, clean_llm_response


VALID_LETTERS = ("A", "B", "C", "D")

logger = logging.getLogger(__name__)


class Evaluator:
    def __init__(self, db_logger=None):
        self.db_logger = db_logger
        self.model = config.MODEL
        self.client = openai.OpenAI(
            base_url=config.API_BASE, api_key=config.API_KEY,
            timeout=httpx.Timeout(config.CLIENT_TIMEOUT_SECONDS, connect=10.0),
            max_retries=0,
        )

    def _call_llm(self, system: str, messages: list[dict], temperature: float = 0.5, max_tokens: int = 300) -> str:
        if config.DRY_RUN:
            return "[Dry-run evaluator response]"

        full_messages = [{"role": "system", "content": system}] + messages

        for attempt in range(config.MAX_RETRIES):
            try:
                rate_limit(self.model)
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=full_messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
                return clean_llm_response(response.choices[0].message.content or "")
            except (openai.RateLimitError, openai.APIConnectionError, openai.APITimeoutError) as e:
                wait = min(config.RETRY_BASE_DELAY * (attempt + 1), config.RETRY_MAX_DELAY)
                logger.warning(f"Evaluator: {type(e).__name__} attempt {attempt+1}/{config.MAX_RETRIES}, retrying in {wait:.0f}s...")
                time.sleep(wait)
            except Exception as e:
                wait = min(config.RETRY_BASE_DELAY * (attempt + 1), config.RETRY_MAX_DELAY)
                logger.error(f"Evaluator: Error attempt {attempt+1}/{config.MAX_RETRIES}: {e}, retrying in {wait:.0f}s...")
                time.sleep(wait)
        return "[Evaluator unavailable]"

    def generate_questions(self, topics_covered: list[str], rng=None) -> list[dict]:
        """Return the full MCQ exam. Default path: load the hand-curated static test
        bank (authored by a different model family than the agents, eliminating
        self-preference bias). Falls back to runtime LLM generation only if the
        bank import fails. Options are shuffled per-run using `rng` so the correct
        letter distribution is flat regardless of canonical ordering in the bank."""
        import random as _random
        _rng = rng or _random.Random(42)

        try:
            from simulation.static_test_bank import STATIC_QUESTIONS
        except ImportError as e:
            logger.warning(
                f"Static test bank unavailable ({e}); falling back to LLM question generation."
            )
            return self._generate_questions_via_llm(topics_covered, _rng)

        questions: list[dict] = []
        for i, q in enumerate(STATIC_QUESTIONS, start=1):
            shuffled_options, shuffled_correct = self._shuffle_options(
                dict(q["options"]), q["correct"], _rng,
            )
            questions.append({
                "number": i,
                "type": q["type"],
                "topic": q["topic"],
                "question": q["question"],
                "options": shuffled_options,
                "correct": shuffled_correct,
            })
        return questions

    def _generate_questions_via_llm(self, topics_covered: list[str], rng,
                                     per_type: int = 10) -> list[dict]:
        """Fallback: generate MCQs via LLM. Used only if the static bank is missing.
        Returns per_type × 3 questions (default 30)."""
        questions: list[dict] = []
        n_topics = len(topics_covered)
        if n_topics == 0:
            return questions

        number = 1
        for q_type in ["impulse", "deep", "axiom"]:
            if n_topics >= per_type:
                selected = rng.sample(topics_covered, per_type)
            else:
                selected = (topics_covered * (per_type // n_topics + 1))[:per_type]
                rng.shuffle(selected)

            for topic in selected:
                q = self._generate_one_question(topic, q_type, number, rng)
                if q is not None:
                    questions.append(q)
                number += 1

        return questions

    def _generate_one_question(self, topic: str, q_type: str, number: int, rng) -> dict | None:
        """Generate one four-option MCQ. Returns a question dict or None if unparseable after retries."""
        type_instructions = {
            "impulse": "A quick-recall factual question testing a specific fact, definition, constant, or named result.",
            "deep": "A multi-step analytical question requiring reasoning across concepts, with options that represent different lines of reasoning.",
            "axiom": "A claim about a fundamental principle, with options that probe whether it is universally true and why (e.g. 'True because...', 'False because...').",
        }
        system = (
            "You are a precise MCQ question generator for a university-level exam. "
            "Output exactly one question with four answer options, marking the correct one. "
            "Distractors must be plausible — related concepts, common misconceptions, or "
            "near-misses — not obviously wrong. Exactly one option must be clearly correct."
        )
        user_msg = (
            f"Topic: {topic}\n"
            f"Question type: {q_type}\n"
            f"Instructions: {type_instructions[q_type]}\n\n"
            f"Output in this EXACT format — no preamble, no trailing commentary:\n"
            f"QUESTION: <the question>\n"
            f"A) <option A>\n"
            f"B) <option B>\n"
            f"C) <option C>\n"
            f"D) <option D>\n"
            f"CORRECT: <single letter A, B, C, or D>"
        )

        for attempt in range(config.MAX_RETRIES):
            response = self._call_llm(
                system, [{"role": "user", "content": user_msg}],
                temperature=0.7, max_tokens=400,
            )
            parsed = self._parse_mcq(response)
            if parsed is not None:
                question_text, options, correct_letter = parsed
                # Shuffle options so the correct letter isn't biased by the generator
                shuffled_options, shuffled_correct = self._shuffle_options(options, correct_letter, rng)
                return {
                    "number": number,
                    "type": q_type,
                    "topic": topic,
                    "question": question_text,
                    "options": shuffled_options,
                    "correct": shuffled_correct,
                }

            logger.warning(f"Evaluator: MCQ parse failed for #{number} ({q_type}) attempt {attempt+1}, retrying...")
            time.sleep(config.RETRY_BASE_DELAY)

        logger.error(f"Evaluator: could not generate MCQ #{number} after all retries, skipping")
        return None

    @staticmethod
    def _parse_mcq(response: str) -> tuple[str, dict[str, str], str] | None:
        """Parse QUESTION/A)/B)/C)/D)/CORRECT block. Returns (question, options, correct_letter) or None."""
        if not response:
            return None

        q_match = re.search(r'(?im)^\s*QUESTION\s*:\s*(.+?)(?=\n\s*[A-D][\)\.]|\Z)', response, re.DOTALL)
        if not q_match:
            return None
        question_text = q_match.group(1).strip()
        if len(question_text) < 5:
            return None

        options: dict[str, str] = {}
        for letter in VALID_LETTERS:
            m = re.search(
                rf'(?im)^\s*{letter}\s*[\)\.]\s*(.+?)(?=\n\s*[A-D]\s*[\)\.]|\n\s*CORRECT\s*:|\Z)',
                response, re.DOTALL,
            )
            if not m:
                return None
            text = m.group(1).strip()
            if len(text) < 1:
                return None
            options[letter] = text

        c_match = re.search(r'(?im)^\s*CORRECT\s*:\s*([A-Da-d])', response)
        if not c_match:
            return None
        correct = c_match.group(1).upper()

        return question_text, options, correct

    @staticmethod
    def _shuffle_options(options: dict[str, str], correct_letter: str, rng) -> tuple[dict[str, str], str]:
        """Shuffle the four option texts into A/B/C/D slots; return new options dict and the new correct letter."""
        texts = [options[l] for l in VALID_LETTERS]
        correct_text = options[correct_letter]
        rng.shuffle(texts)
        new_options = {letter: texts[i] for i, letter in enumerate(VALID_LETTERS)}
        new_correct = next(l for l, t in new_options.items() if t == correct_text)
        return new_options, new_correct

    @staticmethod
    def _extract_chosen_letter(answer: str) -> str | None:
        """Extract the agent's chosen letter from its response. Returns 'A'|'B'|'C'|'D' or None."""
        if not answer:
            return None

        # Prefer the LAST 'ANSWER: X' in the response (agents may cite options mid-reasoning)
        matches = re.findall(r'(?i)ANSWER\s*:\s*([A-Da-d])\b', answer)
        if matches:
            return matches[-1].upper()

        # Fallback: a bare letter on its own line (last occurrence)
        for line in reversed(answer.strip().split("\n")):
            s = line.strip().rstrip(".)(").upper()
            if s in VALID_LETTERS:
                return s

        return None

    @staticmethod
    def extract_labeled_letter(response: str, labels: tuple[str, ...]) -> str | None:
        """Extract a letter from a response, preferring any of the given line labels
        (e.g. 'LETTER', 'CURRENT_LETTER', 'FINAL_LETTER'). Uses the LAST match to handle
        agents that reconsider mid-response. Falls back to a trailing bare letter."""
        if not response:
            return None
        for label in labels:
            matches = re.findall(rf'(?i){label}\s*:\s*([A-Da-d])\b', response)
            if matches:
                return matches[-1].upper()
        for line in reversed(response.strip().split("\n")):
            s = line.strip().rstrip(".)(").upper()
            if s in VALID_LETTERS:
                return s
        return None

    @staticmethod
    def extract_reasoning(response: str, label: str = "REASONING") -> str:
        """Extract a single-line reasoning field from a structured response."""
        if not response:
            return ""
        m = re.search(rf'(?im)^\s*{label}\s*:\s*(.+?)(?:\n\s*[A-Z_]+\s*:|\Z)', response, re.DOTALL)
        if m:
            return m.group(1).strip()
        return ""

    def score_answer(self, question: str, answer: str, q_type: str, topic: str,
                     correct: str = "") -> tuple[float, str]:
        """Deterministic MCQ scoring: 1.0 if chosen letter matches correct, 0.0 otherwise.
        No LLM call — safe under DRY_RUN too. Unparseable answers score 0."""
        if not correct:
            return 0.0, "no correct letter provided"

        chosen = self._extract_chosen_letter(answer)
        if chosen is None:
            return 0.0, f"unparseable; correct was {correct}"
        if chosen == correct.upper():
            return 1.0, f"correct ({chosen})"
        return 0.0, f"chose {chosen}, correct was {correct.upper()}"

