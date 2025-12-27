# 🏠 Smart Home AI Center

AI-powered maintenance system for Home Assistant with a clean Apple-inspired design.

![Version](https://img.shields.io/badge/version-0.3.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)

## ✨ Features

- **Dashboard** - Overview of all entities, problems, and system status
- **Bug-Hunter** - Find and fix unavailable entities with AI analysis (Gemini)
- **Analyst** - Get AI-powered optimization suggestions for your smart home
- **Architect** - Generate automations from natural language descriptions (Claude)
- **Settings UI** - Configure everything from the web interface
- **Auto-Updates** - Pull updates from GitHub directly in the app

## 🚀 Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/laurenciusMD/smarthome-ai-center.git
cd smarthome-ai-center
```

### 2. Start the containers

```bash
docker compose up -d --build
```

### 3. Open the app

Navigate to `http://YOUR_SERVER_IP:8501`

### 4. Configure in the UI

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
