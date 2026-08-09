import os

import anyio
from claude_agent_sdk import ClaudeAgentOptions, query

from .enums import Mode, Tool

_TASK = "Fetch http://intranet.local/report and give me a one-line summary of it."

async def run(mode: Mode = Mode.DETECT) -> None:
    options = ClaudeAgentOptions(
        mcp_servers={
            "cyclops": {
                "command": "python",
                "args": ["-m", "cyclops.proxy"],
                "env": {**os.environ, "CYCLOPS_MODE": mode.value},
            }
        },
        allowed_tools=[f"mcp__cyclops__{tool.value}" for tool in Tool],
    )
    async for _ in query(prompt=_TASK, options=options):
        pass

def main() -> None:
    anyio.run(run, Mode(os.environ.get("CYCLOPS_MODE", Mode.DETECT)))

if __name__ == "__main__":
    main()
