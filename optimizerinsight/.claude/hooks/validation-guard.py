#!/usr/bin/env python3
"""
Validation Guard Hook - Validates inputs and outputs for agent interactions
"""

import json
import sys
import re
from typing import Dict, List, Optional, Union

class ValidationGuard:
    def __init__(self):
        self.security_patterns = [
            r"rm\s+-rf",
            r"del\s+/[sS]",
            r"format\s+c:",
            r"__import__",
            r"eval\s*\(",
            r"exec\s*\(",
            r"subprocess\.call",
            r"os\.system"
        ]

        self.required_fields = {
            "data-analyzer": ["data_source", "analysis_type"],
            "dashboard-developer": ["component_type", "data_requirements"],
            "optimization-expert": ["problem_type", "constraints"],
            "data-science-researcher": ["research_question", "methodology"],
            "ml-concept-tester": ["model_type", "experiment_objective"],
            "meta-orchestrator": ["task_complexity", "coordination_requirements"]
        }

        self.output_standards = {
            "code_quality": ["proper_imports", "error_handling", "documentation"],
            "data_integrity": ["validation_checks", "type_safety", "boundary_conditions"],
            "security": ["no_hardcoded_secrets", "input_validation", "safe_operations"]
        }

    def validate_security(self, content: str) -> Dict:
        """Check for security issues in the content"""
        issues = []

        for pattern in self.security_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                issues.append(f"Potentially dangerous pattern detected: {pattern}")

        # Check for hardcoded secrets
        secret_patterns = [
            r"password\s*=\s*['\"].*['\"]",
            r"api_key\s*=\s*['\"].*['\"]",
            r"secret\s*=\s*['\"].*['\"]",
            r"token\s*=\s*['\"].*['\"]"
        ]

        for pattern in secret_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                issues.append("Hardcoded secret detected - use environment variables instead")

        return {
            "secure": len(issues) == 0,
            "issues": issues
        }

    def validate_agent_requirements(self, agent_type: str, request_data: Dict) -> Dict:
        """Validate agent-specific requirements"""
        if agent_type not in self.required_fields:
            return {"valid": True, "message": "No specific requirements for this agent type"}

        required = self.required_fields[agent_type]
        missing = []

        for field in required:
            if field not in request_data:
                missing.append(field)

        return {
            "valid": len(missing) == 0,
            "missing_fields": missing,
            "message": f"Missing required fields: {missing}" if missing else "All requirements met"
        }

    def validate_output_quality(self, output: str, agent_type: str) -> Dict:
        """Validate output quality standards"""
        issues = []

        # Check for basic code quality if output contains code
        if "```python" in output or "def " in output or "class " in output:
            # Check for imports at the top
            if "import " not in output.split('\n')[0:5]:
                issues.append("Code should include proper imports")

            # Check for basic error handling
            if "try:" not in output and "except:" not in output and len(output) > 100:
                issues.append("Consider adding error handling for production code")

        # Check for documentation
        if agent_type != "meta-orchestrator" and len(output) > 200:
            if '"""' not in output and "# " not in output:
                issues.append("Code should include documentation or comments")

        return {
            "quality_score": max(0, 100 - len(issues) * 25),
            "issues": issues,
            "recommendations": self._get_quality_recommendations(agent_type)
        }

    def _get_quality_recommendations(self, agent_type: str) -> List[str]:
        """Get quality recommendations for specific agent types"""
        base_recommendations = [
            "Include proper error handling",
            "Add type hints where appropriate",
            "Use descriptive variable names",
            "Follow PEP 8 style guidelines"
        ]

        agent_specific = {
            "data-analyzer": [
                "Validate data inputs before processing",
                "Handle missing or malformed data gracefully",
                "Include data quality checks"
            ],
            "dashboard-developer": [
                "Optimize for user experience",
                "Include loading states for slow operations",
                "Validate user inputs"
            ],
            "optimization-expert": [
                "Document mathematical assumptions",
                "Include solution validation",
                "Explain algorithmic complexity"
            ],
            "data-science-researcher": [
                "Document research methodology and assumptions",
                "Include statistical significance testing",
                "Provide reproducible research artifacts",
                "Validate experimental design"
            ],
            "ml-concept-tester": [
                "Include proper train/validation/test splits",
                "Document model architecture and hyperparameters",
                "Provide performance metrics and baselines",
                "Include experiment reproducibility requirements"
            ]
        }

        return base_recommendations + agent_specific.get(agent_type, [])

    def validate_request(self, request_data: Dict) -> Dict:
        """Main validation function for incoming requests"""
        agent_type = request_data.get("agent_type", "meta-orchestrator")
        message = request_data.get("message", "")

        # Security validation
        security_check = self.validate_security(message)

        # Requirements validation
        requirements_check = self.validate_agent_requirements(agent_type, request_data)

        # Overall validation result
        validation_result = {
            "valid": security_check["secure"] and requirements_check["valid"],
            "security": security_check,
            "requirements": requirements_check,
            "agent_type": agent_type,
            "timestamp": "2025-09-25"
        }

        return validation_result

    def validate_response(self, response: str, agent_type: str) -> Dict:
        """Validate agent response quality"""
        security_check = self.validate_security(response)
        quality_check = self.validate_output_quality(response, agent_type)

        return {
            "valid": security_check["secure"] and quality_check["quality_score"] >= 50,
            "security": security_check,
            "quality": quality_check,
            "agent_type": agent_type
        }

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
            validation_type = data.get("type", "request")  # "request" or "response"
        except json.JSONDecodeError:
            # Fallback: treat as request validation with raw message
            data = {"message": input_data, "type": "request"}
            validation_type = "request"

        # Perform validation
        guard = ValidationGuard()

        if validation_type == "request":
            result = guard.validate_request(data)
        else:
            response_text = data.get("response", "")
            agent_type = data.get("agent_type", "meta-orchestrator")
            result = guard.validate_response(response_text, agent_type)

        result["hook"] = "validation-guard"
        print(json.dumps(result, indent=2))

    except Exception as e:
        error_result = {
            "error": f"Validation failed: {str(e)}",
            "valid": False,
            "hook": "validation-guard"
        }
        print(json.dumps(error_result, indent=2))

if __name__ == "__main__":
    main()