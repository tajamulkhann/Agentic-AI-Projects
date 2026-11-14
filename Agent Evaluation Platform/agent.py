from pathlib import Path
from agentic_core import AgentRun, load_json, result_from_exception

def replay(trace,inject=None):
    events=[dict(e) for e in trace["events"]]
    if inject:
        for ev in events:
            if ev["tool"]==inject:ev["ok"]=False
    tool_failures=sum(not x["ok"] for x in events)
    expected_count=len(trace["expected_tools"])
    complete=all(x in [e["tool"] for e in events] for x in trace["expected_tools"])
    # Approval is an expected safe outcome, not a failed task.
    success=(tool_failures==0 and complete)
    return {"trace_id":trace["id"],"success":success,"tool_failures":tool_failures,"tool_calls":len(events),"latency_ms":trace["latency_ms"],"model_api_cost_usd":trace["model_api_cost_usd"],"expected_status":trace["expected_status"]}

def compare(traces,inject=None):
    records=[replay(t,inject) for t in traces]
    return {"evaluated":len(records),"task_success_rate":round(sum(r["success"] for r in records)/max(1,len(records)),4),"tool_failure_rate":round(sum(r["tool_failures"] for r in records)/max(1,sum(r["tool_calls"] for r in records)),4),"mean_latency_ms":round(sum(r["latency_ms"] for r in records)/max(1,len(records)),3),"model_api_cost_usd":sum(r["model_api_cost_usd"] for r in records),"details":records}

def run(request,base:Path,fault=None):
    a=AgentRun("evaluation_platform",fault)
    a.plan=["Load archived traces","Validate required tools","Replay candidate with injected failure","Compare success and spend"]
    try:
        traces=a.step("load_benchmark",load_json,p=base/"data/benchmark_traces.json")
        if request.get("trace_id"):
            traces=[t for t in traces if t["id"]==request["trace_id"]]
            if not traces:return a.finish("not_found","Trace not found")
        baseline=a.step("baseline",compare,traces=traces)
        candidate=a.step("replay",compare,traces=traces,inject=request.get("inject_tool"))
        return a.finish("success",f"Baseline success {baseline['task_success_rate']:.0%}; candidate success {candidate['task_success_rate']:.0%}. Archived synthetic traces; this run replays scoring, not external agents.",[{"baseline":baseline,"candidate":candidate}])
    except Exception as e:return result_from_exception(a,e)
