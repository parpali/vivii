import requests
import json
import time

M3U_FILE = "vavoo_channels.m3u"
JSON_FILE = "vavoo_full_export.json"
HEADERS = {'User-Agent': 'MediaHubMX/2'}

def main():
    session = requests.Session()
    session.headers.update(HEADERS)
    
    print("Hole Gruppen...")
    try:
        # Direkter Abruf der Gruppen
        groups = session.get("https://www2.vavoo.to/live2/index?output=json", timeout=10).json()
        countries = sorted(list(set([c.get("group") for c in groups if c.get("group")])))
    except Exception as e:
        print(f"Fehler: {e}")
        return

    m3u_lines = ["#EXTM3U"]
    full_data = {}

    for country in countries:
        print(f"Verarbeite: {country}")
        # Wir holen nur die erste Seite (ca. 100 Sender) pro Land für den Test
        payload = {
            "language": "de", "region": "AT", "catalogId": "vto-iptv",
            "filter": {"group": country}, "cursor": 0, "clientVersion": "3.0.2"
        }
        
        try:
            r = session.post("https://vavoo.to/vto-cluster/mediahubmx-catalog.json", json=payload, timeout=10).json()
            items = r.get("items", [])
            
            for item in items:
                name = item.get("name", "Unknown")
                raw_url = item.get("url")
                
                # TEST: Wir schreiben erst mal die RAW URL direkt in die M3U
                # Diese URLs funktionieren nicht direkt im Player, aber wir sehen, ob die M3U geschrieben wird!
                m3u_lines.append(f'#EXTINF:-1 group-title="{country}",{name}')
                m3u_lines.append(raw_url)
            
            full_data[country] = items
        except:
            continue

    # Dateien speichern
    print(f"Speichere M3U mit {len(m3u_lines)//2} Einträgen...")
    with open(M3U_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(m3u_lines))
    
    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(full_data, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()
