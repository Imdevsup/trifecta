"""
Export — Post-simulation analysis export.
Generates summary_stats.json, knowledge_flow.json, and survival_report.md.
"""

import json
from pathlib import Path

import config


def export_all(db_logger, analysis_dir: Path, agents: dict):
    """Run all exports."""
    analysis_dir.mkdir(parents=True, exist_ok=True)
    export_summary_stats(db_logger, analysis_dir, agents)
    export_knowledge_flow(db_logger, analysis_dir)
    export_survival_report(db_logger, analysis_dir)


def export_summary_stats(db_logger, analysis_dir: Path, agents: dict):
    """Export summary statistics."""
    stats = {
        "agents": {},
        "totals": {"interactions": 0, "overflow_events": 0},
    }

    interactions = db_logger.get_all_interactions()
    overflow_events = db_logger.get_overflow_events()
    test_results = db_logger.get_test_results()

    stats["totals"]["interactions"] = len(interactions)
    stats["totals"]["overflow_events"] = len(overflow_events)

    for agent_name in ["alpha", "beta", "gamma"]:
        agent_interactions = [i for i in interactions if i.get("agent") == agent_name]
        agent_overflows = [o for o in overflow_events if o.get("agent") == agent_name]
        agent_tests = [t for t in test_results if t.get("agent") == agent_name]

        tokens_in = sum(i.get("tokens_in", 0) for i in agent_interactions)
        tokens_out = sum(i.get("tokens_out", 0) for i in agent_interactions)

        test_score = sum(t.get("score", 0) for t in agent_tests)
        test_max = len(agent_tests) * 10 if agent_tests else 1

        # Knowledge store sizes
        store_sizes = {}
        if agent_name in agents:
            agent = agents[agent_name]
            store_sizes = {
                "impulse": agent.stores["impulse"].count(),
                "deep_thinking": agent.stores["deep_thinking"].count(),
                "axiom": agent.stores["axiom"].count(),
            }

        stats["agents"][agent_name] = {
            "total_interactions": len(agent_interactions),
            "tokens_in": tokens_in,
            "tokens_out": tokens_out,
            "total_tokens": tokens_in + tokens_out,
            "overflow_events": len(agent_overflows),
            "overflow_by_store": {
                "impulse": len([o for o in agent_overflows if o.get("store_type") == "impulse"]),
                "deep_thinking": len([o for o in agent_overflows if o.get("store_type") == "deep_thinking"]),
                "axiom": len([o for o in agent_overflows if o.get("store_type") == "axiom"]),
            },
            "final_store_sizes": store_sizes,
            "test_score": test_score,
            "test_percentage": test_score / test_max if test_max > 0 else 0,
        }

    # Knowledge store growth curves from snapshots
    snapshots = db_logger.get_snapshots()
    growth = {}
    for snap in snapshots:
        agent = snap.get("agent", "")
        store = snap.get("store_type", "")
        day = snap.get("day", 0)
        count = snap.get("entry_count", 0)
        key = f"{agent}_{store}"
        if key not in growth:
            growth[key] = []
        growth[key].append({"day": day, "count": count})

    stats["knowledge_growth_curves"] = growth

    with open(analysis_dir / "summary_stats.json", "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)


def export_knowledge_flow(db_logger, analysis_dir: Path):
    """Export knowledge flow data (Sankey-diagram-ready)."""
    mutations = db_logger.get_knowledge_mutations()

    flows = []
    for m in mutations:
        source = m.get("agent", "unknown")
        store = m.get("store_type", "unknown")
        mutation = m.get("mutation_type", "unknown")
        day = m.get("day", 0)

        if mutation == "add":
            flows.append({"from": source, "to": f"{source}_{store}", "type": "add", "day": day})
        elif mutation in ("axiom_accepted", "axiom_rejected"):
            flows.append({"from": source, "to": f"axiom_validation", "type": mutation, "day": day})
        elif mutation == "promote":
            flows.append({"from": f"{source}_deep", "to": f"{source}_axiom", "type": "promote", "day": day})
        elif mutation == "demote":
            flows.append({"from": f"{source}_axiom", "to": f"{source}_deep", "type": "demote", "day": day})

    with open(analysis_dir / "knowledge_flow.json", "w", encoding="utf-8") as f:
        json.dump({"flows": flows, "total": len(flows)}, f, indent=2, ensure_ascii=False)


def export_survival_report(db_logger, analysis_dir: Path):
    """Export narrative survival report."""
    test_results = db_logger.get_test_results()
    overflow_events = db_logger.get_overflow_events()

    report_lines = [
        "# Cognitive Triad Simulation — Survival Report",
        "",
        "## Final Test Results",
        "",
    ]

    agent_scores = {}
    for r in test_results:
        agent = r.get("agent", "unknown")
        if agent not in agent_scores:
            agent_scores[agent] = {"total": 0, "count": 0, "by_type": {}}
        agent_scores[agent]["total"] += r.get("score", 0)
        agent_scores[agent]["count"] += 1
        q_type = r.get("question_type", "unknown")
        if q_type not in agent_scores[agent]["by_type"]:
            agent_scores[agent]["by_type"][q_type] = {"total": 0, "count": 0}
        agent_scores[agent]["by_type"][q_type]["total"] += r.get("score", 0)
        agent_scores[agent]["by_type"][q_type]["count"] += 1

    pass_pct = config.PASS_THRESHOLD * 100
    for agent, data in agent_scores.items():
        max_score = data["count"] * 10
        pct = (data["total"] / max_score * 100) if max_score > 0 else 0
        survived = pct >= pass_pct
        status = "SURVIVED" if survived else "ELIMINATED"
        report_lines.append(f"### {agent.upper()} — {status}")
        report_lines.append(f"- Total score: {data['total']:.1f}/{max_score} ({pct:.1f}%)")
        for q_type, type_data in data["by_type"].items():
            type_max = type_data["count"] * 10
            type_pct = (type_data["total"] / type_max * 100) if type_max > 0 else 0
            report_lines.append(f"  - {q_type}: {type_data['total']:.1f}/{type_max} ({type_pct:.1f}%)")
        report_lines.append("")

    # Overflow analysis
    report_lines.extend([
        "## Knowledge Overflow Analysis",
        "",
    ])
    agent_overflows = {}
    for o in overflow_events:
        agent = o.get("agent", "unknown")
        store = o.get("store_type", "unknown")
        key = f"{agent}_{store}"
        agent_overflows[key] = agent_overflows.get(key, 0) + 1

    for key, count in sorted(agent_overflows.items()):
        report_lines.append(f"- {key}: {count} overflow deletions")

    report_lines.extend([
        "",
        "## Key Observations",
        "",
        "- Agents with more overflow events in impulse memory may have prioritized breadth over depth.",
        "- Axiom count reflects Gamma's gatekeeping rigor.",
        "- Deep thinking stores that approached capacity indicate thorough analytical engagement.",
        "",
        "---",
        "*Generated by Cognitive Triad Simulation*",
    ])

    with open(analysis_dir / "survival_report.md", "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))
