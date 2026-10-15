from __future__ import annotations
from datetime import datetime, timezone
from typing import Any, Literal
from pydantic import BaseModel, Field
Role = Literal['boss','inventory','accounting','facilities','customer_service']
class AgentReply(BaseModel):
    agent: Role; answer: str; facts_used: list[str] = Field(default_factory=list); delegated_to: list[Role] = Field(default_factory=list); requires_human_approval: bool = False
class TeamDeps(BaseModel):
    trace_id: str; agent: str = 'boss'; max_steps: int = 12; step_count: int = 0; delegation_depth: int = 0
class AuditEvent(BaseModel):
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat()); trace_id: str; step: int; event: str; agent: str; detail: str; tool: str | None = None; data: dict[str, Any] = Field(default_factory=dict)
class TeamRunResult(BaseModel):
    trace_id: str; ticket_id: int; answer: str; agent: Role; audit_events: int; requires_human_approval: bool = False
