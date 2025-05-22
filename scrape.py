from playwright.sync_api import sync_playwright
import json
import time
import re
import sys

URLS = {
    "gesamt": "https://de.dhv-xc.de/competition/urenschwang-cup#/tab/gesamt",
    "huetten": "https://de.dhv-xc.de/competition/urenschwang-cup#/tab/huetten"
}

OUTPUT_FILES = {
    "gesamt": "dhvxc-data.json",
    "huetten": "dhvxc-data-lokal.json"
}

def extract_score(raw_text):
    # Extrahiere die erste "xxx,xx"-Zahl nach dem Rang – das ist der Score
    match = re.search(r'\d+,\d{2}', raw_text)
    return match.group(0) if match else ""

def scrape_tab(page, tab_name):
    print(f"Scraping {tab_name} tab...")
    
    try:
        page.goto(URLS[tab_name], wait_until="networkidle", timeout=30000)
        print(f"Seite geladen: {URLS[tab_name]}")
        
        # Warte auf Tabelle mit längerer Wartezeit
        print("Warte auf Tabelle...")
        page.wait_for_selector("table", timeout=15000)
        time.sleep(8)  # Längere Wartezeit für dynamische Inhalte
        
        # Prüfe ob Tabelle Daten hat
        rows = page.query_selector_all("table tbody tr")
        print(f"Gefundene Zeilen: {len(rows)}")
        
        if len(rows) == 0:
            print("Keine Tabellenzeilen gefunden!")
            # Versuche alternative Selektoren
            rows = page.query_selector_all("table tr")
            print(f"Alternative Suche - Gefundene Zeilen: {len(rows)}")
        
        top_5 = []

        for i, row in enumerate(rows[:5]):
            try:
                cells = row.query_selector_all("td")
                print(f"Zeile {i+1}: {len(cells)} Zellen gefunden")

                if len(cells) >= 5:
                    # Rang extrahieren (meist steht er in cell[1] als Text)
                    rank_text = cells[1].inner_text().strip()
                    rank = rank_text.split()[0] if rank_text else ""
                    print(f"  Rang: '{rank}'")

                    # Pilot extrahieren
                    pilot_el = cells[2].query_selector("div > div") or cells[2]
                    pilot_name = pilot_el.inner_text().strip()
                    print(f"  Pilot: '{pilot_name}'")

                    # Score extrahieren
                    raw_score = cells[4].inner_text().strip()
                    score = extract_score(raw_score)
                    print(f"  Score: '{score}' (Raw: '{raw_score}')")

                    if rank and pilot_name:  # Nur hinzufügen wenn Rang und Pilot vorhanden
                        top_5.append({
                            "RankNumber": rank,
                            "Pilot": pilot_name,
                            "Score": score
                        })
                else:
                    print(f"  Zeile {i+1} hat nur {len(cells)} Zellen, überspringe...")
                    
            except Exception as e:
                print(f"Fehler beim Verarbeiten von Zeile {i+1}: {e}")
                continue

        # In entsprechende Datei speichern
        print(f"Speichere {len(top_5)} Einträge in {OUTPUT_FILES[tab_name]}")
        with open(OUTPUT_FILES[tab_name], "w", encoding="utf-8") as f:
            json.dump(top_5, f, ensure_ascii=False, indent=2)
        
        print(f"Daten erfolgreich in {OUTPUT_FILES[tab_name]} gespeichert")
        return top_5
        
    except Exception as e:
        print(f"Fehler beim Scrapen von {tab_name}: {e}")
        # Erstelle leere Datei als Fallback
        with open(OUTPUT_FILES[tab_name], "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=2)
        return []

def run():
    try:
        with sync_playwright() as p:
            print("Starte Browser...")
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            # User Agent setzen um nicht als Bot erkannt zu werden
            page.set_extra_http_headers({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            })
            
            # Scrape beide Tabs
            gesamt_data = scrape_tab(page, "gesamt")
            huetten_data = scrape_tab(page, "huetten")
            
            print(f"\n=== ZUSAMMENFASSUNG ===")
            print(f"Gesamt tab: {len(gesamt_data)} entries scraped")
            print(f"Huetten tab: {len(huetten_data)} entries scraped")
            
            browser.close()
            
            if len(gesamt_data) == 0 and len(huetten_data) == 0:
                print("WARNUNG: Keine Daten gefunden!")
                sys.exit(1)
                
    except Exception as e:
        print(f"Kritischer Fehler: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run()