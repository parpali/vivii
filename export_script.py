import requests
import json
import time
import os

# Konfiguration
M3U_PATH = "vavoo_channels.m3u"
JSON_PATH = "vavoo_full_export.json"
HEADERS = {
    'User-Agent': 'MediaHubMX/2',
    'Accept': 'application/json'
}

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
    session.headers.update(HEADERS)
    
    print("Rufe Gruppen ab...")
    try:
        groups_res = session.get("https://www2.vavoo.to/live2/index", params={"output": "json"}, timeout=10)
        countries = sorted(list(set([c.get("group") for c in groups_res.json() if c.get("group")])))
    except Exception as e:
        print(f"Fehler beim Gruppenabruf: {e}")
        return

    m3u_content = "#EXTM3U\n"
    full_dump = {}

    for country in countries:
        print(f"Verarbeite Land: {country}")
        cursor = 0
        country_channels = []
        
        while True:
            payload = {
                "language": "de", "region": "AT", "catalogId": "vto-iptv",
                "filter": {"group": country}, "cursor": cursor, "clientVersion": "3.0.2"
            }
            try:
                res = session.post("https://vavoo.to/vto-cluster/mediahubmx-catalog.json", json=payload, timeout=15)
                data = res.json()
                items = data.get("items", [])
                country_channels.extend(items)
                cursor = data.get("nextCursor")
                if not cursor: break
            except: break
        
        for item in country_channels:
            name = item.get("name", "Unknown")
            # Link auflösen
            resolved_url = resolve_vavoo_link(session, item.get("url"))
            
            if resolved_url:
                # M3U Eintrag hinzufügen
                # tvg-name und group-title helfen IPTV-Playern bei der Sortierung
                m3u_content += f'#EXTINF:-1 tvg-name="{name}" group-title="{country}",{name}\n'
                m3u_content += f'{resolved_url}\n'
                
                # Für JSON speichern
                item["resolved_url"] = resolved_url
                time.sleep(0.05) # Kurze Pause

        full_dump[country] = country_channels

    # Speichern der Dateien
    with open(M3U_PATH, 'w', encoding='utf-8') as f:
        f.write(m3u_content)
    
    with open(JSON_PATH, 'w', encoding='utf-8') as f:
        json.dump(full_dump, f, ensure_ascii=False, indent=4)
        
    print(f"Export beendet. M3U gespeichert unter {M3U_PATH}")

if __name__ == "__main__":
    main()
