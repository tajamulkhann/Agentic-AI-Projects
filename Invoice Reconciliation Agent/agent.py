from pathlib import Path
import csv
from agentic_core import AgentRun, result_from_exception

def read_csv(path):
    with Path(path).open(newline="") as f:return list(csv.DictReader(f))

def match(invoice,po,receipt):
    exceptions=[]
    if invoice["supplier"]!=po["supplier"]:exceptions.append("supplier mismatch")
    if abs(float(invoice["unit_price"])-float(po["unit_price"]))>0.01:exceptions.append("price mismatch")
    if float(invoice["qty"])>float(receipt["received_qty"]):exceptions.append("invoiced quantity exceeds received")
    if abs(float(invoice["amount"])-float(invoice["unit_price"])*float(invoice["qty"]))>0.01:exceptions.append("invoice arithmetic mismatch")
    return exceptions

def run(request,base:Path,fault=None):
    a=AgentRun("invoice_reconciliation",fault)
    a.plan=["Extract invoice","Look up PO","Match goods receipt","Check tolerance","Document decision"]
    try:
        invoices=a.step("extract_invoice",read_csv,path=base/"data/invoices.csv")
        invoice=next((i for i in invoices if i["invoice_id"]==request.get("invoice_id")),None)
        if invoice is None:return a.finish("not_found","Invoice not found")
        pos=a.step("lookup_po",read_csv,path=base/"data/purchase_orders.csv")
        po=next((p for p in pos if p["po_id"]==invoice["po_id"]),None)
        if not po:return a.finish("needs_approval","No matching purchase order. Route invoice to AP exception queue.",[{"invoice":invoice}])
        receipts=a.step("lookup_receipt",read_csv,path=base/"data/receipts.csv")
        receipt=next((r for r in receipts if r["po_id"]==po["po_id"]),None)
        if not receipt:return a.finish("needs_approval","No matching goods receipt; manual review needed.")
        issues=a.step("three_way_match",match,invoice=invoice,po=po,receipt=receipt)
        if issues:return a.finish("needs_approval","Discrepancy: "+"; ".join(issues)+". No payment action executed.",[{"invoice_id":invoice["invoice_id"],"issues":issues}])
        return a.finish("success",f"Three-way match passed for {invoice['invoice_id']} (${float(invoice['amount']):.2f}). No payment executed.",[{"invoice":invoice,"po":po,"receipt":receipt}])
    except Exception as e:return result_from_exception(a,e)
