from pathlib import Path
import json
import subprocess
import sys
ROOT=Path(__file__).resolve().parents[1]
PROJECTS=sorted(x for x in ROOT.iterdir() if x.is_dir() and x.name[:2].isdigit())

def test_all_ten_projects_and_evidence():
    assert len(PROJECTS)==10
    for p in PROJECTS:
        for relative in ["README.md","agent.py","app.py","run.py","analysis.ipynb",".env.example","architecture.md","data/README.md","data/eval_cases.json","outputs/evaluation.json","outputs/dashboard.html","outputs/success.json","outputs/failure.json","tests/test_agent.py"]:
            assert (p/relative).is_file(),f"{p.name}/{relative} missing"
        report=json.loads((p/"outputs/evaluation.json").read_text())
        assert report["cases"]>=4
        assert report["passed"]==report["cases"],p.name
        assert report["total_model_api_cost_usd"]==0
