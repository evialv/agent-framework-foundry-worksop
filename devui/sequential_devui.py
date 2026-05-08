# DevUI for the Sequential Workflow: Triage -> Pension Advisor -> Compliance Checker
# Run from repo root: python devui/sequential_workflow_devui.py
import os
from agent_framework import Agent
from agent_framework.orchestrations import SequentialBuilder
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

triage_agent = Agent(
    client=client,
    name="TriageAgent",
    description="Classifies rep requests into service categories.",
    instructions=(
        "Classify Athora Netherlands rep requests as PENSION, LIFE_INSURANCE, CLAIM, COMPLAINT, or OTHER. "
        "Return the category and the policy number if present."
    ),
)

pension_advisor_agent = Agent(
    client=client,
    name="PensionAdvisorAgent",
    description="Drafts pension guidance for the rep.",
    instructions=(
        "Help Athora Netherlands reps explain defined-contribution pension options. "
        "Use only the facts provided by earlier steps; do not give regulated financial advice."
    ),
)

compliance_checker_agent = Agent(
    client=client,
    name="ComplianceCheckerAgent",
    description="Reviews draft for DNB / AFM compliance.",
    instructions=(
        "Review the draft for DNB / AFM guardrails. Flag missing disclaimers, suitability checks, "
        "or unsupported advice. End with APPROVED or NEEDS_REVIEW."
    ),
)

sequential_workflow = SequentialBuilder(
    participants=[triage_agent, pension_advisor_agent, compliance_checker_agent]
).build()

workflow_agent = sequential_workflow.as_agent(
    name="PensionPipeline",
    description="Athora Netherlands sequential workflow: Triage -> Pension Advisor -> Compliance Checker",
)

if __name__ == "__main__":
    print("DevUI starting at http://localhost:8093 ...")
    print("Workflow: TriageAgent -> PensionAdvisorAgent -> ComplianceCheckerAgent")
    serve(entities=[workflow_agent], port=8093, auto_open=True, instrumentation_enabled=True)
