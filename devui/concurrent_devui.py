# DevUI for the Concurrent Workflow: Compliance + Risk + Product (parallel review)
# Run from repo root: python devui/concurrent_workflow_devui.py
import os
from agent_framework import Agent
from agent_framework.orchestrations import ConcurrentBuilder
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

compliance = Agent(
    client=client,
    name="compliance",
    description="Flags DNB / AFM, KYC, or documentation concerns.",
    instructions=(
        "You are an Athora Netherlands compliance reviewer. Flag DNB / AFM, KYC, or documentation concerns "
        "in the rep query. 3 bullets max."
    ),
)

risk = Agent(
    client=client,
    name="risk",
    description="Flags risk-profile and product-fit issues.",
    instructions=(
        "You are a risk reviewer. Flag anything unusual about the requested change, "
        "risk profile, or product fit. 3 bullets max."
    ),
)

product = Agent(
    client=client,
    name="product",
    description="Explains what info the rep needs before discussing changes.",
    instructions=(
        "You are a product specialist. Explain what information the rep needs before discussing changes. "
        "3 bullets max."
    ),
)

review_workflow = ConcurrentBuilder(participants=[compliance, risk, product]).build()

workflow_agent = review_workflow.as_agent(
    name="ParallelReview",
    description="Athora Netherlands concurrent workflow: Compliance + Risk + Product review in parallel",
)

if __name__ == "__main__":
    print("DevUI starting at http://localhost:8094 ...")
    print("Workflow: Compliance | Risk | Product (concurrent)")
    serve(
        entities=[workflow_agent, compliance, risk, product],
        port=8094, auto_open=True, instrumentation_enabled=True,
    )
