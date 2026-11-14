"""Run with: streamlit run app.py  (offline fixture demo)."""
from pathlib import Path
import sys
import json
import streamlit as st
import pandas as pd
BASE=Path(__file__).resolve().parent
sys.path.insert(0,str(BASE.parent))
sys.path.insert(0,str(BASE))
from agentic_core import load_json
from agent import run

st.set_page_config(page_title='Contract Review Agent',layout="wide")
st.title('Contract Review Agent')
st.caption("Offline reproducible agent demo | Synthetic data | No external changes")
examples=load_json(BASE/"data/eval_cases.json")
ids=[v["id"] for v in examples]
choice=st.selectbox("Select an example task",ids)
example=next(c for c in examples if c["id"]==choice)
request_txt=st.text_area("Request JSON (editable)",value=json.dumps(example["request"],indent=2),height=150)
use_model=st.checkbox("Optional hosted LLM planning (sends request to API; may incur charges)",value=False)
fault=st.selectbox("Inject a tool fault",["None"]+sorted({str(x.get("fault")) for x in examples if x.get("fault")}))
if st.button("Execute local workflow",type="primary"):
    try:
        request=json.loads(request_txt)
        response=run(request,BASE,None if fault=="None" else fault)
        if use_model:
            from agentic_core.model_bridge import suggest_plan
            response["hosted_model_plan"]=suggest_plan(request,load_json(BASE/"data/tool_catalog.json")["allowed_tools"])
            st.subheader("Hosted LLM suggested tool order (advisory only)")
            st.json(response["hosted_model_plan"])
        st.subheader(f"Status: {response['status']}")
        st.write(response["answer"])
        with st.expander("Cited evidence / work artifacts",expanded=True):st.json(response["evidence"])
        with st.expander("Full execution trace"):st.dataframe(pd.DataFrame(response["trace"]),use_container_width=True)
        st.json({"latency_ms":response["latency_ms"],"model_api_cost_usd":response["model_api_cost_usd"],"mode":response["runtime"]})
        if response.get("chart"):
            rows=response["chart"]
            numeric=[k for k,v in rows[0].items() if isinstance(v,(int,float))]
            dims=[k for k in rows[0] if k not in numeric]
            if numeric and dims:st.bar_chart(pd.DataFrame(rows).set_index(dims[0])[numeric])
    except (ValueError,TypeError) as ex:st.error(f"Input error: {ex}")

if (BASE/"outputs/evaluation.json").exists():
    st.divider();st.subheader("Measured local evaluation")
    report=load_json(BASE/"outputs/evaluation.json")
    cols=st.columns(3)
    cols[0].metric("Task success",f"{report['task_success_rate']:.0%}")
    cols[1].metric("Tool failure rate",f"{report['tool_failure_rate']:.1%}")
    cols[2].metric("Mean latency",f"{report['mean_latency_ms']:.2f} ms")
    st.caption(report["cost_note"])
    st.dataframe(pd.DataFrame([{k:v for k,v in c.items() if k!='result'} for c in report["details"]]),use_container_width=True)
