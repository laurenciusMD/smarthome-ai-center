"""
Smart Home AI Center v0.6.0
===========================
Hypermodern UI Design with Glassmorphism
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
from typing import List, Dict, Optional

# ============================================
# CONFIG & CONSTANTS
# ============================================
APP_VERSION = "0.6.0"
CONFIG_FILE = Path("/config/settings.json")
CONFIG_DIR = Path("/config")
HISTORY_FILE = Path("/config/heating_history.json")

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
# HYPERMODERN GLASSMORPHISM CSS
# ============================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    @import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css');

    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Main App Background - Modern Gradient */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 25%, #f093fb 50%, #667eea 100%);
        background-size: 400% 400%;
        animation: gradientShift 15s ease infinite;
    }

    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    .main .block-container {
        padding: 2rem;
        max-width: 1400px;
    }

    /* Glassmorphism Sidebar */
    section[data-testid="stSidebar"] {
        background: rgba(20, 29, 50, 0.85);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }

    section[data-testid="stSidebar"] * {
        color: #cbd5e1 !important;
    }

    section[data-testid="stSidebar"] .stRadio > div > label[data-checked="true"] {
        color: #60a5fa !important;
        background: linear-gradient(135deg, rgba(96, 165, 250, 0.2), rgba(59, 130, 246, 0.3)) !important;
        border-radius: 12px;
        border-left: 3px solid #60a5fa;
        box-shadow: 0 4px 15px rgba(96, 165, 250, 0.2);
        transform: translateX(4px);
        transition: all 0.3s ease;
    }
    
    /* Glassmorphism Metric Cards */
    .metric-card {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border-radius: 20px;
        padding: 28px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.3);
        display: flex;
        justify-content: space-between;
        align-items: center;
        height: 150px;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }

    .metric-card::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
        transition: all 0.6s ease;
        opacity: 0;
    }

    .metric-card:hover::before {
        opacity: 1;
        transform: translate(-25%, -25%);
    }

    .metric-card:hover {
        transform: translateY(-8px);
        box-shadow: 0 12px 48px rgba(0, 0, 0, 0.15);
    }

    .metric-info h2 {
        font-size: 42px;
        font-weight: 800;
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin: 0;
        line-height: 1;
    }

    .metric-info p {
        font-size: 14px;
        color: #64748b;
        margin: 10px 0 0 0;
        font-weight: 500;
    }

    .metric-info .change {
        font-size: 13px;
        font-weight: 700;
        margin-top: 8px;
        padding: 4px 12px;
        border-radius: 20px;
        display: inline-block;
    }

    .change.up {
        background: rgba(34, 197, 94, 0.15);
        color: #16a34a;
    }
    .change.down {
        background: rgba(239, 68, 68, 0.15);
        color: #dc2626;
    }

    .metric-icon {
        width: 64px;
        height: 64px;
        border-radius: 18px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 28px;
        color: white;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
    }

    .icon-yellow { background: linear-gradient(135deg, #fbbf24, #f59e0b); }
    .icon-cyan { background: linear-gradient(135deg, #06b6d4, #0891b2); }
    .icon-green { background: linear-gradient(135deg, #22c55e, #16a34a); }
    .icon-purple { background: linear-gradient(135deg, #a855f7, #9333ea); }
    .icon-red { background: linear-gradient(135deg, #ef4444, #dc2626); }
    .icon-blue { background: linear-gradient(135deg, #3b82f6, #2563eb); }
    
    /* Glassmorphism Content Cards */
    .content-card {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border-radius: 20px;
        padding: 28px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08);
        border: 1px solid rgba(255, 255, 255, 0.3);
        margin-bottom: 20px;
        transition: all 0.3s ease;
    }

    .content-card:hover {
        box-shadow: 0 12px 48px rgba(0, 0, 0, 0.12);
        transform: translateY(-2px);
    }

    .content-card h3 {
        font-size: 18px;
        font-weight: 700;
        color: #1e293b;
        margin: 0 0 20px 0;
        letter-spacing: -0.3px;
    }

    /* Modern Status Badge */
    .status-badge {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 10px 20px;
        border-radius: 30px;
        font-size: 13px;
        font-weight: 700;
        letter-spacing: 0.3px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        transition: all 0.3s ease;
    }

    .status-badge:hover {
        transform: scale(1.05);
    }

    .status-online {
        background: linear-gradient(135deg, #22c55e, #16a34a);
        color: white;
        box-shadow: 0 4px 20px rgba(34, 197, 94, 0.4);
    }

    .status-offline {
        background: linear-gradient(135deg, #ef4444, #dc2626);
        color: white;
        box-shadow: 0 4px 20px rgba(239, 68, 68, 0.4);
    }
    
    /* Modern Logo */
    .logo {
        color: white !important;
        font-size: 24px;
        font-weight: 800;
        padding: 20px 0;
        display: flex;
        align-items: center;
        gap: 12px;
        letter-spacing: -0.5px;
    }

    /* Modern List Items */
    .list-item {
        display: flex;
        align-items: center;
        padding: 16px;
        border-radius: 12px;
        margin-bottom: 8px;
        background: rgba(255, 255, 255, 0.5);
        border: 1px solid rgba(255, 255, 255, 0.2);
        transition: all 0.3s ease;
    }

    .list-item:hover {
        background: rgba(255, 255, 255, 0.8);
        transform: translateX(4px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
    }

    .list-item:last-child {
        margin-bottom: 0;
    }

    .list-icon {
        width: 48px;
        height: 48px;
        border-radius: 14px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-right: 16px;
        font-size: 20px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
    }

    .list-content {
        flex: 1;
    }

    .list-title {
        font-size: 15px;
        font-weight: 600;
        color: #1e293b;
        margin: 0 0 4px 0;
    }

    .list-subtitle {
        font-size: 13px;
        color: #64748b;
        margin: 0;
        font-weight: 500;
    }

    /* Dismissible Error Card */
    .error-card {
        background: rgba(254, 242, 242, 0.95);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(239, 68, 68, 0.2);
        border-radius: 16px;
        padding: 16px 20px;
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        gap: 12px;
        transition: all 0.3s ease;
        position: relative;
    }

    .error-card:hover {
        box-shadow: 0 4px 16px rgba(239, 68, 68, 0.15);
    }

    .error-icon {
        width: 40px;
        height: 40px;
        border-radius: 12px;
        background: linear-gradient(135deg, #ef4444, #dc2626);
        color: white;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 18px;
        flex-shrink: 0;
    }

    .error-content {
        flex: 1;
        color: #991b1b;
    }

    .error-title {
        font-size: 14px;
        font-weight: 600;
        margin: 0 0 4px 0;
        color: #991b1b;
    }

    .error-detail {
        font-size: 12px;
        color: #b91c1c;
        margin: 0;
    }

    .dismiss-btn {
        width: 28px;
        height: 28px;
        border-radius: 8px;
        background: rgba(239, 68, 68, 0.1);
        color: #dc2626;
        border: none;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 14px;
        transition: all 0.2s ease;
        flex-shrink: 0;
    }

    .dismiss-btn:hover {
        background: rgba(239, 68, 68, 0.2);
        transform: scale(1.1);
    }
    
    /* Modern Gradient Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #3b82f6, #2563eb) !important;
        color: white !important;
        border: none !important;
        border-radius: 14px !important;
        padding: 14px 28px !important;
        font-weight: 700 !important;
        font-size: 14px !important;
        box-shadow: 0 8px 24px rgba(59, 130, 246, 0.35) !important;
        transition: all 0.3s ease !important;
        letter-spacing: 0.3px !important;
    }

    .stButton > button:hover {
        transform: translateY(-3px) !important;
        box-shadow: 0 12px 32px rgba(59, 130, 246, 0.45) !important;
        background: linear-gradient(135deg, #2563eb, #1d4ed8) !important;
    }

    .stButton > button:active {
        transform: translateY(-1px) !important;
    }
    
    /* Modern Input Fields */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        border-radius: 14px !important;
        border: 2px solid rgba(255, 255, 255, 0.4) !important;
        padding: 14px 18px !important;
        font-size: 14px !important;
        background: rgba(255, 255, 255, 0.95) !important;
        color: #1e293b !important;
        font-weight: 500 !important;
        transition: all 0.3s ease !important;
    }

    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #3b82f6 !important;
        box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.15) !important;
        background: white !important;
    }

    .stTextInput > label,
    .stTextArea > label,
    .stSelectbox > label {
        color: #1e293b !important;
        font-weight: 700 !important;
        font-size: 14px !important;
        margin-bottom: 8px !important;
    }
    
    /* Selectbox */
    .stSelectbox > div > div {
        border-radius: 10px !important;
        border: 2px solid #e8ecf0 !important;
        background: white !important;
    }
    
    .stSelectbox > div > div > div {
        color: #1a2744 !important;
    }
    
    .stSelectbox [data-baseweb="select"] {
        color: #1a2744 !important;
    }
    
    .stSelectbox [data-baseweb="select"] > div {
        color: #1a2744 !important;
        background: white !important;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background: white !important;
        border-radius: 12px !important;
        font-weight: 500 !important;
        color: #1a2744 !important;
    }
    
    /* Markdown Text - HIGH CONTRAST */
    .stMarkdown, .stMarkdown p, .stMarkdown li, .stMarkdown span, .stMarkdown div {
        color: #0f172a !important;
        font-weight: 500 !important;
    }

    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        color: #1e293b !important;
        font-weight: 800 !important;
    }

    .stMarkdown code {
        background: rgba(30, 41, 59, 0.08) !important;
        color: #0f172a !important;
        padding: 3px 8px !important;
        border-radius: 6px !important;
        font-weight: 600 !important;
        font-size: 13px !important;
    }

    /* Code Blocks - HIGH CONTRAST */
    .stMarkdown pre {
        background: #1e293b !important;
        border-radius: 16px !important;
        padding: 20px !important;
        border: 1px solid rgba(148, 163, 184, 0.2) !important;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1) !important;
    }

    .stMarkdown pre code {
        background: transparent !important;
        color: #e2e8f0 !important;
        font-size: 14px !important;
        font-weight: 500 !important;
        line-height: 1.6 !important;
    }

    /* st.code blocks - HIGH CONTRAST */
    .stCodeBlock,
    [data-testid="stCodeBlock"] {
        background: #1e293b !important;
        border-radius: 16px !important;
        border: 1px solid rgba(148, 163, 184, 0.2) !important;
    }

    .stCodeBlock code,
    [data-testid="stCodeBlock"] code,
    .stCodeBlock pre,
    [data-testid="stCodeBlock"] pre {
        background: #1e293b !important;
        color: #e2e8f0 !important;
        font-weight: 500 !important;
    }

    /* All code elements */
    pre, code {
        color: #e2e8f0 !important;
    }

    pre {
        background: #1e293b !important;
        padding: 20px !important;
        border-radius: 16px !important;
        overflow-x: auto !important;
        border: 1px solid rgba(148, 163, 184, 0.2) !important;
    }

    /* Inline code */
    p code, li code, span code {
        background: rgba(30, 41, 59, 0.08) !important;
        color: #0f172a !important;
        padding: 3px 8px !important;
        border-radius: 6px !important;
        font-weight: 600 !important;
    }
    
    /* Modern Alerts with HIGH CONTRAST */
    .stSuccess > div {
        background: rgba(34, 197, 94, 0.15) !important;
        color: #15803d !important;
        border-radius: 14px !important;
        border: 1px solid rgba(34, 197, 94, 0.3) !important;
        padding: 16px 20px !important;
        font-weight: 600 !important;
        box-shadow: 0 4px 12px rgba(34, 197, 94, 0.1) !important;
    }

    .stSuccess > div p {
        color: #15803d !important;
        font-weight: 600 !important;
    }

    .stError > div {
        background: rgba(239, 68, 68, 0.15) !important;
        color: #991b1b !important;
        border-radius: 14px !important;
        border: 1px solid rgba(239, 68, 68, 0.3) !important;
        padding: 16px 20px !important;
        font-weight: 600 !important;
        box-shadow: 0 4px 12px rgba(239, 68, 68, 0.1) !important;
    }

    .stError > div p {
        color: #991b1b !important;
        font-weight: 600 !important;
    }

    .stWarning > div {
        background: rgba(245, 158, 11, 0.15) !important;
        color: #92400e !important;
        border-radius: 14px !important;
        border: 1px solid rgba(245, 158, 11, 0.3) !important;
        padding: 16px 20px !important;
        font-weight: 600 !important;
        box-shadow: 0 4px 12px rgba(245, 158, 11, 0.1) !important;
    }

    .stWarning > div p, .stWarning > div span {
        color: #92400e !important;
        font-weight: 600 !important;
    }

    .stInfo > div {
        background: rgba(59, 130, 246, 0.15) !important;
        color: #1e40af !important;
        border-radius: 14px !important;
        border: 1px solid rgba(59, 130, 246, 0.3) !important;
        padding: 16px 20px !important;
        font-weight: 600 !important;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.1) !important;
    }

    .stInfo > div p {
        color: #1e40af !important;
        font-weight: 600 !important;
    }
    
    /* Modern Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
        background: transparent;
    }

    .stTabs [data-baseweb="tab"] {
        background: rgba(255, 255, 255, 0.7) !important;
        border-radius: 14px !important;
        color: #1e293b !important;
        padding: 12px 24px !important;
        border: 2px solid rgba(255, 255, 255, 0.3) !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
    }

    .stTabs [data-baseweb="tab"]:hover {
        background: rgba(255, 255, 255, 0.9) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1) !important;
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #3b82f6, #2563eb) !important;
        color: white !important;
        border-color: transparent !important;
        box-shadow: 0 6px 20px rgba(59, 130, 246, 0.4) !important;
        transform: translateY(-2px) !important;
    }

    .stTabs [data-baseweb="tab-panel"] {
        padding-top: 24px;
    }

    /* Tab content text - HIGH CONTRAST */
    .stTabs [data-baseweb="tab-panel"] p,
    .stTabs [data-baseweb="tab-panel"] span,
    .stTabs [data-baseweb="tab-panel"] div,
    .stTabs [data-baseweb="tab-panel"] label {
        color: #0f172a !important;
        font-weight: 500 !important;
    }
    
    /* Divider */
    hr {
        border: none;
        height: 1px;
        background: #e8ecf0;
        margin: 20px 0;
    }
    
    /* Radio as Nav */
    .stRadio > div {
        flex-direction: column;
        gap: 4px;
    }
    
    .stRadio > div > label {
        padding: 12px 16px !important;
        border-radius: 8px !important;
        margin: 0 !important;
        transition: all 0.2s ease;
    }
    
    .stRadio > div > label:hover {
        background: rgba(255, 255, 255, 0.05);
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
        "influx_url": "",
        "influx_token": "",
        "influx_org": "",
        "github_repo": "https://github.com/laurenciusMD/smarthome-ai-center.git",
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
if 'error_logs' not in st.session_state:
    st.session_state.error_logs = []
if 'dismissed_errors' not in st.session_state:
    st.session_state.dismissed_errors = set()
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = None
if 'heating_history' not in st.session_state:
    st.session_state.heating_history = []

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
            error_id = f"{eid}_{state}"
            # Skip dismissed errors
            if error_id not in st.session_state.dismissed_errors:
                errors.append({
                    'id': error_id,
                    'level': 'error',
                    'message': f"Entity nicht verfügbar: {name}",
                    'entity_id': eid,
                    'details': []
                })
    return errors

def dismiss_error(error_id: str):
    """Dismiss an error so it won't be shown again."""
    st.session_state.dismissed_errors.add(error_id)

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
    # /repo is mounted from host in docker-compose
    git_dirs = ["/repo", "/app", "/data", os.getcwd()]
    for git_dir in git_dirs:
        git_path = os.path.join(git_dir, ".git")
        if os.path.exists(git_path):
            try:
                result = subprocess.run(
                    ["git", "pull", "origin", "main"],
                    cwd=git_dir,
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                if result.returncode == 0:
                    return True, f"✅ Update erfolgreich!\n\n{result.stdout}\n\n⚠️ **Neustart erforderlich:**\n```\nsudo docker compose up -d --build\n```"
                else:
                    return False, result.stderr
            except Exception as e:
                return False, str(e)
    return False, """Git Repository nicht gefunden.

**Manuelles Update auf dem Server:**
```
cd /DATA/AppData/smarthome-ai-center
git pull
sudo docker compose up -d --build
```"""

def get_git_status():
    """Get current git status."""
    git_dirs = ["/repo", "/app", "/data", os.getcwd()]
    for git_dir in git_dirs:
        git_path = os.path.join(git_dir, ".git")
        if os.path.exists(git_path):
            try:
                result = subprocess.run(
                    ["git", "log", "-1", "--format=%h - %s (%cr)"],
                    cwd=git_dir,
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if result.returncode == 0 and result.stdout.strip():
                    return result.stdout.strip()
            except:
                pass
    return f"v{APP_VERSION}"

def get_ha_automations():
    """Get all automations from Home Assistant."""
    url = get_setting("ha_url", "").rstrip("/")
    token = get_setting("ha_token", "")
    automations = []
    try:
        # Get automation states
        resp = requests.get(
            f"{url}/api/states",
            headers={"Authorization": f"Bearer {token}"},
            timeout=30
        )
        if resp.status_code == 200:
            states = resp.json()
            for entity in states:
                if entity.get('entity_id', '').startswith('automation.'):
                    automations.append({
                        'entity_id': entity.get('entity_id'),
                        'name': entity.get('attributes', {}).get('friendly_name', entity.get('entity_id')),
                        'state': entity.get('state'),
                        'last_triggered': entity.get('attributes', {}).get('last_triggered'),
                        'mode': entity.get('attributes', {}).get('mode', 'single'),
                        'current': entity.get('attributes', {}).get('current', 0)
                    })
    except:
        pass
    return automations

def get_automation_config(entity_id: str):
    """Get automation configuration/YAML from Home Assistant."""
    url = get_setting("ha_url", "").rstrip("/")
    token = get_setting("ha_token", "")
    try:
        # Try to get config via API
        resp = requests.get(
            f"{url}/api/config/automation/config/{entity_id.replace('automation.', '')}",
            headers={"Authorization": f"Bearer {token}"},
            timeout=30
        )
        if resp.status_code == 200:
            return resp.json()
    except:
        pass
    return None

def get_ha_logbook(entity_id: str = None, hours: int = 24):
    """Get logbook entries from Home Assistant."""
    url = get_setting("ha_url", "").rstrip("/")
    token = get_setting("ha_token", "")
    try:
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=hours)
        
        params = {
            "timestamp": start_time.isoformat()
        }
        if entity_id:
            params["entity"] = entity_id
            
        resp = requests.get(
            f"{url}/api/logbook/{start_time.isoformat()}",
            headers={"Authorization": f"Bearer {token}"},
            params={"entity": entity_id} if entity_id else {},
            timeout=30
        )
        if resp.status_code == 200:
            return resp.json()
    except:
        pass
    return []

def get_climate_entities():
    """Get all climate/heating related entities including EMS-ESP."""
    states = get_ha_states()
    climate_entities = []
    keywords = [
        'climate.', 'sensor.temp', 'sensor.hum', 'valve', 'thermostat',
        'heating', 'heiz', 'ems-esp', 'ems_esp', 'boiler', 'dhw',
        'vorlauf', 'rücklauf', 'flow', 'radiator', 'hc1', 'hc2'
    ]
    for entity in states:
        eid = entity.get('entity_id', '').lower()
        fname = entity.get('attributes', {}).get('friendly_name', '').lower()
        if any(x in eid or x in fname for x in keywords):
            climate_entities.append(entity)
    return climate_entities

def save_heating_history(analysis_data: Dict):
    """Save heating analysis to history file."""
    try:
        history = []
        if HISTORY_FILE.exists():
            with open(HISTORY_FILE, 'r') as f:
                history = json.load(f)

        # Add timestamp
        analysis_data['timestamp'] = datetime.now().isoformat()
        history.append(analysis_data)

        # Keep only last 100 entries
        history = history[-100:]

        # Save to file
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        with open(HISTORY_FILE, 'w') as f:
            json.dump(history, f, indent=2)

        return True
    except Exception as e:
        st.error(f"Fehler beim Speichern der Historie: {e}")
        return False

def load_heating_history() -> List[Dict]:
    """Load heating analysis history."""
    try:
        if HISTORY_FILE.exists():
            with open(HISTORY_FILE, 'r') as f:
                return json.load(f)
        return []
    except:
        return []

def get_influxdb_data(query: str, bucket: str = "homeassistant") -> Optional[List]:
    """Query InfluxDB for historical data from Home Assistant."""
    try:
        influx_url = get_setting("influx_url", "")
        influx_token = get_setting("influx_token", "")
        influx_org = get_setting("influx_org", "")

        if not all([influx_url, influx_token, influx_org]):
            return None

        from influxdb_client import InfluxDBClient

        client = InfluxDBClient(
            url=influx_url,
            token=influx_token,
            org=influx_org,
            timeout=30000
        )

        query_api = client.query_api()
        result = query_api.query(query)

        data = []
        for table in result:
            for record in table.records:
                data.append({
                    'time': record.get_time(),
                    'value': record.get_value(),
                    'field': record.get_field(),
                    'measurement': record.get_measurement(),
                })

        client.close()
        return data
    except ImportError:
        st.warning("⚠️ influxdb-client nicht installiert. Führe aus: pip install influxdb-client")
        return None
    except Exception as e:
        st.error(f"InfluxDB Fehler: {e}")
        return None

def get_heating_history_from_influx(entity_id: str, hours: int = 24) -> Optional[List]:
    """Get heating entity history from InfluxDB."""
    # Build Flux query
    query = f'''
    from(bucket: "homeassistant")
        |> range(start: -{hours}h)
        |> filter(fn: (r) => r["entity_id"] == "{entity_id}")
        |> filter(fn: (r) => r["_field"] == "value")
        |> aggregateWindow(every: 5m, fn: mean, createEmpty: false)
    '''

    return get_influxdb_data(query)

def call_ha_service(domain: str, service: str, data: dict):
    """Call a Home Assistant service."""
    url = get_setting("ha_url", "").rstrip("/")
    token = get_setting("ha_token", "")
    try:
        resp = requests.post(
            f"{url}/api/services/{domain}/{service}",
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
            json=data,
            timeout=30
        )
        return resp.status_code == 200, resp.text
    except Exception as e:
        return False, str(e)

def parse_service_calls(text: str):
    """Parse service calls from AI response text."""
    import re
    import yaml
    
    service_calls = []
    
    # Pattern 1: YAML blocks with service:
    yaml_pattern = r'```(?:yaml)?\s*(service:\s*[\w\.]+.*?)```'
    matches = re.findall(yaml_pattern, text, re.DOTALL | re.IGNORECASE)
    
    for match in matches:
        try:
            parsed = yaml.safe_load(match)
            if isinstance(parsed, dict) and 'service' in parsed:
                service_calls.append(parsed)
        except:
            pass
    
    # Pattern 2: Look for service: domain.action patterns
    service_pattern = r'service:\s*([\w]+)\.([\w]+)'
    for match in re.finditer(service_pattern, text):
        domain, action = match.groups()
        # Try to find associated data
        # This is a simplified parser
        
    return service_calls

def render_response_with_actions(response_text: str, key_prefix: str = "action"):
    """Render AI response with executable service call buttons."""
    import re
    import yaml
    
    # Split response into parts
    parts = re.split(r'(```(?:yaml)?\s*service:.*?```)', response_text, flags=re.DOTALL)
    
    for i, part in enumerate(parts):
        if part.strip().startswith('```') and 'service:' in part.lower():
            # This is a service call block
            yaml_content = re.sub(r'^```(?:yaml)?\s*', '', part)
            yaml_content = re.sub(r'\s*```$', '', yaml_content)
            
            # Display the code
            st.code(yaml_content, language='yaml')
            
            # Try to parse and add execute button
            try:
                parsed = yaml.safe_load(yaml_content)
                if isinstance(parsed, dict) and 'service' in parsed:
                    service_full = parsed.get('service', '')
                    if '.' in service_full:
                        domain, service = service_full.split('.', 1)
                        
                        # Build service data
                        service_data = {}
                        if 'target' in parsed:
                            service_data['target'] = parsed['target']
                        if 'data' in parsed:
                            service_data.update(parsed['data'])
                        if 'entity_id' in parsed:
                            service_data['entity_id'] = parsed['entity_id']
                        
                        # Create execute button
                        col1, col2 = st.columns([1, 4])
                        with col1:
                            if st.button(f"▶️ Ausführen", key=f"{key_prefix}_{i}"):
                                with st.spinner(f"Führe {service_full} aus..."):
                                    success, result = call_ha_service(domain, service, service_data)
                                if success:
                                    st.success(f"✅ {service_full} erfolgreich ausgeführt!")
                                else:
                                    st.error(f"❌ Fehler: {result}")
                        with col2:
                            st.caption(f"Service: `{service_full}`")
            except Exception as e:
                st.caption(f"⚠️ Konnte Service nicht parsen: {e}")
        else:
            # Regular markdown content
            if part.strip():
                st.markdown(part)

# ============================================
# SIDEBAR
# ============================================
with st.sidebar:
    st.markdown(f'<div class="logo">🏠 AI Center</div>', unsafe_allow_html=True)
    
    # Connection Status
    connected, status_msg = check_ha_connection()
    if connected:
        st.markdown(f'<div class="status-badge status-online">● {status_msg}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="status-badge status-offline">● {status_msg}</div>', unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Navigation
    page = st.radio(
        "",
        ["🏠 Dashboard", "🔍 Bug-Hunter", "🔧 Optimizer", "🌡️ Heizung", "📊 Analyst", "🛠️ Architect", "⚙️ Einstellungen"],
        label_visibility="collapsed"
    )

# ============================================
# PAGE: DASHBOARD
# ============================================
if page == "🏠 Dashboard":
    st.markdown("## Dashboard")
    
    # Get data
    entities = get_ha_states()
    errors = get_ha_errors()
    
    # Metrics Row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-info">
                <h2>{len(entities)}</h2>
                <p>Entitäten</p>
            </div>
            <div class="metric-icon icon-yellow">📊</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        unavailable = len([e for e in entities if e.get('state') == 'unavailable'])
        change_class = "down" if unavailable > 0 else "up"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-info">
                <h2>{unavailable}</h2>
                <p>Nicht verfügbar</p>
                <div class="change {change_class}">{'↓' if unavailable == 0 else '↑'} {unavailable}</div>
            </div>
            <div class="metric-icon icon-{'red' if unavailable > 0 else 'green'}">⚠️</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        lights_on = len([e for e in entities if e.get('entity_id', '').startswith('light.') and e.get('state') == 'on'])
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-info">
                <h2>{lights_on}</h2>
                <p>Lichter an</p>
            </div>
            <div class="metric-icon icon-cyan">💡</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        automations = len([e for e in entities if e.get('entity_id', '').startswith('automation.')])
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-info">
                <h2>{automations}</h2>
                <p>Automationen</p>
            </div>
            <div class="metric-icon icon-purple">⚡</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Two columns
    col_left, col_right = st.columns([2, 1])
    
    with col_left:
        st.markdown("""<div class="content-card"><h3>📊 Entitäten nach Domain</h3>""", unsafe_allow_html=True)
        
        if entities:
            domains = {}
            for e in entities:
                domain = e.get('entity_id', 'unknown').split('.')[0]
                domains[domain] = domains.get(domain, 0) + 1
            
            sorted_domains = sorted(domains.items(), key=lambda x: x[1], reverse=True)[:8]
            
            for domain, count in sorted_domains:
                icon = {"light": "💡", "sensor": "📡", "switch": "🔘", "automation": "⚡", 
                        "binary_sensor": "🔴", "climate": "🌡️", "media_player": "🎵", "person": "👤"}.get(domain, "📦")
                st.markdown(f"""
                <div class="list-item">
                    <div class="list-icon" style="background: #f0f4f8;">{icon}</div>
                    <div class="list-content">
                        <p class="list-title">{domain}</p>
                        <p class="list-subtitle">{count} Entitäten</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col_right:
        st.markdown("""<div class="content-card"><h3>⚠️ Aktuelle Probleme</h3>""", unsafe_allow_html=True)
        
        if errors:
            for err in errors[:5]:
                entity_id = err.get('entity_id', '')
                domain = entity_id.split('.')[0] if entity_id else 'unknown'
                st.markdown(f"""
                <div class="list-item">
                    <div class="list-icon" style="background: rgba(255,107,107,0.1); color: #ff6b6b;">❌</div>
                    <div class="list-content">
                        <p class="list-title">{err['message'][:35]}...</p>
                        <p class="list-subtitle">{domain}</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            if len(errors) > 5:
                st.markdown(f"<p style='color:#8896ab; font-size:13px;'>+ {len(errors) - 5} weitere</p>", unsafe_allow_html=True)
        else:
            st.success("✅ Keine Probleme!")
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Refresh button
    if st.button("🔄 Aktualisieren"):
        st.rerun()

# ============================================
# PAGE: BUG-HUNTER (with dismissible errors)
# ============================================
elif page == "🔍 Bug-Hunter":
    st.markdown("## Bug-Hunter")
    st.markdown("Finde und behebe Probleme mit KI-Unterstützung - wegklickbare Fehler!")

    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("🔄 Neu laden"):
            st.session_state.error_logs = get_ha_errors()
            st.rerun()
    with col2:
        if st.button("🗑️ Alle zurücksetzen"):
            st.session_state.dismissed_errors = set()
            st.session_state.error_logs = get_ha_errors()
            st.rerun()

    errors = st.session_state.error_logs
    if not errors:
        errors = get_ha_errors()
        st.session_state.error_logs = errors

    st.markdown(f"""<div class="content-card"><h3>🐛 {len(errors)} Aktive Probleme</h3>""", unsafe_allow_html=True)

    if not errors:
        st.success("🎉 Keine Probleme! Dein System läuft einwandfrei.")
    else:
        st.markdown("</div>", unsafe_allow_html=True)

        # Display errors with dismiss buttons
        for i, err in enumerate(errors[:20]):
            error_id = err.get('id', f"error_{i}")
            col_err, col_dismiss = st.columns([20, 1])

            with col_err:
                with st.expander(f"🔴 {err['message'][:70]}...", expanded=False):
                    st.code(err.get('entity_id', 'N/A'))

                    if st.button(f"🤖 Mit KI analysieren", key=f"analyze_{i}"):
                        with st.spinner("Gemini analysiert..."):
                            prompt = f"""Home Assistant Problem:
{err['message']}
Entity: {err.get('entity_id', 'N/A')}

Antworte auf Deutsch:
1. Mögliche Ursache
2. Lösung
3. Konkrete Schritte zur Behebung"""
                            solution = ask_gemini(prompt)
                        st.markdown(solution)

            with col_dismiss:
                if st.button("✕", key=f"dismiss_{i}", help="Fehler wegklicken"):
                    dismiss_error(error_id)
                    st.session_state.error_logs = get_ha_errors()
                    st.rerun()

        if len(errors) >= 20:
            st.info(f"📋 Es gibt weitere Fehler. Behebe die oberen, damit neue nachrutschen können.")

    if errors:
        st.markdown("</div>", unsafe_allow_html=True)

# ============================================
# PAGE: AUTOMATION OPTIMIZER
# ============================================
elif page == "🔧 Optimizer":
    st.markdown("## Automation Optimizer")
    st.markdown("Analysiere und optimiere bestehende Automationen")
    
    # Session state for optimizer
    if 'optimizer_analysis' not in st.session_state:
        st.session_state.optimizer_analysis = {}
    if 'optimizer_claude_prompt' not in st.session_state:
        st.session_state.optimizer_claude_prompt = {}
    
    # Load automations
    automations = get_ha_automations()
    
    st.markdown(f"""<div class="content-card"><h3>⚡ {len(automations)} Automationen gefunden</h3></div>""", unsafe_allow_html=True)
    
    if not automations:
        st.warning("Keine Automationen gefunden. Prüfe die Home Assistant Verbindung.")
    else:
        for i, auto in enumerate(automations):
            auto_id = auto['entity_id']
            auto_name = auto['name']
            
            with st.expander(f"{'🟢' if auto['state'] == 'on' else '🔴'} {auto_name}", expanded=False):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.markdown(f"**Entity:** `{auto_id}`")
                    st.markdown(f"**Status:** {auto['state']} | **Modus:** {auto['mode']}")
                    if auto['last_triggered']:
                        st.markdown(f"**Zuletzt ausgelöst:** {auto['last_triggered']}")
                
                with col2:
                    # Get config if available
                    config = get_automation_config(auto_id)
                    if config:
                        st.json(config)
                
                st.markdown("---")
                
                # Step 1: Gemini Analysis
                if st.button(f"🔍 Mit Gemini analysieren", key=f"opt_gemini_{i}"):
                    with st.spinner("Gemini analysiert..."):
                        config_str = json.dumps(config, indent=2) if config else "Konfiguration nicht verfügbar"
                        
                        prompt = f"""Analysiere diese Home Assistant Automation und gib Verbesserungsvorschläge:

AUTOMATION: {auto_name}
ENTITY: {auto_id}
STATUS: {auto['state']}
MODUS: {auto['mode']}
ZULETZT AUSGELÖST: {auto['last_triggered']}

KONFIGURATION:
{config_str}

Antworte auf Deutsch mit:
1. Was macht diese Automation?
2. Mögliche Probleme oder Ineffizienzen
3. 3-5 konkrete Verbesserungsvorschläge
4. Bewertung (1-10) der aktuellen Qualität"""

                        analysis = ask_gemini(prompt)
                        st.session_state.optimizer_analysis[auto_id] = analysis
                
                # Show Gemini analysis
                if auto_id in st.session_state.optimizer_analysis:
                    st.markdown("### 🔍 Gemini Analyse")
                    st.markdown(st.session_state.optimizer_analysis[auto_id])
                    
                    st.markdown("---")
                    
                    # Step 2: Prepare Claude prompt
                    if st.button(f"📝 Claude Prompt erstellen", key=f"opt_prep_{i}"):
                        config_str = json.dumps(config, indent=2) if config else "Nicht verfügbar"
                        
                        claude_prompt = f"""Optimiere diese Home Assistant Automation basierend auf der Analyse:

AKTUELLE AUTOMATION:
Name: {auto_name}
Entity: {auto_id}

AKTUELLE KONFIGURATION:
```yaml
{config_str}
```

GEMINI ANALYSE:
{st.session_state.optimizer_analysis[auto_id]}

AUFGABE:
1. Erstelle eine verbesserte Version der Automation
2. Erkläre die Änderungen
3. Gib den vollständigen YAML-Code aus, der direkt in Home Assistant verwendet werden kann

Antworte auf Deutsch."""

                        st.session_state.optimizer_claude_prompt[auto_id] = claude_prompt
                
                # Show and edit Claude prompt
                if auto_id in st.session_state.optimizer_claude_prompt:
                    st.markdown("### 📝 Claude Prompt (bearbeitbar)")
                    edited_prompt = st.text_area(
                        "Prompt anpassen:",
                        value=st.session_state.optimizer_claude_prompt[auto_id],
                        height=300,
                        key=f"prompt_edit_{i}"
                    )
                    
                    if st.button(f"🚀 Mit Claude optimieren", key=f"opt_claude_{i}"):
                        with st.spinner("Claude optimiert..."):
                            result = ask_claude(edited_prompt)
                        
                        st.markdown("### 🎯 Claude Optimierung")
                        st.markdown(result)
                        
                        # TODO: Parse YAML and offer to save
                        st.info("💡 Kopiere den YAML-Code und füge ihn in deine automations.yaml ein.")

# ============================================
# PAGE: HEIZUNGSMANAGEMENT
# ============================================
elif page == "🌡️ Heizung":
    st.markdown("## Heizungsmanagement")
    st.markdown("Intelligente Analyse und Optimierung deiner Heizung")
    
    # Session state for heating chat
    if 'heating_chat_history' not in st.session_state:
        st.session_state.heating_chat_history = []
    if 'heating_context' not in st.session_state:
        st.session_state.heating_context = ""
    
    # Tabs for different sections
    tab1, tab2, tab3 = st.tabs(["📊 Übersicht", "💬 KI-Assistent", "📋 Logs"])
    
    with tab1:
        st.markdown("### Heizungs-Übersicht & Historie")

        # Load history
        history = load_heating_history()
        if history:
            st.markdown(f"""<div class="content-card">
                <h3>📜 Letzte Analysen ({len(history)})</h3>
            </div>""", unsafe_allow_html=True)

            for idx, entry in enumerate(reversed(history[-5:])):
                with st.expander(f"📅 {entry.get('timestamp', 'N/A')[:16]} - {entry.get('type', 'Analyse')}", expanded=False):
                    st.json(entry)

        climate_entities = get_climate_entities()
        automations = get_ha_automations()
        heating_keywords = ['heiz', 'heating', 'temperatur', 'klima', 'thermostat', 'ems', 'vorlauf', 'boiler', 'schimmel']
        heating_automations = [a for a in automations if any(x in a['name'].lower() for x in heating_keywords)]

        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"""<div class="content-card"><h3>🌡️ {len(climate_entities)} Klima/EMS-ESP Entitäten</h3>""", unsafe_allow_html=True)
            
            for entity in climate_entities[:10]:
                eid = entity.get('entity_id', '')
                state = entity.get('state', 'unknown')
                name = entity.get('attributes', {}).get('friendly_name', eid)
                temp = entity.get('attributes', {}).get('current_temperature', '')
                target = entity.get('attributes', {}).get('temperature', '')
                
                temp_info = f" | {temp}°C → {target}°C" if temp and target else f" | {state}"
                
                st.markdown(f"""
                <div class="list-item">
                    <div class="list-icon" style="background: rgba(77, 171, 247, 0.1); color: #4dabf7;">🌡️</div>
                    <div class="list-content">
                        <p class="list-title">{name[:30]}</p>
                        <p class="list-subtitle">{eid}{temp_info}</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""<div class="content-card"><h3>⚡ {len(heating_automations)} Heizungs-Automationen</h3>""", unsafe_allow_html=True)
            
            for auto in heating_automations:
                status_icon = "🟢" if auto['state'] == 'on' else "🔴"
                triggered = auto.get('last_triggered', 'Nie')
                
                st.markdown(f"""
                <div class="list-item">
                    <div class="list-icon" style="background: rgba(0, 196, 140, 0.1); color: #00c48c;">{status_icon}</div>
                    <div class="list-content">
                        <p class="list-title">{auto['name'][:30]}</p>
                        <p class="list-subtitle">Zuletzt: {triggered}</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            if not heating_automations:
                st.info("Keine Heizungs-Automationen gefunden")
            
            st.markdown("</div>", unsafe_allow_html=True)
    
    with tab2:
        st.markdown("### 💬 KI-Assistent für Heizungsprobleme")
        st.markdown("Beschreibe dein Problem und ich analysiere Logs, Entitäten und Automationen.")
        
        # Context builder
        with st.expander("🔧 Kontext konfigurieren", expanded=False):
            include_entities = st.checkbox("Klima-Entitäten einbeziehen", value=True)
            include_automations = st.checkbox("Heizungs-Automationen einbeziehen", value=True)
            include_logs = st.checkbox("Logbook einbeziehen (letzte 24h)", value=True)
            log_hours = st.slider("Log-Zeitraum (Stunden)", 1, 72, 24)
        
        # Build context
        if st.button("🔄 Kontext aktualisieren"):
            context_parts = []
            
            if include_entities:
                climate_entities = get_climate_entities()
                context_parts.append("## KLIMA-ENTITÄTEN\n" + json.dumps([{
                    'entity_id': e.get('entity_id'),
                    'state': e.get('state'),
                    'current_temp': e.get('attributes', {}).get('current_temperature'),
                    'target_temp': e.get('attributes', {}).get('temperature'),
                    'hvac_action': e.get('attributes', {}).get('hvac_action')
                } for e in climate_entities], indent=2))
            
            if include_automations:
                automations = get_ha_automations()
                heating_keywords = ['heiz', 'heating', 'temperatur', 'klima', 'thermostat', 'ems', 'vorlauf', 'boiler', 'schimmel']
                heating_autos = [a for a in automations if any(x in a['name'].lower() for x in heating_keywords)]
                context_parts.append("## HEIZUNGS-AUTOMATIONEN\n" + json.dumps(heating_autos, indent=2))
            
            if include_logs:
                # Get logs for climate entities including EMS-ESP
                logs = get_ha_logbook(hours=log_hours)
                log_keywords = ['climate', 'heiz', 'heating', 'temperatur', 'valve', 'thermostat', 'ems', 'boiler', 'vorlauf', 'dhw']
                heating_logs = [l for l in logs if any(x in str(l).lower() for x in log_keywords)][:50]
                context_parts.append(f"## LOGBOOK (letzte {log_hours}h)\n" + json.dumps(heating_logs, indent=2))
            
            st.session_state.heating_context = "\n\n".join(context_parts)
            st.success(f"✅ Kontext aktualisiert ({len(st.session_state.heating_context)} Zeichen)")
        
        # Show context preview
        if st.session_state.heating_context:
            with st.expander("📋 Aktueller Kontext (Vorschau)"):
                st.code(st.session_state.heating_context[:2000] + "..." if len(st.session_state.heating_context) > 2000 else st.session_state.heating_context)
        
        st.markdown("---")
        
        # Chat interface
        st.markdown("### Chat")
        
        # Display chat history with executable actions
        for idx, msg in enumerate(st.session_state.heating_chat_history):
            if msg['role'] == 'user':
                st.markdown(f"**🧑 Du:** {msg['content']}")
            else:
                st.markdown("**🤖 Claude:**")
                render_response_with_actions(msg['content'], key_prefix=f"heat_chat_{idx}")
            st.markdown("---")
        
        # Input
        user_input = st.text_area("Dein Problem oder deine Frage:", placeholder="z.B.: Die Heizung im Wohnzimmer schaltet sich nicht ab obwohl die Zieltemperatur erreicht ist...", height=100)
        
        col1, col2 = st.columns([1, 4])
        with col1:
            send_button = st.button("📤 Senden", type="primary")
        with col2:
            if st.button("🗑️ Chat leeren"):
                st.session_state.heating_chat_history = []
                st.rerun()
        
        if send_button and user_input:
            # Build full prompt with context
            full_prompt = f"""Du bist ein Experte für Home Assistant Heizungssteuerung.
Der Benutzer hat ein Problem mit seiner Heizung. Analysiere die bereitgestellten Daten und hilf bei der Lösung.

{st.session_state.heating_context}

## CHAT-VERLAUF
{chr(10).join([f"{m['role'].upper()}: {m['content']}" for m in st.session_state.heating_chat_history[-5:]])}

## AKTUELLE FRAGE
{user_input}

Antworte auf Deutsch. Sei konkret und gib wenn möglich:
1. Analyse des Problems basierend auf den Logs/Daten
2. Mögliche Ursachen
3. Konkrete Lösungsvorschläge

Wenn du einen Home Assistant Dienstaufruf empfiehlst, formatiere ihn IMMER so (im YAML Code-Block):
```yaml
service: domain.service_name
target:
  entity_id: entity.id
data:
  parameter: wert
```

Der Benutzer kann diese Dienstaufrufe dann direkt aus der Oberfläche ausführen."""

            # Add user message to history
            st.session_state.heating_chat_history.append({'role': 'user', 'content': user_input})

            with st.spinner("Claude analysiert..."):
                response = ask_claude(full_prompt)

            # Add response to history
            st.session_state.heating_chat_history.append({'role': 'assistant', 'content': response})

            # Save to heating history
            save_heating_history({
                'type': 'chat_analysis',
                'question': user_input,
                'response': response,
                'context_size': len(st.session_state.heating_context)
            })

            st.rerun()
    
    with tab3:
        st.markdown("### 📋 Heizungs-Logs & InfluxDB Historie")

        # InfluxDB Section
        st.markdown("""<div class="content-card"><h3>📊 InfluxDB Historische Daten</h3></div>""", unsafe_allow_html=True)

        influx_configured = all([
            get_setting("influx_url", ""),
            get_setting("influx_token", ""),
            get_setting("influx_org", "")
        ])

        if influx_configured:
            climate_entities = get_climate_entities()
            if climate_entities:
                entity_options = [e.get('entity_id', '') for e in climate_entities[:20]]
                selected_entity = st.selectbox("Entität auswählen", entity_options)
                hours_back = st.slider("Zeitraum (Stunden)", 1, 168, 24)

                if st.button("📈 Daten von InfluxDB abrufen"):
                    with st.spinner("Lade Daten von InfluxDB..."):
                        data = get_heating_history_from_influx(selected_entity, hours_back)

                    if data:
                        st.success(f"✅ {len(data)} Datenpunkte geladen!")

                        # Simple visualization
                        import pandas as pd
                        df = pd.DataFrame(data)
                        if not df.empty and 'time' in df.columns and 'value' in df.columns:
                            df['time'] = pd.to_datetime(df['time'])
                            st.line_chart(df.set_index('time')['value'])
                            st.dataframe(df.tail(20))
                        else:
                            st.json(data[:10])
                    else:
                        st.warning("⚠️ Keine Daten gefunden oder InfluxDB nicht erreichbar.")
        else:
            st.info("💡 Konfiguriere InfluxDB in den Einstellungen, um historische Daten zu analysieren.")

        st.markdown("---")

        # Logbook section
        st.markdown("### 📋 Home Assistant Logbook")

        log_hours = st.selectbox("Zeitraum", [6, 12, 24, 48, 72], index=2)

        if st.button("🔄 Logs laden"):
            logs = get_ha_logbook(hours=log_hours)
            log_keywords = ['climate', 'heiz', 'heating', 'temperatur', 'valve', 'thermostat', 'ems', 'boiler', 'vorlauf', 'dhw']
            heating_logs = [l for l in logs if any(x in str(l).lower() for x in log_keywords)]

            st.markdown(f"**{len(heating_logs)} Heizungs/EMS-ESP Ereignisse gefunden**")

            for log in heating_logs[:50]:
                name = log.get('name', 'Unknown')
                message = log.get('message', log.get('state', ''))
                when = log.get('when', '')

                st.markdown(f"""
                <div class="list-item">
                    <div class="list-content">
                        <p class="list-title">{name}</p>
                        <p class="list-subtitle">{message} - {when}</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)

# ============================================
# PAGE: ANALYST
# ============================================
elif page == "📊 Analyst":
    st.markdown("## System Analyst")
    st.markdown("KI-gestützte Analyse deines Smart Homes")
    
    st.markdown("""<div class="content-card">""", unsafe_allow_html=True)
    
    model = st.selectbox("KI Modell", ["Gemini Flash (günstig)", "Claude (präziser)"])
    
    if st.button("🚀 Analyse starten"):
        with st.spinner("Analysiere..."):
            states = get_ha_states()
            
            summary = {
                'total': len(states),
                'unavailable': len([e for e in states if e.get('state') == 'unavailable']),
                'lights_on': len([e for e in states if e.get('entity_id', '').startswith('light.') and e.get('state') == 'on']),
            }
            
            prompt = f"""Smart Home Analyse:
- {summary['total']} Entitäten
- {summary['unavailable']} nicht verfügbar  
- {summary['lights_on']} Lichter an

Gib 5 konkrete Optimierungsvorschläge auf Deutsch."""

            if "Gemini" in model:
                result = ask_gemini(prompt)
            else:
                result = ask_claude(prompt)
            
            st.session_state.analysis_results = result
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    if st.session_state.analysis_results:
        st.markdown("""<div class="content-card"><h3>📋 Ergebnisse</h3>""", unsafe_allow_html=True)
        st.markdown(st.session_state.analysis_results)
        st.markdown("</div>", unsafe_allow_html=True)

# ============================================
# PAGE: ARCHITECT
# ============================================
elif page == "🛠️ Architect":
    st.markdown("## Automation Architect")
    st.markdown("Erstelle Automationen mit KI")
    
    st.markdown("""<div class="content-card">""", unsafe_allow_html=True)
    
    description = st.text_area(
        "Beschreibe deine Automation",
        placeholder="z.B.: Schalte das Licht im Flur ein wenn Bewegung erkannt wird, aber nur nachts",
        height=100
    )
    
    output_format = st.selectbox("Format", ["Home Assistant YAML", "Node-RED JSON", "Python Script"])
    
    if st.button("🪄 Erstellen"):
        if description:
            with st.spinner("Claude erstellt..."):
                entities = get_ha_states()
                entity_ids = [e.get('entity_id', '') for e in entities][:50]
                
                prompt = f"""Erstelle eine Home Assistant Automation:

BESCHREIBUNG: {description}
FORMAT: {output_format}
ENTITÄTEN: {', '.join(entity_ids[:20])}

Antworte auf Deutsch mit Code."""
                
                result = ask_claude(prompt)
            
            st.markdown("### Ergebnis")
            st.markdown(result)
        else:
            st.warning("Bitte beschreibe deine Automation.")
    
    st.markdown("</div>", unsafe_allow_html=True)

# ============================================
# PAGE: SETTINGS
# ============================================
elif page == "⚙️ Einstellungen":
    st.markdown("## Einstellungen")
    
    settings = st.session_state.settings
    
    # Home Assistant
    st.markdown("""<div class="content-card"><h3>🏠 Home Assistant</h3>""", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        ha_url = st.text_input("URL", value=settings.get("ha_url", ""), placeholder="http://192.168.1.100:8123")
    with col2:
        ha_token = st.text_input("Token", value=settings.get("ha_token", ""), type="password")
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # AI Keys
    st.markdown("""<div class="content-card"><h3>🤖 AI API Keys</h3>""", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        google_key = st.text_input("Google AI (Gemini)", value=settings.get("google_ai_key", ""), type="password")
    with col2:
        anthropic_key = st.text_input("Anthropic (Claude)", value=settings.get("anthropic_key", ""), type="password")

    st.markdown("</div>", unsafe_allow_html=True)

    # InfluxDB Configuration
    st.markdown("""<div class="content-card"><h3>📊 InfluxDB (für historische Daten)</h3>""", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        influx_url = st.text_input("InfluxDB URL", value=settings.get("influx_url", ""), placeholder="http://192.168.1.100:8086")
    with col2:
        influx_org = st.text_input("Organisation", value=settings.get("influx_org", ""), placeholder="homeassistant")
    with col3:
        influx_token = st.text_input("Token", value=settings.get("influx_token", ""), type="password")

    st.info("💡 Mit InfluxDB können historische Daten aus Home Assistant für tiefere Heizungsanalysen abgerufen werden.")

    st.markdown("</div>", unsafe_allow_html=True)
    
    # GitHub
    st.markdown("""<div class="content-card"><h3>📦 GitHub</h3>""", unsafe_allow_html=True)
    
    github_repo = st.text_input("Repository", value=settings.get("github_repo", "https://github.com/laurenciusMD/smarthome-ai-center.git"))
    
    st.markdown(f"**Version:** `{get_git_status()}`")
    
    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("📥 Updates"):
            with st.spinner("Lade..."):
                success, output = git_pull_updates()
            if success:
                st.success("✅ Updates geladen! App neu starten.")
                st.code(output)
            else:
                st.warning("⚠️ Auto-Update nicht möglich")
                st.markdown(output)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Save
    if st.button("💾 Speichern"):
        new_settings = {
            "ha_url": ha_url,
            "ha_token": ha_token,
            "google_ai_key": google_key,
            "anthropic_key": anthropic_key,
            "influx_url": influx_url,
            "influx_token": influx_token,
            "influx_org": influx_org,
            "github_repo": github_repo,
            "theme": "light"
        }
        save_settings(new_settings)
        st.session_state.settings = new_settings
        st.balloons()
        st.success("✅ Gespeichert!")
    
    st.markdown("---")
    
    # Connection Tests
    st.markdown("""<div class="content-card"><h3>🧪 Verbindungstest</h3>""", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Test HA"):
            ok, msg = check_ha_connection()
            if ok:
                st.success("✅ OK")
            else:
                st.error(f"❌ {msg}")
    
    with col2:
        if st.button("Test Gemini"):
            r = ask_gemini("Sag OK")
            if "OK" in r.upper():
                st.success("✅ OK")
            else:
                st.error("❌ Fehler")
    
    with col3:
        if st.button("Test Claude"):
            r = ask_claude("Sag OK")
            if "OK" in r.upper():
                st.success("✅ OK")
            else:
                st.error("❌ Fehler")
    
    st.markdown("</div>", unsafe_allow_html=True)
