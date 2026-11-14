"""Per-project reproducibility and safety contract tests."""
from pathlib import Path
import json
import subprocess
import sys
BASE=Path(__file__).resolve().parents[1]

def test_real_suite():
    proc=subprocess.run([sys.executable,"run.py","--evaluate"],cwd=BASE,capture_output=True,text=True,timeout=120)
    assert proc.returncode==0,proc.stderr
    report=json.loads((BASE/"outputs/evaluation.json").read_text())
    assert report["cases"]>=4
    assert report["task_success_rate"]==1.0,[(c["case"],c["actual_status"]) for c in report["details"] if not c["passed"]]
    assert report["total_model_api_cost_usd"]==0

def test_failure_case_has_a_real_failed_tool():
    report=json.loads((BASE/"outputs/evaluation.json").read_text())
    faulted=[c for c in report["details"] if c["tool_failures"]>0]
    assert faulted and all(c["actual_status"]=="error" for c in faulted)
