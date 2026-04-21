"""
Curriculum Engine — Splits topics into subtopics and generates comprehensive lectures.
The system TEACHES agents first, then agents ask follow-up questions.
"""

import re
import logging

import config

logger = logging.getLogger(__name__)


def split_into_subtopics(topic: str) -> list[str]:
    """
    Split a day's topic description into individual subtopics for teaching.
    Each subtopic becomes a separate comprehensive lecture.
    Supports numbered subtopics (1. ... 2. ...) and sentence-boundary splitting.
    """
    # Extract header (first line before newline, or text before first numbered item)
    lines = topic.strip().split("\n")
    header = lines[0].strip() if lines else ""

    # Try splitting on numbered items (1. ..., 2. ..., etc.)
    numbered_parts = re.split(r'\n\s*(\d+)\.\s+', topic)
    if len(numbered_parts) >= 3:
        # numbered_parts = [header, "1", content1, "2", content2, ...]
        subtopics = []
        for i in range(1, len(numbered_parts), 2):
            num = numbered_parts[i]
            content = numbered_parts[i + 1].strip() if i + 1 < len(numbered_parts) else ""
            if content and len(content) >= config.SUBTOPIC_MIN_LENGTH:
                subtopics.append(f"{header} — {num}. {content}")
        if len(subtopics) >= 2:
            return subtopics

    # Fallback: split on sentence boundaries (period followed by space and uppercase)
    parts = topic.split(": ", 1)
    if len(parts) > 1:
        h = parts[0].strip()
        body = parts[1].strip()
    else:
        h = ""
        body = topic.strip()

    sentences = re.split(r'\.\s+(?=[A-Z])', body)

    subtopics = []
    for s in sentences:
        s = s.strip().rstrip(".")
        if len(s) < config.SUBTOPIC_MIN_LENGTH:
            continue
        if h:
            subtopics.append(f"{h}: {s}")
        else:
            subtopics.append(s)

    if len(subtopics) < 2:
        return [topic]

    return subtopics


def build_lecture_prompt(topic: str, subtopic: str) -> str:
    """Build the user prompt for generating a comprehensive lecture."""
    return (
        f"COMPREHENSIVE LECTURE — {subtopic}\n\n"
        f"Broader context: '{topic[:300]}'\n\n"
        f"Write an EXHAUSTIVE university-level lecture covering:\n\n"
        f"1. FORMAL DEFINITIONS — precise, complete definitions of every key concept\n"
        f"2. KEY THEOREMS & LAWS — state them formally, explain intuition and significance\n"
        f"3. FORMULAS & EQUATIONS — write out every important formula with variable definitions\n"
        f"4. WORKED EXAMPLES — concrete examples showing application of key concepts\n"
        f"5. CONNECTIONS — how this relates to other fields and concepts\n"
        f"6. EDGE CASES & MISCONCEPTIONS — common mistakes, subtle points, counterexamples\n"
        f"7. HISTORICAL CONTEXT — key figures, dates, pivotal discoveries\n"
        f"8. NAMED PHENOMENA — specific named laws, effects, theorems, paradoxes\n\n"
        f"CRITICAL: Pack in MAXIMUM factual density. Every sentence should contain testable knowledge. "
        f"This content will be tested against Humanity's Last Exam — the hardest exam ever created. "
        f"Include specific numbers, names, dates, constants, and precise technical terms. "
        f"Do NOT be vague or hand-wavy. Be a textbook, not a summary."
    )
