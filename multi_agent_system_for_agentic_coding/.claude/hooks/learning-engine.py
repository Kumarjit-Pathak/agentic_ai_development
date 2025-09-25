#!/usr/bin/env python3
"""
Learning Engine Hook - Continuous learning and adaptation system for multi-agent improvement
"""

import json
import sys
import os
import pickle
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
import statistics
import hashlib

@dataclass
class LearningPattern:
    pattern_id: str
    pattern_type: str  # success, failure, performance, quality
    agent_name: str
    context: Dict[str, Any]
    outcome: Dict[str, Any]
    frequency: int
    success_rate: float
    confidence_score: float
    created_at: str
    last_seen: str

@dataclass
class AdaptationRule:
    rule_id: str
    condition: Dict[str, Any]
    action: Dict[str, Any]
    agent_scope: List[str]
    priority: int
    success_count: int
    failure_count: int
    effectiveness_score: float
    created_at: str

@dataclass
class LearningInsight:
    insight_id: str
    insight_type: str
    description: str
    evidence: List[Dict[str, Any]]
    confidence_level: float
    actionable: bool
    impact_estimate: str
    agents_affected: List[str]
    created_at: str

class LearningEngine:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.learning_dir = self.project_root / ".claude" / "learning"
        self.patterns_dir = self.learning_dir / "patterns"
        self.rules_dir = self.learning_dir / "rules"
        self.insights_dir = self.learning_dir / "insights"
        self.models_dir = self.learning_dir / "models"

        # Initialize directories
        for directory in [self.learning_dir, self.patterns_dir, self.rules_dir,
                         self.insights_dir, self.models_dir]:
            directory.mkdir(parents=True, exist_ok=True)

        # Learning state
        self.patterns_cache = {}
        self.rules_cache = {}
        self.insights_cache = {}
        self.learning_history = deque(maxlen=1000)

        # Learning parameters
        self.min_pattern_frequency = 3
        self.min_confidence_threshold = 0.7
        self.adaptation_cooldown = 300  # 5 minutes

    def learn_from_interaction(self, interaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """Learn from a single agent interaction"""
        try:
            # Extract learning features
            features = self._extract_features(interaction_data)

            # Identify patterns
            patterns_found = self._identify_patterns(features)

            # Update existing patterns or create new ones
            updated_patterns = []
            for pattern in patterns_found:
                updated_pattern = self._update_or_create_pattern(pattern)
                updated_patterns.append(updated_pattern)

            # Generate insights
            new_insights = self._generate_insights(features, updated_patterns)

            # Create adaptation rules if applicable
            new_rules = self._create_adaptation_rules(new_insights)

            # Store learning event
            learning_event = {
                "timestamp": datetime.now().isoformat(),
                "interaction_id": interaction_data.get("id", ""),
                "agent": interaction_data.get("agent", ""),
                "patterns_found": len(patterns_found),
                "insights_generated": len(new_insights),
                "rules_created": len(new_rules)
            }

            self.learning_history.append(learning_event)
            self._store_learning_event(learning_event)

            return {
                "success": True,
                "patterns_identified": len(updated_patterns),
                "insights_generated": len(new_insights),
                "rules_created": len(new_rules),
                "learning_event_id": learning_event.get("timestamp")
            }

        except Exception as e:
            return {"success": False, "error": f"Learning failed: {str(e)}"}

    def get_recommendations(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Get recommendations based on learned patterns"""
        try:
            agent_name = context.get("agent", "")
            task_type = context.get("task_type", "")

            # Find relevant patterns
            relevant_patterns = self._find_relevant_patterns(context)

            # Find applicable rules
            applicable_rules = self._find_applicable_rules(context)

            # Generate recommendations
            recommendations = []

            # Pattern-based recommendations
            for pattern in relevant_patterns:
                if pattern.success_rate > 0.8 and pattern.confidence_score > 0.7:
                    recommendations.append({
                        "type": "pattern_based",
                        "recommendation": f"Apply successful pattern: {pattern.pattern_type}",
                        "confidence": pattern.confidence_score,
                        "evidence": f"Seen {pattern.frequency} times with {pattern.success_rate:.1%} success rate",
                        "pattern_id": pattern.pattern_id
                    })

            # Rule-based recommendations
            for rule in applicable_rules:
                if rule.effectiveness_score > 0.6:
                    recommendations.append({
                        "type": "rule_based",
                        "recommendation": f"Apply adaptation rule: {rule.action.get('description', 'Apply rule')}",
                        "confidence": rule.effectiveness_score,
                        "evidence": f"Rule succeeded {rule.success_count} times, failed {rule.failure_count} times",
                        "rule_id": rule.rule_id
                    })

            # Sort by confidence
            recommendations.sort(key=lambda r: r["confidence"], reverse=True)

            return {
                "success": True,
                "recommendations": recommendations[:10],  # Top 10 recommendations
                "patterns_considered": len(relevant_patterns),
                "rules_considered": len(applicable_rules)
            }

        except Exception as e:
            return {"success": False, "error": f"Failed to get recommendations: {str(e)}"}

    def analyze_performance_trends(self, agent_name: Optional[str] = None, time_range: str = "7d") -> Dict[str, Any]:
        """Analyze performance trends and learning progress"""
        try:
            end_time = datetime.now()
            if time_range == "1h":
                start_time = end_time - timedelta(hours=1)
            elif time_range == "24h":
                start_time = end_time - timedelta(days=1)
            elif time_range == "7d":
                start_time = end_time - timedelta(days=7)
            else:
                start_time = end_time - timedelta(days=7)

            # Filter learning events by time range and agent
            filtered_events = [
                event for event in self.learning_history
                if datetime.fromisoformat(event["timestamp"]) >= start_time
                and (not agent_name or event.get("agent") == agent_name)
            ]

            if not filtered_events:
                return {"success": False, "error": "No learning events found for the specified criteria"}

            # Calculate trends
            total_patterns = sum(event["patterns_found"] for event in filtered_events)
            total_insights = sum(event["insights_generated"] for event in filtered_events)
            total_rules = sum(event["rules_created"] for event in filtered_events)

            # Learning velocity (events per hour)
            hours_in_range = (end_time - start_time).total_seconds() / 3600
            learning_velocity = len(filtered_events) / hours_in_range if hours_in_range > 0 else 0

            # Get pattern effectiveness
            pattern_effectiveness = self._calculate_pattern_effectiveness(agent_name)

            # Get rule effectiveness
            rule_effectiveness = self._calculate_rule_effectiveness(agent_name)

            analysis = {
                "time_range": f"{start_time.isoformat()} to {end_time.isoformat()}",
                "agent": agent_name or "all_agents",
                "learning_events": len(filtered_events),
                "patterns_identified": total_patterns,
                "insights_generated": total_insights,
                "rules_created": total_rules,
                "learning_velocity": learning_velocity,
                "pattern_effectiveness": pattern_effectiveness,
                "rule_effectiveness": rule_effectiveness,
                "improvement_indicators": self._calculate_improvement_indicators(filtered_events)
            }

            return {"success": True, "analysis": analysis}

        except Exception as e:
            return {"success": False, "error": f"Failed to analyze trends: {str(e)}"}

    def adapt_agent_behavior(self, agent_name: str, adaptation_context: Dict[str, Any]) -> Dict[str, Any]:
        """Adapt agent behavior based on learned patterns"""
        try:
            # Find relevant adaptations
            relevant_rules = self._find_applicable_rules({
                "agent": agent_name,
                **adaptation_context
            })

            # Apply adaptations
            adaptations_applied = []
            for rule in relevant_rules:
                if rule.effectiveness_score > self.min_confidence_threshold:
                    adaptation_result = self._apply_adaptation_rule(agent_name, rule, adaptation_context)
                    if adaptation_result["success"]:
                        adaptations_applied.append(adaptation_result)

            # Update rule effectiveness based on results
            self._update_rule_effectiveness(relevant_rules, adaptation_context.get("outcome", {}))

            return {
                "success": True,
                "adaptations_applied": len(adaptations_applied),
                "adaptation_details": adaptations_applied
            }

        except Exception as e:
            return {"success": False, "error": f"Failed to adapt behavior: {str(e)}"}

    def generate_learning_report(self) -> Dict[str, Any]:
        """Generate comprehensive learning system report"""
        try:
            # System statistics
            total_patterns = len(self._load_all_patterns())
            total_rules = len(self._load_all_rules())
            total_insights = len(self._load_all_insights())

            # Top patterns by effectiveness
            patterns = self._load_all_patterns()
            top_patterns = sorted(
                patterns.values(),
                key=lambda p: p.success_rate * p.confidence_score,
                reverse=True
            )[:10]

            # Top rules by effectiveness
            rules = self._load_all_rules()
            top_rules = sorted(
                rules.values(),
                key=lambda r: r.effectiveness_score,
                reverse=True
            )[:10]

            # Recent insights
            insights = self._load_all_insights()
            recent_insights = sorted(
                insights.values(),
                key=lambda i: i.created_at,
                reverse=True
            )[:10]

            # Agent learning statistics
            agent_stats = self._calculate_agent_learning_stats()

            report = {
                "timestamp": datetime.now().isoformat(),
                "system_statistics": {
                    "total_patterns": total_patterns,
                    "total_rules": total_rules,
                    "total_insights": total_insights,
                    "learning_events": len(self.learning_history)
                },
                "top_patterns": [
                    {
                        "id": p.pattern_id,
                        "type": p.pattern_type,
                        "agent": p.agent_name,
                        "success_rate": p.success_rate,
                        "confidence": p.confidence_score,
                        "frequency": p.frequency
                    } for p in top_patterns
                ],
                "top_rules": [
                    {
                        "id": r.rule_id,
                        "effectiveness": r.effectiveness_score,
                        "success_count": r.success_count,
                        "failure_count": r.failure_count,
                        "agents": r.agent_scope
                    } for r in top_rules
                ],
                "recent_insights": [
                    {
                        "id": i.insight_id,
                        "type": i.insight_type,
                        "description": i.description,
                        "confidence": i.confidence_level,
                        "actionable": i.actionable
                    } for i in recent_insights
                ],
                "agent_learning_stats": agent_stats
            }

            return {"success": True, "report": report}

        except Exception as e:
            return {"success": False, "error": f"Failed to generate report: {str(e)}"}

    def _extract_features(self, interaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract learning features from interaction data"""
        features = {
            "agent": interaction_data.get("agent", ""),
            "task_type": interaction_data.get("task_type", ""),
            "input_complexity": self._assess_complexity(interaction_data.get("input", {})),
            "output_quality": interaction_data.get("quality_score", 0),
            "response_time": interaction_data.get("response_time", 0),
            "success": interaction_data.get("success", False),
            "error_type": interaction_data.get("error_type", ""),
            "context_size": len(str(interaction_data.get("context", {}))),
            "timestamp": interaction_data.get("timestamp", datetime.now().isoformat())
        }

        # Add domain-specific features
        if "optimization" in features["task_type"]:
            features["optimization_algorithm"] = interaction_data.get("algorithm_used", "")
            features["convergence_achieved"] = interaction_data.get("converged", False)

        if "data_analysis" in features["task_type"]:
            features["data_size"] = interaction_data.get("data_size", 0)
            features["analysis_depth"] = interaction_data.get("analysis_depth", "basic")

        return features

    def _identify_patterns(self, features: Dict[str, Any]) -> List[LearningPattern]:
        """Identify patterns in the features"""
        patterns = []

        # Success/failure patterns
        if features["success"]:
            success_pattern = self._create_pattern(
                "success_pattern",
                features["agent"],
                {
                    "task_type": features["task_type"],
                    "input_complexity": features["input_complexity"],
                    "context_conditions": self._extract_context_conditions(features)
                },
                {"outcome": "success", "quality": features["output_quality"]}
            )
            patterns.append(success_pattern)
        else:
            failure_pattern = self._create_pattern(
                "failure_pattern",
                features["agent"],
                {
                    "task_type": features["task_type"],
                    "error_type": features["error_type"],
                    "conditions": self._extract_failure_conditions(features)
                },
                {"outcome": "failure", "error_type": features["error_type"]}
            )
            patterns.append(failure_pattern)

        # Performance patterns
        if features["response_time"] > 0:
            performance_category = self._categorize_performance(features["response_time"])
            performance_pattern = self._create_pattern(
                "performance_pattern",
                features["agent"],
                {
                    "task_type": features["task_type"],
                    "complexity": features["input_complexity"],
                    "context_size": features["context_size"]
                },
                {"performance_category": performance_category, "response_time": features["response_time"]}
            )
            patterns.append(performance_pattern)

        return patterns

    def _create_pattern(self, pattern_type: str, agent_name: str, context: Dict[str, Any], outcome: Dict[str, Any]) -> LearningPattern:
        """Create a learning pattern"""
        pattern_id = self._generate_pattern_id(pattern_type, agent_name, context)

        return LearningPattern(
            pattern_id=pattern_id,
            pattern_type=pattern_type,
            agent_name=agent_name,
            context=context,
            outcome=outcome,
            frequency=1,
            success_rate=1.0 if outcome.get("outcome") == "success" else 0.0,
            confidence_score=0.5,  # Initial confidence
            created_at=datetime.now().isoformat(),
            last_seen=datetime.now().isoformat()
        )

    def _update_or_create_pattern(self, pattern: LearningPattern) -> LearningPattern:
        """Update existing pattern or create new one"""
        if pattern.pattern_id in self.patterns_cache:
            existing = self.patterns_cache[pattern.pattern_id]

            # Update frequency
            existing.frequency += 1

            # Update success rate
            if pattern.outcome.get("outcome") == "success":
                existing.success_rate = (existing.success_rate * (existing.frequency - 1) + 1.0) / existing.frequency
            else:
                existing.success_rate = (existing.success_rate * (existing.frequency - 1) + 0.0) / existing.frequency

            # Update confidence based on frequency
            existing.confidence_score = min(1.0, existing.frequency / 10.0)
            existing.last_seen = datetime.now().isoformat()

            self._store_pattern(existing)
            return existing
        else:
            self.patterns_cache[pattern.pattern_id] = pattern
            self._store_pattern(pattern)
            return pattern

    def _generate_insights(self, features: Dict[str, Any], patterns: List[LearningPattern]) -> List[LearningInsight]:
        """Generate insights from patterns and features"""
        insights = []

        # High-frequency failure patterns
        failure_patterns = [p for p in patterns if p.pattern_type == "failure_pattern" and p.frequency >= self.min_pattern_frequency]
        for pattern in failure_patterns:
            insight = LearningInsight(
                insight_id=self._generate_insight_id(),
                insight_type="failure_analysis",
                description=f"Agent {pattern.agent_name} frequently fails on {pattern.context.get('task_type', 'unknown')} tasks",
                evidence=[{"pattern_id": pattern.pattern_id, "frequency": pattern.frequency}],
                confidence_level=pattern.confidence_score,
                actionable=True,
                impact_estimate="medium",
                agents_affected=[pattern.agent_name],
                created_at=datetime.now().isoformat()
            )
            insights.append(insight)

        # Performance optimization opportunities
        slow_patterns = [p for p in patterns if p.pattern_type == "performance_pattern" and p.outcome.get("performance_category") == "slow"]
        if slow_patterns:
            insight = LearningInsight(
                insight_id=self._generate_insight_id(),
                insight_type="performance_optimization",
                description="Performance optimization opportunity identified",
                evidence=[{"pattern_id": p.pattern_id} for p in slow_patterns],
                confidence_level=statistics.mean(p.confidence_score for p in slow_patterns),
                actionable=True,
                impact_estimate="high",
                agents_affected=list(set(p.agent_name for p in slow_patterns)),
                created_at=datetime.now().isoformat()
            )
            insights.append(insight)

        return insights

    def _create_adaptation_rules(self, insights: List[LearningInsight]) -> List[AdaptationRule]:
        """Create adaptation rules from insights"""
        rules = []

        for insight in insights:
            if not insight.actionable:
                continue

            if insight.insight_type == "failure_analysis":
                rule = AdaptationRule(
                    rule_id=self._generate_rule_id(),
                    condition={
                        "agents": insight.agents_affected,
                        "failure_pattern_detected": True
                    },
                    action={
                        "type": "fallback_strategy",
                        "description": "Apply alternative approach when failure pattern detected"
                    },
                    agent_scope=insight.agents_affected,
                    priority=3,
                    success_count=0,
                    failure_count=0,
                    effectiveness_score=insight.confidence_level,
                    created_at=datetime.now().isoformat()
                )
                rules.append(rule)

            elif insight.insight_type == "performance_optimization":
                rule = AdaptationRule(
                    rule_id=self._generate_rule_id(),
                    condition={
                        "agents": insight.agents_affected,
                        "performance_issue_detected": True
                    },
                    action={
                        "type": "optimization_strategy",
                        "description": "Apply performance optimization when slow patterns detected"
                    },
                    agent_scope=insight.agents_affected,
                    priority=2,
                    success_count=0,
                    failure_count=0,
                    effectiveness_score=insight.confidence_level,
                    created_at=datetime.now().isoformat()
                )
                rules.append(rule)

        for rule in rules:
            self._store_rule(rule)

        return rules

    def _find_relevant_patterns(self, context: Dict[str, Any]) -> List[LearningPattern]:
        """Find patterns relevant to current context"""
        patterns = self._load_all_patterns()
        relevant = []

        agent = context.get("agent", "")
        task_type = context.get("task_type", "")

        for pattern in patterns.values():
            if pattern.agent_name == agent or not agent:
                if pattern.context.get("task_type") == task_type or not task_type:
                    relevant.append(pattern)

        return relevant

    def _find_applicable_rules(self, context: Dict[str, Any]) -> List[AdaptationRule]:
        """Find rules applicable to current context"""
        rules = self._load_all_rules()
        applicable = []

        agent = context.get("agent", "")

        for rule in rules.values():
            if not agent or agent in rule.agent_scope or "all" in rule.agent_scope:
                applicable.append(rule)

        return applicable

    def _apply_adaptation_rule(self, agent_name: str, rule: AdaptationRule, context: Dict[str, Any]) -> Dict[str, Any]:
        """Apply an adaptation rule"""
        try:
            # This would integrate with the actual agent system
            # For now, we'll simulate the application

            adaptation_applied = {
                "success": True,
                "rule_id": rule.rule_id,
                "action_type": rule.action.get("type"),
                "description": rule.action.get("description"),
                "timestamp": datetime.now().isoformat()
            }

            # Update rule success count
            rule.success_count += 1
            self._store_rule(rule)

            return adaptation_applied

        except Exception as e:
            rule.failure_count += 1
            self._store_rule(rule)
            return {"success": False, "error": str(e)}

    def _calculate_pattern_effectiveness(self, agent_name: Optional[str]) -> Dict[str, Any]:
        """Calculate effectiveness of learned patterns"""
        patterns = self._load_all_patterns()

        if agent_name:
            patterns = {k: v for k, v in patterns.items() if v.agent_name == agent_name}

        if not patterns:
            return {"effectiveness": 0, "patterns_evaluated": 0}

        effectiveness_scores = [p.success_rate * p.confidence_score for p in patterns.values()]

        return {
            "effectiveness": statistics.mean(effectiveness_scores),
            "patterns_evaluated": len(patterns),
            "high_confidence_patterns": len([p for p in patterns.values() if p.confidence_score > 0.8])
        }

    def _calculate_rule_effectiveness(self, agent_name: Optional[str]) -> Dict[str, Any]:
        """Calculate effectiveness of adaptation rules"""
        rules = self._load_all_rules()

        if agent_name:
            rules = {k: v for k, v in rules.items() if agent_name in v.agent_scope}

        if not rules:
            return {"effectiveness": 0, "rules_evaluated": 0}

        effectiveness_scores = [r.effectiveness_score for r in rules.values()]

        return {
            "effectiveness": statistics.mean(effectiveness_scores),
            "rules_evaluated": len(rules),
            "successful_applications": sum(r.success_count for r in rules.values())
        }

    def _calculate_improvement_indicators(self, events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate indicators of system improvement"""
        if len(events) < 10:
            return {"insufficient_data": True}

        # Split events into early and recent
        mid_point = len(events) // 2
        early_events = events[:mid_point]
        recent_events = events[mid_point:]

        early_patterns = statistics.mean(e["patterns_found"] for e in early_events)
        recent_patterns = statistics.mean(e["patterns_found"] for e in recent_events)

        early_insights = statistics.mean(e["insights_generated"] for e in early_events)
        recent_insights = statistics.mean(e["insights_generated"] for e in recent_events)

        return {
            "pattern_identification_trend": "improving" if recent_patterns > early_patterns else "stable",
            "insight_generation_trend": "improving" if recent_insights > early_insights else "stable",
            "learning_acceleration": recent_patterns + recent_insights > early_patterns + early_insights
        }

    def _calculate_agent_learning_stats(self) -> Dict[str, Any]:
        """Calculate learning statistics per agent"""
        patterns = self._load_all_patterns()
        agent_stats = defaultdict(lambda: {"patterns": 0, "success_rate": 0, "avg_confidence": 0})

        for pattern in patterns.values():
            stats = agent_stats[pattern.agent_name]
            stats["patterns"] += 1
            stats["success_rate"] = (stats["success_rate"] * (stats["patterns"] - 1) + pattern.success_rate) / stats["patterns"]
            stats["avg_confidence"] = (stats["avg_confidence"] * (stats["patterns"] - 1) + pattern.confidence_score) / stats["patterns"]

        return dict(agent_stats)

    def _load_all_patterns(self) -> Dict[str, LearningPattern]:
        """Load all learning patterns from storage"""
        patterns = {}
        for pattern_file in self.patterns_dir.glob("*.json"):
            try:
                with open(pattern_file, 'r') as f:
                    pattern_data = json.load(f)
                pattern = LearningPattern(**pattern_data)
                patterns[pattern.pattern_id] = pattern
            except Exception:
                continue
        return patterns

    def _load_all_rules(self) -> Dict[str, AdaptationRule]:
        """Load all adaptation rules from storage"""
        rules = {}
        for rule_file in self.rules_dir.glob("*.json"):
            try:
                with open(rule_file, 'r') as f:
                    rule_data = json.load(f)
                rule = AdaptationRule(**rule_data)
                rules[rule.rule_id] = rule
            except Exception:
                continue
        return rules

    def _load_all_insights(self) -> Dict[str, LearningInsight]:
        """Load all learning insights from storage"""
        insights = {}
        for insight_file in self.insights_dir.glob("*.json"):
            try:
                with open(insight_file, 'r') as f:
                    insight_data = json.load(f)
                insight = LearningInsight(**insight_data)
                insights[insight.insight_id] = insight
            except Exception:
                continue
        return insights

    def _store_pattern(self, pattern: LearningPattern):
        """Store pattern to file"""
        pattern_file = self.patterns_dir / f"{pattern.pattern_id}.json"
        with open(pattern_file, 'w') as f:
            json.dump(asdict(pattern), f, indent=2)

    def _store_rule(self, rule: AdaptationRule):
        """Store rule to file"""
        rule_file = self.rules_dir / f"{rule.rule_id}.json"
        with open(rule_file, 'w') as f:
            json.dump(asdict(rule), f, indent=2)

    def _store_insight(self, insight: LearningInsight):
        """Store insight to file"""
        insight_file = self.insights_dir / f"{insight.insight_id}.json"
        with open(insight_file, 'w') as f:
            json.dump(asdict(insight), f, indent=2)

    def _store_learning_event(self, event: Dict[str, Any]):
        """Store learning event to log"""
        log_file = self.learning_dir / "learning_events.jsonl"
        with open(log_file, 'a') as f:
            f.write(json.dumps(event) + '\n')

    def _generate_pattern_id(self, pattern_type: str, agent_name: str, context: Dict[str, Any]) -> str:
        """Generate unique pattern ID"""
        content = f"{pattern_type}_{agent_name}_{json.dumps(context, sort_keys=True)}"
        return hashlib.md5(content.encode()).hexdigest()

    def _generate_rule_id(self) -> str:
        """Generate unique rule ID"""
        return f"rule_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{os.urandom(4).hex()}"

    def _generate_insight_id(self) -> str:
        """Generate unique insight ID"""
        return f"insight_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{os.urandom(4).hex()}"

    def _assess_complexity(self, input_data: Dict[str, Any]) -> str:
        """Assess complexity of input data"""
        size = len(str(input_data))
        if size < 100:
            return "low"
        elif size < 1000:
            return "medium"
        else:
            return "high"

    def _extract_context_conditions(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """Extract context conditions that might influence success"""
        return {
            "complexity": features["input_complexity"],
            "context_size": features["context_size"],
            "time_of_day": datetime.now().hour
        }

    def _extract_failure_conditions(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """Extract conditions that might have led to failure"""
        return {
            "complexity": features["input_complexity"],
            "error_type": features["error_type"],
            "response_time": features["response_time"]
        }

    def _categorize_performance(self, response_time: float) -> str:
        """Categorize performance based on response time"""
        if response_time < 1.0:
            return "fast"
        elif response_time < 5.0:
            return "normal"
        else:
            return "slow"

    def _update_rule_effectiveness(self, rules: List[AdaptationRule], outcome: Dict[str, Any]):
        """Update rule effectiveness based on outcomes"""
        success = outcome.get("success", False)

        for rule in rules:
            if success:
                rule.success_count += 1
            else:
                rule.failure_count += 1

            # Update effectiveness score
            total_applications = rule.success_count + rule.failure_count
            if total_applications > 0:
                rule.effectiveness_score = rule.success_count / total_applications

            self._store_rule(rule)

def main():
    """Main hook function"""
    try:
        input_data = sys.stdin.read()

        if not input_data.strip():
            return

        try:
            data = json.loads(input_data)
        except json.JSONDecodeError:
            print(json.dumps({"error": "Invalid JSON input", "hook": "learning-engine"}))
            return

        engine = LearningEngine()
        operation = data.get("operation", "")

        result = {"hook": "learning-engine", "timestamp": datetime.now().isoformat()}

        if operation == "learn":
            interaction_data = data.get("interaction_data", {})
            result.update(engine.learn_from_interaction(interaction_data))

        elif operation == "get_recommendations":
            context = data.get("context", {})
            result.update(engine.get_recommendations(context))

        elif operation == "analyze_trends":
            agent_name = data.get("agent_name")
            time_range = data.get("time_range", "7d")
            result.update(engine.analyze_performance_trends(agent_name, time_range))

        elif operation == "adapt_behavior":
            agent_name = data.get("agent_name", "")
            adaptation_context = data.get("adaptation_context", {})
            result.update(engine.adapt_agent_behavior(agent_name, adaptation_context))

        elif operation == "generate_report":
            result.update(engine.generate_learning_report())

        else:
            result.update({"success": False, "error": f"Unknown operation: {operation}"})

        print(json.dumps(result, indent=2))

    except Exception as e:
        error_result = {
            "error": f"Learning engine failed: {str(e)}",
            "hook": "learning-engine",
            "success": False
        }
        print(json.dumps(error_result, indent=2))

if __name__ == "__main__":
    main()