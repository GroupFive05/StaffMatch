import os
import streamlit as st
import requests
import plotly.graph_objects as go

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

st.set_page_config(
    page_title="AI Practice Advisory — Accenture Italy",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    /* ── FONT ── */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    /* ── SIDEBAR ── */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0a0a0a 0%, #1a1a2e 100%) !important;
    }
    /* nasconde la linea nativa Streamlit tra sidebar e main */
    [data-testid="stSidebarContent"] { border-right: none !important; }
    section[data-testid="stSidebar"] + div { border-left: none !important; box-shadow: none !important; }
    [data-testid="stSidebar"] .stMarkdown p,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] .stCaption { color: #aaaaaa !important; }
    [data-testid="stSidebar"] .stButton > button {
        background-color: transparent !important;
        color: #cccccc !important;
        border: none !important;
        border-radius: 8px !important;
        text-align: left !important;
        font-weight: 400 !important;
        padding: 8px 12px !important;
        transition: all 0.2s ease !important;
    }
    [data-testid="stSidebar"] .stButton > button:hover {
        background: linear-gradient(90deg, #A100FF22, #A100FF44) !important;
        color: #ffffff !important;
        border-left: 3px solid #A100FF !important;
        padding-left: 15px !important;
    }

    /* ── MAIN AREA ── */
    .main .block-container { padding-top: 2rem; padding-bottom: 2rem; max-width: 1200px; }
    .stApp { background: var(--background-color); }

    /* ── TITOLI PAGINA ── */
    .main-title {
        color: var(--text-color);
        font-size: 1.8rem;
        font-weight: 800;
        margin-bottom: 0;
        letter-spacing: -0.5px;
    }
    .sub-title { color: #888; font-size: 0.85rem; margin-top: 2px; }

    /* ── LOGIN ── */
    .login-app-title {
        color: #A100FF;
        font-size: 2.2rem;
        font-weight: 900;
        letter-spacing: -1px;
        margin: 0 0 0.2rem 0;
        line-height: 1.1;
    }
    .login-sub1 { color: #444; font-size: 0.88rem; font-weight: 500; margin: 0; }
    .login-sub2 { color: #999; font-size: 0.78rem; margin: 0.15rem 0 0 0; }

    /* ── COCKPIT FIXED HEADER (top-left main area) ── */
    #sm-cockpit-header {
        position: fixed; top: 0; left: 22rem; z-index: 9998;
        height: 3.75rem;
        display: flex; align-items: center; padding-left: 0.5rem;
    }
    #sm-cockpit-header .sm-cockpit-name {
        font-size: 2.2rem; font-weight: 900;
        color: #A100FF !important; white-space: nowrap; letter-spacing: -1px;
    }
    .page-header {
        background: white;
        border-radius: 16px;
        padding: 1.2rem 1.5rem;
        margin-bottom: 1.5rem;
        border-left: 4px solid #A100FF;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    }

    /* ── METRIC CARDS ── */
    div[data-testid="metric-container"] {
        background: white !important;
        border-radius: 16px !important;
        padding: 1.2rem 1.5rem !important;
        border: none !important;
        box-shadow: 0 4px 16px rgba(0,0,0,0.08) !important;
        transition: transform 0.2s ease, box-shadow 0.2s ease !important;
    }
    div[data-testid="metric-container"]:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 24px rgba(161,0,255,0.12) !important;
    }
    div[data-testid="metric-container"] label {
        color: #888 !important;
        font-size: 0.8rem !important;
        font-weight: 500 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
    }
    div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
        color: #1a1a2e !important;
        font-size: 2.2rem !important;
        font-weight: 800 !important;
    }

    /* ── CONTAINERS / CARDS ── */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background: white !important;
        border-radius: 16px !important;
        border: 1px solid #eee !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05) !important;
        transition: box-shadow 0.2s ease !important;
    }
    div[data-testid="stVerticalBlockBorderWrapper"]:hover {
        box-shadow: 0 4px 16px rgba(161,0,255,0.08) !important;
    }

    /* ── EXPANDERS ── */
    div[data-testid="stExpander"] {
        background: white !important;
        border-radius: 12px !important;
        border: 1px solid #eee !important;
        margin-bottom: 8px !important;
        overflow: hidden !important;
        box-shadow: 0 1px 4px rgba(0,0,0,0.04) !important;
    }
    div[data-testid="stExpander"]:hover {
        border-color: #A100FF44 !important;
        box-shadow: 0 2px 12px rgba(161,0,255,0.08) !important;
    }
    div[data-testid="stExpander"] summary {
        font-weight: 600 !important;
        padding: 12px 16px !important;
    }

    /* ── BUTTONS ── */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #A100FF, #7B00CC) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        padding: 10px 20px !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 4px 12px rgba(161,0,255,0.3) !important;
    }
    .stButton > button[kind="primary"]:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 6px 20px rgba(161,0,255,0.4) !important;
    }
    .stButton > button:not([kind="primary"]) {
        border-radius: 8px !important;
        border: 1px solid #ddd !important;
        font-weight: 500 !important;
        transition: all 0.2s ease !important;
    }
    .stButton > button:not([kind="primary"]):hover {
        border-color: #A100FF !important;
        color: #A100FF !important;
    }

    /* ── TABS ── */
    .stTabs [data-baseweb="tab-list"] {
        background: white !important;
        border-radius: 12px !important;
        padding: 6px !important;
        gap: 4px !important;
        border: 1px solid #eee !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05) !important;
        margin-bottom: 1rem !important;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px !important;
        font-weight: 500 !important;
        color: #666 !important;
        padding: 8px 16px !important;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #A100FF, #7B00CC) !important;
        color: white !important;
        font-weight: 600 !important;
    }

    /* ── INPUTS ── */
    .stTextInput > div > div > input,
    .stSelectbox > div > div,
    .stMultiSelect > div > div,
    .stNumberInput > div > div > input,
    .stTextArea > div > div > textarea {
        border-radius: 10px !important;
        border: 1.5px solid #e0e0e0 !important;
        transition: border-color 0.2s ease !important;
    }
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #A100FF !important;
        box-shadow: 0 0 0 3px rgba(161,0,255,0.1) !important;
    }

    /* ── PROGRESS BARS ── */
    .stProgress > div > div > div {
        background: linear-gradient(90deg, #A100FF, #7B00CC) !important;
        border-radius: 999px !important;
    }
    .stProgress > div > div {
        border-radius: 999px !important;
        background: rgba(161,0,255,0.15) !important;
    }
    /* testo percentuale visibile in dark mode */
    [data-testid="stProgress"] p,
    [data-testid="stProgress"] span,
    .stProgress p, .stProgress span { color: var(--text-color) !important; }

    /* ── ALERTS ── */
    div[data-testid="stAlert"] {
        border-radius: 12px !important;
        border: none !important;
    }

    /* ── DIVIDER ── */
    hr { border-color: #eee !important; margin: 1rem 0 !important; }

    /* ── SCROLLBAR ── */
    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: #f1f1f1; border-radius: 3px; }
    ::-webkit-scrollbar-thumb { background: #A100FF66; border-radius: 3px; }
    ::-webkit-scrollbar-thumb:hover { background: #A100FF; }

    /* area input chat: occupa tutta la larghezza disponibile */
    [data-testid="stBottom"] { padding: 1rem 0 1.5rem 0 !important; }
    [data-testid="stChatInput"] {
        border-radius: 16px !important;
        border: 1.5px solid rgba(161,0,255,0.3) !important;
        box-shadow: 0 4px 20px rgba(161,0,255,0.12) !important;
    }
    [data-testid="stChatInput"] textarea {
        min-height: 80px !important;
        padding: 1rem 1.2rem !important;
        font-size: 0.95rem !important;
        line-height: 1.5 !important;
    }
    [data-testid="stChatMessage"] {
        background: var(--background-color) !important;
        border-radius: 12px !important;
        border: 1px solid rgba(161,0,255,0.15) !important;
        margin-bottom: 8px !important;
    }
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
        background: var(--secondary-background-color) !important;
        border-color: rgba(161,0,255,0.3) !important;
    }
    [data-testid="stChatMessageContent"] p,
    [data-testid="stChatMessageContent"] span,
    [data-testid="stChatMessageContent"] li,
    [data-testid="stChatMessageContent"] td,
    [data-testid="stChatMessageContent"] th,
    [data-testid="stChatMessage"] p,
    [data-testid="stChatMessage"] span,
    [data-testid="stChatMessage"] li { color: var(--text-color) !important; }
    [data-testid="stChatMessage"] strong { color: #A100FF !important; }
    [data-testid="stChatInput"] textarea {
        border-radius: 12px !important;
        border: 1.5px solid rgba(161,0,255,0.3) !important;
        color: var(--text-color) !important;
    }
    [data-testid="stChatInput"] textarea:focus {
        border-color: #A100FF !important;
        box-shadow: 0 0 0 3px rgba(161,0,255,0.1) !important;
    }
</style>
""", unsafe_allow_html=True)

# ── session state ──────────────────────────────────────────────────────────────
for k in ["token", "user", "page", "match_opp_id"]:
    if k not in st.session_state:
        st.session_state[k] = None

# ── helpers ────────────────────────────────────────────────────────────────────
def api(method: str, endpoint: str, **kwargs):
    headers = kwargs.pop("headers", {})
    if st.session_state.token:
        headers["Authorization"] = f"Bearer {st.session_state.token}"
    try:
        return requests.request(method, f"{BACKEND_URL}{endpoint}",
                                headers=headers, timeout=60, **kwargs)
    except requests.exceptions.ConnectionError:
        st.error(f"Backend non raggiungibile ({BACKEND_URL}).")
        return None
    except Exception as _e:
        st.error(f"Errore chiamata API: {type(_e).__name__}: {_e}")
        return None

def get_groups():
    if not st.session_state.user:
        return []
    if "cached_groups" in st.session_state:
        return st.session_state.cached_groups
    groups = st.session_state.user.get("gruppi", [])
    st.session_state.cached_groups = groups
    return groups

def can_write(groups):
    return any(g in groups for g in ["Manager", "Executive", "Administrator"])

def is_executive_or_admin(groups):
    return any(g in groups for g in ["Executive", "Administrator"])

def is_admin(groups):
    return "Administrator" in groups

def nav(page: str):
    st.session_state.page = page
    st.rerun()

# ── LOGIN ──────────────────────────────────────────────────────────────────────
def show_login():
    _, col, _ = st.columns([1, 2, 1])
    with col:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown('<p class="login-app-title">D&amp;A Advisory Cockpit</p>', unsafe_allow_html=True)
        st.markdown(
            '<p class="login-sub1">Intelligent Staffing &amp; Practice Management Platform</p>'
            '<p class="login-sub2">D&amp;A Practice · Accenture Italy · Powered by SAP AI Core &amp; Claude</p>',
            unsafe_allow_html=True
        )
        st.markdown("<br>", unsafe_allow_html=True)

        with st.form("login"):
            email    = st.text_input("Email aziendale", placeholder="nome.cognome@accenture.com")
            password = st.text_input("Password", type="password")
            ok       = st.form_submit_button("Accedi →", use_container_width=True, type="primary")

        if ok:
            if not email or not password:
                st.error("Inserisci email e password.")
                return
            resp = api("POST", "/auth/login", json={"email": email, "password": password})
            if resp is None:
                return
            if resp.status_code == 200:
                data = resp.json()
                st.session_state.token = data["access_token"]
                me = api("GET", "/auth/me")
                if me and me.status_code == 200:
                    st.session_state.user = me.json()
                st.session_state.page = "dashboard"
                st.session_state.pop("cached_groups", None)
                st.rerun()
            else:
                st.error("Credenziali non valide.")

# ── SIDEBAR ────────────────────────────────────────────────────────────────────
def show_sidebar(groups):
    with st.sidebar:
        st.markdown("## 🎯 AI Practice Advisory")
        u = st.session_state.user or {}

        # Header fisso in alto a destra — nome + Logout allineati con ⋮
        nome_hdr = u.get('nome', '')
        cognome_hdr = u.get('cognome', '')
        st.markdown(f"""
<style>
#sm-userbar {{
    background: rgba(161,0,255,0.08);
    border-radius: 8px;
    padding: 8px 12px;
    margin: 0 0 0.75rem 0;
    display: flex; align-items: center; justify-content: space-between;
}}
#sm-userbar .sm-name {{
    font-size: 0.78rem; font-weight: 600;
    color: #aaaaaa; white-space: nowrap;
}}
#sm-userbar .sm-exit {{
    font-size: 0.70rem; color: #A100FF;
    border: 1px solid #A100FF; border-radius: 6px;
    padding: 2px 8px; background: transparent; cursor: pointer;
    transition: all 0.2s ease; line-height: 1;
    text-decoration: none; display: inline-flex; align-items: center;
}}
#sm-userbar .sm-exit:hover {{ background: #A100FF; color: white; }}
</style>
<div id="sm-userbar">
  <span class="sm-name">{nome_hdr} {cognome_hdr}</span>
  <a href="?logout=1" class="sm-exit">Logout</a>
</div>
<div id="sm-cockpit-header">
  <span class="sm-cockpit-name">D&amp;A Advisory Cockpit</span>
