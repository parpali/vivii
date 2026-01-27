# -*- coding: utf-8 -*-
import requests
import json
import time
import os

def main():
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'MediaHubMX/2',
        'Accept': 'application/json',
        'Content-Type': 'application/json; charset=utf-8'
    })
    
    try:
        group_res = session.get("https://www2.vavoo.to/live2/index?output=json", timeout=20).json()
        countries = sorted(list(set([c.get("group") for c in group_res if c.get("group")])))
    except Exception as e:
        print(f"Fehler beim Laden der Gruppen: {e}")
        return

    m3u_lines = ["#EXTM3U"]
    full_json_data = {} # Hier werden die Daten für die JSON gesammelt

    for country in countries:
        payload = {
            "language": "de", "region": "AT", "catalogId": "vto-iptv", "id": "vto-iptv",
            "adult": False, "search": "", "sort": "name", "filter": {"group": country},
            "cursor": 0, "clientVersion": "3.0.2"
        }

        try:
            r = session.post("https://vavoo.to/vto-cluster/mediahubmx-catalog.json", 
                             data=json.dumps(payload), timeout=30)
            
            if r.status_code == 200:
                items = r.json().get("items", [])
                
                # Daten für JSON speichern
                full_json_data[country] = []
                
                for item in items:
                    # Name säubern (alles nach dem Punkt weg)
                    clean_name = item.get("name", "Unknown").split(".")[0].strip()
                    url = item.get("url", "")
                    
                    if url:
                        # M3U Liste füllen
                        m3u_lines.append(f'#EXTINF:-1 group-title="{country}",{clean_name}')
                        m3u_lines.append(url)
                        
                        # JSON Liste füllen
                        full_json_data[country].append({
                            "name": clean_name,
                            "url": url,
                            "group": country
                        })
                print(f"Erfolg: {country} ({len(items)} Kanäle)")
            else:
                print(f"Status {r.status_code} bei {country}")
        except Exception:
            continue
        
        time.sleep(0.05)

    # --- BEIDE DATEIEN SCHREIBEN ---
    
    # 1. M3U speichern
    with open("vavoo_all.m3u", "w", encoding="utf-8") as f:
        f.write("\n".join(m3u_lines))
    
    # 2. JSON speichern (WICHTIG: Überschreibt die alte Datei)
    with open("vavoo_full.json", "w", encoding="utf-8") as f:
        json.dump(full_json_data, f, ensure_ascii=False, indent=4)
        
    print("M3U und JSON erfolgreich aktualisiert.")

if __name__ == "__main__":
    main()
