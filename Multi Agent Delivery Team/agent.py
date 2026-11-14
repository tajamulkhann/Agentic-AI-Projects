from pathlib import Path
import subprocess
import tempfile
import sys
from agentic_core import AgentRun, load_json, result_from_exception

def plan(spec):
    if spec["feature"] not in ("discount","tax"):return None
    return {"task":spec["task_id"],"acceptance":spec["acceptance"],"feature":spec["feature"]}

def implement(spec):
    pct = float(spec["percent"]) / 100
    sign = "-" if spec["feature"] == "discount" else "+"
    return f"def price_after_change(price):\n    return round(price * (1 {sign} {pct}), 2)\n"

def test_isolated(source,acceptance):
    with tempfile.TemporaryDirectory(prefix="agent-team-") as td:
        path=Path(td)
        (path/"feature.py").write_text(source)
        code = ("from feature import price_after_change\n"
                "def test_acceptance():\n"
                f"    assert price_after_change({acceptance['price']}) == {acceptance['expected']}\n")
        (path/"test_feature.py").write_text(code)
        p=subprocess.run([sys.executable,"-m","pytest","-q","-p","no:cacheprovider","test_feature.py"],cwd=path,capture_output=True,text=True,timeout=20)
        return {"passed":p.returncode==0,"stdout":p.stdout[-1000:],"stderr":p.stderr[-500:]}

def review(source,result):
    return result["passed"] and "eval(" not in source and "exec(" not in source and "price_after_change" in source

def run(request,base:Path,fault=None):
    a=AgentRun("multi_agent_delivery",fault)
    a.plan=["Planner: scope acceptance","Developer: implement","Tester: isolated regression","Reviewer: check output","Handoff"]
    try:
        specs=a.step("load_specs",load_json,p=base/"data/specs.json")
        spec=next((s for s in specs if s["task_id"]==request.get("task_id")),None)
        if not spec:return a.finish("not_found","Task not found")
        blueprint=a.step("planner",plan,spec=spec)
        if blueprint is None:return a.finish("needs_approval","Unsupported feature requires architecture review.")
        source=a.step("developer",implement,spec=spec)
        tests=a.step("tester",test_isolated,source=source,acceptance=spec["acceptance"])
        good=a.step("reviewer",review,source=source,result=tests)
        if not good:return a.finish("error","Review rejected generated code.",[{"tests":tests}])
        out=base/"outputs";out.mkdir(exist_ok=True)
        (out/f"{spec['task_id'].lower()}_feature.py").write_text(source)
        return a.finish("success",f"Planner, developer, tester and reviewer accepted {spec['task_id']}; tests passed.",[{"code":source,"test":tests}],handoff="human review before deployment")
    except Exception as e:return result_from_exception(a,e)
