# Microsoft Agent Framework Workshop

Welcome to the [Microsoft Agent Framework](https://github.com/microsoft/agent-framework) workshop! This project is designed to help you learn and practice implementing single- and multi-agent systems using Agent Framework and get acquainted with [Microsoft Foundry](https://ai.azure.com). The repository contains a series of progressive examples and demos that will guide you through building increasingly complex agent systems, from simple interactions to sophisticated multi-agent collaborative scenarios.

## Setup

### Prerequisites

- **Python 3.12+**
- **Azure CLI** (`az`) — [install guide](https://learn.microsoft.com/cli/azure/install-azure-cli)
- **VS Code** with the Jupyter extension (recommended)
- An **Azure subscription** with access to Azure AI Foundry

### 1. Sign in to Azure

We **highly encourage** using `AzureCliCredential` — no API keys to manage, no secrets to leak. All notebooks are pre-configured to use it:

```bash
az login
```

> If you have API keys as an alternative option, let us know during the workshop and we'll help you set that up!

### 2. Create an Azure AI Foundry project & deploy a model

1. Go to [Azure AI Foundry](https://ai.azure.com) and create a new **project**
2. Inside the project, go to **Model catalog** and deploy **gpt-4.1** (or the model your instructor specifies)
3. Copy your **project endpoint** from the project overview page — you'll need it in step 5

### 3. Create a virtual environment & install dependencies

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
```

### 4. Configure environment variables

Copy the example file and fill in your project endpoint and model name:

```bash
cp .env.example .env
```

Edit `.env` and set:

```
FOUNDRY_PROJECT_ENDPOINT=https://<your-project>.services.ai.azure.com/api/projects/<project-id>
FOUNDRY_MODEL=gpt-4.1
```

### 5. (Optional )Register the Jupyter kernel

This creates a dedicated kernel so VS Code knows which Python environment to use:

```bash
python -m ipykernel install --user --name=agent-fw-workshop --display-name "Agent Framework Workshop (3.12)"
```

Open any notebook in VS Code and select **"Agent Framework Workshop (3.12)"** as the kernel (top-right corner).

---

## Getting Started

Start with the first folder `01-singleagents` and progress through them sequentially.

Use documentation on https://learn.microsoft.com/en-us/agent-framework/ to help you with getting up to speed and figuring out what steps to take to complete the exercises.

### Project Structure

```
├── 01-singleagents/                          # Chapter 1: Single agents & DevUI
│   ├── 01.1-single-agents.ipynb              #   Agent, FoundryChatClient, @tool, sessions, memory
│   ├── 01.2-foundry-devui.ipynb              #   Launch DevUI to chat with your agent in the browser
│   └── 01-exercises.ipynb                    #   Exercises: build an agent, add memory, implement middleware
│
├── 02-workflows/                             # Chapter 2: Multi-agent workflows & orchestration
│   ├── 02.1-intro-workflows.ipynb            #   WorkflowBuilder, executors, edges, WorkflowEvent streaming
│   ├── 02.2-workflows-part1.ipynb            #   Sequential (SequentialBuilder) & Concurrent (ConcurrentBuilder)
│   ├── 02.3-workflows-part2-orchestration.ipynb  #   Handoff pattern & Magentic orchestration (discussion)
│   └── 02-exercises.ipynb                    #   Exercises: multi-agent workflow, custom executor with streaming
│
├── 03-foundry-agents/                        # Chapter 3: Foundry Agents — register, deploy, observe
│   ├── 03.1-foundry-agents.ipynb             #   Register agents in Foundry, observability via App Insights
│   ├── agent.yaml                            #   Declarative agent definition
│   └── agent_server.py                       #   FastAPI server exposing agent via API (port forwarding demo)
│
├── 04-evaluations/                           # Chapter 4: Evaluations — measure agent quality
│   ├── 04.1-evaluations.ipynb                #   Foundry evaluations: groundedness, relevance, coherence
│   └── eval_responses.jsonl                  #   Sample eval dataset
│
├── devui/                                    # Standalone DevUI scripts (run from repo root)
│   ├── sequential_workflow_devui.py          #   Triage → Advisor → Compliance pipeline (port 8090)
│   ├── concurrent_workflow_devui.py          #   Compliance | Risk | Product parallel review (port 8094)
│   └── handoff_workflow_devui.py             #   PolicyPal triage → ClaimsAgent / RiskAgent (port 8096)
│
├── requirements.txt                          # All pip dependencies
└── .env.example                              # Template for environment variables
```

Open the notebooks in order — each chapter builds on the previous one.

---

### Chapter 1 — Single Agents

Your first agents. Learn the core building blocks before moving to multi-agent patterns.

**Theory** covers creating an `Agent` with `FoundryChatClient`, adding tools with the `@tool` decorator, managing conversation state with sessions and memory providers, and launching **DevUI** to interact with your agent in the browser.

**Exercises:**

1. Build your first agent from scratch — create a client, define tools, have a multi-turn conversation
2. Add memory using `SimpleMemoryProvider` so your agent remembers context across sessions
3. Implement middleware (`@agent_middleware`, `@chat_middleware`, `@function_middleware`) for logging, guardrails, and tool-call inspection

---

### Chapter 2 — Workflows

Move from single agents to multi-agent orchestration. Learn when and how to compose agents.

**Theory** covers four orchestration patterns:

- **Sequential** — deterministic pipeline where agents process in order
- **Concurrent** — fan-out the same input to multiple agents in parallel, collect all results
- **Handoff** — conversational routing where a coordinator decides at runtime which specialist takes over
- **Magentic** — open-ended orchestration where the plan itself is discovered (discussed, not built)

Some patterns have a **DevUI script** in `devui/` for interactive experimentation — run them from the repo root:

```bash
python devui/sequential_devui.py
python devui/concurrent_devui.py
python devui/handoff_devui.py
```

---

### Chapter 3 — Foundry Agents

Use Azure AI Foundry's hosted agent capabilities — prompt agents, YAML definitions, and built-in tools.

**Theory** covers:

- Creating **prompt agents** via the Foundry SDK (server-side agents with web search, code interpreter, etc.)
- Chatting with prompt agents programmatically
- Defining agents declaratively with **YAML agent definitions** (`agent.yaml`)
- How Foundry prompt agents compare to Agent Framework local agents

---

### Chapter 4 — Evaluations

Get compliance sign-off with repeatable, automated evaluation of agent quality.

**Theory** covers:

- Building an evaluation dataset with expected facts (ground truth)
- **Local evaluators** — `keyword_check`, `tool_calls_present`, custom `@evaluator` (cheap, fast, run on every PR)
- Expected-output comparison to catch prompt regressions
- **Foundry-grade evaluators** — Task Adherence, Coherence, Safety (the numbers compliance wants)
- Wiring evaluations into a **CI gate** with `raise_for_status()`

