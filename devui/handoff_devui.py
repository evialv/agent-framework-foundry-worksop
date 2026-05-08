# DevUI for the Handoff Workflow: PolicyPal triage -> ClaimsAgent / RiskAgent
# Run from repo root: python devui/handoff_workflow_devui.py
import os
from typing import Annotated
from agent_framework import Agent, tool
from agent_framework.orchestrations import HandoffBuilder
from agent_framework.devui import serve
from agent_framework.foundry import FoundryChatClient
from azure.identity import AzureCliCredential
from dotenv import load_dotenv

load_dotenv()

client = FoundryChatClient(
    project_endpoint=os.environ["FOUNDRY_PROJECT_ENDPOINT"],
    model=os.environ["FOUNDRY_MODEL"],
    credential=AzureCliCredential(),
)

@tool(approval_mode="never_require")
def open_claim(
    policy_number: Annotated[str, "Policy number"],
    description: Annotated[str, "Short description"],
) -> str:
    """Open a new Athora Netherlands claim file. Returns the claim ID."""
    return f"Claim opened: ATH-CLM-{abs(hash(policy_number)) % 100000:05d} - '{description}'"


@tool(approval_mode="never_require")
def review_product_change(
    policy_number: Annotated[str, "Policy number"],
    requested_change: Annotated[str, "Requested change"],
) -> str:
    """Return risk and compliance guardrails for a requested product or contribution change."""
    return (
        f"Risk review for {policy_number}: {requested_change}. "
        "Confirm suitability, risk profile, and DNB / AFM disclosure requirements before execution."
    )


@tool(approval_mode="never_require")
def explain_risk_profile(
    policy_number: Annotated[str, "Policy number"],
) -> str:
    """Return a plain-language summary of the policy's risk profile."""
    return (
        f"Policy {policy_number} risk profile: balanced (60% equities / 40% bonds). "
        "Recent volatility is within the expected range for this profile."
    )



policypal_triage = Agent(
    client=client,
    name="policypal_triage",
    description="Frontline triage - routes to ClaimsAgent or RiskAgent",
    require_per_service_call_history_persistence=True,
    instructions=(
        "You are PolicyPal, Athora Netherlands' frontline assistant. Greet the rep briefly and route the request "
        "to the right specialist by transferring control. Use claims_agent for new claims, "
        "and risk_agent for product changes, contribution changes, or risk-profile questions. "
        "Do not handle these yourself."
    ),
)

claims_agent = Agent(
    client=client,
    name="claims_agent",
    description="Handles claim intake using open_claim tool",
    require_per_service_call_history_persistence=True,
    instructions="You handle Athora Netherlands claim intake. Use open_claim once you have a policy number and description.",
    tools=[open_claim],
)

risk_agent = Agent(
    client=client,
    name="risk_agent",
    description="Handles product changes and risk-profile questions",
    require_per_service_call_history_persistence=True,
    instructions=(
        "You handle product-change and risk-profile questions. Use review_product_change for requested changes; "
        "use explain_risk_profile for risk explanations. Keep DNB / AFM guardrails visible."
    ),
    tools=[review_product_change, explain_risk_profile],
)


handoff_workflow = (
    HandoffBuilder(participants=[policypal_triage, claims_agent, risk_agent])
    .with_start_agent(policypal_triage)
    .build()
)

if __name__ == "__main__":
    print("DevUI starting at http://localhost:8096 ...")
    print("Workflow: PolicyPal triage -> ClaimsAgent / RiskAgent (handoff)")
    print()
    print("Try these example queries:")
    print("  - A customer wants to file a claim on policy NL-2031-887 for water damage")
    print("  - I need to lower the contribution on policy NL-2031-887 to 300 EUR/month")
    print("  - Customer is asking about their risk profile on policy NL-2045-112")
    serve(
        entities=[handoff_workflow, policypal_triage, claims_agent, risk_agent],
        port=8096, auto_open=True, instrumentation_enabled=True,
    )
