 import asyncio
from playwright.async_api import async_playwright
import json

URL = "https://www.dhv-xc.de/xc/modules/leonardo/index.php?name=leonardo&op=clubs"
HEADERS = {'User-Agent': 'Mozilla/5.0'}

def scrape_dhvxc():
    response = requests.get(URL, headers=HEADERS)
    soup = BeautifulSoup(response.text, 'html.parser')

    table = soup.find('table')
    if not table:
        print("❌ Tabelle nicht gefunden")
        return

    rows = table.find_all('tr')[1:]

    results = []
    for row in rows:
        cols = row.find_all('td')
        if len(cols) >= 3:
            platz = cols[0].text.strip()
            verein = cols[1].text.strip()
            punkte = cols[2].text.strip().replace('.', '')
            results.append({
                'platz': int(platz),
                'verein': verein,
                'punkte': int(punkte) if punkte.isdigit() else 0
            })

        # Speichern der Daten in einer JSON-Datei
        with open("dhvxc-data.json", "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

        await browser.close()

# Ausführen des Skripts
asyncio.run(scrape_urenschwang_cup())
