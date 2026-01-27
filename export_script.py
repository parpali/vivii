# -*- coding: utf-8 -*-
import requests
import json
import time
import os

def main():
    session = requests.Session()
    # Identische Header wie im erfolgreichen Termux-Test
    session.headers.update({
        'User-Agent': 'MediaHubMX/2',
        'Accept': 'application/json',
        'Content-Type': 'application/json; charset=utf-8',
        'Accept-Encoding': 'gzip'
    })
    
    print("--- VAVOO GITHUB EXPORT ---")
    
    # 1. Länderliste laden
    try:
        group_res = session.get("https://www2.vavoo.to/live2/index?output=json", timeout=20).json()
        countries = sorted(list(set([c.get("group") for c in group_res if c.get("group")])))
        print(f"Gefundene Länder: {len(countries)}")
    except Exception as e:
        print(f"Fehler beim Laden der Gruppen: {e}")
        return

    m3u_lines = ["#EXTM3U"]
    full_data = {}

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
            # Senden als String verhindert Fehler 400 auf GitHub
            r = session.post(
                "https://vavoo.to/vto-cluster/mediahubmx-catalog.json", 
                data=json.dumps(payload), 
                timeout=30
            )
            
            if r.status_code == 200:
                items = r.json().get("items", [])
                full_data[country] = items
                for item in items:
                    name = item.get("name", "Unknown").split(".")[0].strip()
                    url = item.get("url", "")
                    if url:
                        m3u_lines.append(f'#EXTINF:-1 group-title="{country}",{name}')
                        m3u_lines.append(url)
                print(f"Erfolg: {country} ({len(items)} Kanäle)")
            else:
                print(f"Problem: {country} (Status {r.status_code})")
                
        except Exception:
            print(f"Timeout bei: {country}")
            continue
        
        time.sleep(0.1)

    # 3. Dateien schreiben
    with open("vavoo_all.m3u", "w", encoding="utf-8") as f:
        f.write("\n".join(m3u_lines))
    
    with open("vavoo_full.json", "w", encoding="utf-8") as f:
        json.dump(full_data, f, ensure_ascii=False, indent=4)
        
    print("Export abgeschlossen.")

if __name__ == "__main__":
    main()
