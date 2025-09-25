#!/usr/bin/env python3
"""
Context Injector Hook - Injects relevant project context based on agent type
"""

import json
import sys
import os
from pathlib import Path
from typing import Dict, List, Optional

class ContextInjector:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.context_map = {
            "data-analyzer": {
                "files": ["*.xlsx", "*.csv", "*.py"],
                "context": "Data files and analysis scripts in optimizer insight project",
                "focus": "Excel constraint mappings, SKU data, shelf constraints"
            },
            "dashboard-developer": {
                "files": ["*.py", "constraint_analysis_dashboard*.py", ".env"],
                "context": "Streamlit dashboard application with constraint analysis features",
                "focus": "UI components, data visualization, user interaction patterns"
            },
            "optimization-expert": {
                "files": ["*constraint*.xlsx", "*mapping*.xlsx", "*.py"],
                "context": "Constraint optimization problem with retail space allocation",
                "focus": "Mathematical models, constraint definitions, optimization algorithms"
            },
            "data-science-researcher": {
                "files": ["*.xlsx", "*.py", "*.ipynb", "*.md"],
                "context": "Advanced research environment for mathematical modeling and statistical analysis",
                "focus": "Research methodologies, advanced statistics, mathematical modeling, hypothesis testing"
            },
            "ml-concept-tester": {
                "files": ["*.py", "*.ipynb", "*.pkl", "*.joblib"],
                "context": "Machine learning experimentation and AI concept testing environment",
                "focus": "ML/DL model development, AI experimentation, concept validation, performance testing"
            },
            "strategic-planner": {
                "files": ["*.md", ".claude/memory/**", ".claude/templates/**", "*.json"],
                "context": "Strategic planning and project memory management environment",
                "focus": "Project planning, iteration reflection, memory management, constraint tracking"
            },
            "meta-orchestrator": {
                "files": ["*.md", "*.py", ".claude/**"],
                "context": "Full project overview with agent coordination capabilities",
                "focus": "Project structure, agent capabilities, workflow coordination"
            }
        }

    def get_project_context(self, agent_type: str) -> Dict:
        """Get relevant project context for specific agent"""
        if agent_type not in self.context_map:
            agent_type = "meta-orchestrator"

        config = self.context_map[agent_type]

        # Get file structure
        relevant_files = self._find_relevant_files(config["files"])

        # Build context
        context = {
            "agent_type": agent_type,
            "project_name": "Optimizer Insight - Constraint Analysis Dashboard",
            "project_description": config["context"],
            "focus_areas": config["focus"],
            "relevant_files": relevant_files[:10],  # Limit to top 10
            "project_structure": self._get_basic_structure(),
            "technologies": ["Python", "Streamlit", "Pandas", "OpenAI", "LangChain"],
            "domain": "Retail optimization, constraint analysis, business intelligence"
        }

        return context

    def _find_relevant_files(self, patterns: List[str]) -> List[str]:
        """Find files matching the given patterns"""
        relevant_files = []

        try:
            for pattern in patterns:
                if "**" in pattern:
                    # Handle recursive patterns
                    pattern_path = self.project_root / pattern.replace("**", "")
                    if pattern_path.parent.exists():
                        for file in pattern_path.parent.rglob(pattern_path.name):
                            if file.is_file():
                                relevant_files.append(str(file.relative_to(self.project_root)))
                else:
                    # Handle simple glob patterns
                    for file in self.project_root.glob(pattern):
                        if file.is_file():
                            relevant_files.append(str(file.relative_to(self.project_root)))
        except Exception:
            pass  # Handle permission errors gracefully

        return relevant_files

    def _get_basic_structure(self) -> Dict:
        """Get basic project structure"""
        try:
            structure = {
                "root_files": [],
                "directories": [],
                "key_files": []
            }

            # List root files
            for item in self.project_root.iterdir():
                if item.is_file():
                    structure["root_files"].append(item.name)
                elif item.is_dir() and not item.name.startswith('.'):
                    structure["directories"].append(item.name)

            # Identify key files
            key_patterns = ["*dashboard*.py", "*.md", ".env", "requirements*.txt"]
            for pattern in key_patterns:
                for file in self.project_root.glob(pattern):
                    if file.is_file():
                        structure["key_files"].append(file.name)

            return structure

        except Exception:
            return {"error": "Could not read project structure"}

    def inject_context(self, agent_type: str, original_message: str) -> str:
        """Inject context into the message"""
        context = self.get_project_context(agent_type)

        context_section = f"""

## Project Context
**Agent Role**: {context['agent_type']}
**Project**: {context['project_name']}
**Description**: {context['project_description']}
**Focus Areas**: {context['focus_areas']}

**Key Technologies**: {', '.join(context['technologies'])}
**Domain**: {context['domain']}

**Relevant Files**:
{chr(10).join(f"- {file}" for file in context['relevant_files'][:5])}

---

"""

        return context_section + original_message

def main():
    """Main hook function"""
    try:
        # Read input from stdin
        input_data = sys.stdin.read()

        if not input_data.strip():
            return

        # Parse input
        try:
            data = json.loads(input_data)
            message = data.get("message", "")
            agent_type = data.get("agent_type", "meta-orchestrator")
        except json.JSONDecodeError:
            # Fallback
            message = input_data
            agent_type = "meta-orchestrator"

        if not message:
            return

        # Inject context
        injector = ContextInjector()
        enhanced_message = injector.inject_context(agent_type, message)

        # Output enhanced message
        result = {
            "enhanced_message": enhanced_message,
            "context_injected": True,
            "agent_type": agent_type,
            "hook": "context-injector"
        }

        print(json.dumps(result, indent=2))

    except Exception as e:
        error_result = {
            "error": f"Context injection failed: {str(e)}",
            "original_message": input_data,
            "hook": "context-injector"
        }
        print(json.dumps(error_result, indent=2))

if __name__ == "__main__":
    main()