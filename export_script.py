import requests
import json
import time

# Konfiguration
M3U_FILE = "vavoo_channels.m3u"
JSON_FILE = "vavoo_full_export.json"

def resolve_vavoo_link(session, link):
    url = "https://vavoo.to/vto-cluster/mediahubmx-resolve.json"
    payload = {"language": "de", "region": "AT", "url": link, "clientVersion": "3.0.2"}
    try:
        res = session.post(url, json=payload, timeout=10)
        return res.json()[0].get("url")
    except:
        return None

def main():
    session = requests.Session()
    session.headers.update({'User-Agent': 'MediaHubMX/2'})
    
    print("Hole Ländergruppen...")
    try:
        groups = session.get("https://www2.vavoo.to/live2/index?output=json", timeout=10).json()
        countries = sorted(list(set([c.get("group") for c in groups if c.get("group")])))
    except Exception as e:
        print(f"Fehler beim Laden der Gruppen: {e}")
        return

    m3u_lines = ["#EXTM3U"]
    full_data = {}

    for country in countries:
        print(f"Verarbeite: {country}")
        payload = {"language":"de","region":"AT","catalogId":"vto-iptv","filter":{"group":country},"cursor":0,"clientVersion":"3.0.2"}
        
        try:
            r = session.post("https://vavoo.to/vto-cluster/mediahubmx-catalog.json", json=payload, timeout=15).json()
            items = r.get("items", [])
            country_channels = []

            for item in items:
                name = item.get("name")
                vavoo_url = item.get("url")
                
                # Link auflösen
                resolved = resolve_vavoo_link(session, vavoo_url)
                if resolved:
                    # M3U Eintrag
                    m3u_lines.append(f'#EXTINF:-1 group-title="{country}",{name}')
                    m3u_lines.append(resolved)
                    
                    # JSON Daten
                    item["resolved_url"] = resolved
                    country_channels.append(item)
                    
                time.sleep(0.05) # Rate limiting Schutz
            
            full_data[country] = country_channels
        except:
            continue

    # Dateien schreiben
    with open(M3U_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(m3u_lines))
    
    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(full_data, f, ensure_ascii=False, indent=4)
    
    print("Dateien erfolgreich lokal erstellt.")

if __name__ == "__main__":
    main()
