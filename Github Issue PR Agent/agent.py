from pathlib import Path
import difflib
import subprocess
import sys
import tempfile
import shutil
from agentic_core import AgentRun, load_json, result_from_exception

def load_issue(issues,issue_id):
    return next((x for x in issues if x["id"]==issue_id),None)

def propose_patch(source):
    old="discounted=round(price*(1-discount_rate),2)"
    new="discounted=price*(1-discount_rate)"
    if old not in source:raise ValueError("Known defect pattern absent; no automatic patch")
    return source.replace(old,new)

def verify_patch(repo,patched):
    with tempfile.TemporaryDirectory(prefix="agent-pr-") as temp:
        work=Path(temp)/"repo";shutil.copytree(repo,work)
        (work/"billing.py").write_text(patched)
        check=subprocess.run([sys.executable,"-m","pytest","-q","-p","no:cacheprovider","test_billing.py"],cwd=work,capture_output=True,text=True,timeout=20,check=False)
        return {"passed":check.returncode==0,"returncode":check.returncode,"stdout":check.stdout[-2000:],"stderr":check.stderr[-1200:]}

def run(request,base:Path,fault=None):
    a=AgentRun("issue_to_pr",fault)
    a.plan=["Select local issue","Inspect allowlisted fixture source","Propose minimal patch","Run tests in a temporary copy","Draft PR, no push"]
    try:
        issues=a.step("issues",load_json,p=base/"data/issues.json")
        issue=a.step("lookup_issue",load_issue,issues=issues,issue_id=request.get("issue_id"))
        if not issue:return a.finish("not_found","No matching issue in local fixture.")
        if issue["issue_type"]!="calculation":return a.finish("needs_approval","Unsupported security-sensitive change; human design review required.")
        repo=base/"data/fixture_repo";original=(repo/"billing.py").read_text()
        patch=a.step("propose_patch",propose_patch,source=original)
        check=a.step("run_tests",verify_patch,repo=repo,patched=patch)
        if not check["passed"]:return a.finish("error","Isolated regression tests failed.",[{"test_output":check}])
        diff="".join(difflib.unified_diff(original.splitlines(True),patch.splitlines(True),fromfile="a/billing.py",tofile="b/billing.py"))
        out=base/"outputs";out.mkdir(exist_ok=True)
        (out/"proposed_fix.patch").write_text(diff)
        (out/"pr_draft.md").write_text(f"# Fixes local issue #{issue['id']}\n\n{issue['title']}\n\nTests: pass in isolated fixture repo. Requires human review. Not pushed.\n")
        return a.finish("success",f"Patch ready for review for issue #{issue['id']}; tests passed. No remote PR created.",[{"patch":diff,"test_output":check}],pr_created=False)
    except Exception as e:return result_from_exception(a,e)
