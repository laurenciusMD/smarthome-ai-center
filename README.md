# 🏠 Smart Home AI Center

AI-powered maintenance system for Home Assistant with a clean Apple-inspired design.

![Version](https://img.shields.io/badge/version-0.5.2-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Docker Pulls](https://img.shields.io/docker/pulls/laurencius/smarthome-ai-center)
![Docker Image Size](https://img.shields.io/docker/image-size/laurencius/smarthome-ai-center)

## ✨ Features

- **Dashboard** - Overview of all entities, problems, and system status
- **Bug-Hunter** - Find and fix unavailable entities with AI analysis (Gemini)
- **Analyst** - Get AI-powered optimization suggestions for your smart home
- **Architect** - Generate automations from natural language descriptions (Claude)
- **Settings UI** - Configure everything from the web interface
- **Auto-Updates** - Pull updates from GitHub directly in the app

## 🚀 Quick Start

### Option 1: Using Docker Hub (Recommended)

```bash
# Create docker-compose.yml
wget https://raw.githubusercontent.com/laurenciusMD/smarthome-ai-center/main/docker-compose.yml

# Or create manually with:
version: '3.8'
services:
  app:
    image: laurencius/smarthome-ai-center:latest
    container_name: smarthome-ai-center
    restart: unless-stopped
    ports:
      - "8501:8501"
    environment:
      - TZ=Europe/Berlin
    volumes:
      - ./config:/config
      - ./data/exports:/app/exports

# Start the container
docker compose up -d
```

### Option 2: Build from Source

```bash
# Clone the repository
git clone https://github.com/laurenciusMD/smarthome-ai-center.git
cd smarthome-ai-center

# Start the containers
docker compose up -d --build
```

### Option 3: CasaOS Installation

**Method 1: Using Docker Run Command (Recommended)**

In CasaOS, go to "Custom Install" and use:

```bash
docker run -d \
  --name smarthome-ai-center \
  --restart unless-stopped \
  -p 8501:8501 \
  -v ~/smarthome-config:/config \
  -v ~/smarthome-exports:/app/exports \
  -e TZ=Europe/Berlin \
  laurencius/smarthome-ai-center:latest
```

**Method 2: Using Docker Compose in CasaOS**

If importing the docker-compose.yml file, ensure port mapping is correct:
- Check that port 8501 is properly exposed
- Verify with: `docker ps | grep smarthome` should show `0.0.0.0:8501->8501/tcp`

**Troubleshooting:**
If you can't access the app after installation, the port might not be mapped correctly. Fix with:

```bash
# Stop and remove the container
docker stop <container-name>
docker rm <container-name>

# Recreate with proper port mapping (see Method 1 above)
```

---

## Next Steps

### 1. Open the app

Navigate to `http://YOUR_SERVER_IP:8501`

### 2. Configure in the UI

Go to **⚙️ Einstellungen** and enter:
- Your Home Assistant URL and Token
- Google AI Key (free at aistudio.google.com)
- Anthropic API Key (optional, for better automation generation)

## 🔧 Configuration

All configuration is done through the web UI. Settings are stored locally in `./config/settings.json`.

**No API keys or tokens are stored in Git!**

### Environment Variables (Optional)

You can also use environment variables via `.env` file:

```env
# Optional - UI settings take priority
HA_URL=http://192.168.1.100:8123
HA_TOKEN=your_token
GOOGLE_AI_KEY=AIza...
ANTHROPIC_API_KEY=sk-ant-...
```

## 📦 Tech Stack

- **Frontend**: Streamlit with custom Apple-style CSS
- **AI**: Google Gemini Flash + Anthropic Claude
- **Database**: InfluxDB v2
- **Container**: Docker Compose

## 🐳 Docker Hub

Pre-built images are available on Docker Hub:

```bash
docker pull laurencius/smarthome-ai-center:latest
```

**Available Tags:**
- `latest` - Latest stable version from main branch
- `v0.5.2` - Specific version tags
- `0.5` - Minor version tags
- `0` - Major version tags

**Supported Platforms:**
- `linux/amd64` - x86_64 systems (Intel/AMD)
- `linux/arm64` - ARM64 systems (Raspberry Pi 4/5, Apple Silicon)

## 🔄 Updates

Updates can be pulled directly from the Settings page in the app, or manually:

```bash
cd /path/to/smarthome-ai-center
git pull
docker compose up -d --build
```

## 📁 Directory Structure

```
smarthome-ai-center/
├── app/
│   ├── main.py          # Main Streamlit application
│   ├── Dockerfile       # Container definition
│   └── requirements.txt # Python dependencies
├── config/              # Local settings (gitignored)
│   └── settings.json    # API keys, URLs, etc.
├── data/                # Exports and generated files
├── docker-compose.yml   # Service definitions
└── README.md
```

## 🤖 AI Models Used

| Feature | Model | Cost |
|---------|-------|------|
| Bug-Hunter | Gemini Flash | ~0.001€/analysis |
| Analyst | Gemini or Claude | ~0.001€ or ~0.02€ |
| Architect | Claude | ~0.02€/generation |

## 📄 License

MIT License - feel free to use and modify!

---

Made with ❤️ for the Home Assistant community
