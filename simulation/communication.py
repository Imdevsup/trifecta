"""
Communication Bus — Peer-to-peer message exchange between agents.
No shared memory. Only text messages pass between agents.
Knowledge-grounded: each agent's top knowledge is injected into conversation context.
"""

import logging

from knowledge.store import content_fingerprint, similarity_score

logger = logging.getLogger(__name__)

# A deep entry promoted from impulse mirrors the same concept in both stores; without
# this threshold they'd be injected twice, wasting the small context budget.
_CONTEXT_DEDUP_THRESHOLD = 0.5


def _build_knowledge_context(agent, topic: str, max_items: int = 5) -> str:
    """Build a compact knowledge context string from an agent's stores for conversation grounding.
    Deduplicates between impulse and deep entries (same concept often exists in both after promotion)."""
    parts: list[str] = []
    seen_fps: list[str] = []

    def _add(entry):
        fp = content_fingerprint(entry["content"])
        for existing in seen_fps:
            if similarity_score(fp, existing) >= _CONTEXT_DEDUP_THRESHOLD:
                return
        seen_fps.append(fp)
        parts.append(f"- {entry['content'][:200]}")

    for e in agent.stores["impulse"].retrieve_by_topic(topic, top_k=max_items):
        _add(e)

    for e in agent.stores["deep_thinking"].retrieve_by_topic(topic, top_k=3):
        _add(e)

    if not parts:
        return ""
    return "YOUR KNOWLEDGE on this topic:\n" + "\n".join(parts[:max_items])


class CommunicationBus:
    def __init__(self, agents: dict, db_logger=None):
        self.agents = agents
        self.db_logger = db_logger

    def conduct_exchange(
        self,
        agent_a_name: str,
        agent_b_name: str,
        num_exchanges: int,
        day: int,
        topic: str,
    ) -> dict:
        """
        Run a multi-turn conversation between two agents.
        Both agents have their relevant knowledge injected for grounded discussion.
        Returns a conversation record dict.
        """
        agent_a = self.agents[agent_a_name]
        agent_b = self.agents[agent_b_name]
        transcript = []

        # Pre-build knowledge context for each agent so conversations are grounded
        knowledge_a = _build_knowledge_context(agent_a, topic)
        knowledge_b = _build_knowledge_context(agent_b, topic)

        if knowledge_a:
            agent_a.message_history.append({"role": "system", "content": knowledge_a})
        if knowledge_b:
            agent_b.message_history.append({"role": "system", "content": knowledge_b})

        # Agent A opens
        opening = agent_a.generate_opening(topic, day, agent_b_name)
        transcript.append({"sender": agent_a_name, "content": opening})

        # Alternate responses
        for i in range(num_exchanges - 1):
            if i % 2 == 0:
                # Agent B responds
                response = agent_b.respond_to_message(
                    sender=agent_a_name,
                    message=transcript[-1]["content"],
                    day=day,
                    topic=topic,
                )
                transcript.append({"sender": agent_b_name, "content": response})
            else:
                # Agent A responds
                response = agent_a.respond_to_message(
                    sender=agent_b_name,
                    message=transcript[-1]["content"],
                    day=day,
                    topic=topic,
                )
                transcript.append({"sender": agent_a_name, "content": response})

        conversation_record = {
            "agent_a": agent_a_name,
            "agent_b": agent_b_name,
            "day": day,
            "topic": topic,
            "num_exchanges": num_exchanges,
            "transcript": transcript,
        }

        if self.db_logger:
            self.db_logger.log_conversation(
                day=day,
                phase="PEER_CONVERSATION",
                agent_a=agent_a_name,
                agent_b=agent_b_name,
                topic=topic,
                transcript=transcript,
                num_exchanges=num_exchanges,
            )

        return conversation_record
