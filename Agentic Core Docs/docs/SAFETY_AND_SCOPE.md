# Safety, realism and integration scope

The ten applications here are **offline working baselines**. Tool orchestration, traces,
errors, evaluation and review checkpoints are executable without an account.
No claim is made that a hosted LLM was called or that real-world agents were deployed.

Specific boundaries:
- Research only verifies agreement inside its bundled corpus. `synthetic://` references are not public citations.
- SQL uses a read-only SQLite connection, query templates and an SQLite authorizer.
- Support can *propose* refunds; it cannot issue refunds or change accounts.
- GitHub project creates a local patch and PR draft. It does not create a remote PR.
- Invoice agent does not pay invoices.
- Pipeline agent does not run incident remediation.
- Contract agent flags playbook patterns only, not legal advice.
- Browser agent defaults to static form inspection and never submits. An optional Playwright adapter fills and screenshots a *local* form without submitting.
- Software team builds in a local temporary folder, runs tests and hands off for review. It does not deploy.
- Evaluation platform replays archived fixture traces. `run_all.py` runs the actual local agents for live *fixture* evaluation.

For real integrations, add provider adapters behind approval/permissions boundaries and run
separate benchmarks. Real API tokens and inference spend are zero in the included evidence;
compute, developer time and hosting are not modeled. Avoid executing untrusted generated code
without OS or container sandbox isolation. Python temporary directories are **not** a secure
sandbox for arbitrary untrusted code.
