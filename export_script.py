# -*- coding: utf-8 -*-
import requests
import json
import time
import os

# Neue Session mit stärkerer Tarnung
session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    'Accept': 'application/json',
    'X-Requested-With': 'com.mediahubmx.browser'
})

def resolve_link(link):
    url = "https://vavoo.to/vto-cluster/mediahubmx-resolve.json"
    _data = {"language": "de", "region": "AT", "url": link, "clientVersion": "3.0.2"}
    try:
        # Längerer Timeout für GitHub
        res = session.post(url, json=_data, timeout=15).json()
        return res[0]["url"]
    except:
        return None

def filterout(name):
    return name.split(".")[0].strip()

def get_germany_channels():
    channels = {}
    # Versuche verschiedene Cluster-URLs, falls eine blockiert ist
    base_url = "https://vavoo.to/vto-cluster/mediahubmx-catalog.json"
    
    def _fetch(group, cursor=0, germany_filter=False):
        _data = {
            "language": "de", "region": "AT", "catalogId": "vto-iptv",
            "filter": {"group": group}, "cursor": cursor, "clientVersion": "3.0.2"
        }
        try:
            r = session.post(base_url, json=_data, timeout=20).json()
            items = r.get("items", [])
            for item in items:
                if germany_filter:
                    if any(ele in item["name"] for ele in ["DE :", " |D"]):
                        name = filterout(item["name"])
                        if name not in channels: channels[name] = item["url"]
                else:
                    name = filterout(item["name"])
                    if name not in channels: channels[name] = item["url"]
            
            if r.get("nextCursor"):
                _fetch(group, r.get("nextCursor"), germany_filter)
        except Exception as e:
            print(f"Fehler bei {group}: {e}")

    _fetch("Balkans", germany_filter=True)
    _fetch("Germany", germany_filter=False)
    return channels

def main():
    print("Starte Export...")
    results = get_germany_channels()
    
    if not results:
        print("Immer noch keine Kanäle gefunden. Vavoo blockiert GitHub IP.")
        # Wir erstellen eine Dummy-Datei, damit der Workflow nicht komplett leer bleibt
        with open("vavoo_germany.m3u", "w") as f: f.write("#EXTM3U\n# ERROR: IP BLOCKED BY VAVOO")
        return

    m3u_lines = ["#EXTM3U"]
    for name, raw_url in results.items():
        stream_url = resolve_link(raw_url)
        if stream_url:
            m3u_lines.append(f'#EXTINF:-1 group-title="Germany",{name}')
            m3u_lines.append(stream_url)
        time.sleep(0.1)

    with open("vavoo_germany.m3u", "w", encoding="utf-8") as f:
        f.write("\n".join(m3u_lines))
    
    with open("vavoo_full_export.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()
