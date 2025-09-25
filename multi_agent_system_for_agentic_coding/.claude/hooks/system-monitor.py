#!/usr/bin/env python3
"""
System Monitor Hook - Real-time monitoring of agent performance, system health, and resource usage
"""

import json
import sys
import os
import time
import psutil
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from collections import deque
import statistics

@dataclass
class AgentMetrics:
    agent_name: str
    response_time: float
    success_rate: float
    error_count: int
    requests_handled: int
    resource_usage: Dict[str, float]
    quality_score: float
    last_activity: str
    status: str

@dataclass
class SystemMetrics:
    timestamp: str
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    network_io: Dict[str, float]
    active_agents: int
    total_requests: int
    total_errors: int
    average_response_time: float

@dataclass
class AlertThreshold:
    metric: str
    warning_threshold: float
    critical_threshold: float
    duration: int  # seconds
    enabled: bool

class SystemMonitor:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.monitoring_dir = self.project_root / ".claude" / "monitoring"
        self.metrics_dir = self.monitoring_dir / "metrics"
        self.alerts_dir = self.monitoring_dir / "alerts"
        self.config_file = self.monitoring_dir / "monitor_config.json"

        # Initialize directories
        for directory in [self.monitoring_dir, self.metrics_dir, self.alerts_dir]:
            directory.mkdir(parents=True, exist_ok=True)

        # Monitoring state
        self.agent_metrics = {}
        self.system_metrics_history = deque(maxlen=1000)
        self.alert_thresholds = self._load_alert_thresholds()
        self.active_alerts = {}

        # Performance tracking
        self.request_times = deque(maxlen=100)
        self.error_counts = {}
        self.success_counts = {}

        # Monitoring thread
        self.monitoring_active = False
        self.monitoring_thread = None

    def start_monitoring(self) -> Dict[str, Any]:
        """Start continuous system monitoring"""
        if self.monitoring_active:
            return {"success": False, "message": "Monitoring already active"}

        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()

        return {"success": True, "message": "System monitoring started"}

    def stop_monitoring(self) -> Dict[str, Any]:
        """Stop continuous system monitoring"""
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)

        return {"success": True, "message": "System monitoring stopped"}

    def collect_system_metrics(self) -> SystemMetrics:
        """Collect current system metrics"""
        try:
            # CPU and Memory
            cpu_usage = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')

            # Network I/O
            network_io = psutil.net_io_counters()
            network_data = {
                "bytes_sent": network_io.bytes_sent,
                "bytes_recv": network_io.bytes_recv,
                "packets_sent": network_io.packets_sent,
                "packets_recv": network_io.packets_recv
            }

            # Agent statistics
            active_agents = len([a for a in self.agent_metrics.values() if a.status == "active"])
            total_requests = sum(a.requests_handled for a in self.agent_metrics.values())
            total_errors = sum(a.error_count for a in self.agent_metrics.values())

            # Average response time
            avg_response_time = statistics.mean(self.request_times) if self.request_times else 0

            metrics = SystemMetrics(
                timestamp=datetime.now().isoformat(),
                cpu_usage=cpu_usage,
                memory_usage=memory.percent,
                disk_usage=(disk.used / disk.total) * 100,
                network_io=network_data,
                active_agents=active_agents,
                total_requests=total_requests,
                total_errors=total_errors,
                average_response_time=avg_response_time
            )

            # Store metrics
            self.system_metrics_history.append(metrics)
            self._store_metrics(metrics)

            return metrics

        except Exception as e:
            print(f"Error collecting system metrics: {e}")
            return None

    def record_agent_activity(self, agent_name: str, activity_data: Dict[str, Any]) -> Dict[str, Any]:
        """Record activity for a specific agent"""
        try:
            # Update or create agent metrics
            if agent_name not in self.agent_metrics:
                self.agent_metrics[agent_name] = AgentMetrics(
                    agent_name=agent_name,
                    response_time=0.0,
                    success_rate=100.0,
                    error_count=0,
                    requests_handled=0,
                    resource_usage={},
                    quality_score=100.0,
                    last_activity=datetime.now().isoformat(),
                    status="active"
                )

            agent_metrics = self.agent_metrics[agent_name]

            # Update metrics based on activity
            if "response_time" in activity_data:
                response_time = activity_data["response_time"]
                agent_metrics.response_time = response_time
                self.request_times.append(response_time)

            if "success" in activity_data:
                agent_metrics.requests_handled += 1
                if activity_data["success"]:
                    self.success_counts[agent_name] = self.success_counts.get(agent_name, 0) + 1
                else:
                    self.error_counts[agent_name] = self.error_counts.get(agent_name, 0) + 1
                    agent_metrics.error_count += 1

                # Calculate success rate
                total = self.success_counts.get(agent_name, 0) + self.error_counts.get(agent_name, 0)
                if total > 0:
                    agent_metrics.success_rate = (self.success_counts.get(agent_name, 0) / total) * 100

            if "quality_score" in activity_data:
                agent_metrics.quality_score = activity_data["quality_score"]

            if "resource_usage" in activity_data:
                agent_metrics.resource_usage = activity_data["resource_usage"]

            agent_metrics.last_activity = datetime.now().isoformat()

            # Store agent metrics
            self._store_agent_metrics(agent_metrics)

            # Check for alerts
            self._check_agent_alerts(agent_metrics)

            return {"success": True, "metrics_updated": True}

        except Exception as e:
            return {"success": False, "error": f"Failed to record activity: {str(e)}"}

    def get_system_health(self) -> Dict[str, Any]:
        """Get comprehensive system health report"""
        try:
            current_metrics = self.collect_system_metrics()

            # Calculate trends
            recent_metrics = list(self.system_metrics_history)[-10:]
            trends = self._calculate_trends(recent_metrics)

            # Agent health summary
            agent_health = {}
            for agent_name, metrics in self.agent_metrics.items():
                health_score = self._calculate_agent_health_score(metrics)
                agent_health[agent_name] = {
                    "health_score": health_score,
                    "status": metrics.status,
                    "success_rate": metrics.success_rate,
                    "response_time": metrics.response_time,
                    "last_activity": metrics.last_activity
                }

            # Active alerts
            active_alerts = [alert for alert in self.active_alerts.values() if alert["status"] == "active"]

            return {
                "success": True,
                "timestamp": datetime.now().isoformat(),
                "system_metrics": asdict(current_metrics) if current_metrics else {},
                "trends": trends,
                "agent_health": agent_health,
                "active_alerts": active_alerts,
                "overall_health_score": self._calculate_overall_health_score()
            }

        except Exception as e:
            return {"success": False, "error": f"Failed to get system health: {str(e)}"}

    def get_performance_analytics(self, time_range: Optional[str] = "1h") -> Dict[str, Any]:
        """Get performance analytics for specified time range"""
        try:
            end_time = datetime.now()
            if time_range == "1h":
                start_time = end_time - timedelta(hours=1)
            elif time_range == "24h":
                start_time = end_time - timedelta(days=1)
            elif time_range == "7d":
                start_time = end_time - timedelta(days=7)
            else:
                start_time = end_time - timedelta(hours=1)

            # Filter metrics by time range
            filtered_metrics = [
                m for m in self.system_metrics_history
                if datetime.fromisoformat(m.timestamp) >= start_time
            ]

            if not filtered_metrics:
                return {"success": False, "error": "No metrics available for specified time range"}

            # Calculate analytics
            analytics = {
                "time_range": f"{start_time.isoformat()} to {end_time.isoformat()}",
                "total_requests": sum(m.total_requests for m in filtered_metrics),
                "total_errors": sum(m.total_errors for m in filtered_metrics),
                "average_cpu_usage": statistics.mean(m.cpu_usage for m in filtered_metrics),
                "average_memory_usage": statistics.mean(m.memory_usage for m in filtered_metrics),
                "peak_cpu_usage": max(m.cpu_usage for m in filtered_metrics),
                "peak_memory_usage": max(m.memory_usage for m in filtered_metrics),
                "average_response_time": statistics.mean(m.average_response_time for m in filtered_metrics),
                "error_rate": 0
            }

            # Calculate error rate
            if analytics["total_requests"] > 0:
                analytics["error_rate"] = (analytics["total_errors"] / analytics["total_requests"]) * 100

            # Agent performance breakdown
            agent_performance = {}
            for agent_name, metrics in self.agent_metrics.items():
                agent_performance[agent_name] = {
                    "success_rate": metrics.success_rate,
                    "average_response_time": metrics.response_time,
                    "requests_handled": metrics.requests_handled,
                    "error_count": metrics.error_count,
                    "quality_score": metrics.quality_score
                }

            return {
                "success": True,
                "analytics": analytics,
                "agent_performance": agent_performance
            }

        except Exception as e:
            return {"success": False, "error": f"Failed to get analytics: {str(e)}"}

    def create_alert(self, alert_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new monitoring alert"""
        try:
            alert_id = f"alert_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(self.active_alerts)}"

            alert = {
                "id": alert_id,
                "type": alert_data.get("type", "warning"),
                "message": alert_data.get("message", ""),
                "metric": alert_data.get("metric", ""),
                "value": alert_data.get("value", 0),
                "threshold": alert_data.get("threshold", 0),
                "agent": alert_data.get("agent", "system"),
                "timestamp": datetime.now().isoformat(),
                "status": "active",
                "acknowledged": False
            }

            self.active_alerts[alert_id] = alert
            self._store_alert(alert)

            return {"success": True, "alert_id": alert_id}

        except Exception as e:
            return {"success": False, "error": f"Failed to create alert: {str(e)}"}

    def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.monitoring_active:
            try:
                # Collect system metrics
                self.collect_system_metrics()

                # Check system-level alerts
                self._check_system_alerts()

                # Clean up old data
                self._cleanup_old_data()

                time.sleep(30)  # Monitor every 30 seconds

            except Exception as e:
                print(f"Error in monitoring loop: {e}")
                time.sleep(60)  # Wait longer if there's an error

    def _check_system_alerts(self):
        """Check system metrics against alert thresholds"""
        if not self.system_metrics_history:
            return

        current_metrics = self.system_metrics_history[-1]

        # Check CPU usage
        if current_metrics.cpu_usage > 80:
            self.create_alert({
                "type": "warning",
                "message": f"High CPU usage: {current_metrics.cpu_usage:.1f}%",
                "metric": "cpu_usage",
                "value": current_metrics.cpu_usage,
                "threshold": 80
            })

        # Check memory usage
        if current_metrics.memory_usage > 85:
            self.create_alert({
                "type": "warning",
                "message": f"High memory usage: {current_metrics.memory_usage:.1f}%",
                "metric": "memory_usage",
                "value": current_metrics.memory_usage,
                "threshold": 85
            })

        # Check error rate
        if current_metrics.total_requests > 0:
            error_rate = (current_metrics.total_errors / current_metrics.total_requests) * 100
            if error_rate > 10:
                self.create_alert({
                    "type": "critical",
                    "message": f"High error rate: {error_rate:.1f}%",
                    "metric": "error_rate",
                    "value": error_rate,
                    "threshold": 10
                })

    def _check_agent_alerts(self, agent_metrics: AgentMetrics):
        """Check agent metrics against alert thresholds"""
        # Low success rate alert
        if agent_metrics.success_rate < 90:
            self.create_alert({
                "type": "warning",
                "message": f"Low success rate for {agent_metrics.agent_name}: {agent_metrics.success_rate:.1f}%",
                "metric": "success_rate",
                "value": agent_metrics.success_rate,
                "threshold": 90,
                "agent": agent_metrics.agent_name
            })

        # High response time alert
        if agent_metrics.response_time > 5.0:
            self.create_alert({
                "type": "warning",
                "message": f"High response time for {agent_metrics.agent_name}: {agent_metrics.response_time:.2f}s",
                "metric": "response_time",
                "value": agent_metrics.response_time,
                "threshold": 5.0,
                "agent": agent_metrics.agent_name
            })

        # Low quality score alert
        if agent_metrics.quality_score < 70:
            self.create_alert({
                "type": "warning",
                "message": f"Low quality score for {agent_metrics.agent_name}: {agent_metrics.quality_score:.1f}",
                "metric": "quality_score",
                "value": agent_metrics.quality_score,
                "threshold": 70,
                "agent": agent_metrics.agent_name
            })

    def _calculate_trends(self, metrics_list: List[SystemMetrics]) -> Dict[str, str]:
        """Calculate trends from metrics history"""
        if len(metrics_list) < 2:
            return {}

        trends = {}

        # CPU trend
        cpu_values = [m.cpu_usage for m in metrics_list]
        trends["cpu_usage"] = self._calculate_trend(cpu_values)

        # Memory trend
        memory_values = [m.memory_usage for m in metrics_list]
        trends["memory_usage"] = self._calculate_trend(memory_values)

        # Response time trend
        response_values = [m.average_response_time for m in metrics_list]
        trends["response_time"] = self._calculate_trend(response_values)

        return trends

    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend direction from a list of values"""
        if len(values) < 2:
            return "stable"

        recent_avg = statistics.mean(values[-3:])
        older_avg = statistics.mean(values[:-3]) if len(values) > 3 else values[0]

        if recent_avg > older_avg * 1.1:
            return "increasing"
        elif recent_avg < older_avg * 0.9:
            return "decreasing"
        else:
            return "stable"

    def _calculate_agent_health_score(self, metrics: AgentMetrics) -> float:
        """Calculate overall health score for an agent"""
        # Weighted health score calculation
        success_weight = 0.4
        response_weight = 0.3
        quality_weight = 0.3

        # Normalize response time (lower is better)
        response_score = max(0, 100 - (metrics.response_time * 20))

        health_score = (
            metrics.success_rate * success_weight +
            response_score * response_weight +
            metrics.quality_score * quality_weight
        )

        return min(100, max(0, health_score))

    def _calculate_overall_health_score(self) -> float:
        """Calculate overall system health score"""
        if not self.agent_metrics:
            return 100

        agent_scores = [self._calculate_agent_health_score(m) for m in self.agent_metrics.values()]
        return statistics.mean(agent_scores)

    def _store_metrics(self, metrics: SystemMetrics):
        """Store system metrics to file"""
        metrics_file = self.metrics_dir / f"system_{datetime.now().strftime('%Y%m%d')}.jsonl"
        with open(metrics_file, 'a') as f:
            f.write(json.dumps(asdict(metrics)) + '\n')

    def _store_agent_metrics(self, metrics: AgentMetrics):
        """Store agent metrics to file"""
        metrics_file = self.metrics_dir / f"agent_{metrics.agent_name}_{datetime.now().strftime('%Y%m%d')}.jsonl"
        with open(metrics_file, 'a') as f:
            f.write(json.dumps(asdict(metrics)) + '\n')

    def _store_alert(self, alert: Dict[str, Any]):
        """Store alert to file"""
        alert_file = self.alerts_dir / f"alert_{datetime.now().strftime('%Y%m%d')}.jsonl"
        with open(alert_file, 'a') as f:
            f.write(json.dumps(alert) + '\n')

    def _load_alert_thresholds(self) -> Dict[str, AlertThreshold]:
        """Load alert thresholds from configuration"""
        if not self.config_file.exists():
            return self._create_default_thresholds()

        try:
            with open(self.config_file, 'r') as f:
                config = json.load(f)

            thresholds = {}
            for threshold_data in config.get("alert_thresholds", []):
                threshold = AlertThreshold(**threshold_data)
                thresholds[threshold.metric] = threshold

            return thresholds

        except Exception as e:
            print(f"Error loading alert thresholds: {e}")
            return self._create_default_thresholds()

    def _create_default_thresholds(self) -> Dict[str, AlertThreshold]:
        """Create default alert thresholds"""
        defaults = {
            "cpu_usage": AlertThreshold("cpu_usage", 70.0, 90.0, 300, True),
            "memory_usage": AlertThreshold("memory_usage", 80.0, 95.0, 300, True),
            "response_time": AlertThreshold("response_time", 2.0, 5.0, 180, True),
            "error_rate": AlertThreshold("error_rate", 5.0, 15.0, 120, True),
            "success_rate": AlertThreshold("success_rate", 95.0, 85.0, 300, True)
        }

        # Save default configuration
        config = {
            "alert_thresholds": [asdict(threshold) for threshold in defaults.values()]
        }

        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)

        return defaults

    def _cleanup_old_data(self):
        """Clean up old monitoring data"""
        cutoff_date = datetime.now() - timedelta(days=7)

        # Clean up old metric files
        for metrics_file in self.metrics_dir.glob("*.jsonl"):
            try:
                file_date = datetime.strptime(metrics_file.stem.split('_')[-1], '%Y%m%d')
                if file_date < cutoff_date:
                    metrics_file.unlink()
            except (ValueError, IndexError):
                continue

        # Clean up old alert files
        for alert_file in self.alerts_dir.glob("*.jsonl"):
            try:
                file_date = datetime.strptime(alert_file.stem.split('_')[-1], '%Y%m%d')
                if file_date < cutoff_date:
                    alert_file.unlink()
            except (ValueError, IndexError):
                continue

