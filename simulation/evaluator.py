"""
Evaluator — Final-test question generator and scorer.
Generates 30 questions (10 impulse, 10 deep, 10 axiom) sampled from the
accumulated curriculum (all eight domains) and grades agent answers 0-10
with a strict rubric. Orchestration lives in simulation.curriculum_test.CurriculumTest.
"""

import time
import logging
import re

import openai
import httpx

import config
from agents.base_agent import rate_limit, clean_llm_response

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
        """Generate exactly 30 test questions: 10 impulse, 10 deep, 10 axiom.
        Samples 10 topics per type from the covered topics (with wraparound if <10 topics)."""
        import random as _random
        _rng = rng or _random.Random(42)

        questions = []
        n_topics = len(topics_covered)
        if n_topics == 0:
            return questions

        number = 1
        for q_type in ["impulse", "deep", "axiom"]:
            # Sample 10 topics for this question type
            if n_topics >= 10:
                selected = _rng.sample(topics_covered, 10)
            else:
                # Fewer than 10 topics: cycle through them
                selected = (topics_covered * (10 // n_topics + 1))[:10]
                _rng.shuffle(selected)

            for topic in selected:
                q = self._generate_one_question(topic, q_type, number)
                questions.append({"number": number, "type": q_type, "topic": topic, "question": q})
                number += 1

        return questions

    def _generate_one_question(self, topic: str, q_type: str, number: int) -> str:
        type_instructions = {
            "impulse": "Generate a quick-recall factual question that tests basic knowledge. It should be answerable in 1-2 sentences.",
            "deep": "Generate a multi-step analytical question that requires reasoning across concepts. It should need 3-5 sentences to answer properly.",
            "axiom": "Generate a true/false claim about a fundamental principle, and ask the respondent to evaluate whether it's universally true and justify their answer.",
        }
        system = (
            "You are a fair test question generator for an educational assessment. "
            "Generate exactly ONE question. Output ONLY the question, nothing else."
        )
        messages = [
            {"role": "user", "content": (
                f"Topic: {topic}\n"
                f"Question type: {q_type}\n"
                f"Instructions: {type_instructions[q_type]}\n"
                f"Generate question #{number}."
            )}
        ]
        return self._call_llm(system, messages, temperature=0.7, max_tokens=150)

    def _extract_score(self, response: str) -> tuple[float | None, str]:
        """Robustly extract a score from an LLM grading response.
        Tries multiple patterns: 'SCORE: X', 'X/10', 'Score: X', bare leading number, etc.
        Returns (score_or_None, reasoning_string)."""
        reasoning = ""

        # Try REASONING: line first
        for line in response.split("\n"):
            if "REASONING:" in line.upper():
                reasoning = line.split(":", 1)[-1].strip()
                break

        # Pattern 1: "SCORE: X" or "Score: X"
        m = re.search(r'(?i)score\s*:\s*([\d.]+)', response)
        if m:
            return min(10.0, max(0.0, float(m.group(1)))), reasoning

        # Pattern 2: "X/10" or "X / 10"
        m = re.search(r'([\d.]+)\s*/\s*10', response)
        if m:
            return min(10.0, max(0.0, float(m.group(1)))), reasoning

        # Pattern 3: "X out of 10"
        m = re.search(r'([\d.]+)\s+out\s+of\s+10', response, re.IGNORECASE)
        if m:
            return min(10.0, max(0.0, float(m.group(1)))), reasoning

        # Pattern 4: response starts with a number (model just outputs "7\nReasoning...")
        m = re.match(r'\s*([\d.]+)\s', response)
        if m:
            val = float(m.group(1))
            if 0 <= val <= 10:
                return val, reasoning

        # Pattern 5: any standalone number 0-10 in the first line
        first_line = response.strip().split("\n")[0] if response.strip() else ""
        nums = re.findall(r'\b(\d+(?:\.\d+)?)\b', first_line)
        for n in nums:
            val = float(n)
            if 0 <= val <= 10:
                return val, reasoning

        return None, reasoning

    def score_answer(self, question: str, answer: str, q_type: str, topic: str) -> tuple[float, str]:
        """Score an agent's answer 0-10. Returns (score, reasoning).
        Retries until the LLM returns a parseable score."""
        if config.DRY_RUN:
            return 5.0, "[dry-run placeholder score]"

        system = (
            "You are a STRICT academic exam grader. Grade the answer 0-10 using this rubric:\n"
            "  1-2: Wrong, irrelevant, or nonsensical answer\n"
            "  3-4: Partially correct but with major errors or critical omissions\n"
            "  5-6: Correct core idea but shallow, vague, or missing important details\n"
            "  7-8: Mostly correct and well-reasoned, minor gaps or imprecisions\n"
            "  9:   Excellent — accurate, thorough, and well-structured\n"
            "  10:  Perfect — flawless, comprehensive, demonstrates deep mastery\n\n"
            "BE DISCRIMINATING. Do NOT default to 7-8 for everything. A mediocre answer "
            "that restates the question or gives only surface-level facts deserves 4-5. "
            "Reserve 9-10 for genuinely outstanding answers.\n\n"
            "Reply ONLY in this format:\n"
            "SCORE: <number>\n"
            "REASONING: <one sentence explaining the score>"
        )
        messages = [
            {"role": "user", "content": (
                f"Topic: {topic}\nType: {q_type}\n"
                f"Question: {question[:500]}\n"
                f"Answer: {answer[:800]}\n"
                f"Grade 0-10 using the strict rubric."
            )}
        ]

        for attempt in range(config.MAX_RETRIES):
            response = self._call_llm(system, messages, temperature=0.2, max_tokens=80)
            score, reasoning = self._extract_score(response)

            if score is not None:
                return score, reasoning if reasoning else response.strip()

            logger.warning(f"Evaluator: no score parseable from response (attempt {attempt+1}), retrying...")
            time.sleep(config.RETRY_BASE_DELAY)

        # All retries exhausted — return 0 with the raw response as reasoning
        logger.error("Evaluator: could not get valid score after all retries")
        return 0.0, response.strip()

