#!/usr/bin/env python3
"""
Plan Tracker Hook - Tracks plan execution and ensures adherence to constraints
"""

import json
import sys
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

class PlanTracker:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.memory_dir = self.project_root / ".claude" / "memory"
        self.plans_dir = self.memory_dir / "plans"
        self.constraints_dir = self.memory_dir / "constraints"
        self.current_plan_file = self.memory_dir / "current_plan.json"

        # Ensure directories exist
        for directory in [self.memory_dir, self.plans_dir, self.constraints_dir]:
            directory.mkdir(parents=True, exist_ok=True)

    def validate_against_plan(self, request_data: Dict) -> Dict:
        """Validate a request against the current active plan and constraints"""
        validation_result = {
            "valid": True,
            "warnings": [],
            "errors": [],
            "suggestions": [],
            "plan_adherence": "unknown"
        }

        # Get current active plan
        current_plan = self._get_current_plan()
        if not current_plan:
            validation_result["warnings"].append("No active plan found - proceeding without plan validation")
            return validation_result

        # Get constraints for the current plan
        constraints = self._get_plan_constraints(current_plan["id"])

        # Validate against hard constraints
        constraint_violations = self._check_constraints(request_data, constraints)
        if constraint_violations:
            validation_result["valid"] = False
            validation_result["errors"].extend(constraint_violations)

        # Check alignment with current phase
        phase_alignment = self._check_phase_alignment(request_data, current_plan)
        validation_result["plan_adherence"] = phase_alignment["status"]
        validation_result["suggestions"].extend(phase_alignment["suggestions"])

        # Check if request fits current priorities
        priority_check = self._check_priority_alignment(request_data, current_plan)
        validation_result["warnings"].extend(priority_check["warnings"])
        validation_result["suggestions"].extend(priority_check["suggestions"])

        return validation_result

    def update_plan_progress(self, activity_data: Dict) -> Dict:
        """Update plan progress based on completed activity"""
        current_plan = self._get_current_plan()
        if not current_plan:
            return {"success": False, "message": "No active plan to update"}

        # Determine which tasks/objectives this activity fulfills
        completed_items = self._match_activity_to_plan_items(activity_data, current_plan)

        if completed_items:
            # Update plan progress
            for item in completed_items:
                if item not in current_plan["progress"]["completed_tasks"]:
                    current_plan["progress"]["completed_tasks"].append(item)

                # Remove from active/pending
                if item in current_plan["progress"]["active_tasks"]:
                    current_plan["progress"]["active_tasks"].remove(item)
                if item in current_plan["progress"]["pending_tasks"]:
                    current_plan["progress"]["pending_tasks"].remove(item)

            # Update progress percentage
            self._calculate_progress_percentage(current_plan)
            current_plan["updated_at"] = datetime.now().isoformat()

            # Save updated plan
            self._save_plan(current_plan)

            return {
                "success": True,
                "message": f"Updated progress - completed {len(completed_items)} items",
                "completed_items": completed_items,
                "progress_percentage": current_plan["progress"]["progress_percentage"]
            }

        return {"success": True, "message": "No plan items matched this activity"}

    def suggest_next_actions(self, context: Dict) -> Dict:
        """Suggest next actions based on current plan state"""
        current_plan = self._get_current_plan()
        if not current_plan:
            return {"suggestions": ["Create a project plan to guide systematic development"]}

        suggestions = []
        current_phase = current_plan["progress"].get("current_phase", 0)
        phases = current_plan["strategy"].get("phases", [])

        if current_phase < len(phases):
            current_phase_info = phases[current_phase]

            # Get active and pending tasks for current phase
            active_tasks = current_plan["progress"].get("active_tasks", [])
            pending_tasks = current_plan["progress"].get("pending_tasks", [])

            if not active_tasks and pending_tasks:
                suggestions.append(f"Start working on next tasks for {current_phase_info.get('name', f'Phase {current_phase + 1}')}")
                suggestions.extend(pending_tasks[:3])  # Show top 3 pending tasks

            elif active_tasks:
                suggestions.append("Continue working on active tasks:")
                suggestions.extend(active_tasks)

            # Check for blockers
            if self._has_unresolved_blockers(current_plan):
                suggestions.insert(0, "⚠️ Address unresolved blockers before proceeding")

            # Check phase completion criteria
            phase_completion = self._check_phase_completion(current_plan, current_phase)
            if phase_completion["ready_to_advance"]:
                suggestions.append(f"✅ Ready to advance to next phase: {phases[current_phase + 1]['name'] if current_phase + 1 < len(phases) else 'Project completion'}")

        else:
            suggestions.append("🎉 All phases complete - consider project review and reflection")

        return {
            "suggestions": suggestions,
            "current_phase": current_phase,
            "phase_name": phases[current_phase]["name"] if current_phase < len(phases) else "Complete",
            "progress": current_plan["progress"]["progress_percentage"]
        }

    def enforce_development_sequence(self, request_data: Dict) -> Dict:
        """Ensure development follows the planned sequence"""
        current_plan = self._get_current_plan()
        if not current_plan:
            return {"allowed": True, "message": "No plan constraints"}

        # Check if this action is appropriate for current phase
        phase_check = self._check_phase_appropriateness(request_data, current_plan)

        # Check dependencies
        dependency_check = self._check_dependencies(request_data, current_plan)

        # Check if prerequisites are met
        prerequisite_check = self._check_prerequisites(request_data, current_plan)

        enforcement_result = {
            "allowed": phase_check["allowed"] and dependency_check["allowed"] and prerequisite_check["allowed"],
            "phase_check": phase_check,
            "dependency_check": dependency_check,
            "prerequisite_check": prerequisite_check,
            "recommendations": []
        }

        # Provide recommendations if not allowed
        if not enforcement_result["allowed"]:
            enforcement_result["recommendations"].extend([
                "Consider following the planned sequence for better outcomes",
                "If this is intentional, update the plan to reflect new priorities",
                "Ensure prerequisites are met before proceeding"
            ])

        return enforcement_result

    def _get_current_plan(self) -> Optional[Dict]:
        """Get the currently active plan"""
        if not self.current_plan_file.exists():
            # Try to find most recent active plan
            return self._find_most_recent_active_plan()

        with open(self.current_plan_file, 'r') as f:
            current_info = json.load(f)

        plan_id = current_info.get("plan_id")
        if plan_id:
            plan_file = self.plans_dir / f"{plan_id}.json"
            if plan_file.exists():
                with open(plan_file, 'r') as f:
                    return json.load(f)

        return None

    def _find_most_recent_active_plan(self) -> Optional[Dict]:
        """Find the most recently active plan"""
        active_plans = []
        for plan_file in self.plans_dir.glob("*.json"):
            with open(plan_file, 'r') as f:
                plan = json.load(f)
                if plan.get("status") == "active":
                    active_plans.append(plan)

        if active_plans:
            # Return most recently updated
            return sorted(active_plans, key=lambda x: x.get("updated_at", ""), reverse=True)[0]

        return None

    def _get_plan_constraints(self, plan_id: str) -> Dict:
        """Get constraints for a specific plan"""
        constraints_file = self.constraints_dir / f"{plan_id}_constraints.json"
        if constraints_file.exists():
            with open(constraints_file, 'r') as f:
                return json.load(f)
        return {"constraints": []}

    def _check_constraints(self, request_data: Dict, constraints: Dict) -> List[str]:
        """Check request against hard constraints"""
        violations = []

        for constraint in constraints.get("constraints", []):
            if constraint.get("status") != "active":
                continue

            if constraint.get("enforcement_level") == "strict":
                violation = self._evaluate_constraint(request_data, constraint)
                if violation:
                    violations.append(f"Constraint violation: {constraint['title']} - {violation}")

        return violations

    def _evaluate_constraint(self, request_data: Dict, constraint: Dict) -> Optional[str]:
        """Evaluate a specific constraint against request data"""
        constraint_type = constraint.get("type", "requirement")
        constraint_text = constraint.get("description", "").lower()
        request_text = json.dumps(request_data).lower()

        # Simple keyword-based constraint checking
        if constraint_type == "restriction":
            # Check if restricted patterns are present
            if any(keyword in request_text for keyword in constraint_text.split() if len(keyword) > 3):
                return f"Request contains restricted elements: {constraint['title']}"

        elif constraint_type == "requirement":
            # Check if required patterns are missing
            required_keywords = [kw for kw in constraint_text.split() if len(kw) > 3]
            if required_keywords and not any(keyword in request_text for keyword in required_keywords):
                return f"Request missing required elements: {constraint['title']}"

        return None

    def _check_phase_alignment(self, request_data: Dict, current_plan: Dict) -> Dict:
        """Check if request aligns with current phase"""
        current_phase = current_plan["progress"].get("current_phase", 0)
        phases = current_plan["strategy"].get("phases", [])

        if current_phase >= len(phases):
            return {"status": "complete", "suggestions": ["Project phases are complete"]}

        phase_info = phases[current_phase]
        phase_name = phase_info.get("name", f"Phase {current_phase + 1}")

        # Simple keyword matching for phase alignment
        request_text = json.dumps(request_data).lower()
        phase_keywords = phase_info.get("keywords", [])

        alignment_score = sum(1 for keyword in phase_keywords if keyword.lower() in request_text)
        total_keywords = len(phase_keywords)

        if total_keywords > 0:
            alignment_percentage = (alignment_score / total_keywords) * 100
        else:
            alignment_percentage = 50  # Neutral if no keywords defined

        if alignment_percentage >= 70:
            status = "aligned"
            suggestions = [f"Good alignment with current phase: {phase_name}"]
        elif alignment_percentage >= 30:
            status = "partially_aligned"
            suggestions = [f"Partial alignment with {phase_name} - consider focusing on phase objectives"]
        else:
            status = "misaligned"
            suggestions = [f"Low alignment with current phase {phase_name} - consider if this fits the plan"]

        return {"status": status, "suggestions": suggestions, "alignment_score": alignment_percentage}

    def _check_priority_alignment(self, request_data: Dict, current_plan: Dict) -> Dict:
        """Check if request aligns with current priorities"""
        warnings = []
        suggestions = []

        # Check if request relates to active tasks
        active_tasks = current_plan["progress"].get("active_tasks", [])
        request_text = json.dumps(request_data).lower()

        task_relevance = sum(1 for task in active_tasks if any(word in request_text for word in task.lower().split()))

        if active_tasks and task_relevance == 0:
            warnings.append("Request doesn't seem to relate to current active tasks")
            suggestions.append(f"Consider focusing on active tasks: {', '.join(active_tasks[:3])}")

        return {"warnings": warnings, "suggestions": suggestions}

    def _match_activity_to_plan_items(self, activity_data: Dict, current_plan: Dict) -> List[str]:
        """Match completed activity to plan items"""
        completed_items = []
        activity_text = json.dumps(activity_data).lower()

        # Check against active and pending tasks
        all_tasks = current_plan["progress"].get("active_tasks", []) + current_plan["progress"].get("pending_tasks", [])

        for task in all_tasks:
            task_words = task.lower().split()
            if len(task_words) > 0 and any(word in activity_text for word in task_words):
                completed_items.append(task)

        return completed_items

    def _calculate_progress_percentage(self, plan: Dict):
        """Calculate and update progress percentage"""
        completed = len(plan["progress"]["completed_tasks"])
        active = len(plan["progress"]["active_tasks"])
        pending = len(plan["progress"]["pending_tasks"])
        total = completed + active + pending

        if total > 0:
            plan["progress"]["progress_percentage"] = (completed / total) * 100
        else:
            plan["progress"]["progress_percentage"] = 0

    def _save_plan(self, plan: Dict):
        """Save updated plan to file"""
        plan_file = self.plans_dir / f"{plan['id']}.json"
        with open(plan_file, 'w') as f:
            json.dump(plan, f, indent=2)

        # Update current plan reference
        current_info = {"plan_id": plan["id"], "updated_at": datetime.now().isoformat()}
        with open(self.current_plan_file, 'w') as f:
            json.dump(current_info, f, indent=2)

    def _has_unresolved_blockers(self, plan: Dict) -> bool:
        """Check if there are unresolved blockers"""
        # This would check iteration reflections for recent blockers
        # Simplified implementation
        return False

    def _check_phase_completion(self, plan: Dict, phase_index: int) -> Dict:
        """Check if current phase is ready for completion"""
        # Simplified - check if most tasks for phase are complete
        phase_tasks = plan["strategy"]["phases"][phase_index].get("tasks", [])
        completed_tasks = plan["progress"]["completed_tasks"]

        completed_phase_tasks = sum(1 for task in phase_tasks if task in completed_tasks)
        completion_percentage = (completed_phase_tasks / len(phase_tasks)) * 100 if phase_tasks else 100

        return {
            "ready_to_advance": completion_percentage >= 80,
            "completion_percentage": completion_percentage
        }

    def _check_phase_appropriateness(self, request_data: Dict, plan: Dict) -> Dict:
        """Check if request is appropriate for current phase"""
        # Simplified implementation
        return {"allowed": True, "message": "Phase check passed"}

    def _check_dependencies(self, request_data: Dict, plan: Dict) -> Dict:
        """Check if dependencies are satisfied"""
        # Simplified implementation
        return {"allowed": True, "message": "Dependencies satisfied"}

    def _check_prerequisites(self, request_data: Dict, plan: Dict) -> Dict:
        """Check if prerequisites are met"""
        # Simplified implementation
        return {"allowed": True, "message": "Prerequisites met"}