</div>
""", unsafe_allow_html=True)

        pages = [
            ("🧑‍💻", "Risorse",      "risorsa_v2"),
            ("📊", "Dashboard ",    "dashboard_v2"),
            ("🗂", "Gestione Staffing ", "staffing_management_v2"),
            ("🧪", "Matching AI v2",  "matching_v2"),
            ("✨", "Practice Advisor", "chatbot"),
        ]
        if is_executive_or_admin(groups):
            pages.append(("📋", "Approvazioni", "approvazioni"))
        if is_admin(groups):
            pages.append(("⚙️", "Amministrazione", "admin"))

        for icon, label, key in pages:
            active = "→ " if st.session_state.page == key else "   "
            if st.button(f"{active}{icon} {label}", use_container_width=True, key=f"nav_{key}"):
                st.session_state.page = key
                st.rerun()

# ── DASHBOARD ──────────────────────────────────────────────────────────────────
def show_dashboard(groups):
    st.markdown('<p class="main-title">🏠 D&amp;A Practice Overview</p>', unsafe_allow_html=True)
    st.markdown("---")

    r_res  = api("GET", "/resources/")
    r_proj = api("GET", "/projects/")
    r_opp  = api("GET", "/opportunities/")

    resources    = r_res.json()  if r_res  and r_res.status_code  == 200 else []
    projects     = r_proj.json() if r_proj and r_proj.status_code == 200 else []
    opportunities= r_opp.json()  if r_opp  and r_opp.status_code  == 200 else []

    active_proj  = [p for p in projects     if p.get("stato") == "Active"]
    open_opp     = [o for o in opportunities if o.get("stato") == "New"]
    avail_res    = [r for r in resources     if r.get("disponibilita_percentuale", 0) >= 50]

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("👥 Risorse GDL",       len(resources))
    c2.metric("📁 Progetti Attivi",   len(active_proj))
    c3.metric("🎯 Opportunity Aperte",len(open_opp))
    c4.metric("✅ Alta Disponibilità", len(avail_res))

    st.markdown("---")
    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("### 🎯 Opportunity Aperte")
        if open_opp:
            for o in open_opp[:5]:
                with st.container(border=True):
                    st.markdown(f"**{o.get('titolo','')}**")
                    st.caption(f"Cliente: {o.get('cliente','')}  |  Inizio: {o.get('data_inizio','')}")
                    skills_req = o.get("skill_richieste", [])
                    if skills_req:
                        ids = [s.get("skill_id","") for s in skills_req[:3]]
                        st.caption("Skills: " + ", ".join(ids))
        else:
            st.info("Nessuna opportunity aperta.")

    with col_b:
        st.markdown("### 👥 Top Disponibilità")
        sorted_res = sorted(resources, key=lambda r: r.get("disponibilita_percentuale", 0), reverse=True)
        for r in sorted_res[:6]:
            disp = int(r.get("disponibilita_percentuale", 0))
            c_name, c_prog = st.columns([2, 3])
            with c_name:
                st.markdown(f"**{r.get('nome','')} {r.get('cognome','')}**")
                st.caption(r.get("ruolo_nome", ""))
            with c_prog:
                color = "normal" if disp >= 50 else "off"
                st.progress(disp / 100, text=f"{disp}%")

# ── RISORSE ────────────────────────────────────────────────────────────────────
def show_risorse(groups):
    st.markdown('<p class="main-title">👥 Risorse GDL</p>', unsafe_allow_html=True)
    st.markdown("---")

    tab_labels = ["📋 Lista", "➕ Nuova Risorsa"] if can_write(groups) else ["📋 Lista"]
    tabs = st.tabs(tab_labels)

    with tabs[0]:
        resp     = api("GET", "/resources/")
        sk_resp  = api("GET", "/skills/")
        if not resp or resp.status_code != 200:
            st.error("Errore nel caricamento risorse.")
            return
        resources = resp.json()
        skill_id_map_res = {s["id"]: s["nome"] for s in (sk_resp.json() if sk_resp and sk_resp.status_code == 200 else [])}

        col_s, col_f = st.columns([3, 1])
        with col_s:
            search = st.text_input("🔍 Cerca nome/cognome")
        with col_f:
            only_avail = st.checkbox("Solo disponibili (>0%)")

        if search:
            resources = [r for r in resources
                         if search.lower() in f"{r.get('nome','')} {r.get('cognome','')}".lower()]
        if only_avail:
            resources = [r for r in resources if r.get("disponibilita_percentuale", 0) > 0]

        if not resources:
            st.info("Nessuna risorsa trovata.")
        for r in resources:
            disp = int(r.get("disponibilita_percentuale", 0))
            icon = "🟢" if disp >= 50 else ("🟡" if disp > 0 else "🔴")
            label = f"{icon} **{r.get('nome','')} {r.get('cognome','')}** — {r.get('ruolo_nome','')} · {r.get('seniority','')}"
            with st.expander(label):
                c1, c2, c3 = st.columns(3)
                with c1:
                    st.markdown(f"📧 `{r.get('email','')}`")
                    st.markdown(f"🏷 Mansione: **{r.get('ruolo_nome','')}** ({r.get('seniority','')})")
                    st.markdown(f"💶 €{r.get('costo_orario', 0):.0f}/h")
                with c2:
                    st.markdown(f"**Disponibilità: {disp}%**")
                    st.progress(disp / 100)
                    lingue = r.get("lingue", [])
                    if lingue:
                        st.caption("🌐 " + " · ".join(lingue))
                with c3:
                    skills_raw = r.get("skill_ids", [])
                    if skills_raw:
                        st.markdown("**Skills:**")
                        for sk in skills_raw:
                            if isinstance(sk, dict):
                                sk_nome = skill_id_map_res.get(sk.get("skill_id",""), sk.get("skill_id",""))
                                sk_lv   = sk.get("livello", "?")
                                st.caption(f"  • {sk_nome} — lv.**{sk_lv}**/5")

    if can_write(groups) and len(tabs) > 1:
        with tabs[1]:
            _form_crea_risorsa()

def _api_detail(r, fallback="Nessuna risposta dal backend"):
    if r is None:
        return fallback
    try:
        return r.json().get("detail", f"HTTP {r.status_code}")
    except Exception:
        return f"HTTP {r.status_code}: {r.text[:200]}"

def _form_crea_risorsa():
    import datetime as _dt
    if st.session_state.pop("cr_last_success", False):
        st.success("✅ Risorsa creata con successo!")
    if "cr_last_error" in st.session_state:
        st.error(f"Errore: {st.session_state.pop('cr_last_error')}")

    mansioni_r = api("GET", "/mansioni/")
    skills_r   = api("GET", "/skills/")
    groups_r   = api("GET", "/roles/")

    mansioni  = mansioni_r.json() if mansioni_r and mansioni_r.status_code == 200 else []
    skills    = skills_r.json()   if skills_r   and skills_r.status_code   == 200 else []
    rgroups   = groups_r.json()   if groups_r   and groups_r.status_code   == 200 else []

    mansione_map = {m["nome"]: m["id"] for m in mansioni}
    skill_map    = {s["nome"]: s["id"] for s in skills}
    group_map    = {g["nome"]: g["id"] for g in rgroups}

    c1, c2 = st.columns(2)
    with c1:
        nome  = st.text_input("Nome *", key="cr_nome")
        email = st.text_input("Email *", key="cr_email")
    with c2:
        cognome = st.text_input("Cognome *", key="cr_cognome")
        data_n  = st.date_input("Data di nascita", value=None, format="YYYY-MM-DD",
                                min_value=_dt.date(1940, 1, 1), key="cr_datanascita")

    ruolo_sel = st.selectbox("Mansione *", list(mansione_map.keys()), key="cr_mansione")

    skills_sel = st.multiselect("Skills", list(skill_map.keys()), key="cr_skills")
    if skills_sel:
        st.markdown("**Livello per ogni skill:**")
        cols_sk = st.columns(min(len(skills_sel), 3))
        for i, s in enumerate(skills_sel):
            with cols_sk[i % 3]:
                st.slider(s, 1, 5, 3, key=f"cr_slv_{s}",
                          help="1 = Base · 3 = Intermedio · 5 = Expert")

    lingue_options = ["Italiano", "Inglese", "Tedesco", "Francese", "Spagnolo"]
    if "cr_lingue" not in st.session_state:
        st.session_state["cr_lingue"] = ["Italiano", "Inglese"]
    lingue_sel = st.multiselect("Lingue", lingue_options, key="cr_lingue")

    c3, c4 = st.columns(2)
    with c3:
        group_sel = st.selectbox("Ruolo autorizzativo *", list(group_map.keys()), key="cr_gruppo")
    with c4:
        costo = st.number_input("Costo orario €/h (0 = default ruolo)", 0.0, 500.0, 0.0, key="cr_costo")

    if st.button("✅ Crea Risorsa", type="primary", use_container_width=True, key="cr_submit"):
        nome_v  = st.session_state.get("cr_nome","").strip()
        cogn_v  = st.session_state.get("cr_cognome","").strip()
        email_v = st.session_state.get("cr_email","").strip()
        if not all([nome_v, cogn_v, email_v, ruolo_sel]):
            st.error("Compila i campi obbligatori (*).")
            return
        sel_skills = st.session_state.get("cr_skills", [])
        skill_ids  = [{"skill_id": skill_map[s], "livello": st.session_state.get(f"cr_slv_{s}", 3)}
                      for s in sel_skills]
        payload = {
            "nome": nome_v, "cognome": cogn_v, "email": email_v,
            "data_nascita": str(st.session_state.get("cr_datanascita", _dt.date.today())),
            "ruolo_id": mansione_map[ruolo_sel],
            "skill_ids": skill_ids,
            "lingue": [l.lower() for l in st.session_state.get("cr_lingue", [])],
            "gruppo_ruolo_ids": [group_map[group_sel]],
        }
        costo_v = st.session_state.get("cr_costo", 0.0)
        if costo_v > 0:
            payload["costo_orario"] = costo_v
        r = api("POST", "/resources/", json=payload)
        if r and r.status_code == 201:
            for k in [k2 for k2 in list(st.session_state.keys()) if k2.startswith("cr_")]:
                del st.session_state[k]
            st.session_state["cr_last_success"] = True
            st.rerun()
        else:
            if r is None:
                detail = "Nessuna risposta dal backend"
            else:
                try:
                    detail = r.json().get("detail", f"HTTP {r.status_code}")
                except Exception:
                    detail = f"HTTP {r.status_code}: {r.text[:200]}"
            st.session_state["cr_last_error"] = detail
            st.rerun()

# ── PROGETTI ───────────────────────────────────────────────────────────────────
def show_progetti(groups):
    st.markdown('<p class="main-title">📁 Progetti</p>', unsafe_allow_html=True)
    st.markdown("---")

    tab_labels = ["📋 Lista", "➕ Nuovo Progetto"] if can_write(groups) else ["📋 Lista"]
    tabs = st.tabs(tab_labels)
    current_uid = (st.session_state.user or {}).get("id", "")

    with tabs[0]:
        resp = api("GET", "/projects/")
        if not resp or resp.status_code != 200:
            st.error("Errore nel caricamento progetti.")
            return
        projects = resp.json()
        if not projects:
            st.info("Nessun progetto presente.")

        for p in projects:
            stato   = p.get("stato", "")
            icon    = "🟢" if stato == "Active" else ("🔴" if stato == "Closed" else "🟡")
            is_owner= p.get("manager_id") == current_uid or is_admin(groups)

            with st.expander(f"{icon} **{p.get('nome','')}** — {p.get('cliente','')}  [{stato}]  ({p.get('num_risorse',0)} risorse)"):
                # dettaglio progetto
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown(f"**Stato:** {stato}")
                    st.markdown(f"**Inizio:** {p.get('data_inizio','')}")
                    st.markdown(f"**Fine prevista:** {p.get('data_fine_prevista','')}")
                with c2:
                    ref = p.get("referente_it_cliente", {})
                    if ref:
                        st.markdown(f"**Referente:** {ref.get('nome','')} {ref.get('cognome','')}")
                    desc = p.get("descrizione","")
                    if desc:
                        st.caption(desc[:160])

                # risorse allocate (carica dettaglio)
                if stato == "Active":
                    st.markdown("**Risorse allocate:**")
                    det_r = api("GET", f"/projects/{p['id']}")
                    allocs = det_r.json().get("allocazioni",[]) if det_r and det_r.status_code == 200 else []
                    res_map = {r["id"]: r for r in (api("GET","/resources/").json() if api("GET","/resources/") else [])}

                    if allocs:
                        for a in allocs:
                            r_info = res_map.get(a.get("risorsa_id",""), {})
                            r_nome = f"{r_info.get('nome','')} {r_info.get('cognome','')}"
                            ac1, ac2, ac3 = st.columns([3,2,2])
                            with ac1:
                                st.markdown(f"• **{r_nome}** — {a.get('ruolo_nel_progetto','')}")
                            with ac2:
                                st.markdown(f"📊 {a.get('percentuale',0)}%")
                            with ac3:
                                if is_owner and can_write(groups):
                                    if st.button("🔓 Rilascia", key=f"rel_{a['id']}"):
                                        pr = api("POST", f"/project-changes/propose/{p['id']}",
                                                 json={"change_type":"remove_resource",
                                                       "payload":{"allocation_id": a["id"]},
                                                       "note_manager":""})
                                        if pr and pr.status_code == 201:
                                            st.success("Richiesta di rilascio inviata all'Executive.")
                                        else:
                                            detail = _api_detail(pr)
                                            st.error(f"Errore: {detail}")
                    else:
                        st.caption("Nessuna risorsa allocata.")

                    # aggiungi risorsa
                    if is_owner and can_write(groups):
                        with st.expander("➕ Proponi aggiunta risorsa"):
                            res_resp2 = api("GET", "/resources/")
                            all_res = res_resp2.json() if res_resp2 and res_resp2.status_code == 200 else []
                            allocated_ids = {a.get("risorsa_id") for a in allocs}
                            free_res = [r for r in all_res if r["id"] not in allocated_ids]
                            if free_res:
                                res_opts = {f"{r['nome']} {r['cognome']} ({r.get('ruolo_nome','')})": r["id"] for r in free_res}
                                with st.form(f"add_res_{p['id']}"):
                                    sel_res   = st.selectbox("Risorsa", list(res_opts.keys()))
                                    perc      = st.slider("Percentuale allocazione", 10, 100, 50, 10)
                                    ruolo_prj = st.text_input("Ruolo nel progetto", value="Consultant")
                                    note_add  = st.text_input("Note (opzionale)")
                                    if st.form_submit_button("📤 Proponi", type="primary"):
                                        proj_det = api("GET", f"/projects/{p['id']}")
                                        d_ini = proj_det.json().get("data_inizio","") if proj_det else ""
                                        d_fin = proj_det.json().get("data_fine_prevista","") if proj_det else ""
                                        pr = api("POST", f"/project-changes/propose/{p['id']}",
                                                 json={"change_type":"add_resource",
                                                       "payload":{"risorsa_id": res_opts[sel_res],
                                                                  "percentuale": perc,
                                                                  "data_inizio": d_ini,
                                                                  "data_fine": d_fin,
                                                                  "ruolo_nel_progetto": ruolo_prj},
                                                       "note_manager": note_add})
                                        if pr and pr.status_code == 201:
                                            st.success("Richiesta inviata all'Executive!")
                                        else:
                                            detail = _api_detail(pr)
                                            st.error(f"Errore: {detail}")

                        # modifica info progetto
                        with st.expander("✏️ Proponi modifica info progetto"):
                            with st.form(f"edit_prj_{p['id']}"):
                                new_nome  = st.text_input("Nome", value=p.get("nome",""))
                                new_cli   = st.text_input("Cliente", value=p.get("cliente",""))
                                new_fine  = st.text_input("Data fine (YYYY-MM-DD)", value=p.get("data_fine_prevista",""))
                                new_desc  = st.text_area("Descrizione", value=p.get("descrizione",""))
                                note_edit = st.text_input("Note per l'Executive (opzionale)")
                                if st.form_submit_button("📤 Proponi modifica", type="primary"):
                                    pr = api("POST", f"/project-changes/propose/{p['id']}",
                                             json={"change_type":"update_info",
                                                   "payload":{"nome":new_nome,"cliente":new_cli,
                                                              "data_fine_prevista":new_fine,
                                                              "descrizione":new_desc},
                                                   "note_manager": note_edit})
                                    if pr and pr.status_code == 201:
                                        st.success("Richiesta di modifica inviata all'Executive!")
                                    else:
                                        detail = _api_detail(pr)
                                        st.error(f"Errore: {detail}")

    if can_write(groups) and len(tabs) > 1:
        with tabs[1]:
            _form_crea_progetto()

def _form_crea_progetto():
    skills_r = api("GET", "/skills/")
    skills   = skills_r.json() if skills_r and skills_r.status_code == 200 else []
    skill_map = {s["nome"]: s["id"] for s in skills}
    manager_id = (st.session_state.user or {}).get("id", "")

    with st.form("form_progetto", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            nome          = st.text_input("Nome progetto *")
            cliente       = st.text_input("Cliente *")
            ref_nome      = st.text_input("Referente cliente — Nome")
            data_inizio   = st.date_input("Data inizio")
        with c2:
            skill_princ   = st.selectbox("Skill principale *", list(skill_map.keys()))
            skill_sec     = st.multiselect("Skills secondarie", list(skill_map.keys()))
            ref_cognome   = st.text_input("Referente cliente — Cognome")
            data_fine     = st.date_input("Data fine prevista")

        descrizione = st.text_area("Descrizione")

        if st.form_submit_button("✅ Crea Progetto", type="primary", use_container_width=True):
            if not all([nome, cliente]):
                st.error("Compila i campi obbligatori (*).")
                return
            payload = {
                "nome": nome, "cliente": cliente,
                "referente_it_cliente": {"nome": ref_nome, "cognome": ref_cognome},
                "manager_id": manager_id,
                "skill_principale_id": skill_map.get(skill_princ, ""),
                "skill_secondarie_ids": [skill_map[s] for s in skill_sec],
                "data_inizio": str(data_inizio),
                "data_fine_prevista": str(data_fine),
                "descrizione": descrizione,
            }
            r = api("POST", "/projects/", json=payload)
            if r and r.status_code == 201:
                st.success("✅ Progetto creato!")
            else:
                detail = _api_detail(r)
                st.error(f"Errore: {detail}")

# ── OPPORTUNITY ────────────────────────────────────────────────────────────────
def show_opportunity(groups):
    st.markdown('<p class="main-title">🎯 Opportunity</p>', unsafe_allow_html=True)
    st.markdown("---")

    tab_labels = ["📋 Lista", "➕ Nuova Opportunity"] if can_write(groups) else ["📋 Lista"]
    tabs = st.tabs(tab_labels)

    with tabs[0]:
        resp      = api("GET", "/opportunities/")
        mans_resp = api("GET", "/mansioni/")
        res_resp  = api("GET", "/resources/")
        mr_resp   = api("GET", "/match/all/results") if False else None  # placeholder
        if not resp or resp.status_code != 200:
            st.error("Errore nel caricamento opportunity.")
            return
        opportunities  = resp.json()
        mans_map       = {m["id"]: m["nome"] for m in (mans_resp.json() if mans_resp and mans_resp.status_code == 200 else [])}
        res_name_map   = {r["id"]: f"{r.get('nome','')} {r.get('cognome','')}" for r in (res_resp.json() if res_resp and res_resp.status_code == 200 else [])}
        if not opportunities:
            st.info("Nessuna opportunity presente.")

        current_uid = (st.session_state.user or {}).get("id", "")

        for o in opportunities:
            stato = o.get("stato","")
            icon  = "🟢" if stato == "New" else ("🔵" if stato == "Active" else ("🟡" if stato == "Pending" else "🔴"))
            is_owner = o.get("manager_id") == current_uid or is_admin(groups)

            # carica risultati matching per questa opportunity (solo se esistono)
            slots = o.get("slot_risorse", [])
            confirmed_per_slot = {}  # slot_index → (risorsa_id, risorsa_nome)
            mr = api("GET", f"/match/{o['id']}/results")
            if mr and mr.status_code == 200:
                for sl_data in mr.json().get("slots", []):
                    for cand in sl_data.get("candidates", []):
                        if cand.get("stato") == "Confirmed":
                            sidx = sl_data["slot_index"]
                            confirmed_per_slot[sidx] = cand.get("risorsa_nome", "?")
                            break

            n_confirmed  = len(confirmed_per_slot)
            n_slots_tot  = len(slots)
            match_badge  = f"  ✅ {n_confirmed}/{n_slots_tot} slot confermati" if confirmed_per_slot else ""

            with st.expander(f"{icon} **{o.get('titolo','')}** — {o.get('cliente','')}  [{stato}]{match_badge}"):
                # ── dettaglio ──
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown(f"**Inizio:** {o.get('data_inizio','')}")
                    st.markdown(f"**Fine prevista:** {o.get('data_fine_prevista','')}")
                    st.markdown(f"**Risorse richieste:** {n_slots_tot}")
                    for idx, sl in enumerate(slots, 1):
                        mn      = mans_map.get(sl.get("mansione_id",""), sl.get("mansione_id",""))
                        conf_nm = confirmed_per_slot.get(idx - 1)
                        slot_lbl = f"  Slot {idx}: {mn} — {sl.get('percentuale_allocazione','')}%"
                        if conf_nm:
                            st.caption(f"{slot_lbl}  ✅ *{conf_nm}*")
                        else:
                            st.caption(slot_lbl)
                with c2:
                    for s in o.get("skill_richieste", []):
                        st.markdown(f"  • `{s.get('skill_id','')}` lv.{s.get('livello_minimo','')}")
                    desc = o.get("descrizione","")
                    if desc:
                        st.caption(desc[:160])

                # ── azioni ──
                if can_write(groups):
                    action_cols = st.columns(4)
                    with action_cols[0]:
                        if stato == "New" and st.button("🤖 Matching AI", key=f"goto_match_{o['id']}"):
                            st.session_state.match_opp_id = o["id"]
                            st.session_state.page = "matching"
                            st.rerun()
                    with action_cols[1]:
                        if stato in ("New", "Active"):
                            if st.button("📤 Richiedi Promozione", key=f"promo_{o['id']}"):
                                r = api("POST", f"/promotions/request/{o['id']}")
                                if r and r.status_code == 201:
                                    st.success("✅ Richiesta inviata!")
                                    st.rerun()
                                else:
                                    detail = _api_detail(r)
                                    st.error(f"Errore: {detail}")
                        elif stato == "Pending":
                            st.info("⏳ Approvazione in corso")
                    with action_cols[2]:
                        if is_owner and stato in ("New", "Active"):
                            if st.button("✏️ Modifica", key=f"edit_opp_{o['id']}"):
                                st.session_state[f"editing_opp_{o['id']}"] = True
                                st.rerun()
                    with action_cols[3]:
                        if is_owner and stato == "New":
                            if st.button("🗑️ Elimina", key=f"del_opp_{o['id']}"):
                                st.session_state[f"confirm_del_opp_{o['id']}"] = True
                                st.rerun()

                    # ── form eliminazione ──
                    if st.session_state.get(f"confirm_del_opp_{o['id']}"):
                        st.warning("Confermi l'eliminazione di questa opportunity?")
                        cc1, cc2 = st.columns(2)
                        with cc1:
                            if st.button("Sì, elimina", key=f"yes_del_{o['id']}", type="primary"):
                                r = api("DELETE", f"/opportunities/{o['id']}")
                                if r and r.status_code == 204:
                                    st.session_state.pop(f"confirm_del_opp_{o['id']}", None)
                                    st.rerun()
                                else:
                                    detail = _api_detail(r)
                                    st.error(f"Errore: {detail}")
                        with cc2:
                            if st.button("Annulla", key=f"no_del_{o['id']}"):
                                st.session_state.pop(f"confirm_del_opp_{o['id']}", None)
                                st.rerun()

                    # ── form modifica ──
                    if st.session_state.get(f"editing_opp_{o['id']}"):
                        st.markdown("#### ✏️ Modifica Opportunity")
                        skills_r  = api("GET", "/skills/")
                        mans_r2   = api("GET", "/mansioni/")
                        skills    = skills_r.json() if skills_r and skills_r.status_code == 200 else []
                        mansioni  = mans_r2.json() if mans_r2 and mans_r2.status_code == 200 else []
                        skill_map = {s["nome"]: s["id"] for s in skills}
                        skill_id_to_nome = {s["id"]: s["nome"] for s in skills}
                        mans_options = [m["nome"] for m in mansioni]
                        mans_id_map  = {m["nome"]: m["id"] for m in mansioni}

                        cur_slots = o.get("slot_risorse", [])
                        nslots_key = f"edit_nslots_{o['id']}"
                        if nslots_key not in st.session_state:
                            st.session_state[nslots_key] = len(cur_slots) or 1
                        n_edit_slots = st.number_input(
                            "Numero di risorse (slot)", 1, 10,
                            key=nslots_key
                        )

                        with st.form(f"form_edit_opp_{o['id']}"):
                            ec1, ec2 = st.columns(2)
                            with ec1:
                                new_titolo  = st.text_input("Titolo", value=o.get("titolo",""))
                                new_cliente = st.text_input("Cliente", value=o.get("cliente",""))
                                new_inizio  = st.text_input("Data inizio (YYYY-MM-DD)", value=o.get("data_inizio",""))
                            with ec2:
                                new_fine    = st.text_input("Data fine (YYYY-MM-DD)", value=o.get("data_fine_prevista",""))

                            st.markdown("**Composizione team richiesto:**")
                            for si in range(int(n_edit_slots)):
                                sc1, sc2 = st.columns(2)
                                prev_slot = cur_slots[si] if si < len(cur_slots) else {}
                                prev_mans = mans_map.get(prev_slot.get("mansione_id",""), mans_options[0] if mans_options else "")
                                prev_perc = prev_slot.get("percentuale_allocazione", 100)
                                with sc1:
                                    m_idx = mans_options.index(prev_mans) if prev_mans in mans_options else 0
                                    st.selectbox(f"Mansione — Risorsa {si+1}", mans_options, index=m_idx, key=f"eopp_m_{o['id']}_{si}")
                                with sc2:
                                    st.slider(f"Allocazione % — Risorsa {si+1}", 10, 100, int(prev_perc), 10, key=f"eopp_p_{o['id']}_{si}")

                            cur_skills = [skill_id_to_nome.get(s.get("skill_id",""), s.get("skill_id",""))
                                          for s in o.get("skill_richieste",[])]
                            new_skills = st.multiselect("Skills richieste", list(skill_map.keys()), default=[s for s in cur_skills if s in skill_map])
                            new_lv     = st.slider("Livello minimo skills", 1, 5, 3)
                            new_desc   = st.text_area("Descrizione", value=o.get("descrizione",""))

                            c_save, c_cancel = st.columns(2)
                            with c_save:
                                save = st.form_submit_button("💾 Salva", type="primary", use_container_width=True)
                            with c_cancel:
                                cancel = st.form_submit_button("Annulla", use_container_width=True)

                            if save:
                                new_slots = [
                                    {
                                        "mansione_id": mans_id_map.get(st.session_state.get(f"eopp_m_{o['id']}_{si}", mans_options[0] if mans_options else ""), ""),
                                        "percentuale_allocazione": st.session_state.get(f"eopp_p_{o['id']}_{si}", 100),
                                    }
                                    for si in range(int(n_edit_slots))
                                ]
                                payload = {
                                    "titolo": new_titolo, "cliente": new_cliente,
                                    "data_inizio": new_inizio, "data_fine_prevista": new_fine,
                                    "descrizione": new_desc,
                                    "skill_richieste": [{"skill_id": skill_map[s], "livello_minimo": new_lv} for s in new_skills],
                                    "slot_risorse": new_slots,
                                }
                                r = api("PATCH", f"/opportunities/{o['id']}", json=payload)
                                if r and r.status_code == 200:
                                    st.session_state.pop(f"editing_opp_{o['id']}", None)
                                    st.session_state.pop(nslots_key, None)
                                    st.rerun()
                                else:
                                    detail = _api_detail(r)
                                    st.error(f"Errore: {detail}")
                            if cancel:
                                st.session_state.pop(f"editing_opp_{o['id']}", None)
                                st.session_state.pop(nslots_key, None)
                                st.rerun()

    if can_write(groups) and len(tabs) > 1:
        with tabs[1]:
            _form_crea_opportunity()

def _form_crea_opportunity():
    skills_r  = api("GET", "/skills/")
    mans_r    = api("GET", "/mansioni/")
    skills    = skills_r.json() if skills_r and skills_r.status_code == 200 else []
    mansioni  = mans_r.json()   if mans_r   and mans_r.status_code   == 200 else []
    skill_map = {s["nome"]: s["id"] for s in skills}
    mans_options = [m["nome"] for m in mansioni]
    mans_id_map  = {m["nome"]: m["id"] for m in mansioni}
    manager_id   = (st.session_state.user or {}).get("id", "")

    import datetime as _dt2

    n_slots = st.number_input(
        "Numero di risorse necessarie", 1, 10, 1, key="nopp_nslots",
        help="Definisce quanti slot/ruoli servono per questa opportunity"
    )

    c1, c2 = st.columns(2)
    with c1:
        st.text_input("Titolo *",                  key="nopp_titolo")
        st.text_input("Cliente *",                 key="nopp_cliente")
        st.text_input("Referente — Nome",          key="nopp_ref_nome")
        st.date_input("Data inizio",               key="nopp_data_inizio")
    with c2:
        st.text_input("Referente — Cognome",       key="nopp_ref_cognome")
        st.date_input("Data fine prevista",        key="nopp_data_fine")

    st.markdown("**Composizione team richiesto:**")
    for si in range(int(n_slots)):
        sc1, sc2 = st.columns(2)
        with sc1:
            st.selectbox(f"Mansione — Risorsa {si+1}", mans_options, key=f"nopp_slot_m_{si}")
        with sc2:
            st.slider(f"Allocazione % — Risorsa {si+1}", 10, 100, 100, 10, key=f"nopp_slot_p_{si}")

    st.multiselect("Skills richieste *", list(skill_map.keys()), key="nopp_skills")
    st.slider("Livello minimo skills (1–5)", 1, 5, 3, key="nopp_lv_min")
    st.text_area("Descrizione", key="nopp_descrizione")

    if st.button("✅ Crea Opportunity", type="primary", use_container_width=True, key="nopp_submit"):
        titolo_v   = (st.session_state.get("nopp_titolo") or "").strip()
        cliente_v  = (st.session_state.get("nopp_cliente") or "").strip()
        skills_v   = st.session_state.get("nopp_skills") or []
        if not all([titolo_v, cliente_v, skills_v]):
            st.error("Compila i campi obbligatori (*): Titolo, Cliente e almeno una Skill.")
            return
        slot_risorse = [
            {
                "mansione_id": mans_id_map.get(st.session_state.get(f"nopp_slot_m_{si}", mans_options[0] if mans_options else ""), ""),
                "percentuale_allocazione": st.session_state.get(f"nopp_slot_p_{si}", 100),
            }
            for si in range(int(n_slots))
        ]
        payload = {
            "titolo": titolo_v,
            "cliente": cliente_v,
            "referente_it_cliente": {
                "nome":    st.session_state.get("nopp_ref_nome", ""),
                "cognome": st.session_state.get("nopp_ref_cognome", ""),
            },
            "manager_id": manager_id,
            "skill_richieste": [{"skill_id": skill_map[s], "livello_minimo": st.session_state.get("nopp_lv_min", 3)}
                                 for s in skills_v],
            "slot_risorse": slot_risorse,
            "data_inizio":       str(st.session_state.get("nopp_data_inizio", _dt2.date.today())),
            "data_fine_prevista": str(st.session_state.get("nopp_data_fine",   _dt2.date.today())),
            "descrizione": st.session_state.get("nopp_descrizione", ""),
        }
        r = api("POST", "/opportunities/", json=payload)
        if r and r.status_code == 201:
            st.success("✅ Opportunity creata!")
            for k in [k2 for k2 in list(st.session_state.keys()) if k2.startswith("nopp_")]:
                del st.session_state[k]
            st.rerun()
        else:
            detail = _api_detail(r)
            st.error(f"Errore: {detail}")

# ── CHATBOT HANA ───────────────────────────────────────────────────────────────
def show_chatbot(groups):
    st.markdown('<p class="main-title">✨ Practice Advisor</p>', unsafe_allow_html=True)
    st.caption("Interroga i dati di risorse, progetti e opportunity della practice · Powered by **Claude** via SAP AI Core")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    if not st.session_state.chat_history:
        st.caption("✨ Inizia a scrivere per interrogare i dati della practice")
    else:
        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
        if st.button("🗑️ Cancella conversazione", key="chat_clear"):
            st.session_state.chat_history = []
            st.rerun()

    question = st.chat_input("Scrivi qui la tua domanda…")
    if question:
        st.session_state.chat_history.append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.markdown(question)

        with st.chat_message("assistant"):
            with st.spinner("Claude sta elaborando…"):
                prior_history = st.session_state.chat_history[:-1]
                resp = api("POST", "/chat/", json={"question": question, "history": prior_history})
                if resp and resp.status_code == 200:
                    answer = resp.json().get("answer", "")
                else:
                    answer = f"Errore nella risposta del backend ({resp.status_code if resp else 'non raggiungibile'})."
                st.markdown(answer)
                st.session_state.chat_history.append({"role": "assistant", "content": answer})


# ── MATCHING AI ────────────────────────────────────────────────────────────────
def show_matching(groups):
    st.markdown('<p class="main-title">🤖 Matching AI</p>', unsafe_allow_html=True)
    st.caption("Powered by **Claude Sonnet 4.6** via SAP AI Core")
    st.markdown("---")

    r_opp = api("GET", "/opportunities/")
    opps  = r_opp.json() if r_opp and r_opp.status_code == 200 else []

    if not opps:
        st.info("Nessuna opportunity presente.")
        return

    opp_map = {o["titolo"]: o["id"] for o in opps}

    presel_id = st.session_state.match_opp_id
    presel_title = next((t for t, i in opp_map.items() if i == presel_id), None) if presel_id else None
    default_idx  = list(opp_map.keys()).index(presel_title) if presel_title and presel_title in opp_map else 0

    sel_title = st.selectbox("Seleziona Opportunity", list(opp_map.keys()), index=default_idx)
    sel_id    = opp_map[sel_title]
    st.session_state.match_opp_id = sel_id

    if can_write(groups):
        if st.button("🚀 Esegui Matching AI", type="primary"):
            with st.spinner("🤖 Claude sta analizzando le risorse disponibili… (10–20 sec)"):
                r = api("POST", f"/match/{sel_id}")
                if r and r.status_code == 200:
                    st.success("✅ Matching completato!")
                    st.rerun()
                else:
                    detail = _api_detail(r)
                    st.error(f"Errore: {detail}")

    st.markdown("---")
    st.markdown("### 📊 Shortlist per Slot")

    r_res = api("GET", f"/match/{sel_id}/results")
    if r_res is None:
        return
    if r_res.status_code == 404:
        st.info("Nessun risultato. Esegui prima il matching.")
        return
    if r_res.status_code != 200:
        st.error("Errore nel caricamento risultati.")
        return

    data  = r_res.json()
    slots = data.get("slots", [])

    if not slots:
        st.info("Nessun risultato disponibile.")
        return

    for slot in slots:
        sidx    = slot["slot_index"]
        mn      = slot.get("mansione_nome","")
        perc    = slot.get("percentuale_allocazione","")
        cands   = slot.get("candidates", [])
        n_confirmed = sum(1 for c in cands if c.get("stato") == "Confirmed")

        st.markdown(f"#### Slot {sidx+1} — {mn} @ {perc}%"
                    + (f"  ✅ *({n_confirmed} confermato/i)*" if n_confirmed else ""))

        if not cands:
            st.caption("Nessun candidato trovato per questo slot.")
            continue

        for i, item in enumerate(cands, 1):
            score  = item.get("score", 0)
            stato  = item.get("stato", "Proposed")
            nome   = item.get("risorsa_nome", "")
            motiv  = item.get("motivazione", "")
            disp   = item.get("disponibilita", 0)
            rid    = item.get("id","")
            ruolo_n = item.get("ruolo_nome","")
            senio   = item.get("seniority","")

            score_color = "🟢" if score >= 80 else ("🟡" if score >= 60 else "🔴")
            status_icon = {"Confirmed": "✅", "Rejected": "❌", "Proposed": "⏳"}.get(stato, "⏳")

            with st.container(border=True):
                c1, c2, c3, c4 = st.columns([3, 2, 2, 2])
                with c1:
                    st.markdown(f"**{i}. {nome}**")
                    if ruolo_n:
                        st.caption(f"🏷 {ruolo_n}" + (f" · {senio}" if senio else ""))
                    st.caption(motiv[:120] + "…" if len(motiv) > 120 else motiv)
                with c2:
                    st.markdown(f"{score_color} **{score}/100**")
                    st.progress(score / 100)
                with c3:
                    st.markdown(f"Disponibilità: **{int(disp)}%**")
                    st.markdown(f"{status_icon} {stato}")
                with c4:
                    if can_write(groups) and stato == "Proposed":
                        col_ok, col_no = st.columns(2)
                        with col_ok:
                            if st.button("✅", key=f"ok_{rid}", help="Conferma"):
                                api("PATCH", f"/match/{sel_id}/results/{rid}",
                                    params={"stato": "Confirmed"})
                                st.rerun()
                        with col_no:
                            if st.button("❌", key=f"no_{rid}", help="Rifiuta"):
                                api("PATCH", f"/match/{sel_id}/results/{rid}",
                                    params={"stato": "Rejected"})
                                st.rerun()
                    elif stato == "Confirmed" and can_write(groups):
                        if st.button("↩️", key=f"undo_{rid}", help="Riporta a Proposed"):
                            api("PATCH", f"/match/{sel_id}/results/{rid}",
                                params={"stato": "Proposed"})
                            st.rerun()
        st.markdown("---")

# ── APPROVAZIONI ──────────────────────────────────────────────────────────────
def show_approvazioni(groups):
    st.markdown('<p class="main-title">📋 Approvazioni Promozione</p>', unsafe_allow_html=True)
    st.caption("Richieste di promozione Opportunity → Progetto Attivo")
    st.markdown("---")

    tab_pending, tab_history = st.tabs(["⏳ In Attesa", "📜 Storico"])

    with tab_pending:
        r = api("GET", "/promotions/pending")  # noqa: E501
        if not r or r.status_code != 200:
            st.error("Errore nel caricamento richieste.")
            return
        pending = r.json()

        if not pending:
            st.info("Nessuna richiesta in attesa.")
        else:
            for req in pending:
                opp = req.get("opportunity", {})
                with st.container(border=True):
                    st.markdown(f"### 🎯 {req.get('opportunity_titolo','')} — {req.get('opportunity_cliente','')}")
                    c1, c2 = st.columns(2)
                    with c1:
                        st.markdown(f"**Richiesta da:** {req.get('requested_by_nome','')}")
                        st.markdown(f"**Data richiesta:** {req.get('requested_at','')[:10]}")
                        note = req.get("note_manager","")
                        if note:
                            st.markdown(f"**Note Manager:** {note}")
                    with c2:
                        st.markdown("**Risorse confermate per slot:**")
                        for sd in req.get("slots_dettaglio", []):
                            st.markdown(f"  • Slot {sd['slot_index']+1}: {sd.get('nome','')} — **{sd.get('percentuale_allocazione','')}%**")

                    st.markdown("---")
                    note_col, btn_col = st.columns([3, 2])
                    with note_col:
                        nota_exec = st.text_input("Note Executive (opzionale)",
                                                  key=f"nota_{req['id']}", label_visibility="collapsed",
                                                  placeholder="Note Executive (opzionale)")
                    with btn_col:
                        col_ok, col_no = st.columns(2)
                        with col_ok:
                            if st.button("✅ Approva", key=f"appr_{req['id']}", type="primary"):
                                rv = api("PATCH", f"/promotions/{req['id']}/review",
                                         params={"decision": "Approved", "note_executive": nota_exec})
                                if rv and rv.status_code == 200:
                                    st.success("✅ Opportunity promossa a Progetto Attivo!")
                                    st.rerun()
                                else:
                                    detail = _api_detail(rv)
                                    st.error(f"Errore: {detail}")
                        with col_no:
                            if st.button("❌ Rifiuta", key=f"rif_{req['id']}"):
                                rv = api("PATCH", f"/promotions/{req['id']}/review",
                                         params={"decision": "Rejected", "note_executive": nota_exec})
                                if rv and rv.status_code == 200:
                                    st.warning("Richiesta rifiutata — Opportunity riportata in stato New.")
                                    st.rerun()
                                else:
                                    detail = _api_detail(rv)
                                    st.error(f"Errore: {detail}")

    with tab_history:
        r2 = api("GET", "/promotions/")
        if r2 and r2.status_code == 200:
            all_reqs = [x for x in r2.json() if x.get("stato") != "Pending"]
            if not all_reqs:
                st.info("Nessuna richiesta elaborata.")
            for req in reversed(all_reqs):
                icon = "✅" if req.get("stato") == "Approved" else "❌"
                st.markdown(f"{icon} **{req.get('opportunity_titolo','')}** — "
                            f"{req.get('stato','')} il {(req.get('reviewed_at') or '')[:10]}")

    # ── TAB: modifiche progetto ──
    st.markdown("---")
    st.markdown("### 🔧 Richieste Modifica Progetto")
    rpc = api("GET", "/project-changes/pending")
    if rpc and rpc.status_code == 200:
        pcr_list = rpc.json()
        if not pcr_list:
            st.info("Nessuna richiesta di modifica progetto in attesa.")
        for req in pcr_list:
            ct = req.get("change_type","")
            ct_label = {"update_info":"✏️ Modifica info","add_resource":"➕ Aggiungi risorsa","remove_resource":"🔓 Rilascia risorsa"}.get(ct, ct)
            with st.container(border=True):
                st.markdown(f"### {ct_label} — **{req.get('project_nome','')}** ({req.get('project_cliente','')})")
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown(f"**Richiesto da:** {req.get('requested_by_nome','')}")
                    st.markdown(f"**Data:** {req.get('requested_at','')[:10]}")
                    if req.get("note_manager"):
                        st.markdown(f"**Note:** {req['note_manager']}")
                with c2:
                    if ct == "update_info":
                        pl = req.get("payload",{})
                        for k,v in pl.items():
                            st.markdown(f"  • `{k}`: {v}")
                    elif ct in ("add_resource","remove_resource"):
                        r_nome = req.get("risorsa_nome","")
                        alloc  = req.get("allocazione",{})
                        pl     = req.get("payload",{})
                        st.markdown(f"**Risorsa:** {r_nome}")
                        if ct == "add_resource":
                            st.markdown(f"**Allocazione:** {pl.get('percentuale','')}%  —  {pl.get('ruolo_nel_progetto','')}")
                        elif ct == "remove_resource" and alloc:
                            st.markdown(f"**Allocazione attuale:** {alloc.get('percentuale','')}%")

                st.markdown("---")
                note_col2, btn_col2 = st.columns([3,2])
                with note_col2:
                    nota_e2 = st.text_input("Note Executive", key=f"nota_pcr_{req['id']}",
                                            label_visibility="collapsed", placeholder="Note Executive (opzionale)")
                with btn_col2:
                    col_ok2, col_no2 = st.columns(2)
                    with col_ok2:
                        if st.button("✅ Approva", key=f"appr_pcr_{req['id']}", type="primary"):
                            rv = api("PATCH", f"/project-changes/{req['id']}/review",
                                     params={"decision":"Approved","note_executive":nota_e2})
                            if rv and rv.status_code == 200:
                                st.success("✅ Modifica applicata!")
                                st.rerun()
                            else:
                                detail = _api_detail(rv)
                                st.error(f"Errore: {detail}")
                    with col_no2:
                        if st.button("❌ Rifiuta", key=f"rif_pcr_{req['id']}"):
                            rv = api("PATCH", f"/project-changes/{req['id']}/review",
                                     params={"decision":"Rejected","note_executive":nota_e2})
                            if rv and rv.status_code == 200:
                                st.warning("Richiesta rifiutata.")
                                st.rerun()
                            else:
                                detail = _api_detail(rv)
                                st.error(f"Errore: {detail}")


def _form_modifica_dipendente():
    st.markdown("### ✏️ Modifica Dipendente")

    res_r = api("GET", "/resources/")
    resources = res_r.json() if res_r and res_r.status_code == 200 else []
    if not resources:
        st.info("Nessuna risorsa disponibile.")
        return

    res_opts = {f"{r['nome']} {r['cognome']} — {r.get('ruolo_nome','')}": r["id"] for r in sorted(resources, key=lambda r: r.get("ruolo_nome",""))}
    sel_label = st.selectbox("Seleziona dipendente da modificare", list(res_opts.keys()), key="edit_dip_sel")
    sel_id    = res_opts[sel_label]
    sel_res   = next(r for r in resources if r["id"] == sel_id)

    mansioni_r = api("GET", "/mansioni/")
    skills_r   = api("GET", "/skills/")
    groups_r   = api("GET", "/roles/")

    mansioni  = mansioni_r.json() if mansioni_r and mansioni_r.status_code == 200 else []
    skills    = skills_r.json()   if skills_r   and skills_r.status_code   == 200 else []
    rgroups   = groups_r.json()   if groups_r   and groups_r.status_code   == 200 else []

    mansione_map = {m["nome"]: m["id"] for m in mansioni}
    mansione_id_map = {m["id"]: m["nome"] for m in mansioni}
    skill_map    = {s["nome"]: s["id"] for s in skills}
    skill_id_map = {s["id"]: s["nome"] for s in skills}
    group_map    = {g["nome"]: g["id"] for g in rgroups}
    group_id_map = {g["id"]: g["nome"] for g in rgroups}

    import datetime as _dt

    cur_mansione = mansione_id_map.get(sel_res.get("ruolo_id",""), "")
    cur_skill_data = {
        skill_id_map.get(s.get("skill_id",""), s.get("skill_id","")): s.get("livello", 3)
        for s in sel_res.get("skill_ids", []) if isinstance(s, dict)
    }
    cur_skills   = list(cur_skill_data.keys())
    cur_groups   = [group_id_map.get(gid,"?") for gid in sel_res.get("gruppo_ruolo_ids",[])]
    cur_lingue   = [l.capitalize() for l in sel_res.get("lingue", [])]
    lingue_options = ["Italiano", "Inglese", "Tedesco", "Francese", "Spagnolo"]

    _raw_dn = sel_res.get("data_nascita","")
    try:
        _default_dn = _dt.date.fromisoformat(_raw_dn)
    except Exception:
        _default_dn = _dt.date(1990, 1, 1)

    # ── anagrafica + mansione + lingue + ruolo + costo (in form) ──────────────
    with st.form(f"form_edit_dip_{sel_id}", clear_on_submit=False):
        c1, c2 = st.columns(2)
        with c1:
            new_nome    = st.text_input("Nome *", value=sel_res.get("nome",""))
            new_email   = st.text_input("Email *", value=sel_res.get("email",""))
        with c2:
            new_cognome = st.text_input("Cognome *", value=sel_res.get("cognome",""))
            new_data_n  = st.date_input("Data di nascita", value=_default_dn,
                                        format="YYYY-MM-DD",
                                        min_value=_dt.date(1940, 1, 1))

        man_idx = list(mansione_map.keys()).index(cur_mansione) if cur_mansione in mansione_map else 0
        new_mansione = st.selectbox("Mansione", list(mansione_map.keys()), index=man_idx)
        new_lingue   = st.multiselect("Lingue", lingue_options,
                                      default=[l for l in cur_lingue if l in lingue_options])
        new_ruolo    = st.selectbox("Ruolo (autorizzativo)", list(group_map.keys()),
                                    index=list(group_map.keys()).index(cur_groups[0]) if cur_groups and cur_groups[0] in group_map else 0)
        new_costo    = st.number_input("Costo orario €/h", 0.0, 500.0,
                                       float(sel_res.get("costo_orario", 0.0)))
        save = st.form_submit_button("💾 Salva Modifiche", type="primary", use_container_width=True)

    # ── skills con livello per-skill (fuori dal form) ──────────────────────────
    st.markdown("**Skills assegnate:**")
    _sk_key = f"ed_skills_{sel_id}"
    if _sk_key not in st.session_state:
        st.session_state[_sk_key] = [s for s in cur_skills if s in skill_map]
    new_skills = st.multiselect("Seleziona skills", list(skill_map.keys()), key=_sk_key)
    if new_skills:
        st.markdown("**Livello per ogni skill:**")
        cols_sk = st.columns(min(len(new_skills), 3))
        for i, s in enumerate(new_skills):
            default_lv = cur_skill_data.get(s, 3)
            with cols_sk[i % 3]:
                st.slider(s, 1, 5, default_lv, key=f"ed_slv_{sel_id}_{s}",
                          help="1 = Base · 3 = Intermedio · 5 = Expert")

    # ── submit ─────────────────────────────────────────────────────────────────
    if save:
        if not all([new_nome, new_cognome, new_email]):
            st.error("Compila i campi obbligatori (*).")
        else:
            sel_skills_now = st.session_state.get(_sk_key, [])
            skill_ids = [{"skill_id": skill_map[s], "livello": st.session_state.get(f"ed_slv_{sel_id}_{s}", 3)}
                         for s in sel_skills_now if s in skill_map]
            payload = {
                "nome": new_nome, "cognome": new_cognome, "email": new_email,
                "data_nascita": str(new_data_n),
                "ruolo_id": mansione_map[new_mansione],
                "skill_ids": skill_ids,
                "lingue": [l.lower() for l in new_lingue],
                "gruppo_ruolo_ids": [group_map[new_ruolo]],
                "costo_orario": new_costo,
            }
            r = api("PUT", f"/resources/{sel_id}", json=payload)
            if r and r.status_code == 200:
                st.success("✅ Dipendente aggiornato!")
                st.session_state.pop(_sk_key, None)
            else:
                detail = _api_detail(r)
                st.error(f"Errore: {detail}")


# ── ADMIN ──────────────────────────────────────────────────────────────────────
def show_admin(groups):
    st.markdown('<p class="main-title">⚙️ Amministrazione</p>', unsafe_allow_html=True)
    st.markdown("---")

    tab_users, tab_groups, tab_skills, tab_new_dip, tab_edit_dip = st.tabs([
        "👥 Assegna Ruolo", "🔐 Ruoli Autorizzativi", "🛠 Skills",
        "👤 Nuovo Dipendente", "✏️ Modifica Dipendente"
    ])

    with tab_users:
        st.markdown("### Assegna Ruolo a una Risorsa")
        r_res = api("GET", "/resources/")
        r_grp = api("GET", "/roles/")
        resources   = r_res.json() if r_res and r_res.status_code == 200 else []
        role_groups = r_grp.json() if r_grp and r_grp.status_code == 200 else []
        grp_map     = {g["nome"]: g["id"] for g in role_groups}
        grp_id_map  = {g["id"]: g["nome"] for g in role_groups}

        # barre di ricerca
        sc1, sc2 = st.columns(2)
        with sc1:
            search_nome = st.text_input("🔍 Cerca per nome", key="admin_search_nome")
        with sc2:
            ruoli_presenti = sorted({r.get("ruolo_nome","") for r in resources if r.get("ruolo_nome","")})
            filter_ruolo   = st.selectbox("Filtra per mansione", ["— tutti —"] + ruoli_presenti, key="admin_filter_ruolo")

        # filtra
        filtered = resources
        if search_nome:
            filtered = [r for r in filtered
                        if search_nome.lower() in f"{r.get('nome','')} {r.get('cognome','')}".lower()]
        if filter_ruolo != "— tutti —":
            filtered = [r for r in filtered if r.get("ruolo_nome","") == filter_ruolo]

        # ordina per ruolo attuale
        filtered = sorted(filtered, key=lambda r: r.get("ruolo_nome",""))

        # etichetta con ruolo professionale e gruppo di accesso
        def _res_label(r):
            grp_names = ", ".join(grp_id_map.get(gid,"?") for gid in r.get("gruppo_ruolo_ids",[]))
            sen = r.get("seniority", "")
            mansione = r.get("ruolo_nome","")
            return f"{r['nome']} {r['cognome']}  |  👔 Mansione: {mansione} ({sen})  |  🔑 Ruolo: {grp_names}"

        res_labels = [_res_label(r) for r in filtered]
        res_ids    = [r["id"] for r in filtered]

        if not res_labels:
            st.info("Nessuna risorsa trovata con i filtri selezionati.")
        else:
            sel_idx  = st.selectbox("Risorsa", range(len(res_labels)),
                                    format_func=lambda i: res_labels[i],
                                    key="admin_sel_res")
            sel_res  = filtered[sel_idx]

            cur_grps = [grp_id_map.get(gid,"?") for gid in sel_res.get("gruppo_ruolo_ids",[])]
            st.caption(f"Ruolo attuale: **{', '.join(cur_grps) if cur_grps else 'nessuno'}**")

            sel_grps = st.multiselect("Nuovo Ruolo da assegnare", list(grp_map.keys()),
                                      default=[g for g in cur_grps if g in grp_map])

            if st.button("Aggiorna Gruppi", type="primary"):
                gids = [grp_map[g] for g in sel_grps]
                r    = api("PATCH", f"/roles/resources/{sel_res['id']}/groups", json=gids)
                if r and r.status_code == 200:
                    st.success("✅ Gruppi aggiornati!")
                    st.session_state.pop("cached_groups", None)
                else:
                    detail = _api_detail(r)
                    st.error(f"Errore: {detail}")

    with tab_groups:
        st.markdown("### Ruoli Autorizzativi — Permessi e Utenti Assegnati")

        PERMESSI = {
            "Employee": [
                "👁 Visualizza risorse, progetti, opportunity",
                "👁 Visualizza risultati matching AI",
            ],
            "Manager": [
                "✅ Tutto ciò che può fare Employee",
                "➕ Crea e modifica le proprie opportunity",
                "🤖 Lancia il Matching AI",
                "✔️ Conferma/rifiuta risorse dalla shortlist",
                "📤 Richiede promozione Opportunity → Progetto (approvazione Executive)",
                "🔧 Propone modifiche al proprio progetto (approvazione Executive)",
            ],
            "Executive": [
                "✅ Tutto ciò che può fare Manager",
                "📋 Approva o rifiuta promozioni Opportunity → Progetto",
                "📋 Approva o rifiuta modifiche ai progetti",
            ],
            "Administrator": [
                "✅ Tutto ciò che può fare Executive",
                "👤 Aggiunge e modifica dipendenti",
                "🛠 Aggiunge nuove skill",
                "🔑 Assegna ruoli autorizzativi alle risorse",
            ],
        }

        r_grp2 = api("GET", "/roles/")
        r_res  = api("GET", "/resources/?include_system=true")
        all_groups  = r_grp2.json() if r_grp2 and r_grp2.status_code == 200 else []
        all_res     = r_res.json()  if r_res  and r_res.status_code  == 200 else []

        grp_id_map2 = {g["id"]: g["nome"] for g in all_groups}

        _ROLE_ORDER = ["Employee", "Manager", "Executive", "Administrator"]
        for g in sorted(all_groups, key=lambda x: _ROLE_ORDER.index(x["nome"]) if x["nome"] in _ROLE_ORDER else 99):
            gname = g["nome"]
            utenti = [r for r in all_res if g["id"] in r.get("gruppo_ruolo_ids", [])]
            icon   = {"Employee":"🟢","Manager":"🔵","Executive":"🟣","Administrator":"🔴"}.get(gname,"⚪")

            with st.expander(f"{icon} **{gname}** — {len(utenti)} utenti assegnati"):
                col_perm, col_utenti = st.columns([3, 2])
                with col_perm:
                    st.markdown("**Permessi:**")
                    for p in PERMESSI.get(gname, ["(nessuna configurazione)"]):
                        st.markdown(f"  {p}")
                with col_utenti:
                    st.markdown("**Utenti assegnati:**")
                    if utenti:
                        for u in sorted(utenti, key=lambda x: x.get("cognome","")):
                            st.markdown(f"  • {u.get('nome','')} {u.get('cognome','')} — *{u.get('ruolo_nome','')}*")
                    else:
                        st.caption("Nessun utente assegnato")

    with tab_skills:
        st.markdown("### Skill Esistenti")
        sk_r = api("GET", "/skills/")
        skills_list = sk_r.json() if sk_r and sk_r.status_code == 200 else []
        funz = [s for s in skills_list if s.get("categoria") == "Funzionale"]
        tecn = [s for s in skills_list if s.get("categoria") == "Tecnica"]
        sc1, sc2 = st.columns(2)
        with sc1:
            st.markdown("**Funzionali**")
            for s in funz:
                st.markdown(f"  • `{s['id']}` {s['nome']}")
        with sc2:
            st.markdown("**Tecniche**")
            for s in tecn:
                st.markdown(f"  • `{s['id']}` {s['nome']}")

        st.markdown("### ➕ Aggiungi Skill")
        with st.form("form_skill"):
            sk_nome = st.text_input("Nome skill *")
            sk_cat  = st.selectbox("Categoria", ["Funzionale", "Tecnica"])
            sk_desc = st.text_input("Descrizione (opzionale)")
            if st.form_submit_button("✅ Crea Skill", type="primary"):
                if not sk_nome:
                    st.error("Il nome è obbligatorio.")
                else:
                    r = api("POST", "/skills/", json={"nome": sk_nome, "categoria": sk_cat, "descrizione": sk_desc})
                    if r and r.status_code == 201:
                        st.success(f"✅ Skill '{sk_nome}' creata!")
                        st.rerun()
                    else:
                        detail = _api_detail(r)
                        st.error(f"Errore: {detail}")

    with tab_new_dip:
        st.markdown("### ➕ Aggiungi Dipendente")
        _form_crea_risorsa()

    with tab_edit_dip:
        _form_modifica_dipendente()
# ── RISORSA V2 ────────────────────────────────────────────────────────────────
def show_risorsa_v2(groups):
    if "show_new_resource_v2" not in st.session_state:
        st.session_state["show_new_resource_v2"] = False

    # ── TITOLO E PULSANTE NUOVA RISORSA ───────────────────────────────────────
    title_col, button_col = st.columns([4, 1])

    with title_col:
        st.markdown(
            '<p class="main-title">👥 Risorsa v2</p>',
            unsafe_allow_html=True
        )

    with button_col:
        if st.button(
            "➕ Nuova risorsa",
            type="primary",
            use_container_width=True,
            key="open_new_resource_v2"
        ):
            st.session_state["show_new_resource_v2"] = True

    # ── FORM NUOVA RISORSA ────────────────────────────────────────────────────
    if st.session_state["show_new_resource_v2"]:
        catalog_response = api(
            "GET",
            "/sm/resource-form-catalogs"
        )

        if (
            catalog_response is None
            or catalog_response.status_code != 200
        ):
            st.error("Impossibile caricare i valori del form.")

        else:
            catalogs = catalog_response.json()

            levels = catalogs.get("levels", [])
            skills_catalog = catalogs.get("skills", [])
            languages_catalog = catalogs.get("languages", [])
            certifications_catalog = catalogs.get(
                "certifications",
                []
            )

            form_title_col, close_col = st.columns([4, 1])

            with form_title_col:
                st.markdown("### ➕ Nuova risorsa")

            with close_col:
                if st.button(
                    "✖ Chiudi",
                    key="close_new_resource_v2",
                    use_container_width=True
                ):
                    st.session_state["show_new_resource_v2"] = False
                    st.rerun()

            with st.form("new_resource_v2_form"):
                st.markdown("#### Anagrafica")

                col1, col2 = st.columns(2)

                with col1:
                    new_eid = st.number_input(
                        "EID *",
                        min_value=1,
                        step=1
                    )

                    new_nome = st.text_input(
                        "Nome *"
                    )

                    new_cognome = st.text_input(
                        "Cognome *"
                    )

                    new_email = st.text_input(
                        "Email *"
                    )

                with col2:
                    level_options = {
                        f"{item['level']} - {item['level_name']}": item["level"]
                        for item in levels
                    }

                    selected_level_label = st.selectbox(
                        "Level *",
                        list(level_options.keys())
                    )

                    new_level = level_options[selected_level_label]

                    new_anni_esperienza = st.number_input(
                        "Anni di esperienza",
                        min_value=0,
                        max_value=60,
                        step=1
                    )

                    new_is_stagista = st.checkbox(
                        "Stagista"
                    )

                # ── SKILL E LINGUE ─────────────────────────────────────────────
                st.markdown("#### Skill e lingue")

                col3, col4 = st.columns(2)

                skill_options = [
                    item["skill_name"]
                    for item in skills_catalog
                ]

                language_options = [
                    item["language_code"]
                    for item in languages_catalog
                ]

                with col3:
                    new_skills = st.multiselect(
                        "Skill",
                        skill_options
                    )

                with col4:
                    new_languages = st.multiselect(
                        "Lingue",
                        language_options
                    )

                # ── CERTIFICAZIONI ─────────────────────────────────────────────
                st.markdown("#### Certificazioni")

                certification_options = {
                    f"{item['cert_id']} - {item['nome_cert']}": item["cert_id"]
                    for item in certifications_catalog
                }

                selected_new_certifications = st.multiselect(
                    "Certificazioni",
                    list(certification_options.keys())
                )

                certification_details = []

                for selected_certification in selected_new_certifications:
                    cert_id = certification_options[
                        selected_certification
                    ]

                    st.markdown(
                        f"**{selected_certification}**"
                    )

                    cert_col1, cert_col2 = st.columns(2)

                    with cert_col1:
                        cert_city = st.text_input(
                            "City",
                            key=f"new_resource_city_{cert_id}"
                        )

                    with cert_col2:
                        cert_expiration = st.date_input(
                            "Data scadenza",
                            key=f"new_resource_expiration_{cert_id}"
                        )

                    certification_details.append({
                        "cert_id": cert_id,
                        "city": cert_city,
                        "expiration_date": cert_expiration.isoformat()
                    })

                # ── SALVATAGGIO ────────────────────────────────────────────────
                st.markdown("---")

                save_resource = st.form_submit_button(
                    "💾 Salva risorsa",
                    type="primary",
                    use_container_width=True
                )

                if save_resource:
                    if (
                        not new_nome.strip()
                        or not new_cognome.strip()
                        or not new_email.strip()
                    ):
                        st.error(
                            "EID, Nome, Cognome ed Email sono obbligatori."
                        )

                    else:
                        payload = {
                            "eid": int(new_eid),
                            "nome": new_nome.strip(),
                            "cognome": new_cognome.strip(),
                            "email": new_email.strip().lower(),
                            "level": int(new_level),
                            "anni_esperienza": int(new_anni_esperienza),
                            "is_stagista": new_is_stagista,
                            "skills": new_skills,
                            "languages": new_languages,
                            "certifications": certification_details
                        }

                        create_response = api(
                            "POST",
                            "/sm/risorse-v2",
                            json=payload
                        )

                        if create_response is None:
                            st.error(
                                "Nessuna risposta dal backend."
                            )

                        elif create_response.status_code == 200:
                            st.success(
                                "✅ Risorsa creata correttamente."
                            )

                            st.session_state[
                                "show_new_resource_v2"
                            ] = False

                            st.rerun()

                        else:
                            st.error(
                                _api_detail(create_response)
                            )

    # ── CARICAMENTO RISORSE ───────────────────────────────────────────────────
    response = api(
        "GET",
        "/sm/risorse-v2"
    )

    if response is None:
        st.error("Nessuna risposta dal backend.")
        return

    if response.status_code != 200:
        st.error(
            f"Errore nel caricamento: {_api_detail(response)}"
        )
        return

    resources = response.json()

    if not resources:
        st.info("Nessuna risorsa presente.")
        return

    # ── VALORI FILTRI ─────────────────────────────────────────────────────────
    all_levels = sorted({
        resource.get("level_name")
        for resource in resources
        if resource.get("level_name")
    })

    all_skills = sorted({
        skill.get("skill_name")
        for resource in resources
        for skill in resource.get("skills", [])
        if skill.get("skill_name")
    })

    all_languages = sorted({
        language.get("language_code")
        for resource in resources
        for language in resource.get("languages", [])
        if language.get("language_code")
    })

    all_certifications = sorted({
        certification.get("nome_cert")
        for resource in resources
        for certification in resource.get("certifications", [])
        if certification.get("nome_cert")
    })

    # ── FILTRI ────────────────────────────────────────────────────────────────
    filter_row_1 = st.columns([3, 2, 2])

    with filter_row_1[0]:
        search = st.text_input(
            "🔍 Cerca per nome, cognome o email",
            key="risorsa_v2_search"
        )

    with filter_row_1[1]:
        selected_levels = st.multiselect(
            "Level",
            all_levels,
            key="risorsa_v2_levels"
        )

    with filter_row_1[2]:
        only_available = st.checkbox(
            "Solo risorse disponibili",
            key="risorsa_v2_available"
        )

    filter_row_2 = st.columns(3)

    with filter_row_2[0]:
        selected_skills = st.multiselect(
            "Skill",
            all_skills,
            key="risorsa_v2_skills"
        )

    with filter_row_2[1]:
        selected_certifications_filter = st.multiselect(
            "Certificazioni",
            all_certifications,
            key="risorsa_v2_certifications"
        )

    with filter_row_2[2]:
        selected_languages = st.multiselect(
            "Lingue",
            all_languages,
            key="risorsa_v2_languages"
        )

    # ── APPLICAZIONE FILTRI ───────────────────────────────────────────────────
    filtered_resources = resources

    if search:
        search_value = search.strip().lower()

        filtered_resources = [
            resource
            for resource in filtered_resources
            if search_value in (
                f"{resource.get('nome', '')} "
                f"{resource.get('cognome', '')} "
                f"{resource.get('email', '')}"
            ).lower()
        ]

    if selected_levels:
        filtered_resources = [
            resource
            for resource in filtered_resources
            if resource.get("level_name") in selected_levels
        ]

    if selected_skills:
        filtered_resources = [
            resource
            for resource in filtered_resources
            if set(selected_skills).issubset({
                skill.get("skill_name")
                for skill in resource.get("skills", [])
            })
        ]

    if selected_certifications_filter:
        filtered_resources = [
            resource
            for resource in filtered_resources
            if set(selected_certifications_filter).issubset({
                certification.get("nome_cert")
                for certification in resource.get(
                    "certifications",
                    []
                )
            })
        ]

    if selected_languages:
        filtered_resources = [
            resource
            for resource in filtered_resources
            if set(selected_languages).issubset({
                language.get("language_code")
                for language in resource.get("languages", [])
            })
        ]

    # Disponibili = verdi + arancioni
    if only_available:
        filtered_resources = [
            resource
            for resource in filtered_resources
            if int(resource.get("disponibilita") or 0) > 0
        ]

    filtered_resources = sorted(
        filtered_resources,
        key=lambda resource: (
            resource.get("cognome", ""),
            resource.get("nome", "")
        )
    )

    # ── KPI DINAMICI ──────────────────────────────────────────────────────────
    total_filtered = len(filtered_resources)

    certified_count = sum(
        1
        for resource in filtered_resources
        if resource.get("certifications")
    )

    available_count = sum(
        1
        for resource in filtered_resources
        if int(resource.get("disponibilita") or 0) > 0
    )

    not_available_count = sum(
        1
        for resource in filtered_resources
        if int(resource.get("disponibilita") or 0) == 0
    )

    kpi_1, kpi_2, kpi_3, kpi_4 = st.columns(4)

    kpi_1.metric(
        "👥 Risorse",
        total_filtered
    )

    kpi_2.metric(
        "🎓 Con certificazioni",
        certified_count
    )

    kpi_3.metric(
        "✅ Disponibili",
        available_count
    )

    kpi_4.metric(
        "🔴 Non disponibili",
        not_available_count
    )

    st.markdown("---")

    st.caption(
        f"{total_filtered} risorse trovate su {len(resources)}"
    )

    # ── VISTE ─────────────────────────────────────────────────────────────────
    tab_cards, tab_table = st.tabs([
        "🗂 Schede",
        "📋 Tabella"
    ])

   

    # ── VISTA SCHEDE ──────────────────────────────────────────────────────────
    with tab_cards:
        for resource in filtered_resources:
            availability = int(
                resource.get("disponibilita") or 0
            )

            availability_status = resource.get(
                "availability_status",
                "green"
            )

            if availability_status == "red":
                availability_icon = "🔴"
            elif availability_status == "orange":
                availability_icon = "🟠"
            else:
                availability_icon = "🟢"

            level_name = (
                resource.get("level_name")
                or "Level non indicato"
            )

            intern_label = (
                " · 🌱 Stagista"
                if resource.get("is_stagista")
                else ""
            )

            label = (
                f"{availability_icon} "
                f"{resource.get('nome', '')} "
                f"{resource.get('cognome', '')}"
                f" — {level_name}{intern_label}"
            )

            with st.expander(label):
                col_profile, col_skills, col_certifications = st.columns(
                    [1.3, 1, 1.8]
                )

                # ── ANAGRAFICA ────────────────────────────────────────────────
                with col_profile:
                    st.markdown("#### Anagrafica")

                    st.markdown(
                        f"🆔 EID: `{resource.get('eid', '')}`"
                    )

                    st.markdown(
                        f"📧 `{resource.get('email') or '—'}`"
                    )

                    st.markdown(
                        f"🏷 Level: "
                        f"**{resource.get('level') or '—'}** "
                        f"· {level_name}"
                    )

                    st.markdown(
                        f"⏳ Esperienza: "
                        f"**{resource.get('anni_esperienza') or 0} anni**"
                    )

                    available_from = resource.get(
                        "available_from"
                    )

                    if available_from:
                        st.markdown(
                            f"📅 Disponibile dal: "
                            f"**{available_from}**"
                        )
                    else:
                        st.markdown(
                            "📅 Disponibile dal: **Subito**"
                        )

                    st.markdown(
                        f"**Disponibilità: {availability}%**"
                    )

                    st.progress(
                        min(max(availability, 0), 100) / 100
                    )

                    # ── MANAGER ───────────────────────────────────────────────
                    managers = resource.get(
                        "managers",
                        []
                    )

                    st.markdown(
                        "#### Manager di riferimento"
                    )

                    if managers:
                        for manager in managers:
                            manager_name = (
                                f"{manager.get('nome', '')} "
                                f"{manager.get('cognome', '')}"
                            ).strip()

                            st.markdown(
                                f"👤 **{manager_name}**"
                            )

                            if manager.get("email"):
                                st.caption(
                                    manager.get("email")
                                )
                    else:
                        st.caption(
                            "Manager non disponibile."
                        )

                    # ── LINGUE ────────────────────────────────────────────────
                    languages = [
                        language.get("language_code")
                        for language in resource.get(
                            "languages",
                            []
                        )
                        if language.get("language_code")
                    ]

                    if languages:
                        st.markdown(
                            "🌐 " + " · ".join(languages)
                        )
                    else:
                        st.caption(
                            "Nessuna lingua registrata."
                        )

                # ── SKILL ─────────────────────────────────────────────────────
                with col_skills:
                    st.markdown("#### Skill")

                    skills = resource.get(
                        "skills",
                        []
                    )

                    if skills:
                        for skill in skills:
                            st.markdown(
                                f"• {skill.get('skill_name', '')}"
                            )
                    else:
                        st.caption(
                            "Nessuna skill registrata."
                        )

                # ── CERTIFICAZIONI ────────────────────────────────────────────
                with col_certifications:
                    st.markdown(
                        "#### Certificazioni"
                    )

                    certifications = resource.get(
                        "certifications",
                        []
                    )

                    if certifications:
                        for certification in certifications:
                            expiration_date = (
                                certification.get(
                                    "expiration_date"
                                )
                                or "—"
                            )

                            st.markdown(
                                f"🎓 **"
                                f"{certification.get('nome_cert', '')}"
                                f"**"
                            )

                            st.caption(
                                f"{certification.get('cert_id', '')}"
                                f" · Scadenza: {expiration_date}"
                            )
                    else:
                        st.caption(
                            "Nessuna certificazione registrata."
                        )

    # ── VISTA TABELLA ─────────────────────────────────────────────────────────
    with tab_table:
        table_rows = []

        for resource in filtered_resources:
            managers_text = ", ".join(
                (
                    f"{manager.get('nome', '')} "
                    f"{manager.get('cognome', '')}"
                ).strip()
                for manager in resource.get(
                    "managers",
                    []
                )
            )

            table_rows.append({
                "Stato": {
                    "green": "Verde",
                    "orange": "Arancione",
                    "red": "Rosso"
                }.get(
                    resource.get("availability_status"),
                    ""
                ),

                "EID":
                    resource.get("eid", ""),

                "Nome":
                    (
                        f"{resource.get('nome', '')} "
                        f"{resource.get('cognome', '')}"
                    ).strip(),

                "Email":
                    resource.get("email", ""),

                "Level":
                    resource.get("level_name", ""),

                "Anni esperienza":
                    resource.get(
                        "anni_esperienza"
                    ) or 0,

                "Allocazione attiva %":
                    resource.get(
                        "active_allocation"
                    ) or 0,

                "Disponibilità %":
                    resource.get(
                        "disponibilita"
                    ) or 0,

                "Disponibile dal":
                    resource.get(
                        "available_from"
                    ) or "Subito",

                "Manager":
                    managers_text,

                "Skill":
                    ", ".join(
                        skill.get(
                            "skill_name",
                            ""
                        )
                        for skill in resource.get(
                            "skills",
                            []
                        )
                    ),

                "Lingue":
                    ", ".join(
                        language.get(
                            "language_code",
                            ""
                        )
                        for language in resource.get(
                            "languages",
                            []
                        )
                    ),

                "Certificazioni":
                    ", ".join(
                        certification.get(
                            "nome_cert",
                            ""
                        )
                        for certification in resource.get(
                            "certifications",
                            []
                        )
                    )
            })

        st.dataframe(
            table_rows,
            use_container_width=True,
            hide_index=True
        )

# ── DASHBOARD V2 ──────────────────────────────────────────────────────────────
def show_dashboard_v2(groups):
    st.markdown(
        '<p class="main-title">📊 StaffMatch Dashboard</p>',
        unsafe_allow_html=True
    )

    response = api(
        "GET",
        "/sm/dashboard-v2"
    )

    if response is None:
        st.error("Nessuna risposta dal backend.")
        return

    if response.status_code != 200:
        st.error(
            f"Errore nel caricamento dashboard: {_api_detail(response)}"
        )
        return

    data = response.json()

    commercial_rows = data.get("commercial_rows", [])
    contract_rows = data.get("contract_rows", [])
    osr_rows = data.get("osr_rows", [])
    resource_rows = data.get("resource_rows", [])
    filters = data.get("filters", {})

    # ── PALETTE ────────────────────────────────────────────────────────────────
    purple = "#7B2CBF"
    purple_dark = "#5A189A"
    purple_light = "#C77DFF"
    dashboard_palette = [
    "#2563EB",  # blu
    "#06B6D4",  # cyan
    "#14B8A6",  # teal
    "#22C55E",  # verde
    "#F59E0B",  # amber
    "#F97316",  # arancio
    "#EC4899",  # pink
    "#8B5CF6",  # violet
    "#6366F1",  # indigo
    "#EF4444"   # rosso
]

    # ── FILTRI ────────────────────────────────────────────────────────────────
    st.markdown("#### Filtri")

    filter_1, filter_2, filter_3 = st.columns(3)

    with filter_1:
        selected_industries = st.multiselect(
            "Industry",
            filters.get("industries", [])
        )

    with filter_2:
        selected_clients = st.multiselect(
            "Cliente",
            filters.get("clients", [])
        )

    with filter_3:
        selected_technologies = st.multiselect(
            "Technology",
            filters.get("technologies", [])
        )

    filter_4, filter_5, filter_6 = st.columns(3)

    with filter_4:
        selected_statuses = st.multiselect(
            "Opportunity Status",
            filters.get("opportunity_statuses", [])
        )

    with filter_5:
        selected_service_groups = st.multiselect(
            "Service Group",
            filters.get("service_groups", [])
        )

    manager_options = {
        manager.get("name"): manager.get("eid")
        for manager in filters.get("managers", [])
        if manager.get("name")
    }

    with filter_6:
        selected_manager_names = st.multiselect(
            "Manager",
            list(manager_options.keys())
        )

    selected_manager_eids = {
        manager_options[name]
        for name in selected_manager_names
    }

    # ── FILTRO OPPORTUNITY ────────────────────────────────────────────────────
    filtered_commercial = commercial_rows

    if selected_industries:
        filtered_commercial = [
            row
            for row in filtered_commercial
            if row.get("industry_sector") in selected_industries
        ]

    if selected_clients:
        filtered_commercial = [
            row
            for row in filtered_commercial
            if row.get("client_name") in selected_clients
        ]

    if selected_technologies:
        filtered_commercial = [
            row
            for row in filtered_commercial
            if row.get("main_tech_cluster") in selected_technologies
        ]

    if selected_statuses:
        filtered_commercial = [
            row
            for row in filtered_commercial
            if row.get("opportunity_status") in selected_statuses
        ]

    if selected_service_groups:
        filtered_commercial = [
            row
            for row in filtered_commercial
            if row.get("service_group") in selected_service_groups
        ]

    if selected_manager_eids:
        filtered_commercial = [
            row
            for row in filtered_commercial
            if row.get("manager_eid") in selected_manager_eids
        ]

    # ── FILTER CONTRACTS ──────────────────────────────────────────────────────
    filtered_contracts = contract_rows

    if selected_industries:
        filtered_contracts = [
            row
            for row in filtered_contracts
            if row.get("industry_sector") in selected_industries
        ]

    if selected_clients:
        filtered_contracts = [
            row
            for row in filtered_contracts
            if row.get("client_name") in selected_clients
        ]

    if selected_service_groups:
        filtered_contracts = [
            row
            for row in filtered_contracts
            if row.get("service_group") in selected_service_groups
        ]

    if selected_manager_eids:
        filtered_contracts = [
            row
            for row in filtered_contracts
            if row.get("manager_eid") in selected_manager_eids
        ]

    # Se filtro Technology o Opportunity Status,
    # considero solo i contratti collegati alle opportunity rimaste.
    if selected_technologies or selected_statuses:
        visible_contract_ids = {
            row.get("contract_id")
            for row in filtered_commercial
            if row.get("contract_id")
        }

        filtered_contracts = [
            row
            for row in filtered_contracts
            if row.get("contract_id") in visible_contract_ids
        ]

    # ── KPI LIVE ──────────────────────────────────────────────────────────────
    opportunity_value = sum(
        float(row.get("opportunity_value") or 0)
        for row in filtered_commercial
    )

    pipeline_value = sum(
        float(row.get("opportunity_value") or 0)
        for row in filtered_commercial
        if row.get("opportunity_status") == "Pipeline"
    )

    contract_revenue = sum(
        float(row.get("contract_revenue") or 0)
        for row in filtered_contracts
    )

    contract_costs = sum(
        float(row.get("contract_costs") or 0)
        for row in filtered_contracts
    )

    contract_margin = (
        contract_revenue
        - contract_costs
    )

    opportunity_count = len(
        filtered_commercial
    )

    active_contract_count = sum(
        1
        for row in filtered_contracts
        if row.get("contract_status") == "Active"
    )

    available_resources = sum(
        1
        for resource in resource_rows
        if int(resource.get("disponibilita") or 0) > 0
    )

    fully_allocated_resources = sum(
        1
        for resource in resource_rows
        if int(resource.get("disponibilita") or 0) == 0
    )

    # ── KPI COMMERCIALI ───────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("### Commercial Overview")

    kpi1, kpi2, kpi3, kpi4 = st.columns(4)

    kpi1.metric(
        "Opportunity Value",
        f"€ {opportunity_value / 1_000_000:.2f} M"
    )

    kpi2.metric(
        "Pipeline Value",
        f"€ {pipeline_value / 1_000_000:.2f} M"
    )

    kpi3.metric(
        "Contract Revenue",
        f"€ {contract_revenue / 1_000_000:.2f} M"
    )

    kpi4.metric(
        "Margin",
        f"€ {contract_margin / 1_000_000:.2f} M"
    )

    kpi5, kpi6, kpi7, kpi8 = st.columns(4)

    kpi5.metric(
        "Opportunity",
        opportunity_count
    )

    kpi6.metric(
        "Contratti attivi",
        active_contract_count
    )

    kpi7.metric(
        "Risorse disponibili",
        available_resources
    )

    kpi8.metric(
        "Fully allocated",
        fully_allocated_resources
    )
        # ── GRAFICI COMMERCIALI ───────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("### Commercial Performance")

    # Aggregazione Opportunity per Technology
    technology_value = {}

    for row in filtered_commercial:
        technology = row.get("main_tech_cluster") or "Non classificata"

        technology_value[technology] = (
            technology_value.get(technology, 0)
            + float(row.get("opportunity_value") or 0)
        )

    technology_sorted = sorted(
        technology_value.items(),
        key=lambda item: item[1],
        reverse=True
    )

    # Aggregazione Opportunity per numero
    technology_count = {}

    for row in filtered_commercial:
        technology = row.get("main_tech_cluster") or "Non classificata"

        technology_count[technology] = (
            technology_count.get(technology, 0) + 1
        )

    technology_count_sorted = sorted(
        technology_count.items(),
        key=lambda item: item[1],
        reverse=True
    )

    # Aggregazione Revenue per Industry
    industry_revenue = {}

    for row in filtered_contracts:
        industry = row.get("industry_sector") or "Non classificata"

        industry_revenue[industry] = (
            industry_revenue.get(industry, 0)
            + float(row.get("contract_revenue") or 0)
        )

    industry_sorted = sorted(
        industry_revenue.items(),
        key=lambda item: item[1],
        reverse=True
    )

    chart_col1, chart_col2 = st.columns(2)

    # ── Opportunity Value by Technology ───────────────────────────────────────
    with chart_col1:
        st.markdown("#### Opportunity Value by Technology")

        fig_technology_value = go.Figure()

        fig_technology_value.add_trace(
            go.Bar(
                x=[
                    item[0]
                    for item in technology_sorted
                ],
                y=[
                    item[1]
                    for item in technology_sorted
                ],
                marker_color=[
                    dashboard_palette[i % len(dashboard_palette)]
                    for i in range(len(technology_sorted))
                ],
                hovertemplate=(
                    "<b>%{x}</b><br>"
                    "Value: €%{y:,.0f}"
                    "<extra></extra>"
                )
            )
        )

        fig_technology_value.update_layout(
            height=380,
            margin=dict(
                l=20,
                r=20,
                t=20,
                b=80
            ),
            showlegend=False,
            plot_bgcolor="white",
            paper_bgcolor="white",
            yaxis_title="Opportunity Value (€)",
            xaxis_title=""
        )

        st.plotly_chart(
            fig_technology_value,
            use_container_width=True
        )

    # ── Technology Distribution ───────────────────────────────────────────────
    with chart_col2:
        st.markdown("#### Technology Distribution")

        fig_technology_distribution = go.Figure(
            data=[
                go.Pie(
                    labels=[
                        item[0]
                        for item in technology_sorted
                    ],
                    values=[
                        item[1]
                        for item in technology_sorted
                    ],
                    hole=0.58,
                    marker=dict(
                        colors=dashboard_palette
                    ),
                    hovertemplate=(
                        "<b>%{label}</b><br>"
                        "Value: €%{value:,.0f}<br>"
                        "%{percent}"
                        "<extra></extra>"
                    )
                )
            ]
        )

        fig_technology_distribution.update_layout(
            height=380,
            margin=dict(
                l=20,
                r=20,
                t=20,
                b=20
            ),
            showlegend=True,
            legend=dict(
                orientation="v"
            ),
            paper_bgcolor="white"
        )

        st.plotly_chart(
            fig_technology_distribution,
            use_container_width=True
        )

    chart_col3, chart_col4 = st.columns(2)

    # ── Revenue by Industry ───────────────────────────────────────────────────
    with chart_col3:
        st.markdown("#### Contract Revenue by Industry")

        fig_industry = go.Figure()

        fig_industry.add_trace(
            go.Bar(
                x=[
                    item[0]
                    for item in industry_sorted
                ],
                y=[
                    item[1]
                    for item in industry_sorted
                ],
                marker_color=[
                    dashboard_palette[i % len(dashboard_palette)]
                    for i in range(len(industry_sorted))
                ],
                hovertemplate=(
                    "<b>%{x}</b><br>"
                    "Revenue: €%{y:,.0f}"
                    "<extra></extra>"
                )
            )
        )

        fig_industry.update_layout(
            height=380,
            margin=dict(
                l=20,
                r=20,
                t=20,
                b=80
            ),
            showlegend=False,
            plot_bgcolor="white",
            paper_bgcolor="white",
            yaxis_title="Revenue (€)",
            xaxis_title=""
        )

        st.plotly_chart(
            fig_industry,
            use_container_width=True
        )

    # ── Technology Ranking ────────────────────────────────────────────────────
    with chart_col4:
        st.markdown("#### Technology Ranking")

        ranking_desc = technology_count_sorted[:10]
        ranking_display = list(
            reversed(ranking_desc)
        )

        fig_ranking = go.Figure()

        fig_ranking.add_trace(
            go.Bar(
                x=[
                    item[1]
                    for item in ranking_display
                ],
                y=[
                    item[0]
                    for item in ranking_display
                ],
                orientation="h",
                marker_color=[
                    dashboard_palette[i % len(dashboard_palette)]
                    for i in range(len(ranking_display))
                ],
                text=[
                    item[1]
                    for item in ranking_display
                ],
                textposition="outside",
                hovertemplate=(
                    "<b>%{y}</b><br>"
                    "Opportunity: %{x}"
                    "<extra></extra>"
                )
            )
        )

        fig_ranking.update_layout(
            height=380,
            margin=dict(
                l=20,
                r=40,
                t=20,
                b=20
            ),
            showlegend=False,
            plot_bgcolor="white",
            paper_bgcolor="white",
            xaxis_title="Numero Opportunity",
            yaxis_title=""
        )

        st.plotly_chart(
            fig_ranking,
            use_container_width=True
        )
        # ── STAFFING OVERVIEW ─────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("### Staffing Overview")

    # Se sono attivi filtri commerciali, mostriamo le risorse
    # associate alle opportunity rimaste dopo i filtri.
    commercial_filters_active = any([
        selected_industries,
        selected_clients,
        selected_technologies,
        selected_statuses,
        selected_service_groups,
        selected_manager_eids
    ])

    filtered_resources = resource_rows

    if commercial_filters_active:
        visible_opportunity_ids = {
            row.get("opportunity_id")
            for row in filtered_commercial
            if row.get("opportunity_id")
        }

        visible_resource_eids = {
            row.get("resource_eid")
            for row in osr_rows
            if row.get("opportunity_id") in visible_opportunity_ids
        }

        filtered_resources = [
            resource
            for resource in resource_rows
            if resource.get("eid") in visible_resource_eids
        ]

    # ── KPI STAFFING DINAMICI ─────────────────────────────────────────────────
    staffing_total = len(filtered_resources)

    staffing_available = sum(
        1
        for resource in filtered_resources
        if int(resource.get("disponibilita") or 0) > 0
    )

    staffing_fully_allocated = sum(
        1
        for resource in filtered_resources
        if int(resource.get("disponibilita") or 0) == 0
    )

    staffing_average_allocation = (
        sum(
            min(
                int(resource.get("active_allocation") or 0),
                100
            )
            for resource in filtered_resources
        ) / staffing_total
        if staffing_total > 0
        else 0
    )

    staffing_kpi1, staffing_kpi2, staffing_kpi3, staffing_kpi4 = st.columns(4)

    staffing_kpi1.metric(
        "Risorse",
        staffing_total
    )

    staffing_kpi2.metric(
        "Disponibili",
        staffing_available
    )

    staffing_kpi3.metric(
        "Fully allocated",
        staffing_fully_allocated
    )

    staffing_kpi4.metric(
        "Allocazione media",
        f"{staffing_average_allocation:.1f}%"
    )

    # ── AGGREGAZIONI STAFFING ─────────────────────────────────────────────────
    availability_distribution = {
        "Disponibili": 0,
        "Parzialmente allocate": 0,
        "Fully allocated": 0
    }

    level_distribution = {}
    skill_distribution = {}
    manager_distribution = {}

    for resource in filtered_resources:
        availability_status = resource.get(
            "availability_status",
            "green"
        )

        if availability_status == "red":
            availability_distribution[
                "Fully allocated"
            ] += 1

        elif availability_status == "orange":
            availability_distribution[
                "Parzialmente allocate"
            ] += 1

        else:
            availability_distribution[
                "Disponibili"
            ] += 1

        level_name = (
            resource.get("level_name")
            or "Non classificato"
        )

        level_distribution[level_name] = (
            level_distribution.get(level_name, 0) + 1
        )

        for skill in resource.get("skills", []):
            skill_name = skill.get("skill_name")

            if skill_name:
                skill_distribution[skill_name] = (
                    skill_distribution.get(skill_name, 0) + 1
                )

        for manager in resource.get("managers", []):
            manager_name = (
                f"{manager.get('nome', '')} "
                f"{manager.get('cognome', '')}"
            ).strip()

            if manager_name:
                manager_distribution[manager_name] = (
                    manager_distribution.get(
                        manager_name,
                        0
                    ) + 1
                )

    level_sorted = sorted(
        level_distribution.items(),
        key=lambda item: item[1],
        reverse=True
    )

    skill_sorted = sorted(
        skill_distribution.items(),
        key=lambda item: item[1],
        reverse=True
    )[:10]

    manager_sorted = sorted(
        manager_distribution.items(),
        key=lambda item: item[1],
        reverse=True
    )[:10]

    staffing_col1, staffing_col2 = st.columns(2)

    # ── RESOURCE AVAILABILITY ─────────────────────────────────────────────────
    with staffing_col1:
        st.markdown("#### Resource Availability")

        fig_availability = go.Figure(
            data=[
                go.Pie(
                    labels=list(
                        availability_distribution.keys()
                    ),
                    values=list(
                        availability_distribution.values()
                    ),
                    hole=0.60,
                    marker=dict(
                        colors=[
                            "#DC2626",  # Disponibili,
                            "#F59E0B",  # Parzialmente allocate
                            "#16A34A"   # Fully allocated
                        ]
                    ),
                    hovertemplate=(
                        "<b>%{label}</b><br>"
                        "Risorse: %{value}<br>"
                        "%{percent}"
                        "<extra></extra>"
                    )
                )
            ]
        )

        fig_availability.update_layout(
            height=380,
            margin=dict(
                l=20,
                r=20,
                t=20,
                b=20
            ),
            showlegend=True,
            paper_bgcolor="white",
            annotations=[
                dict(
                    text=str(staffing_total),
                    x=0.5,
                    y=0.5,
                    font_size=28,
                    showarrow=False
                )
            ]
        )

        st.plotly_chart(
            fig_availability,
            use_container_width=True
        )

    # ── RESOURCES BY LEVEL ────────────────────────────────────────────────────
    with staffing_col2:
        st.markdown("#### Resources by Level")

        level_display = list(
            reversed(level_sorted)
        )

        fig_levels = go.Figure()

        fig_levels.add_trace(
            go.Bar(
                x=[
                    item[1]
                    for item in level_display
                ],
                y=[
                    item[0]
                    for item in level_display
                ],
                orientation="h",
                marker_color=[
                    dashboard_palette[i % len(dashboard_palette)]
                    for i in range(len(level_display))
                ],
                text=[
                    item[1]
                    for item in level_display
                ],
                textposition="outside",
                hovertemplate=(
                    "<b>%{y}</b><br>"
                    "Risorse: %{x}"
                    "<extra></extra>"
                )
            )
        )

        fig_levels.update_layout(
            height=380,
            margin=dict(
                l=20,
                r=40,
                t=20,
                b=20
            ),
            showlegend=False,
            plot_bgcolor="white",
            paper_bgcolor="white",
            xaxis_title="Numero risorse",
            yaxis_title=""
        )

        st.plotly_chart(
            fig_levels,
            use_container_width=True
        )

    staffing_col3, staffing_col4 = st.columns(2)

    # ── TOP SKILLS ─────────────────────────────────────────────────────────────
    with staffing_col3:
        st.markdown("#### Top Skills")

        skill_display = list(
            reversed(skill_sorted)
        )

        fig_skills = go.Figure()

        fig_skills.add_trace(
            go.Bar(
                x=[
                    item[1]
                    for item in skill_display
                ],
                y=[
                    item[0]
                    for item in skill_display
                ],
                orientation="h",
                marker_color=[
                    dashboard_palette[i % len(dashboard_palette)]
                    for i in range(len(skill_display))
                ],
                text=[
                    item[1]
                    for item in skill_display
                ],
                textposition="outside",
                hovertemplate=(
                    "<b>%{y}</b><br>"
                    "Risorse: %{x}"
                    "<extra></extra>"
                )
            )
        )

        fig_skills.update_layout(
            height=380,
            margin=dict(
                l=20,
                r=40,
                t=20,
                b=20
            ),
            showlegend=False,
            plot_bgcolor="white",
            paper_bgcolor="white",
            xaxis_title="Numero risorse",
            yaxis_title=""
        )

        st.plotly_chart(
            fig_skills,
            use_container_width=True
        )

    # ── STAFFING BY MANAGER ───────────────────────────────────────────────────
    with staffing_col4:
        st.markdown("#### Staffing by Manager")

        manager_display = list(
            reversed(manager_sorted)
        )

        if manager_display:
            fig_managers = go.Figure()

            fig_managers.add_trace(
                go.Bar(
                    x=[
                        item[1]
                        for item in manager_display
                    ],
                    y=[
                        item[0]
                        for item in manager_display
                    ],
                    orientation="h",
                    marker_color=[
                        dashboard_palette[i % len(dashboard_palette)]
                        for i in range(len(manager_display))
                    ],
                    text=[
                        item[1]
                        for item in manager_display
                    ],
                    textposition="outside",
                    hovertemplate=(
                        "<b>%{y}</b><br>"
                        "Risorse: %{x}"
                        "<extra></extra>"
                    )
                )
            )

            fig_managers.update_layout(
                height=380,
                margin=dict(
                    l=20,
                    r=40,
                    t=20,
                    b=20
                ),
                showlegend=False,
                plot_bgcolor="white",
                paper_bgcolor="white",
                xaxis_title="Risorse su OSR valide",
                yaxis_title=""
            )

            st.plotly_chart(
                fig_managers,
                use_container_width=True
            )

        else:
            st.info(
                "Nessun manager associato alle OSR valide "
                "per i filtri selezionati."
            )
# ── GESTIONE STAFFING V2 ─────────────────────────────────────────────────────
def show_staffing_management_v2(groups):

    if "staffing_v2_view" not in st.session_state:
        st.session_state["staffing_v2_view"] = "osr"

    st.markdown(
        '<p class="main-title">🗂 Gestione Staffing v2</p>',
        unsafe_allow_html=True
    )

    # ── NAVIGAZIONE ───────────────────────────────────────────────────────────
    nav_osr, nav_opp, nav_contract = st.columns(3)

    with nav_osr:
        if st.button(
            "👥 OSR",
            use_container_width=True,
            type="primary"
            if st.session_state["staffing_v2_view"] == "osr"
            else "secondary",
            key="staffing_nav_osr"
        ):
            st.session_state["staffing_v2_view"] = "osr"
            st.rerun()

    with nav_opp:
        if st.button(
            "💼 Opportunity",
            use_container_width=True,
            type="primary"
            if st.session_state["staffing_v2_view"] == "opportunity"
            else "secondary",
            key="staffing_nav_opportunity"
        ):
            st.session_state["staffing_v2_view"] = "opportunity"
            st.rerun()

    with nav_contract:
        if st.button(
            "📄 Contratti",
            use_container_width=True,
            type="primary"
            if st.session_state["staffing_v2_view"] == "contract"
            else "secondary",
            key="staffing_nav_contract"
        ):
            st.session_state["staffing_v2_view"] = "contract"
            st.rerun()

    st.markdown("---")

    # ── DATI LIVE ─────────────────────────────────────────────────────────────
    response = api(
        "GET",
        "/sm/staffing-management-v2"
    )

    if response is None:
        st.error("Nessuna risposta dal backend.")
        return

    if response.status_code != 200:
        st.error(
            f"Errore nel caricamento: {_api_detail(response)}"
        )
        return

    data = response.json()

    osr_rows = data.get("osr", [])
    opportunity_rows = data.get("opportunities", [])
    contract_rows = data.get("contracts", [])

    # ── VISTA OSR ─────────────────────────────────────────────────────────────
    if st.session_state["staffing_v2_view"] == "osr":

        st.markdown("### OSR")

        filter_1, filter_2, filter_3 = st.columns([3, 2, 2])

        with filter_1:
            osr_search = st.text_input(
                "🔍 Cerca OSR, risorsa, EID, opportunity o cliente",
                key="staffing_osr_search"
            )

        osr_statuses = sorted({
            row.get("calculated_status")
            for row in osr_rows
            if row.get("calculated_status")
        })

        with filter_2:
            selected_osr_statuses = st.multiselect(
                "Stato OSR",
                osr_statuses,
                key="staffing_osr_status"
            )

        with filter_3:
            only_missing_resources = st.checkbox(
                "OSR senza risorsa",
                key="staffing_osr_missing_resource"
            )

        filter_4, filter_5, filter_6 = st.columns(3)

        opportunity_options = sorted({
            row.get("opportunity_title")
            for row in osr_rows
            if row.get("opportunity_title")
        })

        with filter_4:
            selected_osr_opportunities = st.multiselect(
                "Opportunity",
                opportunity_options,
                key="staffing_osr_opportunity"
            )

        role_options = sorted({
            row.get("project_role")
            for row in osr_rows
            if row.get("project_role")
        })

        with filter_5:
            selected_roles = st.multiselect(
                "Ruolo",
                role_options,
                key="staffing_osr_role"
            )

        manager_options = sorted({
            (
                f"{row.get('manager_nome') or ''} "
                f"{row.get('manager_cognome') or ''}"
            ).strip()
            for row in osr_rows
            if row.get("manager_eid") is not None
        })

        with filter_6:
            selected_osr_managers = st.multiselect(
                "Manager",
                manager_options,
                key="staffing_osr_manager"
            )

        # ── APPLICAZIONE FILTRI OSR ───────────────────────────────────────────
        filtered_osr = osr_rows

        if osr_search:
            search_value = osr_search.strip().lower()

            filtered_osr = [
                row
                for row in filtered_osr
                if search_value in (
                    f"{row.get('osr_id', '')} "
                    f"{row.get('resource_eid', '')} "
                    f"{row.get('resource_nome', '')} "
                    f"{row.get('resource_cognome', '')} "
                    f"{row.get('opportunity_id', '')} "
                    f"{row.get('opportunity_title', '')} "
                    f"{row.get('client_name', '')}"
                ).lower()
            ]

        if selected_osr_statuses:
            filtered_osr = [
                row
                for row in filtered_osr
                if row.get("calculated_status")
                in selected_osr_statuses
            ]

        if only_missing_resources:
            filtered_osr = [
                row
                for row in filtered_osr
                if row.get("resource_missing") is True
            ]

        if selected_osr_opportunities:
            filtered_osr = [
                row
                for row in filtered_osr
                if row.get("opportunity_title")
                in selected_osr_opportunities
            ]

        if selected_roles:
            filtered_osr = [
                row
                for row in filtered_osr
                if row.get("project_role")
                in selected_roles
            ]

        if selected_osr_managers:
            filtered_osr = [
                row
                for row in filtered_osr
                if (
                    f"{row.get('manager_nome') or ''} "
                    f"{row.get('manager_cognome') or ''}"
                ).strip()
                in selected_osr_managers
            ]

        # ── KPI OSR DINAMICI ──────────────────────────────────────────────────
        active_osr = sum(
            1 for row in filtered_osr
            if row.get("calculated_status") == "Active"
        )

        rolling_off_osr = sum(
            1 for row in filtered_osr
            if row.get("calculated_status") == "Rolling-off"
        )

        closed_osr = sum(
            1 for row in filtered_osr
            if row.get("calculated_status") == "Closed"
        )

        missing_resource_osr = sum(
            1 for row in filtered_osr
            if row.get("resource_missing") is True
        )

        kpi1, kpi2, kpi3, kpi4 = st.columns(4)

        kpi1.metric(
            "🟢 Active",
            active_osr
        )

        kpi2.metric(
            "🟠 Rolling-off",
            rolling_off_osr
        )

        kpi3.metric(
            "🔴 Closed",
            closed_osr
        )

        kpi4.metric(
            "⚠️ Senza risorsa",
            missing_resource_osr
        )

        st.caption(
            f"{len(filtered_osr)} OSR trovate su {len(osr_rows)}"
        )

        # ── TABELLA OSR ───────────────────────────────────────────────────────
        osr_table = []

        for row in filtered_osr:

            resource_name = (
                f"{row.get('resource_nome') or ''} "
                f"{row.get('resource_cognome') or ''}"
            ).strip()

            manager_name = (
                f"{row.get('manager_nome') or ''} "
                f"{row.get('manager_cognome') or ''}"
            ).strip()

            status = row.get("calculated_status")

            status_label = {
                "Active": "🟢 Active",
                "Rolling-off": "🟠 Rolling-off",
                "Closed": "🔴 Closed"
            }.get(
                status,
                status or "—"
            )

            osr_table.append({
                "Stato": status_label,
                "OSR ID": row.get("osr_id", ""),
                "EID": row.get("resource_eid", ""),
                "Risorsa": resource_name or "⚠️ Non censita",
                "Opportunity": row.get(
                    "opportunity_title",
                    ""
                ),
                "Cliente": row.get(
                    "client_name",
                    ""
                ),
                "Ruolo": row.get(
                    "project_role",
                    ""
                ),
                "Allocazione %": row.get(
                    "allocation_pct",
                    0
                ),
                "Chargeability %": row.get(
                    "chargeability_pct",
                    0
                ),
                "Data inizio": row.get(
                    "start_date",
                    ""
                ),
                "Data fine": row.get(
                    "end_date",
                    ""
                ),
                "Manager": manager_name
            })

        st.dataframe(
            osr_table,
            use_container_width=True,
            hide_index=True
        )

    # ── VISTA OPPORTUNITY - PLACEHOLDER ───────────────────────────────────────
    elif st.session_state["staffing_v2_view"] == "opportunity":

        st.markdown("### Opportunity")

        # ── FILTRI OPPORTUNITY ────────────────────────────────────────────────
        filter_1, filter_2, filter_3 = st.columns([3, 2, 2])

        with filter_1:
            opportunity_search = st.text_input(
                "🔍 Cerca ID, titolo, cliente o contratto",
                key="staffing_opportunity_search"
            )

        stage_options = sorted({
            row.get("opportunity_stage")
            for row in opportunity_rows
            if row.get("opportunity_stage")
        })

        with filter_2:
            selected_stages = st.multiselect(
                "Stage",
                stage_options,
                key="staffing_opportunity_stage"
            )

        status_options = sorted({
            row.get("opportunity_status")
            for row in opportunity_rows
            if row.get("opportunity_status")
        })

        with filter_3:
            selected_statuses = st.multiselect(
                "Status",
                status_options,
                key="staffing_opportunity_status"
            )

        filter_4, filter_5, filter_6 = st.columns(3)

        technology_options = sorted({
            row.get("main_tech_cluster")
            for row in opportunity_rows
            if row.get("main_tech_cluster")
        })

        with filter_4:
            selected_technologies = st.multiselect(
                "Technology",
                technology_options,
                key="staffing_opportunity_technology"
            )

        functional_area_options = sorted({
            row.get("functional_area")
            for row in opportunity_rows
            if row.get("functional_area")
        })

        with filter_5:
            selected_functional_areas = st.multiselect(
                "Functional Area",
                functional_area_options,
                key="staffing_opportunity_functional_area"
            )

        client_options = sorted({
            row.get("client_name")
            for row in opportunity_rows
            if row.get("client_name")
        })

        with filter_6:
            selected_clients = st.multiselect(
                "Cliente",
                client_options,
                key="staffing_opportunity_client"
            )

        only_without_contract = st.checkbox(
            "Opportunity senza contratto",
            key="staffing_opportunity_without_contract"
        )

        # ── APPLICAZIONE FILTRI ───────────────────────────────────────────────
        filtered_opportunities = opportunity_rows

        if opportunity_search:
            search_value = opportunity_search.strip().lower()

            filtered_opportunities = [
                row
                for row in filtered_opportunities
                if search_value in (
                    f"{row.get('opportunity_id', '')} "
                    f"{row.get('opportunity_title', '')} "
                    f"{row.get('client_name', '')} "
                    f"{row.get('contract_id', '')} "
                    f"{row.get('contract_title', '')}"
                ).lower()
            ]

        if selected_stages:
            filtered_opportunities = [
                row
                for row in filtered_opportunities
                if row.get("opportunity_stage") in selected_stages
            ]

        if selected_statuses:
            filtered_opportunities = [
                row
                for row in filtered_opportunities
                if row.get("opportunity_status") in selected_statuses
            ]

        if selected_technologies:
            filtered_opportunities = [
                row
                for row in filtered_opportunities
                if row.get("main_tech_cluster") in selected_technologies
            ]

        if selected_functional_areas:
            filtered_opportunities = [
                row
                for row in filtered_opportunities
                if row.get("functional_area") in selected_functional_areas
            ]

        if selected_clients:
            filtered_opportunities = [
                row
                for row in filtered_opportunities
                if row.get("client_name") in selected_clients
            ]

        if only_without_contract:
            filtered_opportunities = [
                row
                for row in filtered_opportunities
                if row.get("contract_missing") is True
            ]

        # ── KPI ────────────────────────────────────────────────────────────────
        opportunity_value = sum(
            float(row.get("opportunity_value") or 0)
            for row in filtered_opportunities
        )

        opportunity_osr_count = sum(
            int(row.get("osr_count") or 0)
            for row in filtered_opportunities
        )

        opportunities_without_contract = sum(
            1
            for row in filtered_opportunities
            if row.get("contract_missing") is True
        )

        kpi1, kpi2, kpi3, kpi4 = st.columns(4)

        kpi1.metric(
            "Opportunity",
            len(filtered_opportunities)
        )

        kpi2.metric(
            "Valore",
            f"€ {opportunity_value:,.0f}"
        )

        kpi3.metric(
            "OSR collegate",
            opportunity_osr_count
        )

        kpi4.metric(
            "Senza contratto",
            opportunities_without_contract
        )

        st.caption(
            f"{len(filtered_opportunities)} opportunity "
            f"trovate su {len(opportunity_rows)}"
        )

        # ── TABELLA ───────────────────────────────────────────────────────────
        opportunity_table = []

        for row in filtered_opportunities:
            opportunity_table.append({
                "Opportunity ID":
                    row.get("opportunity_id", ""),

                "Titolo":
                    row.get("opportunity_title", ""),

                "Contratto":
                    row.get("contract_id")
                    or "⚠️ Nessun contratto",

                "Cliente":
                    row.get("client_name", ""),

                "Stage":
                    row.get("opportunity_stage", ""),

                "Status":
                    row.get("opportunity_status", ""),

                "Technology":
                    row.get("main_tech_cluster", ""),

                "Functional Area":
                    row.get("functional_area", ""),

                "Data inizio":
                    row.get("start_date", ""),

                "Data fine":
                    row.get("end_date", ""),

                "Valore":
                    row.get("opportunity_value", 0),

                "OSR":
                    row.get("osr_count", 0),

                "Allocazione totale %":
                    row.get("total_allocation", 0)
            })

        st.dataframe(
            opportunity_table,
            use_container_width=True,
            hide_index=True
        )   
    # ── VISTA CONTRATTI - PLACEHOLDER ─────────────────────────────────────────
    elif st.session_state["staffing_v2_view"] == "contract":

        st.markdown("### Contratti")

        # ── FILTRI CONTRATTI ──────────────────────────────────────────────────
        filter_1, filter_2, filter_3 = st.columns([3, 2, 2])

        with filter_1:
            contract_search = st.text_input(
                "🔍 Cerca ID, titolo o cliente",
                key="staffing_contract_search"
            )

        contract_status_options = sorted({
            row.get("contract_status")
            for row in contract_rows
            if row.get("contract_status")
        })

        with filter_2:
            selected_contract_statuses = st.multiselect(
                "Status",
                contract_status_options,
                key="staffing_contract_status"
            )

        industry_options = sorted({
            row.get("industry_sector")
            for row in contract_rows
            if row.get("industry_sector")
        })

        with filter_3:
            selected_industries = st.multiselect(
                "Industry",
                industry_options,
                key="staffing_contract_industry"
            )

        filter_4, filter_5, filter_6 = st.columns(3)

        country_options = sorted({
            row.get("country")
            for row in contract_rows
            if row.get("country")
        })

        with filter_4:
            selected_countries = st.multiselect(
                "Country",
                country_options,
                key="staffing_contract_country"
            )

        service_group_options = sorted({
            row.get("service_group")
            for row in contract_rows
            if row.get("service_group")
        })

        with filter_5:
            selected_service_groups = st.multiselect(
                "Service Group",
                service_group_options,
                key="staffing_contract_service_group"
            )

        manager_options = sorted({
            (
                f"{row.get('manager_nome') or ''} "
                f"{row.get('manager_cognome') or ''}"
            ).strip()
            for row in contract_rows
            if row.get("manager_eid") is not None
        })

        with filter_6:
            selected_contract_managers = st.multiselect(
                "Manager",
                manager_options,
                key="staffing_contract_manager"
            )

        only_cross_practice = st.checkbox(
            "Solo Cross-Practice",
            key="staffing_contract_cross_practice"
        )

        # ── APPLICAZIONE FILTRI ───────────────────────────────────────────────
        filtered_contracts = contract_rows

        if contract_search:
            search_value = contract_search.strip().lower()

            filtered_contracts = [
                row
                for row in filtered_contracts
                if search_value in (
                    f"{row.get('contract_id', '')} "
                    f"{row.get('contract_title', '')} "
                    f"{row.get('client_name', '')}"
                ).lower()
            ]

        if selected_contract_statuses:
            filtered_contracts = [
                row
                for row in filtered_contracts
                if row.get("contract_status")
                in selected_contract_statuses
            ]

        if selected_industries:
            filtered_contracts = [
                row
                for row in filtered_contracts
                if row.get("industry_sector")
                in selected_industries
            ]

        if selected_countries:
            filtered_contracts = [
                row
                for row in filtered_contracts
                if row.get("country")
                in selected_countries
            ]

        if selected_service_groups:
            filtered_contracts = [
                row
                for row in filtered_contracts
                if row.get("service_group")
                in selected_service_groups
            ]

        if selected_contract_managers:
            filtered_contracts = [
                row
                for row in filtered_contracts
                if (
                    f"{row.get('manager_nome') or ''} "
                    f"{row.get('manager_cognome') or ''}"
                ).strip()
                in selected_contract_managers
            ]

        if only_cross_practice:
            filtered_contracts = [
                row
                for row in filtered_contracts
                if bool(row.get("is_cross_practice")) is True
            ]

        # ── KPI ────────────────────────────────────────────────────────────────
        total_revenue = sum(
            float(row.get("contract_revenue") or 0)
            for row in filtered_contracts
        )

        total_costs = sum(
            float(row.get("contract_costs") or 0)
            for row in filtered_contracts
        )

        total_margin = (
            total_revenue
            - total_costs
        )

        active_contracts = sum(
            1
            for row in filtered_contracts
            if row.get("contract_status") == "Active"
        )

        kpi1, kpi2, kpi3, kpi4 = st.columns(4)

        kpi1.metric(
            "Contratti",
            len(filtered_contracts)
        )

        kpi2.metric(
            "Attivi",
            active_contracts
        )

        kpi3.metric(
            "Revenue",
            f"€ {total_revenue:,.0f}"
        )

        kpi4.metric(
            "Margine",
            f"€ {total_margin:,.0f}"
        )

        st.caption(
            f"{len(filtered_contracts)} contratti "
            f"trovati su {len(contract_rows)}"
        )

        # ── TABELLA ───────────────────────────────────────────────────────────
        contract_table = []

        for row in filtered_contracts:
            manager_name = (
                f"{row.get('manager_nome') or ''} "
                f"{row.get('manager_cognome') or ''}"
            ).strip()

            contract_table.append({
                "Contract ID":
                    row.get("contract_id", ""),

                "Titolo":
                    row.get("contract_title", ""),

                "Cliente":
                    row.get("client_name", ""),

                "Industry":
                    row.get("industry_sector", ""),

                "Country":
                    row.get("country", ""),

                "Service Group":
                    row.get("service_group", ""),

                "Manager":
                    manager_name,

                "Data inizio":
                    row.get("start_date", ""),

                "Data fine":
                    row.get("end_date", ""),

                "Revenue":
                    row.get("contract_revenue", 0),

                "Costi":
                    row.get("contract_costs", 0),

                "Margine":
                    row.get("contract_margin", 0),

                "Status":
                    row.get("contract_status", ""),

                "Cross-Practice":
                    row.get("is_cross_practice", False),

                "DA Practice %":
                    row.get("da_practice_pct", 0),

                "Opportunity":
                    row.get("opportunity_count", 0),

                "OSR":
                    row.get("osr_count", 0)
            })

        st.dataframe(
            contract_table,
            use_container_width=True,
            hide_index=True
        )
# ── MAIN ───────────────────────────────────────────────────────────────────────
def show_matching_v2(groups):
    st.markdown('<p class="main-title">🤖 Matching AI v2 — Nuovo modello dati</p>', unsafe_allow_html=True)
    st.caption("Basato sulle 9 tabelle SM_* con dati reali (Valerio) — 150 risorse, 57 opportunity")
    st.markdown("---")

    r = api("GET", "/sm/opportunities")
    if r is None or r.status_code != 200:
        st.error("Impossibile caricare le opportunity.")
        return
    opportunities = r.json()
    if not opportunities:
        st.warning("Nessuna opportunity trovata.")
        return

    options = {
        f"{o['titolo']} ({o['main_tech_cluster']})": o["opportunity_id"]
        for o in opportunities
    }
    selected_label = st.selectbox("Scegli un'opportunity", list(options.keys()))
    selected_id = options[selected_label]

    if st.button("Esegui matching", type="primary"):
        with st.spinner("Calcolo in corso..."):
            r = api("GET", f"/sm/match/{selected_id}")
            if r is None or r.status_code != 200:
                st.error("Errore durante il matching.")
                return
            result = r.json()

        opp = result["opportunity"]
        st.subheader(f"📋 {opp['titolo']}")
        col1, col2, col3 = st.columns(3)
        col1.metric("Tech cluster", opp["main_tech_cluster"])
        col2.metric("Cliente", opp["cliente"] or "—")
        col3.metric("Candidati trovati", len(result["candidati"]))

        st.markdown("---")
        st.subheader("🏆 Classifica candidati")

        for i, c in enumerate(result["candidati"], start=1):
            emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
            with st.container(border=True):
                col_a, col_b, col_c = st.columns([1, 3, 2])
                col_a.markdown(f"### {emoji}")
                col_b.markdown(f"**{c['nome']}**")
                col_b.caption(c["motivazione"])
                col_c.metric("Score", f"{c['score']}/100")


def main():
    if st.query_params.get("logout") == "1":
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.query_params.clear()
        st.rerun()

    if not st.session_state.token:
        show_login()
        return

    groups = get_groups()
    show_sidebar(groups)

    page = st.session_state.page or "dashboard"

    if page == "dashboard":
        show_dashboard(groups)
    elif page == "risorse":
        show_risorse(groups)
    elif page == "risorsa_v2":
        show_risorsa_v2(groups)
    elif page == "dashboard_v2":
        show_dashboard_v2(groups)  
    elif page == "staffing_management_v2":
        show_staffing_management_v2(groups)    
    elif page == "progetti":
        show_progetti(groups)
    elif page == "opportunity":
        show_opportunity(groups)
    elif page == "matching":
        show_matching(groups)
    elif page == "matching_v2":
        show_matching_v2(groups)
    elif page == "chatbot":
        show_chatbot(groups)
    elif page == "approvazioni":
        show_approvazioni(groups)
    elif page == "admin":
        show_admin(groups)

main()
