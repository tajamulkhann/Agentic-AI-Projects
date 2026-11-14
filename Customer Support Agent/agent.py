from pathlib import Path
from agentic_core import AgentRun, load_json, result_from_exception

def find_order(orders,order_id):
    return next((o for o in orders if o["order_id"]==order_id),None)

def decide(order,policy,issue):
    if issue=="refund":
        if order["status"]!="delivered":return "deny","Order has not been delivered."
        if order["days_since_delivery"]>policy["refund"]["window_days"]:return "deny","Outside 30-day return window."
        return "needs_approval",f"Proposed refund: ${order['total']:.2f}; staff approval required. No refund executed."
    if issue=="delivery":return "success",f"Order status is {order['status']}. Escalate tracking if late."
    return "needs_approval","Proposed replacement for human review. No account change executed."

def run(request,base:Path,fault=None):
    a=AgentRun("support_resolution",fault)
    a.plan=["Authenticate order-to-customer link","Retrieve support policy","Investigate order","Draft resolution without execution"]
    try:
        orders=a.step("orders",load_json,p=base/"data/orders.json")
        order=a.step("lookup_order",find_order,orders=orders,order_id=request.get("order_id"))
        if not order or order["customer_id"]!=request.get("customer_id"):
            return a.finish("rejected","Order not found or customer authorization failed.")
        policies=a.step("retrieve_policy",load_json,p=base/"data/policies.json")
        issue=request.get("issue","refund")
        decision,message=a.step("resolve",decide,order=order,policy=policies,issue=issue)
        return a.finish(decision,message,[{"order_id":order["order_id"],"policy":policies.get(issue,policies.get("refund"))}],proposed_action=issue,executed_action=False)
    except Exception as e:return result_from_exception(a,e)
