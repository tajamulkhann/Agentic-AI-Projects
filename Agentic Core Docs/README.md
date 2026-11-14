# 10 Agentic AI Engineering Projects

**Author:** Tajamul Khan | [GitHub](https://github.com/tajamulkhann) | [LinkedIn](https://www.linkedin.com/in/tajamulkhann/) | [Instagram](https://www.instagram.com/tajamul.codes/) | [Topmate](https://topmate.io/tajamulkhan)

> Ten practical Agentic AI Engineering projects covering research, analytics, software development and business automation. Each project includes a STAR-based case study, working code, sample data, saved execution outputs and measurable evaluations.

Each project is a **working offline-first engineering prototype** with explicit tool calls, tracing, isolated fixtures, deterministic policy safeguards, Streamlit UI, an executed success/failure notebook and actual benchmark execution results. This is intended as an educational portfolio, not 10 claimed production deployments or 10 live LLM integrations.

## Projects

| # | Project | Main competency | Local fixture benchmark |
|---|---|---|---|
| 01 | [Deep Research Agent](01-deep-research-agent/README.md) | Search, source comparison, evidence quality and evidence-linked synthesis | 4/4 tasks passed |
| 02 | [SQL Data Analyst Agent](02-sql-data-analyst-agent/README.md) | Schema discovery, safe query routing, SQL authorizers and visualization | 5/5 tasks passed |
| 03 | [Customer Support Resolution Agent](03-customer-support-agent/README.md) | Policy retrieval, authorization checks, approval states and audit traces | 5/5 tasks passed |
| 04 | [GitHub Issue-to-Pull-Request Agent](04-github-issue-pr-agent/README.md) | Code navigation, patch creation, isolated tests and PR handoff | 4/4 tasks passed |
| 05 | [Invoice Reconciliation Agent](05-invoice-reconciliation-agent/README.md) | Document fields, three-way matching, tolerance rules and exception routing | 5/5 tasks passed |
| 06 | [Data Pipeline Incident Agent](06-pipeline-incident-agent/README.md) | Log retrieval, lineage awareness, diagnosis and recovery approval | 5/5 tasks passed |
| 07 | [Contract Review Agent](07-contract-review-agent/README.md) | Clause parsing, policy matching, citations and human legal handoff | 4/4 tasks passed |
| 08 | [Browser Workflow Automation Agent](08-browser-workflow-agent/README.md) | Form inspection, field mapping, local browser adapter and approval gates | 4/4 tasks passed |
| 09 | [Multi-Agent Software Delivery Team](09-multi-agent-delivery-team/README.md) | Role handoffs, acceptance tests, output review and termination | 5/5 tasks passed |
| 10 | [Agent Evaluation & Reliability Platform](10-agent-evaluation-platform/README.md) | Benchmark labels, replay, regression scoring, tool fault injection and cost reporting | 5/5 tasks passed |

## Standard project structure

```text
agentic-ai/
├── agentic_core/               # Shared tracing, tool execution and evaluation
├── 01-deep-research-agent/
│   ├── README.md                # STAR study + measured results + limitations
│   ├── agent.py                 # Actual runnable workflow
│   ├── run.py                   # Reproduce single case or full evaluation
│   ├── app.py                   # Interactive Streamlit interface
│   ├── analysis.ipynb           # Executed success and failure demonstrations
│   ├── architecture.md          # Mermaid diagram + trust boundaries
│   ├── requirements.txt
│   ├── .env.example
│   ├── data/                    # Synthetic fixture + data dictionary + test oracles
│   ├── tests/                   # Pytest test suite
│   └── outputs/
│       ├── evaluation.json     # Full real tool traces and metrics
│       ├── evaluation.csv
│       ├── success.json
│       ├── failure.json
│       ├── overview.png
│       └── dashboard.html      # Works offline in a browser
├── ... 02 through 09 ...
├── 10-agent-evaluation-platform/
├── docs/SAFETY_AND_SCOPE.md
├── requirements.txt
├── .env.example
├── DATA_LICENSE.md
├── run_all.py
└── tests/test_repository.py
```

## Quick start

Python 3.11 is recommended. Core workflow scripts use the Python standard library plus `pytest` for local code-test projects; the pinned requirements add Streamlit, notebook execution and plotting dependencies.

```bash
python -m venv .venv
source .venv/bin/activate
# Windows: .venv\Scripts\activate
python -m pip install -r requirements.txt

# Run and refresh evaluation reports from actual code:
python run_all.py

# Run repository consistency test:
python -m pytest -q tests

# Run one interactive app:
cd 02-sql-data-analyst-agent
streamlit run app.py
```

For project-specific executed notebooks, open `analysis.ipynb` in JupyterLab or VS Code. Each `outputs/dashboard.html` is an offline HTML report with a chart, metrics, a filterable case table and a saved trace; open it directly in any modern browser.

## Verified evidence and how to interpret it

- Benchmarks use small deterministic **synthetic** task fixtures with known expected statuses and answer assertions.
- Every project includes an injected-tool-failure case and the actual exception trace. A benchmark's **passing score** means the failure was handled as expected; it does **not** mean no tool failures occurred.
- Mean latencies are observed *local* milliseconds, not hosted inference latencies. Reported model tokens and direct API cost are zero because the baseline uses no hosted LLM.
- A subset of projects deliberately returns `needs_approval` for safe human handoff. These outcomes are considered correct where specified.
- The research sources, contract obligations, invoices, support orders, repository issues, browser form and benchmark traces are entirely fictional.
- The code uses domain-specific orchestration and rules. It demonstrates agent infrastructure and engineering patterns, but the offline baselines are **not** autonomous general-purpose LLM agents.

### Safety design

SQL is read only and template allowlisted. No refund, payment, contract signature, production remediation, remote PR or browser submission takes place. The optional Playwright adapter can populate **a local fixture page** only. Generated code is tested only against author-controlled fixtures. See [Safety and Scope](docs/SAFETY_AND_SCOPE.md) for details.

## Extending toward production

Use these projects as foundations for real hosted agent systems: introduce a configurable model planner with structured tool schemas, real authenticated read APIs, human approval UIs, retry/backoff, tracing backends, prompt-injection tests, independent evaluation datasets and cost monitoring. Re-evaluate after each integration; do not reuse offline metrics as production claims.

## Optional real hosted model planning

For an API-backed demonstration, set `OPENAI_API_KEY` and run `python run.py --model-plan` inside **any** project, or turn on the optional model-planning checkbox in its Streamlit app. A hosted model returns proposed tool names, which are checked against a per-project allowlist. These are advisory plans, never automatically executed. The offline metrics do not include this hosted path. See [`agentic_core/model_bridge.py`](agentic_core/model_bridge.py).

## Licenses

Code and documentation: MIT. Original synthetic fixture datasets: CC0 1.0. No external datasets are republished.
