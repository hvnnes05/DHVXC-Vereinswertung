from playwright.sync_api import sync_playwright
import json
import time

URL = "https://de.dhv-xc.de/competition/urenschwang-cup#/tab/gesamt"

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(URL)

        # Warte auf Tabelle
        page.wait_for_selector("table")

        # Zusätzliche Wartezeit, da dynamisch geladen wird
        time.sleep(5)

        # Zeilen auslesen
        rows = page.query_selector_all("table tbody tr")
        top_5 = []

        for row in rows[:5]:
            cells = row.query_selector_all("td")

            if len(cells) >= 5:
                # Hole rank aus der ersten Zelle
                rank = cells[0].inner_text().strip()

                # Hole pilot aus der dritten Zelle (aber nur reinen Namen)
                pilot = cells[2].query_selector("div > div")  # Spezifischer
                pilot_name = pilot.inner_text().strip() if pilot else cells[2].inner_text().strip()

                # Hole score aus der fünften Zelle – oft steht der Hauptwert in <strong> oder ähnlichem
                score_el = cells[4].query_selector("strong") or cells[4]
                score_text = score_el.inner_text().strip()

                top_5.append({
                    "RankNumber": rank,
                    "Pilot": pilot_name,
                    "Score": score_text
                })

        # Speichern
        with open("dhvxc-data.json", "w", encoding="utf-8") as f:
            json.dump(top_5, f, ensure_ascii=False, indent=2)

        browser.close()

if __name__ == "__main__":
    run()
