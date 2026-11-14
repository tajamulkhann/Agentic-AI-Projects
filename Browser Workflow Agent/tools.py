from html.parser import HTMLParser
from pathlib import Path

class FormInputs(HTMLParser):
    def __init__(self):super().__init__();self.names=[]
    def handle_starttag(self,tag,attrs):
        if tag=="input":
            a=dict(attrs)
            if "name" in a:self.names.append(a["name"])

def parse_form(html_path):
    p=FormInputs();p.feed(Path(html_path).read_text());return p.names

def validate_supplier(supplier,required):
    missing=[x for x in required if not supplier.get(x)]
    if missing: return [f"Missing: {', '.join(missing)}"]
    if "@" not in supplier["email"] or "." not in supplier["email"].split("@")[-1]:return ["Invalid contact email"]
    return []
