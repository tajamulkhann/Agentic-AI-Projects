from pathlib import Path
from agentic_core import AgentRun, load_json, result_from_exception

def evaluate_clauses(contract,playbook):
    findings=[]
    for line in contract["lines"]:
        rule=playbook.get(line["type"])
        if rule and any(flag in line["text"].lower() for flag in rule["risk_phrases"]):
            findings.append({"clause":line["type"],"line":line["line"],"excerpt":line["text"],"preferred":rule["preferred"],"citation":f"{contract['contract_id']}:L{line['line']}"})
    return findings

def run(request,base:Path,fault=None):
    a=AgentRun("contract_review",fault)
    a.plan=["Retrieve contract","Load policy playbook","Evaluate individual clauses","Write evidenced human review"]
    try:
        contracts=a.step("contracts",load_json,p=base/"data/contracts.json")
        contract=next((c for c in contracts if c["contract_id"]==request.get("contract_id")),None)
        if not contract:return a.finish("not_found","Contract unavailable")
        rules=a.step("playbook",load_json,p=base/"data/playbook.json")
        findings=a.step("review",evaluate_clauses,contract=contract,playbook=rules)
        if findings:
            return a.finish("needs_approval",f"{len(findings)} playbook deviations in {contract['contract_id']} require human legal assessment.",findings,legal_advice=False)
        return a.finish("success",f"No flagged deviations in {contract['contract_id']} under this limited synthetic playbook.",[{"contract":contract["contract_id"]}],legal_advice=False)
    except Exception as e:return result_from_exception(a,e)
