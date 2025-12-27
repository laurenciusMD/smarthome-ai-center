"""
Smart Home AI Center - Main Application
=======================================
AI-powered maintenance system for Home Assistant
"""

import streamlit as st
import os
import requests
import json
from datetime import datetime, timedelta
from anthropic import Anthropic
import google.generativeai as genai
import random

# ============================================
# PAGE CONFIG
# ============================================
st.set_page_config(
    page_title="Smart Home AI Center",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# CUSTOM CSS
# ============================================
st.markdown("""
<style>
    /* Dark theme improvements */
    .stApp {
        background-color: #0e1117;
    }
    
    /* Card styling */
    .metric-card {
        background: linear-gradient(135deg, #1a1f2e 0%, #151922 100%);
        border: 1px solid #2d3748;
        border-radius: 12px;
        padding: 20px;
        margin: 10px 0;
    }
    
    .metric-card h3 {
        color: #63b3ed;
        margin: 0 0 10px 0;
        font-size: 14px;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .metric-card .value {
        color: #fff;
        font-size: 32px;
        font-weight: bold;
    }
    
    /* Status badges */
    .status-ok { color: #48bb78; }
    .status-warn { color: #ecc94b; }
    .status-error { color: #fc8181; }
    
    /* Error list styling */
    .error-item {
        background: #1a1f2e;
        border-left: 4px solid #fc8181;
        padding: 15px;
        margin: 10px 0;
        border-radius: 0 8px 8px 0;
    }
    
    .error-item.warning {
        border-left-color: #ecc94b;
    }
    
    .error-item.info {
        border-left-color: #63b3ed;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background-color: #151922;
    }
    
    /* Button improvements */
    .stButton > button {
        background: linear-gradient(135deg, #4299e1 0%, #3182ce 100%);
        border: none;
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: 600;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #63b3ed 0%, #4299e1 100%);
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# SESSION STATE INIT
# ============================================
if 'ha_cache' not in st.session_state:
    st.session_state.ha_cache = None
if 'ha_cache_time' not in st.session_state:
    st.session_state.ha_cache_time = None
if 'error_logs' not in st.session_state:
    st.session_state.error_logs = []
if 'last_analysis' not in st.session_state:
    st.session_state.last_analysis = None
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = []

# ============================================
# HELPER FUNCTIONS
# ============================================

def get_ha_url():
    return os.getenv("HA_URL", "").rstrip("/")

def get_ha_token():
    return os.getenv("HA_TOKEN", "")

def get_anthropic_key():
    return os.getenv("ANTHROPIC_API_KEY", "")

def get_google_ai_key():
    return os.getenv("GOOGLE_AI_KEY", "")

def ask_gemini(prompt: str) -> str:
    """Ask Gemini Flash for quick analysis (cheaper than Claude)."""
    api_key = get_google_ai_key()
    if not api_key:
        return "❌ Google AI Key nicht konfiguriert (GOOGLE_AI_KEY in .env)"
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"❌ Gemini Fehler: {str(e)}"

def ask_claude(prompt: str) -> str:
    """Ask Claude for complex analysis (better quality)."""
    api_key = get_anthropic_key()
    if not api_key:
        return "❌ Anthropic API Key nicht konfiguriert"
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

def check_ha_connection():
    """Test Home Assistant connection."""
    url = get_ha_url()
    token = get_ha_token()
    if not url or not token:
        return False, "URL oder Token fehlt"
    try:
        resp = requests.get(
            f"{url}/api/",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10
        )
        if resp.status_code == 200:
            return True, resp.json().get("message", "OK")
        return False, f"HTTP {resp.status_code}"
    except requests.exceptions.ConnectionError:
        return False, "Verbindung fehlgeschlagen"
    except Exception as e:
        return False, str(e)

def get_ha_states():
    """Get all entity states from Home Assistant."""
    url = get_ha_url()
    token = get_ha_token()
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

def get_ha_error_log():
    """Get error log from Home Assistant via system_log service."""
    url = get_ha_url()
    token = get_ha_token()
    
    # Try multiple endpoints
    errors_found = []
    
    # Method 1: Try getting persistent notifications (often contain errors)
    try:
        resp = requests.get(
            f"{url}/api/states",
            headers={"Authorization": f"Bearer {token}"},
            timeout=30
        )
        if resp.status_code == 200:
            states = resp.json()
            for entity in states:
                eid = entity.get('entity_id', '')
                state = entity.get('state', '')
                attrs = entity.get('attributes', {})
                
                # Collect unavailable entities as errors
                if state == 'unavailable':
                    errors_found.append(f"ERROR: Entity {eid} is unavailable - {attrs.get('friendly_name', eid)}")
                
                # Collect persistent notifications
                if eid.startswith('persistent_notification.'):
                    msg = attrs.get('message', '')
                    if msg:
                        errors_found.append(f"WARNING: Notification - {msg[:200]}")
    except:
        pass
    
    # Method 2: Check for automations that failed
    try:
        resp = requests.get(
            f"{url}/api/logbook",
            headers={"Authorization": f"Bearer {token}"},
            timeout=30
        )
        if resp.status_code == 200:
            logbook = resp.json()
            for entry in logbook[-100:]:  # Last 100 entries
                msg = entry.get('message', '')
                name = entry.get('name', '')
                if 'error' in msg.lower() or 'failed' in msg.lower():
                    errors_found.append(f"ERROR: {name} - {msg}")
    except:
        pass
    
    return '\n'.join(errors_found)

def get_ha_services():
    """Get available services from Home Assistant."""
    url = get_ha_url()
    token = get_ha_token()
    try:
        resp = requests.get(
            f"{url}/api/services",
            headers={"Authorization": f"Bearer {token}"},
            timeout=30
        )
        if resp.status_code == 200:
            return resp.json()
        return []
    except:
        return []

def parse_error_log(log_text):
    """Parse error log into structured entries."""
    errors = []
    
    for line in log_text.split('\n'):
        line = line.strip()
        if not line:
            continue
        
        # Determine level
        if line.startswith('ERROR:'):
            level = 'error'
            message = line[6:].strip()
        elif line.startswith('WARNING:'):
            level = 'warning'
            message = line[8:].strip()
        else:
            continue
        
        errors.append({
            'level': level,
            'message': message,
            'details': [],
            'timestamp': datetime.now().isoformat()
        })
    
    return errors

def call_claude(prompt, system_prompt="Du bist ein Home Assistant Experte."):
    """Call Claude API for analysis."""
    api_key = get_anthropic_key()
    if not api_key:
        return "Fehler: ANTHROPIC_API_KEY nicht gesetzt"
    
    try:
        client = Anthropic(api_key=api_key)
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4096,
            system=system_prompt,
            messages=[{"role": "user", "content": prompt}]
        )
        return message.content[0].text
    except Exception as e:
        return f"Fehler bei Claude API: {str(e)}"

def get_smart_tip():
    """Get a smart tip for Home Assistant optimization."""
    tips = [
        "💡 **Tipp:** Gruppiere Lichter in Räumen, um sie gemeinsam zu steuern und Automationen zu vereinfachen.",
        "🔋 **Tipp:** Nutze `device_tracker` mit `consider_home` um häufiges Umschalten bei instabiler Verbindung zu vermeiden.",
        "⚡ **Tipp:** Verwende `trigger_variables` in Automationen für dynamischere und wiederverwendbare Trigger.",
        "🌡️ **Tipp:** Setze `window_seconds` bei Template-Sensoren, um Sensorwerte zu glätten.",
        "📊 **Tipp:** Nutze den `statistics` Sensor für Langzeitanalysen von Sensorwerten.",
        "🔒 **Tipp:** Aktiviere 2FA und nutze `trusted_networks` statt offene Zugänge.",
        "⏰ **Tipp:** Verwende `time_pattern` Trigger statt vieler einzelner `at` Trigger.",
        "🎯 **Tipp:** Nutze `choose` in Automationen statt mehrerer ähnlicher Automationen.",
        "💾 **Tipp:** Setze `recorder.purge_keep_days` auf 5-7 Tage um die Datenbank klein zu halten.",
        "🔄 **Tipp:** Nutze `reload_config_entry` Service um Integrationen neu zu laden ohne Neustart."
    ]
    return random.choice(tips)

def refresh_ha_data():
    """Refresh all Home Assistant data."""
    st.session_state.ha_cache = get_ha_states()
    st.session_state.ha_cache_time = datetime.now()
    st.session_state.error_logs = parse_error_log(get_ha_error_log())

# ============================================
# SIDEBAR NAVIGATION
# ============================================
with st.sidebar:
    st.title("🏠 AI Center")
    st.markdown("---")
    
    # Navigation
    page = st.radio(
        "Navigation",
        ["📊 Dashboard", "🔍 Bug-Hunter", "📈 48h Analyst", "🏗️ Architect"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    
    # Connection Status
    ha_ok, ha_msg = check_ha_connection()
    if ha_ok:
        st.success(f"✅ HA verbunden")
    else:
        st.error(f"❌ HA: {ha_msg}")
    
    # Cache info
    if st.session_state.ha_cache_time:
        cache_age = (datetime.now() - st.session_state.ha_cache_time).seconds
        st.caption(f"Cache: {cache_age}s alt")
    
    st.markdown("---")
    st.caption("v0.2.0 | Made with ❤️")

# ============================================
# PAGE: DASHBOARD
# ============================================
if page == "📊 Dashboard":
    st.title("📊 Dashboard")
    st.markdown("Übersicht über dein Smart Home System")
    
    # Refresh Button
    col_refresh, col_spacer = st.columns([1, 4])
    with col_refresh:
        if st.button("🔄 Daten aktualisieren", use_container_width=True):
            with st.spinner("Lade Daten von Home Assistant..."):
                refresh_ha_data()
            st.success("Daten aktualisiert!")
            st.rerun()
    
    st.markdown("---")
    
    # Metrics Row
    col1, col2, col3, col4 = st.columns(4)
    
    entities = st.session_state.ha_cache or []
    error_count = len(st.session_state.error_logs)
    
    with col1:
        st.metric(
            label="📱 Entitäten",
            value=len(entities),
            delta=None
        )
    
    with col2:
        unavailable = len([e for e in entities if e.get('state') == 'unavailable'])
        st.metric(
            label="⚠️ Nicht verfügbar",
            value=unavailable,
            delta=None,
            delta_color="inverse"
        )
    
    with col3:
        st.metric(
            label="🐛 Fehler im Log",
            value=error_count,
            delta=None,
            delta_color="inverse"
        )
    
    with col4:
        lights_on = len([e for e in entities if e.get('entity_id', '').startswith('light.') and e.get('state') == 'on'])
        st.metric(
            label="💡 Lichter an",
            value=lights_on
        )
    
    st.markdown("---")
    
    # Two column layout
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.subheader("🕐 Zuletzt analysiert")
        if st.session_state.last_analysis:
            st.info(f"Letzte Analyse: {st.session_state.last_analysis}")
        else:
            st.info("Noch keine Analyse durchgeführt")
        
        st.subheader("📋 Schnellstatus")
        
        # Entity breakdown
        if entities:
            domains = {}
            for e in entities:
                domain = e.get('entity_id', 'unknown').split('.')[0]
                domains[domain] = domains.get(domain, 0) + 1
            
            sorted_domains = sorted(domains.items(), key=lambda x: x[1], reverse=True)[:8]
            for domain, count in sorted_domains:
                st.write(f"**{domain}**: {count}")
    
    with col_right:
        st.subheader("💡 Smart Tipp des Tages")
        st.markdown(get_smart_tip())
        
        st.subheader("🚨 Letzte Fehler")
        if st.session_state.error_logs:
            for err in st.session_state.error_logs[:3]:
                level_icon = "🔴" if err['level'] == 'error' else "🟡"
                st.markdown(f"{level_icon} {err['message'][:100]}...")
        else:
            st.success("Keine Fehler im Log!")

# ============================================
# PAGE: BUG-HUNTER
# ============================================
elif page == "🔍 Bug-Hunter":
    st.title("🔍 Bug-Hunter")
    st.markdown("Analysiere und behebe Fehler in deinem Home Assistant")
    
    # Refresh logs
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("🔄 Logs laden", use_container_width=True):
            with st.spinner("Lade Fehler-Logs..."):
                log_text = get_ha_error_log()
                st.session_state.error_logs = parse_error_log(log_text)
            st.success(f"{len(st.session_state.error_logs)} Einträge geladen")
            st.rerun()
    
    st.markdown("---")
    
    # Filter
    filter_level = st.selectbox(
        "Filter nach Level",
        ["Alle", "Nur Fehler", "Nur Warnungen"]
    )
    
    errors = st.session_state.error_logs
    if filter_level == "Nur Fehler":
        errors = [e for e in errors if e['level'] == 'error']
    elif filter_level == "Nur Warnungen":
        errors = [e for e in errors if e['level'] == 'warning']
    
    st.markdown(f"**{len(errors)} Einträge gefunden**")
    st.markdown("---")
    
    # Error list
    if not errors:
        st.success("🎉 Keine Fehler gefunden! Dein System läuft sauber.")
    else:
        for i, err in enumerate(errors):
            level_color = "🔴" if err['level'] == 'error' else "🟡"
            
            with st.expander(f"{level_color} {err['message'][:80]}...", expanded=False):
                st.code(err['message'], language=None)
                
                if err['details']:
                    st.markdown("**Details:**")
                    st.code('\n'.join(err['details'][:10]), language=None)
                
                # AI Analysis button - using Gemini (cheaper & faster)
                if st.button(f"🤖 Mit AI analysieren (Gemini)", key=f"analyze_{i}"):
                    with st.spinner("Gemini analysiert den Fehler..."):
                        prompt = f"""Du bist ein Home Assistant Experte. Analysiere diesen Fehler und gib eine Lösung:

FEHLER:
{err['message']}

DETAILS:
{chr(10).join(err['details'][:20]) if err['details'] else 'Keine Details'}

Antworte auf Deutsch mit:
1. Was ist das Problem?
2. Was ist die Ursache?
3. Wie kann man es beheben? (mit konkretem YAML Code falls relevant)

Halte dich kurz und präzise.
"""
                        solution = ask_gemini(prompt)
                    
                    st.markdown("### 🤖 AI Analyse")
                    st.markdown(solution)
                    
                    # Download button for solution
                    st.download_button(
                        label="💾 Lösung als Datei speichern",
                        data=solution,
                        file_name=f"fix_{i}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                        mime="text/markdown"
                    )

# ============================================
# PAGE: 48H ANALYST
# ============================================
elif page == "📈 48h Analyst":
    st.title("📈 48h Analyst")
    st.markdown("Analysiere Sensor-Daten der letzten 48 Stunden auf Ineffizienzen")
    
    # Model selection
    col1, col2 = st.columns([2, 3])
    with col1:
        ai_model = st.selectbox(
            "🤖 AI Modell wählen",
            ["Gemini Flash (günstig)", "Claude (besser)"],
            help="Gemini ist ~10x günstiger, Claude liefert tiefere Analysen"
        )
    
    with col2:
        if "Gemini" in ai_model:
            st.info("💰 Gemini Flash: ~0.001€ pro Analyse")
        else:
            st.warning("💎 Claude: ~0.02€ pro Analyse (bessere Qualität)")
    
    st.markdown("---")
    
    # Analysis trigger
    if st.button("🚀 Analyse starten", type="primary", use_container_width=False):
        with st.spinner("Sammle Daten und analysiere mit AI..."):
            # Get current states
            states = get_ha_states()
            
            # Prepare data summary
            summary_data = {
                'lights': [],
                'climate': [],
                'sensors': [],
                'binary_sensors': [],
                'switches': []
            }
            
            for entity in states:
                eid = entity.get('entity_id', '')
                state = entity.get('state', '')
                attrs = entity.get('attributes', {})
                
                if eid.startswith('light.'):
                    summary_data['lights'].append({
                        'id': eid,
                        'state': state,
                        'brightness': attrs.get('brightness', 'N/A')
                    })
                elif eid.startswith('climate.'):
                    summary_data['climate'].append({
                        'id': eid,
                        'state': state,
                        'current_temp': attrs.get('current_temperature'),
                        'target_temp': attrs.get('temperature'),
                        'hvac_action': attrs.get('hvac_action')
                    })
                elif eid.startswith('sensor.') and 'temperature' in eid.lower():
                    summary_data['sensors'].append({
                        'id': eid,
                        'state': state,
                        'unit': attrs.get('unit_of_measurement', '')
                    })
                elif eid.startswith('binary_sensor.') and ('window' in eid.lower() or 'door' in eid.lower()):
                    summary_data['binary_sensors'].append({
                        'id': eid,
                        'state': state
                    })
            
            # Build prompt
            prompt = f"""Analysiere diese Home Assistant Daten auf Ineffizienzen und Optimierungspotential.

AKTUELLE ZEIT: {datetime.now().strftime('%Y-%m-%d %H:%M')}

LICHTER ({len(summary_data['lights'])} Stück):
{json.dumps(summary_data['lights'][:20], indent=2)}

KLIMAGERÄTE ({len(summary_data['climate'])} Stück):
{json.dumps(summary_data['climate'], indent=2)}

TEMPERATUR-SENSOREN:
{json.dumps(summary_data['sensors'][:15], indent=2)}

FENSTER/TÜR-SENSOREN:
{json.dumps(summary_data['binary_sensors'][:15], indent=2)}

Gib mir MAXIMAL 20 konkrete Verbesserungsvorschläge auf Deutsch. Fokussiere auf:
1. Energieverschwendung (Lichter an wenn nicht nötig, Heizung bei offenem Fenster)
2. Automations-Konflikte
3. Fehlende Automationen die Sinn machen würden
4. Sensor-Anomalien

Format: Nummerierte Liste mit kurzer Erklärung und konkreter Handlungsempfehlung.
"""
            
            # Use selected AI model
            if "Gemini" in ai_model:
                analysis = ask_gemini(prompt)
            else:
                analysis = ask_claude(prompt)
            
            st.session_state.analysis_results = analysis
            st.session_state.last_analysis = datetime.now().strftime('%Y-%m-%d %H:%M')
    
    # Show results
    if st.session_state.analysis_results:
        st.markdown("---")
        st.subheader("📋 Analyse-Ergebnisse")
        st.markdown(st.session_state.analysis_results)
        
        # Download
        st.download_button(
            label="💾 Analyse speichern",
            data=st.session_state.analysis_results,
            file_name=f"analyse_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
            mime="text/markdown"
        )

# ============================================
# PAGE: ARCHITECT
# ============================================
elif page == "🏗️ Architect":
    st.title("🏗️ Architect")
    st.markdown("Erstelle Custom Automations mit AI-Unterstützung")
    
    st.markdown("---")
    
    # Load entities for context
    if st.button("📥 Entitäten laden"):
        with st.spinner("Lade Entitäten..."):
            st.session_state.ha_cache = get_ha_states()
        st.success(f"{len(st.session_state.ha_cache)} Entitäten geladen")
    
    # Show available entities
    entities = st.session_state.ha_cache or []
    if entities:
        with st.expander("📋 Verfügbare Entitäten anzeigen"):
            domains = {}
            for e in entities:
                domain = e.get('entity_id', '').split('.')[0]
                if domain not in domains:
                    domains[domain] = []
                domains[domain].append(e.get('entity_id'))
            
            for domain in sorted(domains.keys()):
                st.markdown(f"**{domain}** ({len(domains[domain])})")
                st.code(', '.join(sorted(domains[domain])[:20]))
    
    st.markdown("---")
    
    # User request
    st.subheader("💭 Was möchtest du automatisieren?")
    
    user_request = st.text_area(
        "Beschreibe deine gewünschte Automation",
        placeholder="Beispiel: Ich möchte, dass das Licht im Flur automatisch angeht wenn Bewegung erkannt wird, aber nur zwischen 18:00 und 8:00 Uhr und nur wenn es dunkel ist.",
        height=120
    )
    
    output_type = st.selectbox(
        "Gewünschtes Output-Format",
        ["Home Assistant Automation (YAML)", "Node-RED Flow (JSON)", "Python Script", "Dashboard Card (YAML)"]
    )
    
    if st.button("🤖 Automation generieren", type="primary"):
        if not user_request:
            st.error("Bitte beschreibe zuerst deine gewünschte Automation!")
        else:
            with st.spinner("Claude erstellt deine Automation..."):
                # Build context
                entity_list = [e.get('entity_id') for e in entities[:100]]
                
                prompt = f"""Erstelle eine Home Assistant Automation basierend auf dieser Anfrage:

ANFRAGE:
{user_request}

GEWÜNSCHTES FORMAT: {output_type}

VERFÜGBARE ENTITÄTEN (Auswahl):
{json.dumps(entity_list, indent=2)}

Antworte auf Deutsch mit:
1. Kurze Erklärung was die Automation macht
2. Der komplette Code im gewünschten Format
3. Installationshinweise (wo einfügen, was beachten)

Nutze wenn möglich die verfügbaren Entitäten. Falls spezifische Entitäten benötigt werden die nicht in der Liste sind, weise darauf hin.
"""
                
                result = call_claude(prompt, system_prompt="Du bist ein Home Assistant Automation-Experte. Erstelle sauberen, funktionierenden Code mit Best Practices.")
                
                st.markdown("---")
                st.subheader("✅ Generierte Automation")
                st.markdown(result)
                
                # Download
                file_ext = "yaml" if "YAML" in output_type else "json" if "JSON" in output_type else "py"
                st.download_button(
                    label="💾 Code herunterladen",
                    data=result,
                    file_name=f"automation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{file_ext}",
                    mime="text/plain"
                )

# ============================================
# FOOTER
# ============================================
st.markdown("---")
st.caption("Smart Home AI Center v0.2.0 | Powered by Claude AI & Home Assistant")
