#!/usr/bin/env python3
"""
Agent Communication Hook - Enables direct agent-to-agent communication and coordination
"""

import json
import sys
import os
import asyncio
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum

class MessageType(Enum):
    REQUEST = "request"
    RESPONSE = "response"
    BROADCAST = "broadcast"
    HANDOFF = "handoff"
    STATUS_UPDATE = "status_update"
    ERROR_REPORT = "error_report"
    COORDINATION = "coordination"

class MessagePriority(Enum):
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4

@dataclass
class AgentMessage:
    id: str
    sender: str
    recipient: str
    message_type: MessageType
    priority: MessagePriority
    subject: str
    content: Dict[str, Any]
    context: Dict[str, Any]
    timestamp: str
    expires_at: Optional[str] = None
    requires_response: bool = False
    correlation_id: Optional[str] = None
    thread_id: Optional[str] = None

class AgentCommunicationSystem:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.comm_dir = self.project_root / ".claude" / "communication"
        self.message_queue_dir = self.comm_dir / "queues"
        self.conversation_dir = self.comm_dir / "conversations"
        self.routing_table_file = self.comm_dir / "routing_table.json"

        # Initialize directories
        for directory in [self.comm_dir, self.message_queue_dir, self.conversation_dir]:
            directory.mkdir(parents=True, exist_ok=True)

        # Agent capabilities and routing
        self.agent_capabilities = self._load_agent_capabilities()
        self.message_handlers = self._initialize_message_handlers()

    def send_message(self, message: AgentMessage) -> Dict[str, Any]:
        """Send a message from one agent to another"""
        try:
            # Validate message
            validation_result = self._validate_message(message)
            if not validation_result["valid"]:
                return {"success": False, "error": validation_result["error"]}

            # Store message in sender's outbox
            self._store_message(message, "outbox", message.sender)

            # Route message to recipient's inbox
            self._route_message(message)

            # Update conversation thread
            self._update_conversation_thread(message)

            # Log communication
            self._log_communication(message, "sent")

            return {
                "success": True,
                "message_id": message.id,
                "timestamp": message.timestamp,
                "routing_info": self._get_routing_info(message.recipient)
            }

        except Exception as e:
            return {"success": False, "error": f"Failed to send message: {str(e)}"}

    def receive_messages(self, agent_name: str, message_type: Optional[MessageType] = None) -> List[AgentMessage]:
        """Retrieve messages for an agent"""
        try:
            inbox_dir = self.message_queue_dir / agent_name / "inbox"
            messages = []

            if not inbox_dir.exists():
                return messages

            for message_file in inbox_dir.glob("*.json"):
                try:
                    with open(message_file, 'r') as f:
                        message_data = json.load(f)

                    message = AgentMessage(**message_data)

                    # Filter by message type if specified
                    if message_type and message.message_type != message_type:
                        continue

                    # Check if message has expired
                    if self._is_message_expired(message):
                        self._archive_message(message, "expired")
                        continue

                    messages.append(message)

                except Exception as e:
                    print(f"Error reading message file {message_file}: {e}")
                    continue

            # Sort by priority and timestamp
            messages.sort(key=lambda m: (m.priority.value, m.timestamp), reverse=True)

            return messages

        except Exception as e:
            print(f"Error retrieving messages for {agent_name}: {e}")
            return []

    def process_message(self, agent_name: str, message_id: str) -> Dict[str, Any]:
        """Mark a message as processed and move to processed folder"""
        try:
            inbox_dir = self.message_queue_dir / agent_name / "inbox"
            processed_dir = self.message_queue_dir / agent_name / "processed"
            processed_dir.mkdir(parents=True, exist_ok=True)

            message_file = inbox_dir / f"{message_id}.json"
            if not message_file.exists():
                return {"success": False, "error": f"Message {message_id} not found"}

            # Move message to processed folder
            processed_file = processed_dir / f"{message_id}.json"
            message_file.rename(processed_file)

            # Log processing
            self._log_communication_event(agent_name, message_id, "processed")

            return {"success": True, "message": "Message marked as processed"}

        except Exception as e:
            return {"success": False, "error": f"Failed to process message: {str(e)}"}

    def send_handoff(self, from_agent: str, to_agent: str, task_context: Dict[str, Any]) -> Dict[str, Any]:
        """Send a task handoff between agents"""
        handoff_message = AgentMessage(
            id=self._generate_message_id(),
            sender=from_agent,
            recipient=to_agent,
            message_type=MessageType.HANDOFF,
            priority=MessagePriority.HIGH,
            subject=f"Task Handoff: {task_context.get('task_name', 'Unknown Task')}",
            content={
                "handoff_type": "task_transfer",
                "task_context": task_context,
                "completion_requirements": task_context.get("completion_requirements", []),
                "expected_outputs": task_context.get("expected_outputs", {}),
                "constraints": task_context.get("constraints", []),
                "deadline": task_context.get("deadline"),
                "priority_level": task_context.get("priority", "normal")
            },
            context={
                "handoff_timestamp": datetime.now().isoformat(),
                "originating_request": task_context.get("original_request"),
                "previous_work": task_context.get("previous_work", {}),
                "quality_requirements": task_context.get("quality_requirements", {})
            },
            timestamp=datetime.now().isoformat(),
            requires_response=True,
            thread_id=self._generate_thread_id()
        )

        return self.send_message(handoff_message)

    def broadcast_message(self, sender: str, subject: str, content: Dict[str, Any], target_agents: Optional[List[str]] = None) -> Dict[str, Any]:
        """Broadcast a message to multiple agents"""
        results = []
        agents_to_notify = target_agents if target_agents else list(self.agent_capabilities.keys())

        for agent in agents_to_notify:
            if agent == sender:  # Don't send to self
                continue

            broadcast_message = AgentMessage(
                id=self._generate_message_id(),
                sender=sender,
                recipient=agent,
                message_type=MessageType.BROADCAST,
                priority=MessagePriority.NORMAL,
                subject=subject,
                content=content,
                context={"broadcast_group": agents_to_notify, "broadcast_timestamp": datetime.now().isoformat()},
                timestamp=datetime.now().isoformat()
            )

            result = self.send_message(broadcast_message)
            results.append({"agent": agent, "result": result})

        return {"success": True, "broadcast_results": results}

    def request_collaboration(self, requester: str, collaborators: List[str], collaboration_context: Dict[str, Any]) -> Dict[str, Any]:
        """Request collaboration between multiple agents"""
        collaboration_id = self._generate_thread_id()
        results = []

        for collaborator in collaborators:
            collab_message = AgentMessage(
                id=self._generate_message_id(),
                sender=requester,
                recipient=collaborator,
                message_type=MessageType.COORDINATION,
                priority=MessagePriority.HIGH,
                subject=f"Collaboration Request: {collaboration_context.get('objective', 'Multi-Agent Task')}",
                content={
                    "collaboration_type": "multi_agent_coordination",
                    "objective": collaboration_context.get("objective"),
                    "role_assignment": collaboration_context.get("role_assignment", {}),
                    "coordination_plan": collaboration_context.get("coordination_plan", {}),
                    "success_criteria": collaboration_context.get("success_criteria", []),
                    "timeline": collaboration_context.get("timeline", {})
                },
                context={
                    "collaboration_id": collaboration_id,
                    "all_collaborators": collaborators,
                    "coordination_timestamp": datetime.now().isoformat(),
                    "coordination_requirements": collaboration_context.get("coordination_requirements", {})
                },
                timestamp=datetime.now().isoformat(),
                requires_response=True,
                thread_id=collaboration_id
            )

            result = self.send_message(collab_message)
            results.append({"collaborator": collaborator, "result": result})

        # Create collaboration tracking entry
        self._track_collaboration(collaboration_id, requester, collaborators, collaboration_context)

        return {"success": True, "collaboration_id": collaboration_id, "invitation_results": results}

    def get_conversation_history(self, thread_id: str) -> List[AgentMessage]:
        """Retrieve conversation history for a thread"""
        try:
            thread_file = self.conversation_dir / f"{thread_id}.json"
            if not thread_file.exists():
                return []

            with open(thread_file, 'r') as f:
                thread_data = json.load(f)

            messages = [AgentMessage(**msg_data) for msg_data in thread_data.get("messages", [])]
            messages.sort(key=lambda m: m.timestamp)

            return messages

        except Exception as e:
            print(f"Error retrieving conversation history for thread {thread_id}: {e}")
            return []

    def _validate_message(self, message: AgentMessage) -> Dict[str, Any]:
        """Validate message structure and content"""
        if not message.sender or not message.recipient:
            return {"valid": False, "error": "Message must have sender and recipient"}

        if message.recipient not in self.agent_capabilities:
            return {"valid": False, "error": f"Unknown recipient agent: {message.recipient}"}

        if not message.subject or not message.content:
            return {"valid": False, "error": "Message must have subject and content"}

        return {"valid": True}

    def _store_message(self, message: AgentMessage, folder: str, agent: str):
        """Store message in agent's folder"""
        agent_dir = self.message_queue_dir / agent / folder
        agent_dir.mkdir(parents=True, exist_ok=True)

        message_file = agent_dir / f"{message.id}.json"
        with open(message_file, 'w') as f:
            json.dump(asdict(message), f, indent=2)

    def _route_message(self, message: AgentMessage):
        """Route message to recipient's inbox"""
        self._store_message(message, "inbox", message.recipient)

    def _update_conversation_thread(self, message: AgentMessage):
        """Update conversation thread with new message"""
        if not message.thread_id:
            message.thread_id = self._generate_thread_id()

        thread_file = self.conversation_dir / f"{message.thread_id}.json"

        if thread_file.exists():
            with open(thread_file, 'r') as f:
                thread_data = json.load(f)
        else:
            thread_data = {
                "thread_id": message.thread_id,
                "participants": [],
                "created_at": datetime.now().isoformat(),
                "messages": []
            }

        # Update participants
        if message.sender not in thread_data["participants"]:
            thread_data["participants"].append(message.sender)
        if message.recipient not in thread_data["participants"]:
            thread_data["participants"].append(message.recipient)

        # Add message
        thread_data["messages"].append(asdict(message))
        thread_data["updated_at"] = datetime.now().isoformat()

        with open(thread_file, 'w') as f:
            json.dump(thread_data, f, indent=2)

    def _log_communication(self, message: AgentMessage, action: str):
        """Log communication events"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "message_id": message.id,
            "sender": message.sender,
            "recipient": message.recipient,
            "message_type": message.message_type.value,
            "priority": message.priority.value,
            "subject": message.subject
        }

        log_file = self.comm_dir / "communication.log"
        with open(log_file, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')

    def _log_communication_event(self, agent: str, message_id: str, event: str):
        """Log communication events"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "agent": agent,
            "message_id": message_id,
            "event": event
        }

        log_file = self.comm_dir / "events.log"
        with open(log_file, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')

    def _is_message_expired(self, message: AgentMessage) -> bool:
        """Check if message has expired"""
        if not message.expires_at:
            return False

        try:
            expiry_time = datetime.fromisoformat(message.expires_at)
            return datetime.now() > expiry_time
        except:
            return False

    def _archive_message(self, message: AgentMessage, reason: str):
        """Archive expired or processed messages"""
        archive_dir = self.comm_dir / "archive" / reason
        archive_dir.mkdir(parents=True, exist_ok=True)

        archive_file = archive_dir / f"{message.id}.json"
        with open(archive_file, 'w') as f:
            json.dump(asdict(message), f, indent=2)

    def _track_collaboration(self, collaboration_id: str, requester: str, collaborators: List[str], context: Dict[str, Any]):
        """Track ongoing collaborations"""
        collab_file = self.comm_dir / "collaborations" / f"{collaboration_id}.json"
        collab_file.parent.mkdir(parents=True, exist_ok=True)

        collab_data = {
            "collaboration_id": collaboration_id,
            "requester": requester,
            "collaborators": collaborators,
            "context": context,
            "status": "active",
            "created_at": datetime.now().isoformat(),
            "progress": {}
        }

        with open(collab_file, 'w') as f:
            json.dump(collab_data, f, indent=2)

    def _load_agent_capabilities(self) -> Dict[str, Dict]:
        """Load agent capabilities from configuration"""
        config_file = self.project_root / ".claude" / "config.json"
        if config_file.exists():
            with open(config_file, 'r') as f:
                config = json.load(f)
                return config.get("agents", {})
        return {}

    def _initialize_message_handlers(self) -> Dict[MessageType, callable]:
        """Initialize message type handlers"""
        return {
            MessageType.REQUEST: self._handle_request,
            MessageType.RESPONSE: self._handle_response,
            MessageType.HANDOFF: self._handle_handoff,
            MessageType.BROADCAST: self._handle_broadcast,
            MessageType.COORDINATION: self._handle_coordination,
            MessageType.ERROR_REPORT: self._handle_error_report
        }

    def _handle_request(self, message: AgentMessage) -> Dict[str, Any]:
        """Handle request messages"""
        return {"status": "processed", "type": "request"}

    def _handle_response(self, message: AgentMessage) -> Dict[str, Any]:
        """Handle response messages"""
        return {"status": "processed", "type": "response"}

    def _handle_handoff(self, message: AgentMessage) -> Dict[str, Any]:
        """Handle task handoff messages"""
        return {"status": "processed", "type": "handoff"}

    def _handle_broadcast(self, message: AgentMessage) -> Dict[str, Any]:
        """Handle broadcast messages"""
        return {"status": "processed", "type": "broadcast"}

    def _handle_coordination(self, message: AgentMessage) -> Dict[str, Any]:
        """Handle coordination messages"""
        return {"status": "processed", "type": "coordination"}

    def _handle_error_report(self, message: AgentMessage) -> Dict[str, Any]:
        """Handle error report messages"""
        return {"status": "processed", "type": "error_report"}

    def _generate_message_id(self) -> str:
        """Generate unique message ID"""
        return f"msg_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"

    def _generate_thread_id(self) -> str:
        """Generate unique thread ID"""
        return f"thread_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"

    def _get_routing_info(self, agent: str) -> Dict[str, Any]:
        """Get routing information for an agent"""
        return {
            "agent": agent,
            "capabilities": self.agent_capabilities.get(agent, {}),
            "queue_path": str(self.message_queue_dir / agent / "inbox")
        }

def main():
    """Main hook function"""
    try:
        input_data = sys.stdin.read()

        if not input_data.strip():
            return

        try:
            data = json.loads(input_data)
        except json.JSONDecodeError:
            print(json.dumps({"error": "Invalid JSON input", "hook": "agent-communication"}))
            return

        comm_system = AgentCommunicationSystem()
        operation = data.get("operation", "")

        result = {"hook": "agent-communication", "timestamp": datetime.now().isoformat()}

        if operation == "send_message":
            message_data = data.get("message", {})
            message = AgentMessage(**message_data)
            result.update(comm_system.send_message(message))

        elif operation == "receive_messages":
            agent_name = data.get("agent_name", "")
            message_type = data.get("message_type")
            if message_type:
                message_type = MessageType(message_type)

            messages = comm_system.receive_messages(agent_name, message_type)
            result.update({
                "success": True,
                "messages": [asdict(msg) for msg in messages],
                "count": len(messages)
            })

        elif operation == "send_handoff":
            from_agent = data.get("from_agent", "")
            to_agent = data.get("to_agent", "")
            task_context = data.get("task_context", {})

            result.update(comm_system.send_handoff(from_agent, to_agent, task_context))

        elif operation == "broadcast":
            sender = data.get("sender", "")
            subject = data.get("subject", "")
            content = data.get("content", {})
            target_agents = data.get("target_agents")

            result.update(comm_system.broadcast_message(sender, subject, content, target_agents))

        elif operation == "request_collaboration":
            requester = data.get("requester", "")
            collaborators = data.get("collaborators", [])
            collaboration_context = data.get("collaboration_context", {})

            result.update(comm_system.request_collaboration(requester, collaborators, collaboration_context))

        elif operation == "get_conversation":
            thread_id = data.get("thread_id", "")
            messages = comm_system.get_conversation_history(thread_id)

            result.update({
                "success": True,
                "conversation": [asdict(msg) for msg in messages],
                "message_count": len(messages)
            })

        else:
            result.update({"success": False, "error": f"Unknown operation: {operation}"})

        print(json.dumps(result, indent=2))

    except Exception as e:
        error_result = {
            "error": f"Communication system failed: {str(e)}",
            "hook": "agent-communication",
            "success": False
        }
        print(json.dumps(error_result, indent=2))

if __name__ == "__main__":
    main()