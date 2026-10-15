from __future__ import annotations
from pathlib import Path
from typing import Any
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
PROJECT_ROOT = Path(__file__).resolve().parents[1]
class CampusCustomsMCP:
    async def ticket_statuses(self) -> Any:
        return await self.call('get_ticket_statuses', {})

    async def cash_balance(self) -> Any:
        return await self.call('get_cash_balance', {})

    async def call(self, tool_name: str, arguments: dict[str, Any] | None = None) -> Any:
        params=StdioServerParameters(command=str(PROJECT_ROOT/'.venv/bin/python'), args=['mcp_server/server.py'], cwd=str(PROJECT_ROOT))
        async with stdio_client(params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize(); result=await session.call_tool(tool_name, arguments or {})
                if result.isError: raise RuntimeError(f'MCP tool {tool_name} failed: {result.content}')
                if not result.content: return None
                return getattr(result.content[0], 'text', result.content[0])
