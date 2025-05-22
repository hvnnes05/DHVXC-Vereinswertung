import asyncio
from playwright.async_api import async_playwright
import json

async def scrape_urenschwang_cup():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto("https://de.dhv-xc.de/competition/urenschwang-cup#/tab/gesamt", wait_until="networkidle")

        # Warten, bis die Tabelle geladen ist
        await page.wait_for_selector("table")

        # Extrahieren der Tabellenzeilen
        rows = await page.query_selector_all("table tbody tr")
        results = []

        for row in rows:
            cells = await row.query_selector_all("td")
            if len(cells) >= 3:
                platz = await cells[0].inner_text()
                verein = await cells[1].inner_text()
                punkte = await cells[2].inner_text()
                results.append({
                    "platz": platz.strip(),
                    "verein": verein.strip(),
                    "punkte": punkte.strip()
                })

        # Speichern der Daten in einer JSON-Datei
        with open("dhvxc-data.json", "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

        await browser.close()

# Ausführen des Skripts
asyncio.run(scrape_urenschwang_cup())
