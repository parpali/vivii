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
    
    # 1. Länderliste laden
    try:
        group_res = session.get("https://www2.vavoo.to/live2/index?output=json", timeout=20).json()
        countries = sorted(list(set([c.get("group") for c in group_res if c.get("group")])))
    except Exception as e:
        print(f"Fehler beim Laden der Gruppen: {e}")
        return

    m3u_lines = ["#EXTM3U"]
    
    # 2. Länder abarbeiten
    for country in countries:
        payload = {
            "language": "de",
            "region": "AT",
            "catalogId": "vto-iptv",
            "id": "vto-iptv",
            "adult": False,
            "search": "",
            "sort": "name",
            "filter": {"group": country},
            "cursor": 0,
            "clientVersion": "3.0.2"
        }

        try:
            # Senden als json.dumps verhindert Fehler 400
            r = session.post(
                "https://vavoo.to/vto-cluster/mediahubmx-catalog.json", 
                data=json.dumps(payload), 
                timeout=30
            )
            
            if r.status_code == 200:
                items = r.json().get("items", [])
                for item in items:
                    # NAME CLEANING: Alles nach dem Punkt entfernen
                    raw_name = item.get("name", "Unknown")
                    clean_name = raw_name.split(".")[0].strip()
                    
                    url = item.get("url", "")
                    if url:
                        m3u_lines.append(f'#EXTINF:-1 group-title="{country}",{clean_name}')
                        m3u_lines.append(url)
                print(f"Erfolg: {country} ({len(items)} Kanäle)")
            else:
                print(f"Status {r.status_code} bei {country}")
                
        except Exception:
            continue
        
        time.sleep(0.05)

    # 3. Datei schreiben
    with open("vavoo_all.m3u", "w", encoding="utf-8") as f:
        f.write("\n".join(m3u_lines))
        
    print("M3U Export fertig.")

if __name__ == "__main__":
    main()
