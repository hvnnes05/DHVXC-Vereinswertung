 import requests
from bs4 import BeautifulSoup
import json

URL = "https://de.dhv-xc.de/competition/urenschwang-cup#/tab/gesamt"  # Beispiel-Link
HEADERS = {'User-Agent': 'Mozilla/5.0'}

def scrape_dhvxc():
    response = requests.get(URL, headers=HEADERS)
    soup = BeautifulSoup(response.text, 'html.parser')

    table = soup.find('table', {'class': 'main_table'})  # ggf. anpassen
    rows = table.find_all('tr')[1:]  # erste Zeile ist Header

    results = []
    for row in rows:
        cols = row.find_all('td')
        if len(cols) < 3:
            continue
        platz = cols[0].text.strip()
        verein = cols[1].text.strip()
        punkte = cols[2].text.strip().replace('.', '')  # Komma/Trennzeichen entfernen
        results.append({
            'platz': int(platz),
            'verein': verein,
            'punkte': int(punkte),
        })

    with open('dhvxc-data.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

if __name__ == '__main__':
    scrape_dhvxc()
