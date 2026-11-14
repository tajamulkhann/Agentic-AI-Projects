from pathlib import Path
from agentic_core import AgentRun, result_from_exception
from tools import schema, query

TEMPLATES={
    "revenue_by_category":"SELECT category,ROUND(SUM(amount),2) AS revenue FROM orders GROUP BY category ORDER BY revenue DESC",
    "revenue_by_customer":"SELECT c.name AS customer, ROUND(SUM(o.amount),2) AS revenue FROM orders o JOIN customers c ON o.customer_id=c.id GROUP BY c.id ORDER BY revenue DESC",
    "monthly_revenue":"SELECT substr(ordered_at,1,7) AS month, ROUND(SUM(amount),2) AS revenue FROM orders GROUP BY month ORDER BY month"
}
def classify(q):
    q=q.lower()
    if any(w in q for w in ("delete","drop","update","insert","alter","truncate")):
        return "unsafe"
    if "category" in q:return "revenue_by_category"
    if "customer" in q:return "revenue_by_customer"
    if "month" in q:return "monthly_revenue"
    return "unsupported"

def run(request,base:Path,fault=None):
    a=AgentRun("sql_analyst",fault)
    a.plan=["Classify question","Inspect read-only schema","Select allowlisted query","Execute and explain"]
    intent=classify(request.get("question",""))
    if intent=="unsafe":return a.finish("rejected","Read-only policy: destructive statements are not permitted.")
    if intent=="unsupported":return a.finish("not_found","Question not supported by the safe SQL templates.")
    try:
        db=base/"data/sales.db"
        tables=a.step("schema",schema,db=db)
        if "orders" not in tables:return a.finish("error","Required table missing")
        sql=TEMPLATES[intent]
        rows=a.step("execute_sql",query,db=db,statement=sql)
        return a.finish("success",f"{intent}: returned {len(rows)} rows using read-only SQL.",[{"sql":sql,"rows":rows}],chart=rows)
    except Exception as e:return result_from_exception(a,e)
