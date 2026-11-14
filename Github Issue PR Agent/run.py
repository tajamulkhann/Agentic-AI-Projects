"""Run from this project directory: python run.py [--evaluate]."""
from pathlib import Path
import argparse
import json
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
sys.path.insert(0,str(Path(__file__).resolve().parent))
from agentic_core import evaluate_suite,load_json
from agent import run

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--evaluate",action="store_true")
    parser.add_argument("--case",default=None,help="Case ID from data/eval_cases.json")
    parser.add_argument("--model-plan",action="store_true",help="Optional hosted LLM plan advice, requires OPENAI_API_KEY; may incur charges")
    args=parser.parse_args()
    BASE=Path(__file__).resolve().parent
    if args.evaluate:
        report=evaluate_suite(run,BASE)
        print(json.dumps({k:report[k] for k in ("passed","cases","task_success_rate","tool_failure_rate","mean_latency_ms","total_model_api_cost_usd")},indent=2))
    else:
        examples=load_json(BASE/"data/eval_cases.json")
        case=next((x for x in examples if x["id"]==args.case),examples[0])
        output=run(case["request"],BASE,case.get("fault"))
        if args.model_plan:
            from agentic_core.model_bridge import suggest_plan
            output["hosted_model_plan"]=suggest_plan(case["request"],load_json(BASE/"data/tool_catalog.json")["allowed_tools"])
        print(json.dumps(output,indent=2,ensure_ascii=False))
