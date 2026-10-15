from __future__ import annotations
import os, uuid
from pathlib import Path
from typing import Any
from dotenv import load_dotenv
from openai import AsyncOpenAI
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIResponsesModel
from pydantic_ai.providers.openai import OpenAIProvider
try:
    from .audit import append_event
    from .mcp_gateway import CampusCustomsMCP
    from .models import AgentReply, AuditEvent, Role, TeamDeps, TeamRunResult
except ImportError:
    from audit import append_event
    from mcp_gateway import CampusCustomsMCP
    from models import AgentReply, AuditEvent, Role, TeamDeps, TeamRunResult
PROJECT_ROOT=Path(__file__).resolve().parents[1]; load_dotenv(PROJECT_ROOT.parents[1]/'.env')
MODEL_NAME='gpt-6-luna'; MAX_STEPS=12; MAX_DELEGATION_DEPTH=4

def model() -> OpenAIResponsesModel:
    key=os.environ.get('PORTKEY_API_KEY')
    if not key: raise RuntimeError('PORTKEY_API_KEY is required for live agent runs')
    client=AsyncOpenAI(api_key=key, base_url=os.environ.get('PORTKEY_BASE_URL','https://api.portkey.ai/v1'), default_headers={'x-portkey-api-key':key,'x-portkey-provider':'openai'})
    return OpenAIResponsesModel(MODEL_NAME, provider=OpenAIProvider(openai_client=client))

def _prompt(role: str) -> str: return (PROJECT_ROOT/'backend'/'prompts'/f'{role}.md').read_text()
mcp_gateway=CampusCustomsMCP(); _agents: dict[Role, Agent[TeamDeps,AgentReply]]={}
async def mcp_lookup(ctx: RunContext[TeamDeps], tool_name: str, arguments: dict[str,Any]) -> Any:
    ctx.deps.step_count += 1
    if ctx.deps.step_count > ctx.deps.max_steps: raise RuntimeError('Agent step/token budget reached; escalate to a human.')
    append_event(AuditEvent(trace_id=ctx.deps.trace_id,step=ctx.deps.step_count,event='mcp_tool_call',agent=ctx.deps.agent,detail=f'Called {tool_name}',tool=tool_name,data=arguments))
    return await mcp_gateway.call(tool_name,arguments)
async def mcp_get_business_context(ctx: RunContext[TeamDeps]) -> Any:
    return await mcp_lookup(ctx, 'get_business_context', {})

async def mcp_list_open_tickets(ctx: RunContext[TeamDeps]) -> Any:
    return await mcp_lookup(ctx, 'list_open_tickets', {})

async def mcp_resolve_customer_order(ctx: RunContext[TeamDeps], ticket_id: int = 101) -> Any:
    return await mcp_lookup(ctx, 'resolve_customer_order_ticket', {'ticket_id': ticket_id})

async def mcp_resolve_rent_notice(ctx: RunContext[TeamDeps], ticket_id: int = 102) -> Any:
    return await mcp_lookup(ctx, 'resolve_rent_notice_ticket', {'ticket_id': ticket_id})

async def mcp_resolve_bulk_price_override(ctx: RunContext[TeamDeps], ticket_id: int = 103) -> Any:
    return await mcp_lookup(ctx, 'resolve_bulk_price_override_ticket', {'ticket_id': ticket_id})


async def delegate_to_agent(ctx: RunContext[TeamDeps], role: Role, task: str) -> AgentReply:
    if role not in _agents: raise ValueError(f'Unknown agent role: {role}')
    if ctx.deps.delegation_depth >= MAX_DELEGATION_DEPTH: raise RuntimeError('Delegation depth limit reached; escalate to a human.')
    append_event(AuditEvent(trace_id=ctx.deps.trace_id,step=ctx.deps.step_count,event='delegation',agent='agent-team',detail=f'Delegating to {role}: {task}'))
    child=ctx.deps.model_copy(update={'agent': role, 'delegation_depth':ctx.deps.delegation_depth+1}); return (await _agents[role].run(task,deps=child)).output
def _make(role: Role): return Agent(model(),name=role,deps_type=TeamDeps,output_type=AgentReply,system_prompt=_prompt(role),tools=[delegate_to_agent, mcp_get_business_context, mcp_list_open_tickets, mcp_resolve_customer_order, mcp_resolve_rent_notice, mcp_resolve_bulk_price_override])
for _role in ('boss','inventory','accounting','facilities','customer_service'): _agents[_role]=_make(_role)  # type: ignore[assignment]
boss=_agents['boss']; inventory=_agents['inventory']; accounting=_agents['accounting']; facilities=_agents['facilities']; customer_service=_agents['customer_service']
async def run_team(ticket_id:int, request:str|None=None)->TeamRunResult:
    trace_id=uuid.uuid4().hex; deps=TeamDeps(trace_id=trace_id,max_steps=MAX_STEPS); append_event(AuditEvent(trace_id=trace_id,step=0,event='team_start',agent='boss',detail=f'Starting ticket {ticket_id}'))
    try:
        result=await boss.run(request or f'Resolve open Campus Customs ticket {ticket_id} using the appropriate specialists and MCP tools.',deps=deps)
        append_event(AuditEvent(trace_id=trace_id,step=deps.step_count,event='team_complete',agent='boss',detail=result.output.answer,data={'facts_used': result.output.facts_used,'delegated_to': result.output.delegated_to}))
        return TeamRunResult(trace_id=trace_id,ticket_id=ticket_id,answer=result.output.answer,agent='boss',audit_events=deps.step_count+2,requires_human_approval=result.output.requires_human_approval)
    except Exception as exc:
        append_event(AuditEvent(trace_id=trace_id,step=deps.step_count,event='team_error',agent='boss',detail=str(exc))); raise
