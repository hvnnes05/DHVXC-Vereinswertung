from playwright.sync_api import sync_playwright
import json
import time

URL = "https://de.dhv-xc.de/competition/urenschwang-cup#/tab/gesamt"

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(URL)

        # Warte auf die Tabelle, z. B. die Klassentabelle mit Rangliste
        page.wait_for_selector("table")

        # Warte etwas länger, falls dynamisch nachgeladen wird
        time.sleep(5)

        # Selektiere die Tabellenzeilen der Rangliste
        rows = page.query_selector_all("table tbody tr")

        top_5 = []

        for row in rows[:5]:
            cells = row.query_selector_all("td")

            if len(cells) >= 5:
                rank = cells[0].inner_text().strip()
                pilot = cells[2].inner_text().strip()
                score = cells[4].inner_text().strip()

                top_5.append({
                    "ranknumber": rank,
                    "pilot": pilot,
                    "score": score
                })

        with open("dhvxc-data.json", "w", encoding="utf-8") as f:
            json.dump(top_5, f, ensure_ascii=False, indent=2)

        browser.close()

if __name__ == "__main__":
    run()