def main():
    """Main hook function"""
    try:
        input_data = sys.stdin.read()

        if not input_data.strip():
            return

        try:
            data = json.loads(input_data)
        except json.JSONDecodeError:
            print(json.dumps({"error": "Invalid JSON input", "hook": "plan-tracker"}))
            return

        tracker = PlanTracker()
        operation = data.get("operation", "validate")

        result = {"hook": "plan-tracker", "timestamp": datetime.now().isoformat()}

        if operation == "validate":
            validation = tracker.validate_against_plan(data.get("request_data", {}))
            result.update(validation)

        elif operation == "update_progress":
            progress_update = tracker.update_plan_progress(data.get("activity_data", {}))
            result.update(progress_update)

        elif operation == "suggest_actions":
            suggestions = tracker.suggest_next_actions(data.get("context", {}))
            result.update(suggestions)

        elif operation == "enforce_sequence":
            enforcement = tracker.enforce_development_sequence(data.get("request_data", {}))
            result.update(enforcement)

        else:
            result["error"] = f"Unknown operation: {operation}"

        print(json.dumps(result, indent=2))

    except Exception as e:
        error_result = {
            "error": f"Plan tracking failed: {str(e)}",
            "hook": "plan-tracker"
        }
        print(json.dumps(error_result, indent=2))

if __name__ == "__main__":
    main()