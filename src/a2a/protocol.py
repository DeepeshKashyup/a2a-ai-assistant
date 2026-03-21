"""A2A (Agent to Agent) protocol pydantic schemas.

# =====================================================================================================================
# 
# =====================================================================================================================  

"""

import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field

class TaskStatus(str, Enum):
    """Lifecycle states of an A2A task."""
    SUBMITTED = "submitted"
    WORKING = "working"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class MessageRole(str, Enum):
    USER = "user"
    AGENT = "agent"

class TextPart(BaseModel):
    """A text content part within an A2A message."""
    type: str = "text"
    text: str

class Message(BaseModel):
    """A single message in an A2A task conversation."""
    role: MessageRole
    part: list[TextPart]

    @classmethod
    def user(cls, text: str) -> "Message":
        return cls(role=MessageRole.USER, parts=[TextPart(text=text)])

    @classmethod
    def agent(cls, text: str) -> "Message":
        return cls(role=MessageRole.AGENT, parts=[TextPart(text=text)])

    @property
    def text(self) -> str:
        """Convenience: return concatenated text of all parts."""
        return " ".join(p.text for p in self.parts)


class TaskSendParams(BaseModel):
    """Parameters for submitting a new task to an agent."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    message: Message
    metadata: Optional[dict[str, Any]] = None


class Task(BaseModel):
    """An A2A task with status tracking and message history."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    status: TaskStatus = TaskStatus.SUBMITTED
    messages: list[Message] = []
    artifacts: Optional[list[dict[str, Any]]] = None
    metadata: Optional[dict[str, Any]] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    def complete(self, reply_text: str, artifacts: list[dict] | None = None) -> None:
        """Mark task as completed with agent reply."""
        self.messages.append(Message.agent(reply_text))
        self.status = TaskStatus.COMPLETED
        self.artifacts = artifacts
        self.updated_at = datetime.utcnow()

    def fail(self, reason: str) -> None:
        """Mark task as failed with error reason."""
        self.messages.append(Message.agent(f"Error: {reason}"))
        self.status = TaskStatus.FAILED
        self.updated_at = datetime.utcnow()


class AgentSkill(BaseModel):
    """Describes a specific capability an agent can perform."""
    id: str
    name: str
    description: str
    input_modes: list[str] = ["text"]
    output_modes: list[str] = ["text"]


class AgentCard(BaseModel):
    """Agent Card — published at /.well-known/agent.json."""
    name: str
    description: str
    url: str
    version: str
    capabilities: dict[str, Any]
    skills: list[AgentSkill]
    default_input_mode: str = "text"
    default_output_mode: str = "text"