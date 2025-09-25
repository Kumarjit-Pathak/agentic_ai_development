#!/usr/bin/env python3
"""
Memory Manager Hook - Manages project memory, plans, and reflection data
"""

import json
import sys
import os
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

class MemoryManager:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.memory_dir = self.project_root / ".claude" / "memory"
        self.plans_dir = self.memory_dir / "plans"
        self.iterations_dir = self.memory_dir / "iterations"
        self.decisions_dir = self.memory_dir / "decisions"
        self.constraints_dir = self.memory_dir / "constraints"

        # Ensure directories exist
        for directory in [self.memory_dir, self.plans_dir, self.iterations_dir,
                         self.decisions_dir, self.constraints_dir]:
            directory.mkdir(parents=True, exist_ok=True)

    def create_project_plan(self, plan_data: Dict) -> str:
        """Create a new project plan and return its ID"""
        plan_id = self._generate_plan_id(plan_data.get("title", "Untitled Project"))

        plan_structure = {
            "id": plan_id,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "status": "active",
            "metadata": {
                "title": plan_data.get("title", "Untitled Project"),
                "description": plan_data.get("description", ""),
                "project_type": plan_data.get("project_type", "data_science"),
                "priority": plan_data.get("priority", "medium"),
                "estimated_duration": plan_data.get("estimated_duration", "unknown")
            },
            "problem_definition": {
                "business_problem": plan_data.get("business_problem", ""),
                "technical_challenge": plan_data.get("technical_challenge", ""),
                "success_criteria": plan_data.get("success_criteria", []),
                "constraints": plan_data.get("constraints", [])
            },
            "strategy": {
                "approach": plan_data.get("approach", ""),
                "methodology": plan_data.get("methodology", ""),
                "phases": plan_data.get("phases", []),
                "agent_assignments": plan_data.get("agent_assignments", {})
            },
            "progress": {
                "current_phase": 0,
                "completed_tasks": [],
                "active_tasks": [],
                "pending_tasks": plan_data.get("phases", []),
                "progress_percentage": 0
            },
            "quality_gates": {
                "standards": plan_data.get("quality_standards", {}),
                "checkpoints": plan_data.get("checkpoints", []),
                "validation_criteria": plan_data.get("validation_criteria", [])
            }
        }

        # Save plan to file
        plan_file = self.plans_dir / f"{plan_id}.json"
        with open(plan_file, 'w') as f:
            json.dump(plan_structure, f, indent=2)

        return plan_id

    def update_plan_progress(self, plan_id: str, updates: Dict) -> bool:
        """Update progress information for a plan"""
        plan_file = self.plans_dir / f"{plan_id}.json"

        if not plan_file.exists():
            return False

        with open(plan_file, 'r') as f:
            plan = json.load(f)

        # Update progress fields
        if "completed_tasks" in updates:
            plan["progress"]["completed_tasks"].extend(updates["completed_tasks"])
            # Remove from active/pending tasks
            for task in updates["completed_tasks"]:
                if task in plan["progress"]["active_tasks"]:
                    plan["progress"]["active_tasks"].remove(task)
                if task in plan["progress"]["pending_tasks"]:
                    plan["progress"]["pending_tasks"].remove(task)

        if "active_tasks" in updates:
            plan["progress"]["active_tasks"] = updates["active_tasks"]

        if "current_phase" in updates:
            plan["progress"]["current_phase"] = updates["current_phase"]

        # Calculate progress percentage
        total_tasks = len(plan["progress"]["completed_tasks"]) + \
                     len(plan["progress"]["active_tasks"]) + \
                     len(plan["progress"]["pending_tasks"])

        if total_tasks > 0:
            plan["progress"]["progress_percentage"] = \
                (len(plan["progress"]["completed_tasks"]) / total_tasks) * 100

        plan["updated_at"] = datetime.now().isoformat()

        # Save updated plan
        with open(plan_file, 'w') as f:
            json.dump(plan, f, indent=2)

        return True

    def create_iteration_reflection(self, plan_id: str, iteration_data: Dict) -> str:
        """Create an iteration reflection record"""
        iteration_id = f"{plan_id}_iter_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        reflection = {
            "id": iteration_id,
            "plan_id": plan_id,
            "created_at": datetime.now().isoformat(),
            "iteration_number": iteration_data.get("iteration_number", 1),
            "objectives": {
                "planned": iteration_data.get("planned_objectives", []),
                "actual": iteration_data.get("actual_objectives", []),
                "achieved": iteration_data.get("achieved_objectives", [])
            },
            "work_completed": {
                "tasks": iteration_data.get("completed_tasks", []),
                "deliverables": iteration_data.get("deliverables", []),
                "quality_score": iteration_data.get("quality_score", 0),
                "time_spent": iteration_data.get("time_spent", "unknown")
            },
            "challenges": {
                "blockers": iteration_data.get("blockers", []),
                "issues": iteration_data.get("issues", []),
                "solutions_applied": iteration_data.get("solutions_applied", [])
            },
            "learnings": {
                "what_worked": iteration_data.get("what_worked", []),
                "what_failed": iteration_data.get("what_failed", []),
                "insights": iteration_data.get("insights", []),
                "recommendations": iteration_data.get("recommendations", [])
            },
            "next_iteration": {
                "planned_focus": iteration_data.get("next_focus", ""),
                "adjustments": iteration_data.get("adjustments", []),
                "risk_mitigation": iteration_data.get("risk_mitigation", [])
            }
        }

        # Save reflection
        reflection_file = self.iterations_dir / f"{iteration_id}.json"
        with open(reflection_file, 'w') as f:
            json.dump(reflection, f, indent=2)

        return iteration_id

    def record_decision(self, plan_id: str, decision_data: Dict) -> str:
        """Record a significant project decision"""
        decision_id = f"{plan_id}_dec_{hashlib.md5(decision_data.get('title', '').encode()).hexdigest()[:8]}"

        decision = {
            "id": decision_id,
            "plan_id": plan_id,
            "created_at": datetime.now().isoformat(),
            "title": decision_data.get("title", ""),
            "description": decision_data.get("description", ""),
            "context": decision_data.get("context", ""),
            "options_considered": decision_data.get("options", []),
            "decision_made": decision_data.get("decision", ""),
            "rationale": decision_data.get("rationale", ""),
            "decision_maker": decision_data.get("decision_maker", "strategic-planner"),
            "impact": {
                "scope": decision_data.get("impact_scope", ""),
                "agents_affected": decision_data.get("agents_affected", []),
                "timeline_impact": decision_data.get("timeline_impact", "none")
            },
            "follow_up": {
                "actions_required": decision_data.get("actions_required", []),
                "monitoring_needed": decision_data.get("monitoring_needed", False),
                "review_date": decision_data.get("review_date", "")
            }
        }

        # Save decision
        decision_file = self.decisions_dir / f"{decision_id}.json"
        with open(decision_file, 'w') as f:
            json.dump(decision, f, indent=2)

        return decision_id

    def manage_constraints(self, plan_id: str, constraint_data: Dict, operation: str = "add") -> bool:
        """Add, update, or remove project constraints"""
        constraints_file = self.constraints_dir / f"{plan_id}_constraints.json"

        # Load existing constraints
        constraints = {"constraints": [], "created_at": datetime.now().isoformat()}
        if constraints_file.exists():
            with open(constraints_file, 'r') as f:
                constraints = json.load(f)

        if operation == "add":
            constraint = {
                "id": hashlib.md5(constraint_data.get("title", "").encode()).hexdigest()[:8],
                "title": constraint_data.get("title", ""),
                "description": constraint_data.get("description", ""),
                "type": constraint_data.get("type", "requirement"),  # requirement, preference, restriction
                "priority": constraint_data.get("priority", "medium"),
                "scope": constraint_data.get("scope", "global"),  # global, phase-specific, agent-specific
                "enforcement_level": constraint_data.get("enforcement", "strict"),  # strict, flexible, advisory
                "created_at": datetime.now().isoformat(),
                "status": "active"
            }
            constraints["constraints"].append(constraint)

        elif operation == "update":
            constraint_id = constraint_data.get("id")
            for i, constraint in enumerate(constraints["constraints"]):
                if constraint["id"] == constraint_id:
                    constraints["constraints"][i].update(constraint_data)
                    constraints["constraints"][i]["updated_at"] = datetime.now().isoformat()
                    break

        elif operation == "remove":
            constraint_id = constraint_data.get("id")
            constraints["constraints"] = [c for c in constraints["constraints"]
                                        if c["id"] != constraint_id]

        constraints["updated_at"] = datetime.now().isoformat()

        # Save constraints
        with open(constraints_file, 'w') as f:
            json.dump(constraints, f, indent=2)

        return True

    def get_plan_memory(self, plan_id: str) -> Optional[Dict]:
        """Retrieve complete memory for a plan"""
        plan_file = self.plans_dir / f"{plan_id}.json"

        if not plan_file.exists():
            return None

        with open(plan_file, 'r') as f:
            plan = json.load(f)

        # Gather related memories
        memory = {
            "plan": plan,
            "iterations": self._get_plan_iterations(plan_id),
            "decisions": self._get_plan_decisions(plan_id),
            "constraints": self._get_plan_constraints(plan_id)
        }

        return memory

    def _get_plan_iterations(self, plan_id: str) -> List[Dict]:
        """Get all iteration reflections for a plan"""
        iterations = []
        for file in self.iterations_dir.glob(f"{plan_id}_iter_*.json"):
            with open(file, 'r') as f:
                iterations.append(json.load(f))
        return sorted(iterations, key=lambda x: x["created_at"])

    def _get_plan_decisions(self, plan_id: str) -> List[Dict]:
        """Get all decisions for a plan"""
        decisions = []
        for file in self.decisions_dir.glob(f"{plan_id}_dec_*.json"):
            with open(file, 'r') as f:
                decisions.append(json.load(f))
        return sorted(decisions, key=lambda x: x["created_at"])

    def _get_plan_constraints(self, plan_id: str) -> Dict:
        """Get all constraints for a plan"""
        constraints_file = self.constraints_dir / f"{plan_id}_constraints.json"
        if constraints_file.exists():
            with open(constraints_file, 'r') as f:
                return json.load(f)
        return {"constraints": []}

    def _generate_plan_id(self, title: str) -> str:
        """Generate a unique plan ID"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        title_hash = hashlib.md5(title.encode()).hexdigest()[:8]
        return f"plan_{timestamp}_{title_hash}"

    def query_memory(self, query: Dict) -> List[Dict]:
        """Query memory based on various criteria"""
        results = []

        # Search plans
        if query.get("search_plans", True):
            for plan_file in self.plans_dir.glob("*.json"):
                with open(plan_file, 'r') as f:
                    plan = json.load(f)
                    if self._matches_query(plan, query):
                        results.append({"type": "plan", "data": plan})

        # Search iterations
        if query.get("search_iterations", True):
            for iteration_file in self.iterations_dir.glob("*.json"):
                with open(iteration_file, 'r') as f:
                    iteration = json.load(f)
                    if self._matches_query(iteration, query):
                        results.append({"type": "iteration", "data": iteration})

        return results

    def _matches_query(self, item: Dict, query: Dict) -> bool:
        """Check if an item matches query criteria"""
        # Implement basic text search
        if "text" in query:
            text = query["text"].lower()
            item_text = json.dumps(item).lower()
            if text not in item_text:
                return False

        # Check date range
        if "date_from" in query or "date_to" in query:
            item_date = item.get("created_at", "")
            if "date_from" in query and item_date < query["date_from"]:
                return False
            if "date_to" in query and item_date > query["date_to"]:
                return False

        # Check status
        if "status" in query and item.get("status") != query["status"]:
            return False

        return True

def main():
    """Main hook function"""
    try:
        input_data = sys.stdin.read()

        if not input_data.strip():
            return

        try:
            data = json.loads(input_data)
        except json.JSONDecodeError:
            print(json.dumps({"error": "Invalid JSON input", "hook": "memory-manager"}))
            return

        manager = MemoryManager()
        operation = data.get("operation", "")

        result = {"hook": "memory-manager", "timestamp": datetime.now().isoformat()}

        if operation == "create_plan":
            plan_id = manager.create_project_plan(data.get("plan_data", {}))
            result["success"] = True
            result["plan_id"] = plan_id
            result["message"] = f"Created plan: {plan_id}"

        elif operation == "update_progress":
            plan_id = data.get("plan_id", "")
            success = manager.update_plan_progress(plan_id, data.get("updates", {}))
            result["success"] = success
            result["message"] = "Progress updated" if success else "Plan not found"

        elif operation == "create_reflection":
            plan_id = data.get("plan_id", "")
            iteration_id = manager.create_iteration_reflection(plan_id, data.get("iteration_data", {}))
            result["success"] = True
            result["iteration_id"] = iteration_id
            result["message"] = f"Created reflection: {iteration_id}"

        elif operation == "record_decision":
            plan_id = data.get("plan_id", "")
            decision_id = manager.record_decision(plan_id, data.get("decision_data", {}))
            result["success"] = True
            result["decision_id"] = decision_id
            result["message"] = f"Recorded decision: {decision_id}"

        elif operation == "manage_constraints":
            plan_id = data.get("plan_id", "")
            operation_type = data.get("constraint_operation", "add")
            success = manager.manage_constraints(plan_id, data.get("constraint_data", {}), operation_type)
            result["success"] = success
            result["message"] = f"Constraint {operation_type} completed"

        elif operation == "get_memory":
            plan_id = data.get("plan_id", "")
            memory = manager.get_plan_memory(plan_id)
            result["success"] = memory is not None
            result["memory"] = memory
            result["message"] = "Memory retrieved" if memory else "Plan not found"

        elif operation == "query":
            query_results = manager.query_memory(data.get("query", {}))
            result["success"] = True
            result["results"] = query_results
            result["message"] = f"Found {len(query_results)} results"

        else:
            result["success"] = False
            result["error"] = f"Unknown operation: {operation}"

        print(json.dumps(result, indent=2))

    except Exception as e:
        error_result = {
            "error": f"Memory management failed: {str(e)}",
            "hook": "memory-manager",
            "success": False
        }
        print(json.dumps(error_result, indent=2))

if __name__ == "__main__":
    main()