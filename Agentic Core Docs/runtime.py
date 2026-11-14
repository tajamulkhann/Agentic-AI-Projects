"""Trace-backed, allowlisted tool orchestration. All costs are actual local API spend ($0)."""
import json
import csv
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


def load_json(p):
    return json.loads(Path(p).read_text(encoding="utf-8"))


@dataclass
class AgentRun:
    """A small auditable state machine. Tools are Python callables, never arbitrary commands."""
    workflow: str
    fault: str | None = None
    trace: list[dict] = field(default_factory=list)
    started: float = field(default_factory=time.perf_counter)
    plan: list[str] = field(default_factory=list)

    def step(self, name: str, fn, **kwargs):
        began = time.perf_counter()
        try:
            if self.fault == name:
                raise RuntimeError(f"Injected tool fault: {name}")
            output = fn(**kwargs)
            self.trace.append({"tool": name, "ok": True, "elapsed_ms": round((time.perf_counter() - began) * 1000, 3), "output_preview": str(output)[:180]})
            return output
        except Exception as exc:
            self.trace.append({"tool": name, "ok": False, "elapsed_ms": round((time.perf_counter() - began) * 1000, 3), "error": f"{type(exc).__name__}: {exc}"})
            raise

    def finish(self, status: str, answer: Any, evidence=None, **fields):
        return {"workflow": self.workflow, "status": status, "answer": answer,
                "plan": self.plan, "evidence": evidence or [], "trace": self.trace,
                "latency_ms": round((time.perf_counter() - self.started) * 1000, 3),
                "model_tokens": 0, "model_api_cost_usd": 0.0, "runtime": "offline deterministic baseline", **fields}


def result_from_exception(run, exc):
    return run.finish("error", f"{type(exc).__name__}: {exc}")


def evaluate_suite(run_fn, base: Path, save=True):
    """Run real code with frozen tasks. Exact status plus expected answer tokens are scored."""
    cases=load_json(base / "data" / "eval_cases.json")
    details=[]
    for case in cases:
        result=run_fn(case["request"], base, case.get("fault"))
        answer_text=json.dumps({"answer":result.get("answer"), "evidence":result.get("evidence")},ensure_ascii=False).lower()
        match_status=result["status"]==case["expected_status"]
        found=all(term.lower() in answer_text for term in case.get("expected_contains",[]))
        details.append({"case":case["id"],"passed":bool(match_status and found),
                        "expected_status":case["expected_status"],"actual_status":result["status"],
                        "tools_called":len(result["trace"]),
                        "tool_failures":sum(not x["ok"] for x in result["trace"]),
                        "latency_ms":result["latency_ms"], "model_tokens":result["model_tokens"],
                        "model_api_cost_usd":result["model_api_cost_usd"],
                        "result":result})
    total_tools=sum(x["tools_called"] for x in details)
    report={"evaluation_type":"actual local executions with synthetic fixtures",
            "cases":len(details),"passed":sum(x["passed"] for x in details),
            "task_success_rate":round(sum(x["passed"] for x in details)/len(details),4),
            "tool_calls":total_tools,
            "tool_failures":sum(x["tool_failures"] for x in details),
            "tool_failure_rate":round(sum(x["tool_failures"] for x in details)/max(1,total_tools),4),
            "mean_latency_ms":round(sum(x["latency_ms"] for x in details)/len(details),3),
            "total_model_api_cost_usd":sum(x["model_api_cost_usd"] for x in details),
            "model_tokens":sum(x["model_tokens"] for x in details),
            "cost_note":"Offline baseline only, excludes machine/hosting cost and does not benchmark a hosted LLM.",
            "details":details}
    if save:
        dest=base/"outputs";dest.mkdir(exist_ok=True)
        (dest/"evaluation.json").write_text(json.dumps(report,indent=2,ensure_ascii=False))
        with (dest/"evaluation.csv").open("w",newline="") as f:
            cols=["case","passed","expected_status","actual_status","tools_called","tool_failures","latency_ms","model_tokens","model_api_cost_usd"]
            w=csv.DictWriter(f,fieldnames=cols);w.writeheader();w.writerows({k:v[k] for k in cols} for v in details)
    return report
