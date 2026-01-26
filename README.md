### 🛠 Automatisiertes Update Script (GitHub Action)

Dieses Script wird in der Datei `.github/workflows/update.yml` verwendet, um die Daten stabil von OHA zu beziehen:

```bash
# 1. Verzeichnis für Cache sicherstellen
mkdir -p data

# 2. Download mit Retry-Logik (verhindert 55kb-Bruchstücke)
curl --retry 5 \
     --retry-delay 5 \
     --location \
     --user-agent "VAVOO/2.6" \
     "[http://oha.to/mediaurl-catalog.json](http://oha.to/mediaurl-catalog.json)" \
     -o data/cache_oha.json

# 3. Validierung (optional: bricht ab, wenn Datei zu klein)
[ $(stat -c%s "data/cache_oha.json") -gt 1000000 ] || exit 1
