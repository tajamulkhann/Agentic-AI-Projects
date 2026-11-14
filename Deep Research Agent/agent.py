from pathlib import Path
from agentic_core import AgentRun, load_json, result_from_exception

def search_sources(query, sources):
    q=query.lower()
    if "emissions" in q or "tug" in q: return [s for s in sources if s["topic"]=="port emissions"]
    if "delay" in q or "supply" in q: return [s for s in sources if s["topic"]=="supply chain delays"]
    return []

def compare_claims(hits):
    groups={}
    for source in hits:
        if isinstance(source["value"],(int,float)):
            groups.setdefault(source["metric"],set()).add(source["value"])
    return [k for k,v in groups.items() if len(v)>1]

def run(request, base:Path, fault=None):
    a=AgentRun("deep_research",fault)
    a.plan=["Retrieve relevant cited documents","Compare numerical claims","Produce provenance-aware report"]
    try:
        sources=a.step("load_corpus",load_json,p=base/"data/sources.json")
        hits=a.step("search",search_sources,query=request.get("question", ""),sources=sources)
        if not hits: return a.finish("not_found","No matching evidence in the bundled corpus; no external web verification performed.")
        conflicts=a.step("compare",compare_claims,hits=hits)
        refs=[{"id":s["id"],"url":s["url"],"excerpt":s["excerpt"],"method":s["quality"]} for s in hits]
        report=f"Found {len(hits)} synthetic sources. " + (f"Conflicting claims for {', '.join(conflicts)}. " if conflicts else "No numeric conflicts detected. ") + "Citations identify in-bundle evidence only, not independently verified facts."
        return a.finish("success",report,refs,conflicts=conflicts)
    except Exception as e:return result_from_exception(a,e)
