import asyncio
from playwright.async_api import async_playwright
import json

# URLs für "gesamt" und "lokal"
URLS = {
    "gesamt": "https://de.dhv-xc.de/competition/vereinswertung#/tab/gesamt",
    "lokal": "https://de.dhv-xc.de/competition/urenschwang-cup#/tab/huetten",
}

OUTPUT_FILES = {
    "gesamt": "dhvxc-data.json",
    "lokal": "dhvxc-data-lokal.json",
}

async def scrape(type_key: str):
    url = URLS[type_key]
    output_file = OUTPUT_FILES[type_key]

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        print(f"Öffne {url} ...")
        await page.goto(url)

        # Warte, bis der Tab-Inhalt geladen ist (eventuell anpassen)
        await page.wait_for_selector("table")  # je nach Seite anpassen

        # Scrape die Top 5 Zeilen der Tabelle
        rows = await page.query_selector_all("table tbody tr")
        data = []

        for i, row in enumerate(rows[:5]):
            cols = await row.query_selector_all("td")
            # Je nach Tabellenstruktur anpassen
            rank = await cols[0].inner_text()
            pilot = await cols[1].inner_text()
            score = await cols[2].inner_text()

            data.append({
                "RankNumber": rank.strip(),
                "Pilot": pilot.strip(),
                "Score": score.strip(),
            })

        await browser.close()

    # Schreibe in JSON
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"{output_file} geschrieben.")

async def main():
    await scrape("gesamt")
    await scrape("lokal")

if __name__ == "__main__":
    asyncio.run(main())
