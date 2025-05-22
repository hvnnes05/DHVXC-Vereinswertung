from playwright.sync_api import sync_playwright
import json
import time
import re

URL = "https://de.dhv-xc.de/competition/urenschwang-cup#/tab/gesamt"

def extract_score(raw_text):
    # Extrahiere die erste "xxx,xx"-Zahl nach dem Rang – das ist der Score
    match = re.search(r'\d+,\d{2}', raw_text)
    return match.group(0) if match else ""

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(URL)

        # Warte auf Tabelle
        page.wait_for_selector("table")
        time.sleep(5)

        rows = page.query_selector_all("table tbody tr")
        top_5 = []

        for row in rows[:5]:
            cells = row.query_selector_all("td")

            if len(cells) >= 5:
                # Rang extrahieren (meist steht er in cell[1] als Text)
                rank_text = cells[1].inner_text().strip()
                rank = rank_text.split()[0] if rank_text else ""

                # Pilot extrahieren
                pilot_el = cells[2].query_selector("div > div") or cells[2]
                pilot_name = pilot_el.inner_text().strip()

                # Score extrahieren
                raw_score = cells[4].inner_text().strip()
                score = extract_score(raw_score)

                top_5.append({
                    "RankNumber": rank,
                    "Pilot": pilot_name,
                    "Score": score
                })

        with open("dhvxc-data.json", "w", encoding="utf-8") as f:
            json.dump(top_5, f, ensure_ascii=False, indent=2)

        browser.close()

if __name__ == "__main__":
    run()
