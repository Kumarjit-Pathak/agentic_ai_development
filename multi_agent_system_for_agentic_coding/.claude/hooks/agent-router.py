#!/usr/bin/env python3
"""
Agent Router Hook - Routes requests to appropriate specialized agents
"""

import json
import re
import sys
from typing import Dict, List, Optional

class AgentRouter:
    def __init__(self):
        self.agents = {
            "data-analyzer": {
                "keywords": ["data", "excel", "csv", "constraint", "analysis", "validation", "quality"],
                "patterns": [r"analyze.*data", r"process.*excel", r"validate.*constraint", r"data.*quality"]
            },
            "dashboard-developer": {
                "keywords": ["streamlit", "dashboard", "ui", "interface", "visualization", "chart", "plot"],
                "patterns": [r"build.*dashboard", r"create.*interface", r"streamlit.*app", r"visualiz"]
            },
            "optimization-expert": {
                "keywords": ["optimization", "constraint", "algorithm", "mathematical", "model", "solver"],
                "patterns": [r"optim", r"constraint.*problem", r"mathematical.*model", r"algorithm"]
            },
            "data-science-researcher": {
                "keywords": ["research", "statistical", "modeling", "hypothesis", "bayesian", "experimental", "academic"],
                "patterns": [r"research.*problem", r"statistical.*model", r"hypothesis.*test", r"experimental.*design", r"literature.*review", r"advanced.*model"]
            },
            "ml-concept-tester": {
                "keywords": ["machine learning", "deep learning", "neural network", "ml", "dl", "ai", "genai", "llm", "experiment"],
                "patterns": [r"machine.*learning", r"deep.*learning", r"neural.*network", r"test.*model", r"ml.*experiment", r"ai.*concept", r"llm.*test"]
            },
            "strategic-planner": {
                "keywords": ["plan", "strategy", "roadmap", "schedule", "timeline", "reflection", "iteration", "memory"],
                "patterns": [r"create.*plan", r"develop.*strategy", r"plan.*project", r"reflect.*iteration", r"track.*progress", r"strategic.*plan"]
            },
            "meta-orchestrator": {
                "keywords": ["coordinate", "manage", "orchestrate", "workflow", "complex"],
                "patterns": [r"coordinate.*agents", r"complex.*task", r"multi.*step"]
            }
        }

    def analyze_request(self, message: str) -> List[str]:
        """Analyze request and determine which agents should handle it"""
        message_lower = message.lower()
        suggested_agents = []

        for agent_name, config in self.agents.items():
            score = 0

            # Check keywords
            for keyword in config["keywords"]:
                if keyword in message_lower:
                    score += 1

            # Check patterns
            for pattern in config["patterns"]:
                if re.search(pattern, message_lower):
                    score += 2

            if score > 0:
                suggested_agents.append((agent_name, score))

        # Sort by score and return agent names
        suggested_agents.sort(key=lambda x: x[1], reverse=True)
        return [agent[0] for agent in suggested_agents]

    def get_routing_suggestion(self, message: str) -> Dict:
        """Get routing suggestion with explanation"""
        agents = self.analyze_request(message)

        if not agents:
            return {
                "primary_agent": "meta-orchestrator",
                "secondary_agents": [],
                "reasoning": "No specific expertise detected, routing to meta-orchestrator for analysis"
            }

        return {
            "primary_agent": agents[0] if agents else "meta-orchestrator",
            "secondary_agents": agents[1:3] if len(agents) > 1 else [],
            "reasoning": f"Detected {', '.join(agents[:2])} expertise needed based on content analysis"
        }

def main():
    """Main hook function"""
    try:
        # Read input from stdin
        input_data = sys.stdin.read()

        if not input_data.strip():
            return

        # Parse input - expect JSON with message field
        try:
            data = json.loads(input_data)
            message = data.get("message", "")
        except json.JSONDecodeError:
            # Fallback: treat input as raw message
            message = input_data

        if not message:
            return

        # Route the request
        router = AgentRouter()
        routing = router.get_routing_suggestion(message)

        # Output routing suggestion
        result = {
            "agent_routing": routing,
            "timestamp": "2025-09-25",
            "hook": "agent-router"
        }

        print(json.dumps(result, indent=2))

    except Exception as e:
        error_result = {
            "error": f"Agent routing failed: {str(e)}",
            "hook": "agent-router"
        }
        print(json.dumps(error_result, indent=2))

if __name__ == "__main__":
    main()