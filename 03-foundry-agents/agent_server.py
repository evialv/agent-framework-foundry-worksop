"""
Minimal FastAPI server exposing PolicyPal as an API.
Run: uvicorn agent_server:app --port 8000
Then forward port 8000 via VS Code (Ctrl+Shift+P → "Ports: Forward a Port").
"""

import os
from typing import Annotated

from azure.identity import AzureCliCredential
from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel, Field

from agent_framework import Agent, tool
from agent_framework.foundry import FoundryChatClient
from agent_framework.observability import configure_otel_providers

load_dotenv()

# --- Observability: traces go to App Insights ---
# configure_otel_providers only exports to console.
# configure_azure_monitor sends traces to App Insights → Foundry portal.
# We call it at startup below, after creating the client.

# --- Tool + Agent ---
POLICIES = {
    "NL-2031-887": {
        "holder": "Jan de Vries",
        "product": "Pension - defined contribution",
        "balance_eur": 78_420.55,
        "monthly_contribution_eur": 350.00,
    },
    "NL-4408-552": {
        "holder": "Sanne Bakker",
        "product": "Life insurance - term",
        "balance_eur": 0.0,
        "monthly_contribution_eur": 42.50,
    },
}


@tool(approval_mode="never_require")
def get_policy(policy_number: Annotated[str, Field(description="Policy number")]) -> str:
    """Look up an Athora Netherlands policy by its number."""
    p = POLICIES.get(policy_number.upper())
    return f"Policy {policy_number}: {p}" if p else f"No policy found for {policy_number}."


client = FoundryChatClient(
    project_endpoint=os.environ["FOUNDRY_PROJECT_ENDPOINT"],
    model=os.environ["FOUNDRY_MODEL"],
    credential=AzureCliCredential(),
)

policypal = Agent(
    client=client,
    name="testdevtunnelagent",
    id="testdevtunnelagent",
    instructions=(
        "You are PolicyPal, an internal assistant for Athora Netherlands reps. "
        "Always use get_policy for any policy fact. "
        "If the policy is not found, say so plainly. Never invent figures."
    ),
    tools=[get_policy],
)

# --- FastAPI ---
app = FastAPI(title="PolicyPal Agent Server")


@app.on_event("startup")
async def startup():
    """Wire up Azure Monitor so traces flow to App Insights → Foundry."""
    await client.configure_azure_monitor(
        enable_sensitive_data=True,
        enable_live_metrics=True,
    )
    print("Azure Monitor configured — traces → App Insights.")


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    response: str


@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    session = policypal.create_session()
    result = await policypal.run(req.message, session=session)
    return ChatResponse(response=result.text)


@app.get("/health")
async def health():
    return {"status": "ok", "agent": "PolicyPal"}
