from pathlib import Path
from agentic_core import AgentRun, load_json, result_from_exception

def diagnose(log):
    if "STORAGE_QUOTA" in log:return "Storage quota exhausted","Escalate capacity investigation; do not purge data automatically."
    if "RATE_LIMIT_429" in log:return "Upstream API rate limit","Check retry/backoff policy and ingestion status."
    if "succeeded" in log:return "No active failure in provided log","No recovery action recommended."
    return "Unknown failure","Collect more logs and escalate to on-call."

def run(request,base:Path,fault=None):
    a=AgentRun("pipeline_triage",fault)
    a.plan=["Load incident log","Inspect pipeline lineage","Diagnose likely cause","Recommend approved response"]
    try:
        incidents=a.step("incidents",load_json,p=base/"data/incidents.json")
        inc=next((i for i in incidents if i["incident_id"]==request.get("incident_id")),None)
        if inc is None:return a.finish("not_found","Incident not found")
        pipelines=a.step("lineage",load_json,p=base/"data/pipelines.json")
        pipe=next((p for p in pipelines if p["pipeline_id"]==inc["pipeline_id"]),None)
        root,recommendation=a.step("diagnose",diagnose,log=inc["log"])
        status="success" if root=="No active failure in provided log" else "needs_approval"
        answer=f"Likely cause: {root}. Recommendation: {recommendation} Remediation not executed."
        return a.finish(status,answer,[{"incident":inc["incident_id"],"log":inc["log"],"upstream":pipe["depends_on"] if pipe else []}])
    except Exception as e:return result_from_exception(a,e)
