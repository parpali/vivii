# -*- coding: utf-8 -*-
import requests
import json
import time
import os

# Konfiguration
M3U_FILE = "vavoo_germany.m3u"
HEADERS = {'User-Agent': 'MediaHubMX/2', 'Accept-Encoding': 'gzip'}
session = requests.Session()
session.headers.update(HEADERS)

def resolve_link(link):
    url = "https://vavoo.to/vto-cluster/mediahubmx-resolve.json"
    _data = {"language": "de", "region": "AT", "url": link, "clientVersion": "3.0.2"}
    try:
        # Kurzer Timeout, um Hänger zu vermeiden
        res = session.post(url, json=_data, timeout=8).json()
        return res[0]["url"]
    except:
        return None

def filterout(name):
    return name.split(".")[0].strip()

def get_germany_channels():
    channels = {}
    
    def _fetch(group, cursor=0, germany_filter=False):
        _data = {
            "language": "de", "region": "AT", "catalogId": "vto-iptv",
            "filter": {"group": group}, "cursor": cursor, "clientVersion": "3.0.2"
        }
        try:
            r = session.post("https://vavoo.to/vto-cluster/mediahubmx-catalog.json", json=_data, timeout=15).json()
            items = r.get("items", [])
            for item in items:
                if germany_filter:
                    if any(ele in item["name"] for ele in ["DE :", " |D"]):
                        name = filterout(item["name"])
                        if name not in channels: channels[name] = item["url"]
                else:
                    name = filterout(item["name"])
                    if name not in channels: channels[name] = item["url"]
            
            next_cursor = r.get("nextCursor")
            if next_cursor:
                _fetch(group, next_cursor, germany_filter)
        except:
            pass

    # Deine Logik: Balkans (gefiltert) + Germany
    _fetch("Balkans", germany_filter=True)
    _fetch("Germany", germany_filter=False)
    return channels

def main():
    print(f"Starte vollständigen Export...")
    results = get_germany_channels()
    if not results:
        print("Keine Kanäle gefunden.")
        return

    m3u_lines = ["#EXTM3U"]
    
    # Jetzt alle Kanäle verarbeiten
    total = len(results)
    for index, (name, raw_url) in enumerate(results.items(), 1):
        print(f"[{index}/{total}] Resolving: {name}")
        
        stream_url = resolve_link(raw_url)
        if stream_url:
            m3u_lines.append(f'#EXTINF:-1 group-title="Germany",{name}')
            m3u_lines.append(stream_url)
        
        # WICHTIG: Kurze Pause, damit GitHub-IPs nicht gesperrt werden
        time.sleep(0.05)

    with open(M3U_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(m3u_lines))
    
    print(f"Fertig! {len(m3u_lines)//2} Streams in {M3U_FILE} gespeichert.")

if __name__ == "__main__":
    main()
