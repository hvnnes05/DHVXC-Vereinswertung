import requests
from bs4 import BeautifulSoup
import json

URL = "https://de.dhv-xc.de/competition/urenschwang-cup#/tab/gesamt"
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

    with open('dhvxc-data.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    scrape_dhvxc()
