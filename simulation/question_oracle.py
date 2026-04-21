"""
Question Oracle -- Answers agent questions and generates lectures via OpenAI.
"""

import time
import logging

import openai
import httpx

import config
from agents.base_agent import rate_limit, clean_llm_response

logger = logging.getLogger(__name__)


class QuestionOracle:
    def __init__(self, db_logger=None):
        self.db_logger = db_logger
        self.model = config.MODEL
        self.client = openai.OpenAI(
            base_url=config.API_BASE, api_key=config.API_KEY,
            timeout=httpx.Timeout(config.CLIENT_TIMEOUT_SECONDS, connect=10.0),
            max_retries=0,
        )

    def _call(self, messages, temperature=0.3, max_tokens=800, day=0, action="", phase="LEARNING"):
        """Single-model LLM call with retry."""
        if config.DRY_RUN:
            return f"[Dry-run oracle: {action}]"

        for attempt in range(config.MAX_RETRIES):
            try:
                rate_limit(self.model)
                start = time.time()
                response = self.client.chat.completions.create(
                    model=self.model, messages=messages,
                    temperature=temperature, max_tokens=max_tokens,
                )
                latency_ms = int((time.time() - start) * 1000)
                content = clean_llm_response(response.choices[0].message.content or "")
                tokens_in = getattr(response.usage, "prompt_tokens", 0) if response.usage else 0
                tokens_out = getattr(response.usage, "completion_tokens", 0) if response.usage else 0

                if self.db_logger:
                    prompt_text = messages[-1]["content"] if messages else ""
                    self.db_logger.log_interaction(
                        day=day, phase=phase, agent="oracle", action=action,
                        prompt_preview=prompt_text, response_preview=content,
                        tokens_in=tokens_in, tokens_out=tokens_out,
                        latency_ms=latency_ms, model=self.model,
                    )
                return content

            except (openai.RateLimitError, openai.APIConnectionError, openai.APITimeoutError) as e:
                wait = min(config.RETRY_BASE_DELAY * (attempt + 1), config.RETRY_MAX_DELAY)
                logger.warning(f"Oracle: {type(e).__name__} attempt {attempt+1}/{config.MAX_RETRIES}, retrying in {wait:.0f}s...")
                time.sleep(wait)
            except Exception as e:
                wait = min(config.RETRY_BASE_DELAY * (attempt + 1), config.RETRY_MAX_DELAY)
                logger.error(f"Oracle: Error attempt {attempt+1}/{config.MAX_RETRIES}: {e}, retrying in {wait:.0f}s...")
                time.sleep(wait)

        return "[Oracle unavailable]"

    def answer(self, question: str, topic: str, day: int = 0, asking_agent: str = "") -> str:
        """Answer a question about the given topic."""
        system_prompt = (
            f"You are a world-class expert professor with deep knowledge across all domains. "
            f"The topic is: '{topic}'.\n\n"
            f"INSTRUCTIONS:\n"
            f"- Answer with MAXIMUM accuracy and detail\n"
            f"- Include specific facts, names, numbers, formulas, theorems, and definitions\n"
            f"- Explain the reasoning and underlying principles\n"
            f"- Be thorough — this knowledge will be tested on Humanity's Last Exam\n"
            f"- Aim for 4-8 sentences of dense, factual content"
        )
        messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": question}]
        return self._call(messages, temperature=0.3, max_tokens=800, day=day,
                          action=f"answer_for_{asking_agent}", phase="LEARNING")

    def generate_lecture(self, topic: str, subtopic: str, day: int) -> str:
        """Generate a comprehensive lecture on a subtopic."""
        from simulation.curriculum import build_lecture_prompt

        system_prompt = (
            "You are a world-class professor writing comprehensive lecture notes. "
            "Cover EVERY key concept, theorem, formula, definition, example, and connection. "
            "Write in a clear, structured format. Include formal definitions, precise formulas, "
            "and concrete examples. Every sentence must contain testable, factual content."
        )
        user_message = build_lecture_prompt(topic, subtopic)
        messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_message}]
        return self._call(messages, temperature=0.3, max_tokens=config.LECTURE_MAX_TOKENS, day=day,
                          action=f"lecture_{subtopic[:50]}", phase="TEACHING")
