"""Optional *real browser* preview against local fixture; install playwright and Chromium.
No page submission is performed here, even when values have been populated.
"""
from pathlib import Path


def preview_in_browser(project_dir:Path, filled_fields:list[dict], screenshot:Path):
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True)
        try:
            page=browser.new_page()
            page.goto((project_dir/"data/supplier_form.html").resolve().as_uri())
            for field in filled_fields:
                page.locator(field["selector"]).fill(field["value"])
            page.screenshot(path=str(screenshot),full_page=True)
            return {"preview_screenshot":str(screenshot),"submitted":False}
        finally:browser.close()
