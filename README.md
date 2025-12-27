# 🏠 Smart Home AI Center

Ein Docker-basiertes Wartungs- und Entwicklungssystem für Home Assistant mit AI-Unterstützung.

## Features

- **📊 Dashboard** - Übersicht über den System-Status und AI-Tipps
- **🔍 Bug-Hunter** - Automatische Fehleranalyse mit Claude AI
- **📈 48h Analyst** - Sensor-Daten Analyse und Optimierungsvorschläge
- **🏗️ Architect** - Custom Automations Generator

## Voraussetzungen

- Docker & Docker Compose (CasaOS oder ähnliches)
- Home Assistant mit aktivierter API
- Anthropic API Key (für Claude)

## Quick Start

### 1. Repository klonen oder Dateien kopieren

```bash
cd /DATA/AppData  # oder dein CasaOS App-Verzeichnis
git clone <repository> smarthome-ai-center
cd smarthome-ai-center
```

### 2. Environment konfigurieren

```bash
cp .env.example .env
nano .env  # Alle Werte ausfüllen!
```

**Wichtig:** Fülle mindestens diese Werte aus:
- `HA_URL` - Deine Home Assistant URL
- `HA_TOKEN` - Long-Lived Access Token aus HA
- `ANTHROPIC_API_KEY` - Dein Claude API Key
- `INFLUX_ADMIN_PASSWORD` - Ein sicheres Passwort
- `INFLUX_TOKEN` - Generiere mit: `openssl rand -hex 32`

### 3. Container starten

```bash
docker-compose up -d
```

### 4. Web-Interface öffnen

Öffne im Browser: `http://<deine-ip>:8501`

## Struktur

```
smarthome-ai-center/
├── docker-compose.yml    # Container-Orchestrierung
├── .env.example          # Template für Konfiguration
├── .env                  # Deine lokale Konfiguration (nicht committen!)
├── app/
│   ├── Dockerfile        # Python/Streamlit Container
│   ├── requirements.txt  # Python Dependencies
│   └── main.py           # Hauptanwendung (wird erweitert)
└── data/
    └── exports/          # Generierte Dateien (Downloads)
```

## Ports

| Service    | Port | Beschreibung |
|------------|------|--------------|
| App (Streamlit) | 8501 | Web-Interface |
| InfluxDB   | 8086 | Datenbank (optional extern) |

## Troubleshooting

### Container starten nicht
```bash
docker-compose logs -f
```

### InfluxDB Verbindungsprobleme
Prüfe ob der Container läuft:
```bash
docker ps | grep influxdb
```

### Home Assistant nicht erreichbar
- Prüfe `HA_URL` in `.env`
- Prüfe ob Token gültig ist
- Prüfe Netzwerk zwischen Docker und HA

## Entwicklung

Für lokale Entwicklung ohne Docker:

```bash
cd app
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
streamlit run main.py
```

## Lizenz

MIT

---

*Powered by Claude AI & Home Assistant*