def main():
    """Main hook function"""
    try:
        input_data = sys.stdin.read()

        if not input_data.strip():
            return

        try:
            data = json.loads(input_data)
        except json.JSONDecodeError:
            print(json.dumps({"error": "Invalid JSON input", "hook": "system-monitor"}))
            return

        monitor = SystemMonitor()
        operation = data.get("operation", "")

        result = {"hook": "system-monitor", "timestamp": datetime.now().isoformat()}

        if operation == "start_monitoring":
            result.update(monitor.start_monitoring())

        elif operation == "stop_monitoring":
            result.update(monitor.stop_monitoring())

        elif operation == "get_health":
            result.update(monitor.get_system_health())

        elif operation == "get_analytics":
            time_range = data.get("time_range", "1h")
            result.update(monitor.get_performance_analytics(time_range))

        elif operation == "record_activity":
            agent_name = data.get("agent_name", "")
            activity_data = data.get("activity_data", {})
            result.update(monitor.record_agent_activity(agent_name, activity_data))

        elif operation == "collect_metrics":
            metrics = monitor.collect_system_metrics()
            result.update({
                "success": True,
                "metrics": asdict(metrics) if metrics else {}
            })

        else:
            result.update({"success": False, "error": f"Unknown operation: {operation}"})

        print(json.dumps(result, indent=2))

    except Exception as e:
        error_result = {
            "error": f"System monitoring failed: {str(e)}",
            "hook": "system-monitor",
            "success": False
        }
        print(json.dumps(error_result, indent=2))

if __name__ == "__main__":
    main()