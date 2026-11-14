from pathlib import Path
from agentic_core import AgentRun, load_json, result_from_exception
from tools import parse_form, validate_supplier

def run(request,base:Path,fault=None):
    a=AgentRun("browser_workflow",fault)
    a.plan=["Inspect local form fields","Load supplier record","Validate each required field","Prepare fill plan","Pause before submission"]
    try:
        fields=a.step("inspect_form",parse_form,html_path=base/"data/supplier_form.html")
        suppliers=a.step("suppliers",load_json,p=base/"data/suppliers.json")
        supplier=next((s for s in suppliers if s["supplier_id"]==request.get("supplier_id")),None)
        if not supplier:return a.finish("not_found","Supplier not found")
        issues=a.step("validate",validate_supplier,supplier=supplier,required=fields)
        if issues:return a.finish("rejected","; ".join(issues)+". No browser submission.")
        plan=[{"selector":f"[name='{key}']","value":supplier[key]} for key in fields]
        return a.finish("needs_approval","Form fill plan prepared; awaiting explicit submit approval. No submission performed.",plan,submitted=False)
    except Exception as e:return result_from_exception(a,e)
