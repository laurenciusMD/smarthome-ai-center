"""
Smart Home AI Center v0.3.0
===========================
AI-powered maintenance system for Home Assistant
Apple-inspired clean design with built-in settings management
"""

import streamlit as st
import os
import requests
import json
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from anthropic import Anthropic
import google.generativeai as genai

# ============================================
# CONFIG & CONSTANTS
# ============================================
APP_VERSION = "0.3.0"
CONFIG_FILE = Path("/config/settings.json")
CONFIG_DIR = Path("/config")

# ============================================
# PAGE CONFIG
# ============================================
st.set_page_config(
    page_title="AI Center",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# APPLE-STYLE CSS
# ============================================
st.markdown("""
<style>
    /* Import SF Pro-like font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global styles - Light Apple theme */
    .stApp {
        background: linear-gradient(180deg, #f5f5f7 0%, #ffffff 100%);
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Main content area */
    .main .block-container {
        padding: 2rem 3rem;
        max-width: 1400px;
    }
    
    /* Sidebar - Apple style */
    section[data-testid="stSidebar"] {
        background: rgba(255, 255, 255, 0.8);
        backdrop-filter: blur(20px);
        border-right: 1px solid rgba(0, 0, 0, 0.1);
    }
    
    section[data-testid="stSidebar"] .block-container {
        padding-top: 2rem;
    }
    
    /* Typography */
    h1 {
        font-weight: 600 !important;
        font-size: 2.5rem !important;
        color: #1d1d1f !important;
        letter-spacing: -0.02em;
    }
    
    h2, h3 {
        font-weight: 600 !important;
        color: #1d1d1f !important;
        letter-spacing: -0.01em;
    }
    
    p, li, span {
        color: #424245;
        line-height: 1.6;
    }
    
    /* Apple-style cards */
    .apple-card {
        background: white;
        border-radius: 18px;
        padding: 24px;
        box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
        border: 1px solid rgba(0, 0, 0, 0.04);
        margin-bottom: 16px;
        transition: all 0.3s ease;
    }
    
    .apple-card:hover {
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.12);
        transform: translateY(-2px);
    }
    
    /* Metric cards */
    .metric-container {
        background: white;
        border-radius: 16px;
        padding: 20px 24px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
        text-align: center;
        border: 1px solid rgba(0, 0, 0, 0.04);
    }
    
    .metric-value {
        font-size: 42px;
        font-weight: 600;
        color: #1d1d1f;
        line-height: 1.1;
    }
    
    .metric-label {
        font-size: 13px;
        color: #86868b;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-top: 8px;
    }
    
    /* Status indicators */
    .status-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        display: inline-block;
        margin-right: 8px;
    }
    
    .status-online { background: #34c759; }
    .status-offline { background: #ff3b30; }
    .status-warning { background: #ff9500; }
    
    /* Buttons - Apple style */
    .stButton > button {
        background: #007aff !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 12px 24px !important;
        font-weight: 500 !important;
        font-size: 15px !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 2px 8px rgba(0, 122, 255, 0.3) !important;
    }
    
    .stButton > button:hover {
        background: #0056b3 !important;
        transform: scale(1.02);
        box-shadow: 0 4px 12px rgba(0, 122, 255, 0.4) !important;
    }
    
    /* Input fields */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > div {
        border-radius: 10px !important;
        border: 1px solid #d2d2d7 !important;
        padding: 12px 16px !important;
        font-size: 15px !important;
        background: white !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #007aff !important;
        box-shadow: 0 0 0 3px rgba(0, 122, 255, 0.2) !important;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background: white !important;
        border-radius: 12px !important;
        border: 1px solid rgba(0, 0, 0, 0.06) !important;
        font-weight: 500 !important;
    }
    
    /* Success/Error/Warning messages */
    .stSuccess > div {
        background: rgba(52, 199, 89, 0.1) !important;
        border-radius: 12px !important;
        border: 1px solid rgba(52, 199, 89, 0.2) !important;
        color: #248a3d !important;
    }
    
    .stError > div {
        background: rgba(255, 59, 48, 0.1) !important;
        border-radius: 12px !important;
        border: 1px solid rgba(255, 59, 48, 0.2) !important;
        color: #d70015 !important;
    }
    
    .stWarning > div {
        background: rgba(255, 149, 0, 0.1) !important;
        border-radius: 12px !important;
        border: 1px solid rgba(255, 149, 0, 0.2) !important;
        color: #c93400 !important;
    }
    
    .stInfo > div {
        background: rgba(0, 122, 255, 0.1) !important;
        border-radius: 12px !important;
        border: 1px solid rgba(0, 122, 255, 0.2) !important;
        color: #0056b3 !important;
    }
    
    /* Code blocks */
    .stCodeBlock {
        border-radius: 12px !important;
        border: 1px solid rgba(0, 0, 0, 0.06) !important;
    }
    
    /* Divider */
    hr {
        border: none;
        height: 1px;
        background: rgba(0, 0, 0, 0.08);
        margin: 24px 0;
    }
    
    /* Logo styling */
    .app-logo {
        font-size: 24px;
        font-weight: 600;
        color: #1d1d1f;
        margin-bottom: 20px;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    
    /* Version badge */
    .version-badge {
        background: #f5f5f7;
        color: #86868b;
        padding: 3px 8px;
        border-radius: 12px;
        font-size: 11px;
        font-weight: 500;
    }
    
    /* Connection status */
    .connection-status {
        display: flex;
        align-items: center;
        padding: 10px 14px;
        border-radius: 10px;
        margin: 12px 0;
        font-size: 13px;
        font-weight: 500;
    }
    
    .connection-online {
        background: rgba(52, 199, 89, 0.15);
        color: #248a3d;
    }
    
    .connection-offline {
        background: rgba(255, 59, 48, 0.15);
        color: #d70015;
    }
    
    /* Radio buttons as pills */
    .stRadio > div {
        gap: 8px;
    }
    
    .stRadio > div > label {
        background: white;
        border: 1px solid #d2d2d7;
        border-radius: 10px;
        padding: 10px 16px;
        margin: 2px 0;
        cursor: pointer;
        transition: all 0.2s ease;
    }
    
    .stRadio > div > label:hover {
        border-color: #007aff;
        background: rgba(0, 122, 255, 0.05);
    }
    
    .stRadio > div > label[data-checked="true"] {
        background: #007aff;
        border-color: #007aff;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# SETTINGS MANAGEMENT
# ============================================

def load_settings():
    """Load settings from config file."""
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    return {
        "ha_url": "",
        "ha_token": "",
        "anthropic_key": "",
        "google_ai_key": "",
        "github_repo": "laurenciusMD/smarthome-ai-center",
        "theme": "light"
    }

def save_settings(settings):
    """Save settings to config file."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, 'w') as f:
        json.dump(settings, f, indent=2)

def get_setting(key, default=""):
    """Get a setting value."""
    settings = load_settings()
    # First check environment variables (for Docker compatibility)
    env_map = {
        "ha_url": "HA_URL",
        "ha_token": "HA_TOKEN", 
        "anthropic_key": "ANTHROPIC_API_KEY",
        "google_ai_key": "GOOGLE_AI_KEY"
    }
    if key in env_map:
        env_val = os.getenv(env_map[key], "")
        if env_val:
            return env_val
    return settings.get(key, default)

# ============================================
# SESSION STATE
# ============================================
if 'settings' not in st.session_state:
    st.session_state.settings = load_settings()
if 'ha_cache' not in st.session_state:
    st.session_state.ha_cache = None
if 'ha_cache_time' not in st.session_state:
    st.session_state.ha_cache_time = None
if 'error_logs' not in st.session_state:
    st.session_state.error_logs = []
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = None

# ============================================
# API FUNCTIONS
# ============================================

def check_ha_connection():
    """Test Home Assistant connection."""
    url = get_setting("ha_url", "").rstrip("/")
    token = get_setting("ha_token", "")
    if not url or not token:
        return False, "Nicht konfiguriert"
    try:
        resp = requests.get(
            f"{url}/api/",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10
        )
        if resp.status_code == 200:
            return True, "Verbunden"
        return False, f"HTTP {resp.status_code}"
    except:
        return False, "Keine Verbindung"

def get_ha_states():
    """Get all entity states from Home Assistant."""
    url = get_setting("ha_url", "").rstrip("/")
    token = get_setting("ha_token", "")
    try:
        resp = requests.get(
            f"{url}/api/states",
            headers={"Authorization": f"Bearer {token}"},
            timeout=30
        )
        if resp.status_code == 200:
            return resp.json()
        return []
    except:
        return []

def get_ha_errors():
    """Get errors from Home Assistant (unavailable entities)."""
    states = get_ha_states()
    errors = []
    for entity in states:
        state = entity.get('state', '')
        if state == 'unavailable':
            eid = entity.get('entity_id', '')
            name = entity.get('attributes', {}).get('friendly_name', eid)
            errors.append({
                'level': 'error',
                'message': f"Entity nicht verfügbar: {name}",
                'entity_id': eid,
                'details': []
            })
    return errors

def ask_gemini(prompt: str) -> str:
    """Ask Gemini Flash for quick analysis."""
    api_key = get_setting("google_ai_key", "")
    if not api_key:
        return "❌ Google AI Key nicht konfiguriert. Gehe zu Einstellungen."
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"❌ Gemini Fehler: {str(e)}"

def ask_claude(prompt: str) -> str:
    """Ask Claude for complex analysis."""
    api_key = get_setting("anthropic_key", "")
    if not api_key:
        return "❌ Anthropic API Key nicht konfiguriert. Gehe zu Einstellungen."
    try:
        client = Anthropic(api_key=api_key)
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text
    except Exception as e:
        return f"❌ Claude Fehler: {str(e)}"

def git_pull_updates():
    """Pull latest updates from GitHub."""
    try:
        result = subprocess.run(
            ["git", "pull", "origin", "main"],
            cwd="/app",
            capture_output=True,
            text=True,
            timeout=60
        )
        return result.returncode == 0, result.stdout + result.stderr
    except Exception as e:
        return False, str(e)

def get_git_status():
    """Get current git status."""
    try:
        result = subprocess.run(
            ["git", "log", "-1", "--format=%h - %s (%cr)"],
            cwd="/app",
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.stdout.strip() if result.returncode == 0 else "Unbekannt"
    except:
        return "Git nicht verfügbar"

# ============================================
# SIDEBAR
# ============================================
with st.sidebar:
    # Logo
    st.markdown(f"""
        <div class="app-logo">
            🏠 AI Center
            <span class="version-badge">v{APP_VERSION}</span>
        </div>
    """, unsafe_allow_html=True)
    
    # Connection Status
    connected, status_msg = check_ha_connection()
    if connected:
        st.markdown("""
            <div class="connection-status connection-online">
                <span class="status-dot status-online"></span>
                Home Assistant verbunden
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
            <div class="connection-status connection-offline">
                <span class="status-dot status-offline"></span>
                {status_msg}
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Navigation
    page = st.radio(
        "Navigation",
        ["🏠 Dashboard", "🔍 Bug-Hunter", "📈 Analyst", "🏗️ Architect", "⚙️ Einstellungen"],
        label_visibility="collapsed"
    )

# ============================================
# PAGE: DASHBOARD
# ============================================
if page == "🏠 Dashboard":
    st.title("Dashboard")
    st.markdown("Übersicht über dein Smart Home System")
    
    # Refresh button
    col1, col2, col3 = st.columns([1, 1, 4])
    with col1:
        if st.button("🔄 Aktualisieren"):
            st.session_state.ha_cache = None
            st.rerun()
    
    # Get data
    entities = get_ha_states()
    errors = get_ha_errors()
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
            <div class="metric-container">
                <div class="metric-value">{len(entities)}</div>
                <div class="metric-label">Entitäten</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        unavailable = len([e for e in entities if e.get('state') == 'unavailable'])
        st.markdown(f"""
            <div class="metric-container">
                <div class="metric-value" style="color: {'#ff3b30' if unavailable > 0 else '#34c759'}">{unavailable}</div>
                <div class="metric-label">Nicht verfügbar</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        lights_on = len([e for e in entities if e.get('entity_id', '').startswith('light.') and e.get('state') == 'on'])
        st.markdown(f"""
            <div class="metric-container">
                <div class="metric-value" style="color: #ff9500">{lights_on}</div>
                <div class="metric-label">Lichter an</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col4:
        automations = len([e for e in entities if e.get('entity_id', '').startswith('automation.')])
        st.markdown(f"""
            <div class="metric-container">
                <div class="metric-value">{automations}</div>
                <div class="metric-label">Automationen</div>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Two columns
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.markdown("""<div class="apple-card">""", unsafe_allow_html=True)
        st.subheader("📊 Entitäten nach Domain")
        
        if entities:
            domains = {}
            for e in entities:
                domain = e.get('entity_id', 'unknown').split('.')[0]
                domains[domain] = domains.get(domain, 0) + 1
            
            sorted_domains = sorted(domains.items(), key=lambda x: x[1], reverse=True)[:8]
            for domain, count in sorted_domains:
                st.markdown(f"**{domain}** · {count}")
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col_right:
        st.markdown("""<div class="apple-card">""", unsafe_allow_html=True)
        st.subheader("⚠️ Probleme")
        
        if errors:
            for err in errors[:5]:
                st.markdown(f"🔴 {err['message'][:60]}...")
            if len(errors) > 5:
                st.markdown(f"*... und {len(errors) - 5} weitere*")
        else:
            st.success("✅ Keine Probleme erkannt!")
        st.markdown("</div>", unsafe_allow_html=True)

# ============================================
# PAGE: BUG-HUNTER
# ============================================
elif page == "🔍 Bug-Hunter":
    st.title("Bug-Hunter")
    st.markdown("Finde und behebe Probleme in deinem System")
    
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("🔄 Probleme laden"):
            st.session_state.error_logs = get_ha_errors()
            st.rerun()
    
    errors = st.session_state.error_logs
    
    st.markdown(f"**{len(errors)} Probleme gefunden**")
    st.markdown("---")
    
    if not errors:
        st.success("🎉 Keine Probleme gefunden! Dein System läuft einwandfrei.")
    else:
        for i, err in enumerate(errors[:20]):  # Limit to 20
            with st.expander(f"🔴 {err['message'][:70]}...", expanded=False):
                st.markdown(f"**Entity ID:** `{err.get('entity_id', 'N/A')}`")
                
                if st.button(f"🤖 Mit Gemini analysieren", key=f"analyze_{i}"):
                    with st.spinner("Analysiere..."):
                        prompt = f"""Du bist ein Home Assistant Experte. Analysiere dieses Problem:

PROBLEM: {err['message']}
ENTITY: {err.get('entity_id', 'N/A')}

Antworte auf Deutsch, kurz und präzise:
1. Mögliche Ursache
2. Lösungsvorschlag
"""
                        solution = ask_gemini(prompt)
                    st.markdown("### Analyse")
                    st.markdown(solution)

# ============================================
# PAGE: ANALYST
# ============================================
elif page == "📈 Analyst":
    st.title("System Analyst")
    st.markdown("Analysiere dein Smart Home auf Optimierungspotential")
    
    # Model selection
    col1, col2 = st.columns([1, 2])
    with col1:
        model = st.selectbox(
            "AI Modell",
            ["Gemini Flash (günstig)", "Claude (präziser)"]
        )
    
    with col2:
        if "Gemini" in model:
            st.info("💰 Gemini: ~0.001€ pro Analyse")
        else:
            st.warning("💎 Claude: ~0.02€ pro Analyse")
    
    if st.button("🚀 Analyse starten", type="primary"):
        with st.spinner("Analysiere System..."):
            states = get_ha_states()
            
            # Build summary
            summary = {
                'total': len(states),
                'unavailable': len([e for e in states if e.get('state') == 'unavailable']),
                'lights_on': len([e for e in states if e.get('entity_id', '').startswith('light.') and e.get('state') == 'on']),
                'domains': {}
            }
            
            for e in states:
                domain = e.get('entity_id', '').split('.')[0]
                summary['domains'][domain] = summary['domains'].get(domain, 0) + 1
            
            prompt = f"""Analysiere dieses Smart Home System und gib Optimierungsvorschläge:

ÜBERSICHT:
- Gesamt Entitäten: {summary['total']}
- Nicht verfügbar: {summary['unavailable']}
- Lichter an: {summary['lights_on']}

DOMAINS:
{json.dumps(summary['domains'], indent=2)}

Gib 5-10 konkrete Verbesserungsvorschläge auf Deutsch.
Fokus auf: Energieeffizienz, Automatisierung, Problemlösung.
"""
            
            if "Gemini" in model:
                result = ask_gemini(prompt)
            else:
                result = ask_claude(prompt)
            
            st.session_state.analysis_results = result
    
    if st.session_state.analysis_results:
        st.markdown("---")
        st.subheader("📋 Ergebnisse")
        st.markdown(st.session_state.analysis_results)

# ============================================
# PAGE: ARCHITECT
# ============================================
elif page == "🏗️ Architect":
    st.title("Automation Architect")
    st.markdown("Erstelle neue Automationen mit AI-Unterstützung")
    
    # Load entities for context
    entities = get_ha_states()
    entity_ids = [e.get('entity_id', '') for e in entities][:100]  # First 100
    
    st.markdown("""<div class="apple-card">""", unsafe_allow_html=True)
    
    description = st.text_area(
        "Beschreibe deine gewünschte Automation",
        placeholder="z.B.: Schalte das Licht im Flur ein wenn Bewegung erkannt wird, aber nur nachts zwischen 22 und 6 Uhr",
        height=120
    )
    
    output_format = st.selectbox(
        "Ausgabeformat",
        ["Home Assistant YAML", "Node-RED JSON", "Python Script"]
    )
    
    if st.button("🪄 Automation erstellen", type="primary"):
        if description:
            with st.spinner("Claude erstellt deine Automation..."):
                prompt = f"""Erstelle eine Home Assistant Automation basierend auf dieser Beschreibung:

BESCHREIBUNG: {description}

VERFÜGBARE ENTITÄTEN (Auswahl):
{chr(10).join(entity_ids[:50])}

AUSGABEFORMAT: {output_format}

Antworte auf Deutsch mit:
1. Kurze Erklärung was die Automation macht
2. Den vollständigen Code
3. Installationshinweise
"""
                result = ask_claude(prompt)
            
            st.markdown("### Deine Automation")
            st.markdown(result)
        else:
            st.warning("Bitte beschreibe zuerst deine gewünschte Automation.")
    
    st.markdown("</div>", unsafe_allow_html=True)

# ============================================
# PAGE: SETTINGS
# ============================================
elif page == "⚙️ Einstellungen":
    st.title("Einstellungen")
    st.markdown("Konfiguriere deine Verbindungen und API Keys")
    
    settings = st.session_state.settings
    
    # Home Assistant Section
    st.markdown("""<div class="apple-card">""", unsafe_allow_html=True)
    st.subheader("🏠 Home Assistant")
    
    col1, col2 = st.columns(2)
    with col1:
        ha_url = st.text_input(
            "Home Assistant URL",
            value=settings.get("ha_url", ""),
            placeholder="http://192.168.1.100:8123"
        )
    with col2:
        ha_token = st.text_input(
            "Long-Lived Access Token",
            value=settings.get("ha_token", ""),
            type="password",
            help="Erstelle unter: Profil → Sicherheit → Langlebige Zugangstoken"
        )
    st.markdown("</div>", unsafe_allow_html=True)
    
    # AI Keys Section
    st.markdown("""<div class="apple-card">""", unsafe_allow_html=True)
    st.subheader("🤖 AI API Keys")
    
    col1, col2 = st.columns(2)
    with col1:
        google_key = st.text_input(
            "Google AI Key (Gemini)",
            value=settings.get("google_ai_key", ""),
            type="password",
            help="Kostenlos unter: aistudio.google.com/apikey"
        )
    with col2:
        anthropic_key = st.text_input(
            "Anthropic API Key (Claude)",
            value=settings.get("anthropic_key", ""),
            type="password",
            help="Unter: console.anthropic.com"
        )
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Save button
    if st.button("💾 Einstellungen speichern", type="primary"):
        new_settings = {
            "ha_url": ha_url,
            "ha_token": ha_token,
            "google_ai_key": google_key,
            "anthropic_key": anthropic_key,
            "github_repo": settings.get("github_repo", ""),
            "theme": settings.get("theme", "light")
        }
        save_settings(new_settings)
        st.session_state.settings = new_settings
        st.success("✅ Einstellungen gespeichert!")
        st.rerun()
    
    st.markdown("---")
    
    # Updates Section
    st.markdown("""<div class="apple-card">""", unsafe_allow_html=True)
    st.subheader("🔄 Updates")
    
    git_status = get_git_status()
    st.markdown(f"**Aktueller Stand:** {git_status}")
    
    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("📥 Updates laden"):
            with st.spinner("Lade Updates von GitHub..."):
                success, output = git_pull_updates()
            if success:
                st.success("✅ Updates geladen! Starte die App neu um Änderungen zu aktivieren.")
                st.code(output)
            else:
                st.error(f"❌ Update fehlgeschlagen: {output}")
    
    with col2:
        st.markdown("*Updates vom GitHub Repository laden*")
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Connection Test
    st.markdown("---")
    st.markdown("""<div class="apple-card">""", unsafe_allow_html=True)
    st.subheader("🧪 Verbindungstest")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Test Home Assistant"):
            connected, msg = check_ha_connection()
            if connected:
                st.success(f"✅ {msg}")
            else:
                st.error(f"❌ {msg}")
    
    with col2:
        if st.button("Test Gemini"):
            result = ask_gemini("Sag nur 'OK' wenn du funktionierst.")
            if "OK" in result or "ok" in result.lower():
                st.success("✅ Gemini verbunden")
            else:
                st.error(f"❌ {result[:100]}")
    
    with col3:
        if st.button("Test Claude"):
            result = ask_claude("Sag nur 'OK' wenn du funktionierst.")
            if "OK" in result or "ok" in result.lower():
                st.success("✅ Claude verbunden")
            else:
                st.error(f"❌ {result[:100]}")
    
    st.markdown("</div>", unsafe_allow_html=True)
