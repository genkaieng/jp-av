from playwright.sync_api import sync_playwright
import yaml
from parser import Parser
import time

base_url = "https://video.dmm.co.jp/av/actress/?syllabary=a"

output = list()

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto(base_url)
    page.get_by_role("link", name="はい").click()

    page.get_by_role("heading", name="AV女優一覧").wait_for()

    html = page.content()
    parser = Parser(html=html, base_url=base_url)
    aiueo_urls = parser.aiueo()

    def gotoWithRetry(url: str, retry=0):
        if retry > 0:
            print("retry:", retry)
        try:
            page.goto(url)
            page.wait_for_load_state("networkidle")
        except Exception as e:
            if retry < 2:
                time.sleep(4 * retry)
                gotoWithRetry(url, retry + 1)
            else:
                raise e

    for url in aiueo_urls:
        gotoWithRetry(url)

        if page.locator("text=から始まる女優は見つかりませんでした。").count() > 0:
            continue

        html = page.content()
        parser = Parser(html=html, base_url=url)
        pages = parser.pages()

        for next in pages:
            print("goto:", next)
            gotoWithRetry(next)

            html = page.content()
            parser = Parser(html=html, base_url=next)
            output = output + parser.parse()

    browser.close()

parser = Parser(html)
output = output + parser.parse()

with open("dist/actress.yaml", "w", encoding="utf-8") as f:
    data = list(
        map(
            lambda item: {"name": item[0], "name_kana": item[1], "pic": item[3]}, output
        )
    )
    yaml.safe_dump(
        {"AV女優一覧": data}, f, allow_unicode=True, default_flow_style=False
    )

print("done!")
