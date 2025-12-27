# Installation auf CasaOS

## Quick Install (nach GitHub Clone)

```bash
# 1. Repo klonen
cd /DATA/AppData
git clone https://github.com/laurenciusMD/smarthome-ai-center.git
cd smarthome-ai-center

# 2. .env erstellen und anpassen
cp .env.example .env
nano .env

# 3. Container starten
docker-compose up -d --build

# 4. Browser öffnen
# http://<CASAOS-IP>:8501
```

## Updates ziehen

```bash
cd /DATA/AppData/smarthome-ai-center
git pull origin main
docker-compose up -d --build
```
