import os
import base64
import streamlit as st
import requests
import plotly.graph_objects as go

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

ASSETS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")


ROLE_LABELS = {
    "Employee": "Data Explorer",
    "Manager": "Executive",
    "Executive": "Executive & Approver",
}


def role_label(name):
    return ROLE_LABELS.get(name, name)


@st.cache_resource
def _asset_b64(filename):
    with open(os.path.join(ASSETS_DIR, filename), "rb") as f:
        return base64.b64encode(f.read()).decode()


st.set_page_config(
    page_title="AI Practice Advisory — Accenture Italy",
    page_icon=os.path.join(ASSETS_DIR, "mira_icon.png"),
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
        background: linear-gradient(180deg, #1A0840 0%, #2C0F63 52%, #5B1DB5 100%) !important;
    }
    [data-testid="stSidebar"][aria-expanded="true"] {
        min-width: 17rem !important;
        max-width: 17rem !important;
        width: 17rem !important;
    }
    [data-testid="stSidebarContent"] {
        border-right: none !important;
        padding: 0 !important;
        scrollbar-gutter: auto !important;
    }
    [data-testid="stSidebarHeader"] {
        background: transparent !important;
        padding: 0 1rem !important;
        margin: 0 !important;
        height: 1.5rem !important;
        min-height: 0 !important;
    }
    [data-testid="stSidebarUserContent"] {
        padding: 0 1rem 6rem 1rem !important;
        margin: 0 !important;
    }
    [data-testid="stSidebar"] [data-testid="stVerticalBlock"] { gap: 0.4rem !important; }
    .sm-logo { text-align: center; padding: 0.25rem 0 0 0; }
    .sm-logo img { width: 100%; max-width: 190px; }
    .sm-tagline {
        text-align: center; color: #F1E9FF; font-size: 0.78rem; font-weight: 500;
        letter-spacing: 0.2em; margin-top: 0.7rem; white-space: nowrap;
    }
    .sm-tagline-sub {
        display: flex; align-items: center; gap: 0.6rem; justify-content: center;
        color: #D4C4F7; font-size: 0.72rem; letter-spacing: 0.32em; margin-top: 0.3rem;
    }
    .sm-tagline-sub::before, .sm-tagline-sub::after {
        content: ""; flex: 1; height: 1px; background: rgba(255,255,255,0.35);
    }
    .sm-logo-bar {
        width: 84px; height: 4px; border-radius: 4px; margin: 0.4rem auto 1rem auto;
        background: linear-gradient(90deg, #EC4899, #8B5CF6, #3B82F6);
    }
    section[data-testid="stSidebar"] + div { border-left: none !important; box-shadow: none !important; }
    [data-testid="stSidebar"] .stMarkdown p,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] .stCaption { color: #D9C9FF !important; }
    [data-testid="stSidebar"] .stButton > button:not([kind="primary"]) {
        background: transparent !important;
        color: #EADFFF !important;
        border: none !important;
        border-radius: 10px !important;
        justify-content: flex-start !important;
        text-align: left !important;
        font-weight: 500 !important;
        font-size: 0.95rem !important;
        padding: 10px 14px !important;
        box-shadow: none !important;
        transition: all 0.2s ease !important;
    }
    [data-testid="stSidebar"] .stButton > button:not([kind="primary"]):hover {
        background: rgba(255,255,255,0.10) !important;
        color: #ffffff !important;
        border: none !important;
        padding: 10px 14px !important;
    }
    [data-testid="stSidebar"] .stButton > button[data-testid="stBaseButton-primary"],
    [data-testid="stSidebar"] .stButton > button[data-testid="stBaseButton-primary"]:hover {
        background: linear-gradient(90deg, #7B2FF7, #8E3BF0) !important;
        color: #ffffff !important;
        border: none !important;
        padding: 10px 14px !important;
        font-weight: 600 !important;
        box-shadow: 0 4px 14px rgba(123,47,247,0.38) !important;
    }
    [data-testid="stSidebar"] .stButton > button,
    [data-testid="stSidebar"] .stButton > button > div {
        display: flex !important;
        justify-content: flex-start !important;
        width: 100% !important;
    }
    [data-testid="stSidebar"] .stButton > button p,
    [data-testid="stSidebar"] .stButton > button [data-testid="stMarkdownContainer"] { text-align: left !important; }

    /* ── MAIN AREA ── */
    .stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"] { background: #F5F2FB !important; }
    [data-testid="stHeader"] { background: transparent !important; }
    [data-testid="stMainBlockContainer"] {
        padding-top: 1.5rem !important;
        padding-bottom: 2rem !important;
        max-width: 1600px !important;
    }

    /* ── TITOLI PAGINA ── */
    .main-title {
        color: #1E1B4B;
        font-size: 1.6rem;
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

    /* ── MIRA THEME ── */
    .mira-title { font-size: 2rem; font-weight: 800; color: #1E1B4B; letter-spacing: -0.5px; line-height: 1.15; margin: 0; }
    .mira-sub { color: #6B7280; font-size: 0.95rem; margin-top: 2px; }
    .st-key-hdr_advisor button {
        border: 1.5px solid #A78BFA !important; background: #ffffff !important; color: #5B21B6 !important;
        border-radius: 999px !important; font-weight: 600 !important; box-shadow: none !important;
    }
    .st-key-hdr_advisor button:hover { background: #F3EEFF !important; border-color: #7C3AED !important; }
    [data-testid="stButtonGroup"] button[data-testid^="stBaseButton-segmented_control"] {
        border-radius: 999px !important; border: 1px solid #E4DDF5 !important; background: #ffffff !important;
        color: #4C1D95 !important; padding: 6px 24px !important; font-weight: 600 !important;
    }
    [data-testid="stButtonGroup"] button[data-testid="stBaseButton-segmented_controlActive"] {
        background: #7C3AED !important; color: #ffffff !important; border-color: #7C3AED !important;
    }
    button[data-testid="stBaseButton-primary"] { background: #7C3AED !important; border-color: #7C3AED !important; color: #ffffff !important; border-radius: 10px !important; }
    button[data-testid="stBaseButton-primary"]:hover { background: #6D28D9 !important; border-color: #6D28D9 !important; }
    [data-baseweb="select"] > div, [data-baseweb="input"], [data-baseweb="base-input"], [data-baseweb="textarea"] {
        background: #ffffff !important; border-color: #E4DDF5 !important; border-radius: 10px !important;
    }
    [data-baseweb="tag"] { background: #EDE9FE !important; color: #4C1D95 !important; }
    [data-testid="stMetric"] {
        background: #ffffff; border: 1px solid #ECE6FA; border-radius: 16px; padding: 14px 18px;
        box-shadow: 0 2px 12px rgba(76,29,149,0.07);
    }
    [data-testid="stMetricValue"] { color: #1E1B4B; font-weight: 800; }
    [data-testid="stExpander"] { background: #ffffff; border: 1px solid #ECE6FA !important; border-radius: 14px; }
    [data-testid="stVerticalBlockBorderWrapper"] {
        border-radius: 16px !important; border-color: #ECE6FA !important;
        background: #ffffff; box-shadow: 0 2px 12px rgba(76,29,149,0.07);
    }
    [class*="st-key-card"] {
        background: #ffffff !important; border: 1px solid #ECE6FA !important; border-radius: 16px !important;
        box-shadow: 0 2px 12px rgba(76,29,149,0.07) !important; padding: 0.9rem 1.1rem !important;
    }
    .card-title { font-size: 1.05rem; font-weight: 700; color: #1E1B4B; margin: 0 0 0.4rem 0; }
    .sec-title { display: flex; align-items: center; gap: 0.6rem; font-size: 1.45rem; font-weight: 800; color: #1E1B4B; margin: 0.6rem 0 0.7rem 0; letter-spacing: -0.3px; }
    .sec-ico { display: inline-flex; color: #7C3AED; }
    .flt-head { display: flex; align-items: center; gap: 0.6rem; margin-bottom: 0.3rem; }
    .flt-head .flt-ico { display: inline-flex; color: #7C3AED; }
    .flt-head .flt-title { font-size: 1.3rem; font-weight: 700; color: #1E1B4B; }
    .flt-head .chip { background: #EDE9FE; color: #6D28D9; font-size: 0.8rem; font-weight: 600; padding: 3px 12px; border-radius: 999px; }
    .st-key-dash_reset button { background: transparent !important; border: none !important; color: #6D28D9 !important; font-weight: 600 !important; box-shadow: none !important; }
    .kpi-card {
        display: flex; align-items: center; gap: 1rem; background: #ffffff; border: 1px solid #ECE6FA;
        border-radius: 16px; padding: 1rem 1.2rem; box-shadow: 0 2px 12px rgba(76,29,149,0.07); height: 100%;
    }
    .kpi-ico { display: flex; align-items: center; justify-content: center; width: 52px; height: 52px; flex: 0 0 52px; border-radius: 14px; background: #F3EEFF; color: #7C3AED; }
    .kpi-label { font-size: 0.9rem; color: #374151; }
    .kpi-value { font-size: 1.95rem; font-weight: 800; color: #1E1B4B; line-height: 1.15; }
    .tech-table { width: 100%; border-collapse: collapse; font-size: 0.85rem; color: #1E1B4B; border: none !important; }
    .tech-table th { text-align: right; font-weight: 600; padding: 7px 6px; border: none !important; border-bottom: 1px solid #ECE6FA !important; white-space: nowrap; background: transparent !important; }
    .tech-table th:first-child, .tech-table td:first-child { text-align: left; }
    .tech-table td { text-align: right; padding: 7px 6px; border: none !important; border-bottom: 1px solid #F4F0FC !important; white-space: nowrap; }
    .tech-table .dot { display: inline-block; width: 12px; height: 12px; border-radius: 3px; margin-right: 8px; vertical-align: -1px; }

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
        background: linear-gradient(135deg, #7C3AED, #6D28D9) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        padding: 10px 20px !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 4px 12px rgba(124,58,237,0.3) !important;
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
        background: linear-gradient(135deg, #7C3AED, #6D28D9) !important;
        color: white !important;
        font-weight: 600 !important;
    }
    [data-baseweb="tab-highlight"], [data-baseweb="tab-border"] {
        background-color: transparent !important; height: 0 !important;
    }
    button[role="tab"] { border-bottom: none !important; box-shadow: none !important; }
    [data-baseweb="tag"], [data-baseweb="tag"] span {
        background-color: #EDE9FE !important; color: #4C1D95 !important;
    }
    [data-testid="stBottom"], [data-testid="stBottom"] > div { background: transparent !important; }

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

        /* ── MATCHING AI · CATEGORY COLORS ───────────────────────────── */

    /* ============================================================
       SKILLS · BLUE
       ============================================================ */

    .st-key-matching_new_skills [data-baseweb="tag"] {
        background: #2563EB !important;
        color: #FFFFFF !important;
        border: none !important;
    }

    .st-key-matching_new_skills [data-baseweb="tag"] span {
        color: #FFFFFF !important;
    }

    /* Skill sliders */
    [class*="st-key-weight_skill"] [data-baseweb="slider"] div[role="slider"] {
        background-color: #2563EB !important;
        border-color: #2563EB !important;
    }

    [class*="st-key-weight_skill"] [data-baseweb="slider"] > div > div {
        background-color: #2563EB !important;
    }


    /* ============================================================
       CERTIFICATIONS · VIOLET
       ============================================================ */

    .st-key-matching_new_certifications [data-baseweb="tag"] {
        background: #8B5CF6 !important;
        color: #FFFFFF !important;
        border: none !important;
    }

    .st-key-matching_new_certifications [data-baseweb="tag"] span {
        color: #FFFFFF !important;
    }

    /* Certification sliders */
    [class*="st-key-weight_certification"] [data-baseweb="slider"] div[role="slider"] {
        background-color: #8B5CF6 !important;
        border-color: #8B5CF6 !important;
    }

    [class*="st-key-weight_certification"] [data-baseweb="slider"] > div > div {
        background-color: #8B5CF6 !important;
    }


    /* ============================================================
       LANGUAGES · TEAL / GREEN
       ============================================================ */

    .st-key-matching_new_languages [data-baseweb="tag"] {
        background: #10B981 !important;
        color: #FFFFFF !important;
        border: none !important;
    }

    .st-key-matching_new_languages [data-baseweb="tag"] span {
        color: #FFFFFF !important;
    }

    /* Language sliders */
    [class*="st-key-weight_language"] [data-baseweb="slider"] div[role="slider"] {
        background-color: #10B981 !important;
        border-color: #10B981 !important;
    }

    [class*="st-key-weight_language"] [data-baseweb="slider"] > div > div {
        background-color: #10B981 !important;
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
        st.error(f"Backend unavailable ({BACKEND_URL}).")
        return None
    except Exception as _e:
        st.error(f"API call error: {type(_e).__name__}: {_e}")
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


_ICONS = {
    "briefcase": '<rect width="20" height="14" x="2" y="7" rx="2" ry="2"/><path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/>',
    "bars": '<path d="M3 3v18h18"/><path d="M18 17V9"/><path d="M13 17V5"/><path d="M8 17v-3"/>',
    "layers": '<path d="m12.83 2.18a2 2 0 0 0-1.66 0L2.6 6.08a1 1 0 0 0 0 1.83l8.58 3.91a2 2 0 0 0 1.66 0l8.58-3.9a1 1 0 0 0 0-1.83Z"/><path d="m22 17.65-9.17 4.16a2 2 0 0 1-1.66 0L2 17.65"/><path d="m22 12.65-9.17 4.16a2 2 0 0 1-1.66 0L2 12.65"/>',
    "target": '<circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/>',
    "euro": '<circle cx="12" cy="12" r="10"/><path d="M16 8h-6a2 2 0 1 0 0 4h4a2 2 0 1 1 0 4H8"/><path d="M12 18V6"/>',
    "file": '<path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z"/><path d="M14 2v4a2 2 0 0 0 2 2h4"/><path d="M10 9H8"/><path d="M16 13H8"/><path d="M16 17H8"/>',
    "users": '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>',
    "user-check": '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><polyline points="16 11 18 13 22 9"/>',
    "filter": '<polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3"/>',
    "trend": '<polyline points="22 7 13.5 15.5 8.5 10.5 2 17"/><polyline points="16 7 22 7 22 13"/>',
    "percent": '<line x1="19" x2="5" y1="5" y2="19"/><circle cx="6.5" cy="6.5" r="2.5"/><circle cx="17.5" cy="17.5" r="2.5"/>',
}


def _svg(name, size=24):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" '
        f'fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" '
        f'stroke-linejoin="round">{_ICONS[name]}</svg>'
    )


def kpi_card(icon, label, value):
    return (
        f'<div class="kpi-card"><div class="kpi-ico">{_svg(icon, 26)}</div>'
        f'<div><div class="kpi-label">{label}</div><div class="kpi-value">{value}</div></div></div>'
    )


def section_title(text, icon):
    st.markdown(
        f'<div class="sec-title"><span class="sec-ico">{_svg(icon, 24)}</span>{text}</div>',
        unsafe_allow_html=True
    )


def card_title(text):
    st.markdown(f'<div class="card-title">{text}</div>', unsafe_allow_html=True)


def chart_layout(fig, height=360, **kwargs):
    kwargs.setdefault("margin", dict(l=10, r=10, t=10, b=10))
    fig.update_layout(
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#1E1B4B", size=12),
        **kwargs
    )
    return fig


def show_app_header():
    left, right = st.columns([6, 1.5])

    with left:
        st.markdown(
            '<div class="mira-title">D&amp;A Advisory Cockpit</div>'
            '<div class="mira-sub">Practice performance, resources and commercial insights</div>',
            unsafe_allow_html=True
        )

    with right:
        if st.button(
            "MIRA Advisor",
            icon=":material/auto_awesome:",
            key="hdr_advisor",
            use_container_width=True
        ):
            st.session_state.page = "chatbot"
            st.rerun()

def nav(page: str):
    st.session_state.page = page
    st.rerun()

# ── LOGIN ──────────────────────────────────────────────────────────────────────
def show_login():
    st.markdown("""
<style>
    [data-testid="stMainBlockContainer"], .main .block-container {
        max-width: 480px !important;
        margin-left: auto !important;
        margin-right: auto !important;
    }
    .login-app-title, .login-sub1, .login-sub2 { text-align: center; }
    [data-testid="InputInstructions"] { display: none !important; }
</style>
""", unsafe_allow_html=True)
    with st.container():
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(
            f'<div style="text-align:center;margin-bottom:0.5rem">'
            f'<img src="data:image/png;base64,{_asset_b64("mira_logo.png")}" style="width:240px;max-width:100%"></div>',
            unsafe_allow_html=True
        )
        st.markdown('<p class="login-app-title">D&amp;A Advisory Cockpit</p>', unsafe_allow_html=True)
        st.markdown(
            '<p class="login-sub1">Intelligent Staffing &amp; Practice Management Platform</p>'
            '<p class="login-sub2">D&amp;A Practice · Accenture Italy · Powered by SAP AI Core &amp; Claude</p>',
            unsafe_allow_html=True
        )
        st.markdown("<br>", unsafe_allow_html=True)

        with st.form("login"):
            email    = st.text_input("Email aziendale", placeholder="name.surname@staffmatch-demo.com")
            password = st.text_input("Password", type="password")
            ok       = st.form_submit_button("Sign in →", use_container_width=True, type="primary")

        if ok:
            if not email or not password:
                st.error("Enter email and password.")
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
                st.session_state.page = "dashboard_v2"
                st.session_state.pop("cached_groups", None)
                st.rerun()
            else:
                st.error("Invalid credentials.")

# ── SIDEBAR ────────────────────────────────────────────────────────────────────
def show_sidebar(groups):
    with st.sidebar:
        st.markdown(
            f'<div class="sm-logo"><img src="data:image/png;base64,{_asset_b64("mira_logo_dark.png")}"></div>'
            f'<div class="sm-tagline">BRINGING TALENT TOGETHER</div>'
            f'<div class="sm-tagline-sub">SINCE TODAY</div>'
            f'<div class="sm-logo-bar"></div>',
            unsafe_allow_html=True
        )
        u = st.session_state.user or {}

        # Header fisso in alto a destra — nome + Logout allineati con ⋮
        nome_hdr = u.get('nome', '')
        cognome_hdr = u.get('cognome', '')
        st.markdown(f"""
<style>
#sm-userbar {{
    background: rgba(255,255,255,0.08);
    border-radius: 10px;
    padding: 8px 12px;
    margin: 0 0 0.5rem 0;
    display: flex; align-items: center; justify-content: space-between;
}}
#sm-userbar .sm-name {{
    font-size: 0.82rem; font-weight: 600;
    color: #EADFFF; white-space: nowrap;
}}
#sm-userbar .sm-exit {{
    font-size: 0.70rem; color: #EADFFF;
    border: 1px solid #B794F6; border-radius: 6px;
    padding: 2px 8px; background: transparent; cursor: pointer;
    transition: all 0.2s ease; line-height: 1;
    text-decoration: none; display: inline-flex; align-items: center;
}}
#sm-userbar .sm-exit:hover {{ background: #7C3AED; color: white; }}
</style>
<div id="sm-userbar">
  <span class="sm-name">{nome_hdr} {cognome_hdr}</span>
  <a href="?logout=1" class="sm-exit">Logout</a>
</div>
""", unsafe_allow_html=True)

        pages = [
            (":material/bar_chart:", "Practice Cockpit", "dashboard_v2"),
            (":material/group:", "Resources", "risorsa_v2"),
            (":material/calendar_month:", "Staffing Management", "staffing_management_v2"),
            (":material/auto_fix_high:", "Match AI", "matching_v2"),
            (":material/auto_awesome:", "Practice Advisor", "chatbot"),
        ]
        if is_admin(groups):
            pages.append((":material/settings:", "Administration & Security", "admin"))

        for icon, label, key in pages:
            is_active = st.session_state.page == key
            if st.button(
                label,
                icon=icon,
                use_container_width=True,
                key=f"nav_{key}",
                type="primary" if is_active else "secondary",
            ):
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

def _api_detail(r, fallback="No response from backend"):
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
    group_map    = {role_label(g["nome"]): g["id"] for g in rgroups}

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
                                            st.success("Richiesta di rilascio inviata all'Executive & Approver.")
                                        else:
                                            detail = _api_detail(pr)
                                            st.error(f"Errore: {detail}")
                    else:
                        st.caption("Nessuna risorsa allocata.")

                    # aggiungi risorsa
                    if is_owner and can_write(groups):
                        with st.expander("➕ Aggiungi risorsa"):
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
                                    if st.form_submit_button("💾 Salva modifica", type="primary"):
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
                                            st.success("Richiesta inviata all'Executive & Approver!")
                                        else:
                                            detail = _api_detail(pr)
                                            st.error(f"Errore: {detail}")

                        # modifica info progetto
                        with st.expander("✏️ Modifica info progetto"):
                            with st.form(f"edit_prj_{p['id']}"):
                                new_nome  = st.text_input("Nome", value=p.get("nome",""))
                                new_cli   = st.text_input("Cliente", value=p.get("cliente",""))
                                new_fine  = st.text_input("Data fine (YYYY-MM-DD)", value=p.get("data_fine_prevista",""))
                                new_desc  = st.text_area("Descrizione", value=p.get("descrizione",""))
                                note_edit = st.text_input("Note per l'Executive & Approver (opzionale)")
                                if st.form_submit_button("💾 Salva modifica", type="primary"):
                                    pr = api("POST", f"/project-changes/propose/{p['id']}",
                                             json={"change_type":"update_info",
                                                   "payload":{"nome":new_nome,"cliente":new_cli,
                                                              "data_fine_prevista":new_fine,
                                                              "descrizione":new_desc},
                                                   "note_manager": note_edit})
                                    if pr and pr.status_code == 201:
                                        st.success("Richiesta di modifica inviata all'Executive & Approver!")
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
    st.caption("Ask questions about practice resources, staffing and opportunities  · Powered by **Claude** via SAP AI Core")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    if not st.session_state.chat_history:
        st.caption("✨ Start typing to explore practice data")
    else:
        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
        if st.button("🗑️ Clear conversation", key="chat_clear"):
            st.session_state.chat_history = []
            st.rerun()

    question = st.chat_input("Type your question here…")
    if question:
        st.session_state.chat_history.append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.markdown(question)

        with st.chat_message("assistant"):
            with st.spinner("Claude is processing your request…"):
                prior_history = st.session_state.chat_history[:-1]
                resp = api("POST", "/chat/", json={"question": question, "history": prior_history})
                if resp and resp.status_code == 200:
                    answer = resp.json().get("answer", "")
                else:
                    answer = f"Backend response error ({resp.status_code if resp else 'non raggiungibile'})."
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
    st.markdown('<p class="main-title">📋 Promotion Approvals</p>', unsafe_allow_html=True)
    st.caption("Opportunity promotion requests → Active Project")
    st.markdown("---")

    tab_pending, tab_history = st.tabs(["⏳ Pending", "📜 History"])

    with tab_pending:
        r = api("GET", "/promotions/pending")  # noqa: E501
        if not r or r.status_code != 200:
            st.error("Error loading requests.")
            return
        pending = r.json()

        if not pending:
            st.info("No pending requests.")
        else:
            for req in pending:
                opp = req.get("opportunity", {})
                with st.container(border=True):
                    st.markdown(f"### 🎯 {req.get('opportunity_titolo','')} — {req.get('opportunity_cliente','')}")
                    c1, c2 = st.columns(2)
                    with c1:
                        st.markdown(f"**Requested by:** {req.get('requested_by_nome','')}")
                        st.markdown(f"**Request Date:** {req.get('requested_at','')[:10]}")
                        note = req.get("note_manager","")
                        if note:
                            st.markdown(f"**Manager Notes:** {note}")
                    with c2:
                        st.markdown("**Confirmed Resources by Slot:**")
                        for sd in req.get("slots_dettaglio", []):
                            st.markdown(f"  • Slot {sd['slot_index']+1}: {sd.get('nome','')} — **{sd.get('percentuale_allocazione','')}%**")

                    st.markdown("---")
                    note_col, btn_col = st.columns([3, 2])
                    with note_col:
                        nota_exec = st.text_input("Executive Notes (optional)",
                                                  key=f"nota_{req['id']}", label_visibility="collapsed",
                                                  placeholder="Executive Notes (optional)")
                    with btn_col:
                        col_ok, col_no = st.columns(2)
                        with col_ok:
                            if st.button("✅ Approve", key=f"appr_{req['id']}", type="primary"):
                                rv = api("PATCH", f"/promotions/{req['id']}/review",
                                         params={"decision": "Approved", "note_executive": nota_exec})
                                if rv and rv.status_code == 200:
                                    st.success("✅ Opportunity promoted to Active Project!")
                                    st.rerun()
                                else:
                                    detail = _api_detail(rv)
                                    st.error(f"Errore: {detail}")
                        with col_no:
                            if st.button("❌ Reject", key=f"rif_{req['id']}"):
                                rv = api("PATCH", f"/promotions/{req['id']}/review",
                                         params={"decision": "Rejected", "note_executive": nota_exec})
                                if rv and rv.status_code == 200:
                                    st.warning("Request rejected — Opportunity returned to New status.")
                                    st.rerun()
                                else:
                                    detail = _api_detail(rv)
                                    st.error(f"Error: {detail}")

    with tab_history:
        r2 = api("GET", "/promotions/")
        if r2 and r2.status_code == 200:
            all_reqs = [x for x in r2.json() if x.get("stato") != "Pending"]
            if not all_reqs:
                st.info("No processed requests.")
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
    group_map    = {role_label(g["nome"]): g["id"] for g in rgroups}
    group_id_map = {g["id"]: role_label(g["nome"]) for g in rgroups}

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
    st.markdown('<p class="main-title">⚙️ Administration &amp; Security</p>', unsafe_allow_html=True)
    st.markdown("---")

    tab_users, tab_groups, tab_skills, tab_new_dip, tab_edit_dip = st.tabs([
        "👥 Assign Role", "🔐 Access Roles", "🛠 Skills",
        "👤 New Employee", "✏️ Edit Employee"
    ])

    with tab_users:
        st.markdown("### Assegna Ruolo a una Risorsa")
        r_res = api("GET", "/resources/")
        r_grp = api("GET", "/roles/")
        resources   = r_res.json() if r_res and r_res.status_code == 200 else []
        role_groups = r_grp.json() if r_grp and r_grp.status_code == 200 else []
        grp_map     = {role_label(g["nome"]): g["id"] for g in role_groups}
        grp_id_map  = {g["id"]: role_label(g["nome"]) for g in role_groups}

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
                "✅ Tutto ciò che può fare Data Explorer",
                "➕ Crea e modifica le proprie opportunity",
                "🤖 Lancia il Matching AI",
                "✔️ Conferma/rifiuta risorse dalla shortlist",
                "📤 Richiede promozione Opportunity → Progetto (approvazione Executive & Approver)",
                "🔧 Modifica il proprio progetto (approvazione Executive & Approver)",
            ],
            "Executive": [
                "✅ Tutto ciò che può fare Executive",
                "📋 Approva o rifiuta promozioni Opportunity → Progetto",
                "📋 Approva o rifiuta modifiche ai progetti",
            ],
            "Administrator": [
                "✅ Tutto ciò che può fare Executive & Approver",
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

            with st.expander(f"{icon} **{role_label(gname)}** — {len(utenti)} utenti assegnati"):
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
            '<p class="main-title">👥 Resources</p>',
            unsafe_allow_html=True
        )

    with button_col:
        if st.button(
            "➕ New Resource",
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
            st.error("Unable to load form values..")

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
                st.markdown("### ➕ New Resource")

            with close_col:
                if st.button(
                    "✖ Close",
                    key="close_new_resource_v2",
                    use_container_width=True
                ):
                    st.session_state["show_new_resource_v2"] = False
                    st.rerun()

            with st.form("new_resource_v2_form"):
                st.markdown("#### Resource Profile")

                col1, col2 = st.columns(2)

                with col1:
                    new_eid = st.number_input(
                        "EID *",
                        min_value=1,
                        step=1
                    )

                    new_nome = st.text_input(
                        "First Name *"
                    )

                    new_cognome = st.text_input(
                        "Last Name *"
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
                        "Years of Experience",
                        min_value=0,
                        max_value=60,
                        step=1
                    )

                    new_is_stagista = st.checkbox(
                        "Intern"
                    )

                # ── SKILL E LINGUE ─────────────────────────────────────────────
                st.markdown("#### Skills & Languages")

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
                        "Skills",
                        skill_options
                    )

                with col4:
                    new_languages = st.multiselect(
                        "Languages",
                        language_options
                    )

                # ── CERTIFICAZIONI ─────────────────────────────────────────────
                st.markdown("#### Certifications")

                certification_options = {
                    f"{item['cert_id']} - {item['nome_cert']}": item["cert_id"]
                    for item in certifications_catalog
                }

                selected_new_certifications = st.multiselect(
                    "Certifications",
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
                            "Expiration Date",
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
                    "💾 Save Resource",
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
                            "EID, First Name, Last Name and Email are required."
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
                                "✅ Resource created successfully."
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
        st.error("No response from backend.")
        return

    if response.status_code != 200:
        st.error(
            f"Loading error: {_api_detail(response)}"
        )
        return

    resources = response.json()

    if not resources:
        st.info("No resources available.")
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
            "🔍 Search by name or email",
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
            "Available Resources Only",
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
            "Certifications",
            all_certifications,
            key="risorsa_v2_certifications"
        )

    with filter_row_2[2]:
        selected_languages = st.multiselect(
            "Languages",
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
        "👥 Resources",
        total_filtered
    )

    kpi_2.metric(
        "🎓 Certified Resources",
        certified_count
    )

    kpi_3.metric(
        "✅ Available",
        available_count
    )

    kpi_4.metric(
        "🔴 Fully Allocated",
        not_available_count
    )

    st.markdown("---")

    st.caption(
        f"{total_filtered} resources found out of {len(resources)}"
    )

    # ── VISTE ─────────────────────────────────────────────────────────────────
    tab_cards, tab_table = st.tabs([
        "📋 Cards",
        "▦ Table"
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
                or "Level not specified"
            )

            intern_label = (
                " · 🌱 Intern"
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
                    st.markdown("#### Resource Profile")

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
                        f"⏳ Experience: "
                        f"**{resource.get('anni_esperienza') or 0} anni**"
                    )

                    available_from = resource.get(
                        "available_from"
                    )

                    if available_from:
                        st.markdown(
                            f"📅 available_from: "
                            f"**{available_from}**"
                        )
                    else:
                        st.markdown(
                            "📅 Available From: **Immediately**"
                        )

                    st.markdown(
                        f"**Availability: {availability}%**"
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
                        "#### Reference Manager"
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
                            "No Reference Manager available."
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
                            "No languages available."
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
                            "No skills available."
                        )

                # ── CERTIFICAZIONI ────────────────────────────────────────────
                with col_certifications:
                    st.markdown(
                        "#### Certifications"
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
                            "No certifications available."
                        )
                st.markdown("---")
                st.markdown("#### Current Assignments")

                current_assignments = resource.get(
                    "current_assignments",
                    []
                )

                if current_assignments:
                    for assignment in current_assignments:
                        osr_status = assignment.get(
                            "osr_status"
                        )

                        if osr_status == "Active":
                            osr_icon = "🟢"

                        elif osr_status == "Rolling-off":
                            osr_icon = "🟠"

                        elif osr_status == "Closed":
                            osr_icon = "🔴"

                        else:
                            osr_icon = "⚪"

                        with st.container(border=True):
                            assign_col1, assign_col2, assign_col3 = (
                                st.columns([1.4, 1.2, 1])
                            )

                            with assign_col1:
                                st.markdown(
                                    f"**{osr_icon} "
                                    f"{assignment.get('osr_id', '')} "
                                    f"· {osr_status or '—'}**"
                                )

                                st.markdown(
                                    f"**Opportunity:** "
                                    f"{assignment.get('opportunity_title') or '—'}"
                                )

                                st.caption(
                                    f"Client: "
                                    f"{assignment.get('client_name') or '—'}"
                                )

                            with assign_col2:
                                st.markdown(
                                    f"**Project Role:** "
                                    f"{assignment.get('project_role') or '—'}"
                                )

                                st.markdown(
                                    f"**Allocation:** "
                                    f"{assignment.get('allocation_pct', 0)}%"
                                )

                            with assign_col3:
                                st.markdown(
                                    f"**Start Date:** "
                                    f"{assignment.get('start_date') or '—'}"
                                )

                                st.markdown(
                                    f"**End Date:** "
                                    f"{assignment.get('end_date') or '—'}"
                                )

                                manager_name = assignment.get(
                                    "manager_name"
                                )

                                if manager_name:
                                    st.caption(
                                        f"Manager: {manager_name}"
                                    )

                else:
                    st.caption(
                        "No active assignments."
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
                    "green": "Available",
                    "orange": "Partially Allocated",
                    "red": "Fully Allocated"
                }.get(
                    resource.get("availability_status"),
                    ""
                ),

                "EID":
                    resource.get("eid", ""),

                "Name":
                    (
                        f"{resource.get('nome', '')} "
                        f"{resource.get('cognome', '')}"
                    ).strip(),

                "Email":
                    resource.get("email", ""),

                "Level":
                    resource.get("level_name", ""),

                "Years of Experience":
                    resource.get(
                        "anni_esperienza"
                    ) or 0,

                "Active Allocation %":
                    resource.get(
                        "active_allocation"
                    ) or 0,

                "Availability %":
                    resource.get(
                        "disponibilita"
                    ) or 0,

                "Available From":
                    resource.get(
                        "available_from"
                    ) or "Immediately",
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

                "Languages":
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

                "Certifications":
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
def _reset_dashboard_filters():
    for key in (
        "dash_f_industry", "dash_f_client", "dash_f_tech",
        "dash_f_status", "dash_f_service", "dash_f_manager"
    ):
        st.session_state[key] = []


def show_dashboard_v2(groups):
    st.markdown(
        '<p style="margin:0 0 0.2rem 0;font-size:0.85rem;color:#6b7280">'
        'Select the analysis view you are interested in</p>',
        unsafe_allow_html=True
    )
    dashboard_view = st.segmented_control(
        "Dashboard view",
        ["Commercial", "Staffing"],
        default="Commercial",
        key="dashboard_v2_view",
        label_visibility="collapsed",
    ) or "Commercial"

    response = api(
        "GET",
        "/sm/dashboard-v2"
    )

    if response is None:
        st.error("No response from backend.")
        return

    if response.status_code != 200:
        st.error(
            f"Dashboard loading error: {_api_detail(response)}"
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
    manager_options = {
        manager.get("name"): manager.get("eid")
        for manager in filters.get("managers", [])
        if manager.get("name")
    }

    with st.container(key="card_filters"):
        filters_head = st.empty()

        filter_row_1 = st.columns([1, 1, 1, 0.55])

        with filter_row_1[0]:
            selected_industries = st.multiselect(
                "Industry",
                filters.get("industries", []),
                key="dash_f_industry"
            )

        with filter_row_1[1]:
            selected_clients = st.multiselect(
                "Client",
                filters.get("clients", []),
                key="dash_f_client"
            )

        with filter_row_1[2]:
            selected_technologies = st.multiselect(
                "Technology",
                filters.get("technologies", []),
                key="dash_f_tech"
            )

        with filter_row_1[3]:
            st.markdown("<div style='height:1.7rem'></div>", unsafe_allow_html=True)
            st.button(
                "Reset Filters",
                icon=":material/refresh:",
                key="dash_reset",
                on_click=_reset_dashboard_filters,
                use_container_width=True
            )

        filter_row_2 = st.columns([1, 1, 1, 0.55])

        with filter_row_2[0]:
            selected_statuses = st.multiselect(
                "Opportunity Status",
                filters.get("opportunity_statuses", []),
                key="dash_f_status"
            )

        with filter_row_2[1]:
            selected_service_groups = st.multiselect(
                "Service Group",
                filters.get("service_groups", []),
                key="dash_f_service"
            )

        with filter_row_2[2]:
            selected_manager_names = st.multiselect(
                "Manager",
                list(manager_options.keys()),
                key="dash_f_manager"
            )

        selected_manager_eids = {
            manager_options[name]
            for name in selected_manager_names
        }

        active_filters = sum(
            1 for selection in (
                selected_industries,
                selected_clients,
                selected_technologies,
                selected_statuses,
                selected_service_groups,
                selected_manager_names
            ) if selection
        )

        filters_head.markdown(
            f'<div class="flt-head"><span class="flt-ico">{_svg("filter", 22)}</span>'
            f'<span class="flt-title">Filters</span>'
            f'<span class="chip">{active_filters} active</span></div>',
            unsafe_allow_html=True
        )

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

    # ── KPI (comuni a Commercial e Staffing) ──────────────────────────────────
    section_title("Practice Indicators", "bars")

    kpi_row_1 = [
        ("briefcase", "Opportunity Value", f"€ {opportunity_value / 1_000_000:.2f} M"),
        ("bars", "Pipeline Value", f"€ {pipeline_value / 1_000_000:.2f} M"),
        ("layers", "Contract Revenue", f"€ {contract_revenue / 1_000_000:.2f} M"),
        ("target", "Margin", f"€ {contract_margin / 1_000_000:.2f} M"),
    ]
    kpi_row_2 = [
        ("euro", "Opportunities", opportunity_count),
        ("file", "Active Contracts", active_contract_count),
        ("users", "Available Resources", available_resources),
        ("user-check", "Fully Allocated", fully_allocated_resources),
    ]

    for kpi_row in (kpi_row_1, kpi_row_2):
        for column, (icon, label, value) in zip(st.columns(4), kpi_row):
            column.markdown(kpi_card(icon, label, value), unsafe_allow_html=True)
        st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

    if dashboard_view == "Commercial":
        section_title("Commercial Performance", "trend")

        technology_value = {}

        for row in filtered_commercial:
            technology = row.get("main_tech_cluster") or "Unclassified"
            technology_value[technology] = (
                technology_value.get(technology, 0)
                + float(row.get("opportunity_value") or 0)
            )

        technology_sorted = sorted(
            technology_value.items(),
            key=lambda item: item[1],
            reverse=True
        )

        technology_count = {}

        for row in filtered_commercial:
            technology = row.get("main_tech_cluster") or "Unclassified"
            technology_count[technology] = (
                technology_count.get(technology, 0) + 1
            )

        technology_count_sorted = sorted(
            technology_count.items(),
            key=lambda item: item[1],
            reverse=True
        )

        industry_value = {}

        for row in filtered_commercial:
            industry = row.get("industry_sector") or "Unclassified"
            industry_value[industry] = (
                industry_value.get(industry, 0)
                + float(row.get("opportunity_value") or 0)
            )

        industry_sorted = sorted(
            industry_value.items(),
            key=lambda item: item[1],
            reverse=True
        )

        bar_purples = [
            "#5B21B6", "#7C3AED", "#8B5CF6", "#A78BFA", "#C4B5FD", "#DDD6FE"
        ]
        tech_palette = [
            "#4C1D95", "#7C3AED", "#A855F7", "#C084FC",
            "#F97316", "#FBBF24", "#D1D5DB"
        ]

        chart_col1, chart_col2 = st.columns(2)

        # ── Opportunity Value & Technology Fragmentation ──────────────────────
        with chart_col1:
            with st.container(key="card_tech_value"):
                card_title("Opportunity Value &amp; Technology Fragmentation")

                if technology_sorted:
                    tech_names = [item[0] for item in technology_sorted]
                    tech_values = [item[1] / 1_000_000 for item in technology_sorted]
                    tech_total = sum(tech_values) or 1
                    tech_pcts = [value / tech_total * 100 for value in tech_values]

                    fig_technology_value = go.Figure()

                    fig_technology_value.add_trace(
                        go.Bar(
                            x=tech_names,
                            y=tech_values,
                            name="Opportunity Value (€ M)",
                            marker_color=[
                                bar_purples[min(i, len(bar_purples) - 1)]
                                for i in range(len(tech_names))
                            ],
                            text=[f"€ {value:.2f} M" for value in tech_values],
                            textposition="outside",
                            cliponaxis=False,
                            hovertemplate=(
                                "<b>%{x}</b><br>"
                                "Value: € %{y:.2f} M"
                                "<extra></extra>"
                            )
                        )
                    )

                    fig_technology_value.add_trace(
                        go.Scatter(
                            x=tech_names,
                            y=tech_pcts,
                            yaxis="y2",
                            name="% of Total",
                            mode="lines+markers",
                            line=dict(color="#F5B301", width=2.5),
                            marker=dict(
                                size=9,
                                color="#F5B301",
                                line=dict(color="white", width=1.5)
                            ),
                            hovertemplate="%{y:.1f}% of total<extra></extra>"
                        )
                    )

                    chart_layout(
                        fig_technology_value,
                        height=380,
                        margin=dict(l=20, r=20, t=30, b=10),
                        showlegend=True,
                        legend=dict(
                            orientation="h", y=-0.22, x=0.5, xanchor="center"
                        ),
                        yaxis=dict(
                            title="Opportunity Value (€ M)",
                            gridcolor="#EEE8FB",
                            rangemode="tozero",
                            automargin=True
                        ),
                        yaxis2=dict(
                            overlaying="y",
                            side="right",
                            ticksuffix="%",
                            showgrid=False,
                            rangemode="tozero",
                            automargin=True
                        ),
                        xaxis=dict(
                            automargin=True,
                            tickvals=tech_names,
                            ticktext=[name.replace(" ", "<br>", 1) for name in tech_names]
                        )
                    )

                    st.plotly_chart(
                        fig_technology_value,
                        use_container_width=True,
                        theme=None
                    )
                else:
                    st.info("No data for the selected filters.")

        # ── Technology Distribution (donut + tabella) ─────────────────────────
        with chart_col2:
            with st.container(key="card_tech_dist"):
                card_title("Technology Distribution")

                distribution = list(technology_sorted[:6])
                others_value = sum(item[1] for item in technology_sorted[6:])

                if others_value > 0:
                    distribution.append(("Others", others_value))

                distribution_total = sum(item[1] for item in distribution)

                if distribution_total > 0:
                    donut_col, table_col = st.columns([1, 1.35])

                    with donut_col:
                        fig_technology_distribution = go.Figure(
                            go.Pie(
                                labels=[item[0] for item in distribution],
                                values=[item[1] for item in distribution],
                                hole=0.64,
                                sort=False,
                                textinfo="none",
                                marker=dict(
                                    colors=tech_palette[:len(distribution)],
                                    line=dict(color="white", width=2)
                                ),
                                hovertemplate=(
                                    "<b>%{label}</b><br>"
                                    "Value: €%{value:,.0f}<br>"
                                    "%{percent}"
                                    "<extra></extra>"
                                )
                            )
                        )

                        chart_layout(
                            fig_technology_distribution,
                            height=380,
                            showlegend=False,
                            annotations=[
                                dict(
                                    text=(
                                        f"<b>€ {distribution_total / 1_000_000:.2f} M</b><br>"
                                        "Opportunity<br>Value"
                                    ),
                                    x=0.5,
                                    y=0.5,
                                    font=dict(size=15, color="#1E1B4B"),
                                    showarrow=False
                                )
                            ]
                        )

                        st.plotly_chart(
                            fig_technology_distribution,
                            use_container_width=True,
                            theme=None
                        )

                    with table_col:
                        table_rows = "".join(
                            f'<tr><td><span class="dot" style="background:{tech_palette[i]}"></span>{name}</td>'
                            f'<td>{value / 1_000_000:.2f}</td>'
                            f'<td>{value / distribution_total:.1%}</td></tr>'
                            for i, (name, value) in enumerate(distribution)
                        )

                        st.markdown(
                            '<div style="height:1.2rem"></div>'
                            '<table class="tech-table"><thead><tr>'
                            '<th>Technology</th><th>Value (€ M)</th><th>% of Total</th>'
                            f'</tr></thead><tbody>{table_rows}</tbody></table>',
                            unsafe_allow_html=True
                        )
                else:
                    st.info("No data for the selected filters.")

        chart_col3, chart_col4 = st.columns(2)

        # ── Opportunity Value by Industry ─────────────────────────────────────
        with chart_col3:
            with st.container(key="card_industry"):
                card_title("Opportunity Value by Industry")

                industry_nonzero = [
                    item for item in industry_sorted if item[1] > 0
                ]

                if not industry_nonzero:
                    st.info("No opportunity value available for the selected filters.")
                else:
                    industry_total = sum(item[1] for item in industry_nonzero)

                    fig_industry = go.Figure(
                        go.Treemap(
                            labels=[item[0] for item in industry_nonzero],
                            parents=[""] * len(industry_nonzero),
                            values=[item[1] for item in industry_nonzero],
                            text=[
                                f"€ {item[1] / 1_000_000:.2f} M"
                                f" ({item[1] / industry_total:.0%})"
                                for item in industry_nonzero
                            ],
                            textinfo="label+text",
                            textfont=dict(size=14),
                            pathbar=dict(visible=False),
                            root_color="white",
                            tiling=dict(pad=0),
                            marker=dict(
                                pad=dict(t=0, l=0, r=0, b=0),
                                colors=[item[1] for item in industry_nonzero],
                                colorscale=[
                                    [0.0, "#DDD6FE"],
                                    [0.5, "#8B5CF6"],
                                    [1.0, "#3B0764"]
                                ],
                                line=dict(width=2, color="white")
                            ),
                            hovertemplate=(
                                "<b>%{label}</b><br>"
                                "Opportunity Value: €%{value:,.0f}"
                                "<extra></extra>"
                            )
                        )
                    )

                    chart_layout(
                        fig_industry,
                        height=360,
                        margin=dict(l=0, r=0, t=10, b=0)
                    )

                    st.plotly_chart(
                        fig_industry,
                        use_container_width=True,
                        theme=None
                    )

        # ── Top 5 Technologies ────────────────────────────────────────────────
        with chart_col4:
            with st.container(key="card_top_tech"):
                card_title("Top 5 Technologies")

                ranking_display = list(reversed(technology_count_sorted[:5]))

                if ranking_display:
                    fig_ranking = go.Figure()

                    fig_ranking.add_trace(
                        go.Bar(
                            x=[item[1] for item in ranking_display],
                            y=[item[0] for item in ranking_display],
                            orientation="h",
                            marker_color="#7C3AED",
                            text=[item[1] for item in ranking_display],
                            textposition="outside",
                            cliponaxis=False,
                            hovertemplate=(
                                "<b>%{y}</b><br>"
                                "Opportunity: %{x}"
                                "<extra></extra>"
                            )
                        )
                    )

                    chart_layout(
                        fig_ranking,
                        height=360,
                        margin=dict(l=10, r=30, t=10, b=10),
                        showlegend=False,
                        xaxis=dict(title="Number of Opportunities", gridcolor="#EEE8FB", automargin=True),
                        yaxis=dict(title="", automargin=True, ticksuffix="   ")
                    )

                    st.plotly_chart(
                        fig_ranking,
                        use_container_width=True,
                        theme=None
                    )
                else:
                    st.info("No data for the selected filters.")
    else:
        # ── STAFFING OVERVIEW ─────────────────────────────────────────────────────
        section_title("Staffing Overview", "users")

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

        staffing_kpis = [
            ("users", "Resources", staffing_total),
            ("user-check", "Available", staffing_available),
            ("layers", "Fully Allocated", staffing_fully_allocated),
            ("percent", "Average Allocation", f"{staffing_average_allocation:.1f}%"),
        ]

        for column, (icon, label, value) in zip(st.columns(4), staffing_kpis):
            column.markdown(kpi_card(icon, label, value), unsafe_allow_html=True)

        st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

        # ── AGGREGAZIONI STAFFING ─────────────────────────────────────────────────
        availability_distribution = {
            "Available": 0,
            "Partially Allocated": 0,
            "Fully Allocated": 0
        }

        level_distribution = {}
        certification_distribution = {}
        manager_distribution = {}

        for resource in filtered_resources:
            availability_status = resource.get(
                "availability_status",
                "green"
            )

            if availability_status == "red":
                availability_distribution[
                    "Fully Allocated"
                ] += 1

            elif availability_status == "orange":
                availability_distribution[
                    "Partially Allocated"
                ] += 1

            else:
                availability_distribution[
                    "Available"
                ] += 1

            level_key = (
                resource.get("level"),
                resource.get("level_name") or "Unclassified"
            )

            level_distribution[level_key] = (
                level_distribution.get(level_key, 0) + 1
            )

            resource_certifications = {
                certification.get("nome_cert") or certification.get("cert_id")
                for certification in resource.get("certifications", [])
            }

            for certification_name in resource_certifications:
                if certification_name:
                    certification_distribution[certification_name] = (
                        certification_distribution.get(certification_name, 0) + 1
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

        # Livello 4 (più alto) in cima, livello 11 (più basso) in fondo
        level_sorted = sorted(
            level_distribution.items(),
            key=lambda item: (
                item[0][0] is None,
                item[0][0] if item[0][0] is not None else 0
            )
        )

        certification_sorted = sorted(
            certification_distribution.items(),
            key=lambda item: item[1],
            reverse=True
        )[:5]

        manager_sorted = sorted(
            manager_distribution.items(),
            key=lambda item: item[1],
            reverse=True
        )[:5]

        staffing_col1, staffing_col2 = st.columns(2)

        # ── RESOURCE AVAILABILITY ─────────────────────────────────────────────
        with staffing_col1:
            with st.container(key="card_availability"):
                card_title("Resource Availability")

                availability_order = [
                    ("Fully Allocated", "#16A34A"),
                    ("Partially Allocated", "#F59E0B"),
                    ("Available", "#DC2626"),
                ]

                if staffing_total > 0:
                    availability_donut_col, availability_table_col = st.columns([1, 1.2])

                    with availability_donut_col:
                        fig_availability = go.Figure(
                            go.Pie(
                                labels=[name for name, _ in availability_order],
                                values=[availability_distribution[name] for name, _ in availability_order],
                                hole=0.64,
                                sort=False,
                                textinfo="none",
                                marker=dict(
                                    colors=[color for _, color in availability_order],
                                    line=dict(color="white", width=2)
                                ),
                                hovertemplate=(
                                    "<b>%{label}</b><br>"
                                    "Resources: %{value}<br>"
                                    "%{percent}"
                                    "<extra></extra>"
                                )
                            )
                        )

                        chart_layout(
                            fig_availability,
                            height=360,
                            showlegend=False,
                            annotations=[
                                dict(
                                    text=f"<b>{staffing_total}</b><br>Resources",
                                    x=0.5,
                                    y=0.5,
                                    font=dict(size=16, color="#1E1B4B"),
                                    showarrow=False
                                )
                            ]
                        )

                        st.plotly_chart(
                            fig_availability,
                            use_container_width=True,
                            theme=None
                        )

                    with availability_table_col:
                        availability_rows = "".join(
                            f'<tr><td><span class="dot" style="background:{color}"></span>{name}</td>'
                            f'<td>{availability_distribution[name]}</td>'
                            f'<td>{availability_distribution[name] / staffing_total:.1%}</td></tr>'
                            for name, color in availability_order
                        )

                        st.markdown(
                            '<div style="height:3rem"></div>'
                            '<table class="tech-table"><thead><tr>'
                            '<th>Status</th><th>Resources</th><th>% of Total</th>'
                            f'</tr></thead><tbody>{availability_rows}</tbody></table>',
                            unsafe_allow_html=True
                        )
                else:
                    st.info("No resources available for the selected filters.")

        # ── RESOURCES BY LEVEL (PIRAMIDE) ─────────────────────────────────────
        with staffing_col2:
            with st.container(key="card_levels"):
                card_title("Resources by Level")

                if level_sorted:
                    level_count = len(level_sorted)
                    pyramid_start = (91, 33, 182)
                    pyramid_end = (221, 214, 254)
                    pyramid_colors = [
                        "#%02x%02x%02x" % tuple(
                            int(
                                pyramid_start[j]
                                + (pyramid_end[j] - pyramid_start[j])
                                * i / max(level_count - 1, 1)
                            )
                            for j in range(3)
                        )
                        for i in range(level_count)
                    ]

                    fig_levels = go.Figure(
                        go.Funnel(
                            y=[
                                f"{key[1]} (L{key[0]})"
                                if key[0] is not None
                                else key[1]
                                for key, _ in level_sorted
                            ],
                            x=[count for _, count in level_sorted],
                            textinfo="value+percent total",
                            textposition="inside",
                            marker=dict(
                                color=pyramid_colors,
                                line=dict(width=2, color="white")
                            ),
                            connector=dict(visible=False),
                            hovertemplate=(
                                "<b>%{y}</b><br>"
                                "Resources: %{x}"
                                "<extra></extra>"
                            )
                        )
                    )

                    chart_layout(
                        fig_levels,
                        height=360,
                        showlegend=False,
                        yaxis=dict(automargin=True)
                    )

                    st.plotly_chart(
                        fig_levels,
                        use_container_width=True,
                        theme=None
                    )
                else:
                    st.info("No resources available for the selected filters.")

        staffing_col3, staffing_col4 = st.columns(2)

        # ── TOP 5 CERTIFICATIONS ──────────────────────────────────────────────
        with staffing_col3:
            with st.container(key="card_certifications"):
                card_title("Top 5 Certifications")

                certification_display = list(reversed(certification_sorted))

                if certification_display:
                    fig_certifications = go.Figure()

                    fig_certifications.add_trace(
                        go.Bar(
                            x=[item[1] for item in certification_display],
                            y=[item[0] for item in certification_display],
                            orientation="h",
                            marker_color="#7C3AED",
                            text=[item[1] for item in certification_display],
                            textposition="outside",
                            cliponaxis=False,
                            hovertemplate=(
                                "<b>%{y}</b><br>"
                                "Certified resources: %{x}"
                                "<extra></extra>"
                            )
                        )
                    )

                    chart_layout(
                        fig_certifications,
                        height=360,
                        margin=dict(l=10, r=30, t=10, b=10),
                        showlegend=False,
                        xaxis=dict(
                            title="Number of Certified Resources",
                            gridcolor="#EEE8FB",
                            automargin=True
                        ),
                        yaxis=dict(title="", automargin=True, ticksuffix="   ")
                    )

                    st.plotly_chart(
                        fig_certifications,
                        use_container_width=True,
                        theme=None
                    )
                else:
                    st.info("No certifications available for the selected filters.")

        # ── TOP 5 MANAGERS BY ACTIVE OSR ──────────────────────────────────────
        with staffing_col4:
            with st.container(key="card_managers"):
                card_title("Top 5 Managers by Active OSR")

                manager_display = list(reversed(manager_sorted))

                if manager_display:
                    fig_managers = go.Figure()

                    fig_managers.add_trace(
                        go.Bar(
                            x=[item[1] for item in manager_display],
                            y=[item[0] for item in manager_display],
                            orientation="h",
                            marker_color="#7C3AED",
                            text=[item[1] for item in manager_display],
                            textposition="outside",
                            cliponaxis=False,
                            hovertemplate=(
                                "<b>%{y}</b><br>"
                                "Resources: %{x}"
                                "<extra></extra>"
                            )
                        )
                    )

                    chart_layout(
                        fig_managers,
                        height=360,
                        margin=dict(l=10, r=30, t=10, b=10),
                        showlegend=False,
                        xaxis=dict(
                            title="Resources on Active OSRs",
                            gridcolor="#EEE8FB",
                            automargin=True
                        ),
                        yaxis=dict(title="", automargin=True, ticksuffix="   ")
                    )

                    st.plotly_chart(
                        fig_managers,
                        use_container_width=True,
                        theme=None
                    )
                else:
                    st.info(
                        "No managers associated with active OSRs "
                        "for the selected filters."
                    )
    # ── GESTIONE STAFFING V2 ─────────────────────────────────────────────────────
def show_staffing_management_v2(groups):

    if "staffing_v2_view" not in st.session_state:
        st.session_state["staffing_v2_view"] = "osr"

    st.markdown(
        '<p class="main-title">🐈 Staffing Management </p>',
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
            "📄 Contracts",
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
        st.error("No response from backend.")
        return

    if response.status_code != 200:
        st.error(
            f"Loading error: {_api_detail(response)}"
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
                "🔍 Search OSR, resource, EID, opportunity or client",
                key="staffing_osr_search"
            )

        osr_statuses = sorted({
            row.get("calculated_status")
            for row in osr_rows
            if row.get("calculated_status")
        })

        with filter_2:
            selected_osr_statuses = st.multiselect(
                "OSR Status",
                osr_statuses,
                key="staffing_osr_status"
            )

        with filter_3:
            only_missing_resources = st.checkbox(
                "OSRs without Resource",
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
                "Project Role",
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
            "⚠️ Without Resource",
            missing_resource_osr
        )

        st.caption(
            f"{len(filtered_osr)} OSRs found out of {len(osr_rows)}"
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
                "Status": status_label,
                "OSR ID": row.get("osr_id", ""),
                "EID": row.get("resource_eid", ""),
                "Resource": resource_name or "⚠️ Non censita",
                "Opportunity": row.get(
                    "opportunity_title",
                    ""
                ),
                "Client": row.get(
                    "client_name",
                    ""
                ),
                "Project Role": row.get(
                    "project_role",
                    ""
                ),
                "Allocation %": row.get(
                    "allocation_pct",
                    0
                ),
                "Chargeability %": row.get(
                    "chargeability_pct",
                    0
                ),
                "Start Date": row.get(
                    "start_date",
                    ""
                ),
                "End Date": row.get(
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
                "🔍 Search ID, title, client or contract",
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
                "Client",
                client_options,
                key="staffing_opportunity_client"
            )

        only_without_contract = st.checkbox(
            "Opportunities without Contract",
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
            "Opportunities",
            len(filtered_opportunities)
        )

        kpi2.metric(
            "Value",
            f"€ {opportunity_value / 1_000_000:.2f} M"
        )

        kpi3.metric(
            "Linked OSRs",
            opportunity_osr_count
        )

        kpi4.metric(
            "Without Contract",
            opportunities_without_contract
        )

        st.caption(
            f"{len(filtered_opportunities)} opportunity "
            f"found out of {len(opportunity_rows)}"
        )

        # ── TABELLA ───────────────────────────────────────────────────────────
        opportunity_table = []

        for row in filtered_opportunities:
            opportunity_table.append({
                "Opportunity ID":
                    row.get("opportunity_id", ""),

                "Title":
                    row.get("opportunity_title", ""),

                "Contract":
                    row.get("contract_id")
                    or "⚠️ No Contract",

                "Client":
                    row.get("client_name", ""),

                "Stage":
                    row.get("opportunity_stage", ""),

                "Status":
                    row.get("opportunity_status", ""),

                "Technology":
                    row.get("main_tech_cluster", ""),

                "Functional Area":
                    row.get("functional_area", ""),

                "Start Date":
                    row.get("start_date", ""),

                "End Date":
                    row.get("end_date", ""),

                "Value":
                    f"€ {float(row.get('opportunity_value') or 0):,.0f}",

                "OSR":
                    row.get("osr_count", 0),

                "Total Allocation %":
                    row.get("total_allocation", 0)
            })

        st.dataframe(
            opportunity_table,
            use_container_width=True,
            hide_index=True
        )   
    # ── VISTA CONTRATTI - PLACEHOLDER ─────────────────────────────────────────
    elif st.session_state["staffing_v2_view"] == "contract":

        st.markdown("### Contracts")

        # ── FILTRI CONTRATTI ──────────────────────────────────────────────────
        filter_1, filter_2, filter_3 = st.columns([3, 2, 2])

        with filter_1:
            contract_search = st.text_input(
                "🔍 Search ID, title or client",
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
            "Cross-Practice Only",
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
            "Contracts",
            len(filtered_contracts)
        )

        kpi2.metric(
            "Active",
            active_contracts
        )

        kpi3.metric(
            "Revenue",
            f"€ {total_revenue / 1_000_000:.2f} M"
        )

        kpi4.metric(
            "Margin",
            f"€ {total_margin / 1_000_000:.2f} M"
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
                    f"€ {float(row.get('contract_revenue') or 0):,.0f}",

                "Costs":
                    f"€ {float(row.get('contract_costs') or 0):,.0f}",

                "Margin":
                    f"€ {float(row.get('contract_margin') or 0):,.0f}",

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
def show_resource_request(groups):
    request_data = st.session_state.get(
        "matching_resource_request",
        {}
    )

    if not request_data:
        st.warning("No resource request is currently available.")

        if st.button("← Back to Matching AI"):
            st.session_state.page = "matching_v2"
            st.rerun()

        return

    candidate = request_data.get(
        "candidate",
        {}
    )

    opportunity = request_data.get(
        "opportunity",
        {}
    )

    st.markdown(
        '<p class="main-title">📩 Resource Request</p>',
        unsafe_allow_html=True
    )

    if st.button(
        "← Back to Matching Results",
        key="back_from_resource_request_page"
    ):
        st.session_state.page = "matching_v2"
        st.rerun()

    st.markdown("---")

    profile_col, context_col = st.columns(2)

    with profile_col:
        st.markdown("#### Selected Resource")

        st.markdown(
            f"**{candidate.get('name', '')}**"
        )

        st.markdown(
            f"EID: `{candidate.get('eid', '')}`"
        )

        st.markdown(
            f"Level: "
            f"**{candidate.get('level_name') or '—'}**"
        )

        st.markdown(
            f"Match Score: "
            f"**{candidate.get('score', 0):.1f}/100**"
        )

        st.markdown(
            f"Available Capacity: "
            f"**{candidate.get('available_capacity_pct', 0)}%**"
        )

    with context_col:
        st.markdown("#### Staffing Context")

        st.markdown(
            f"**Opportunity:** "
            f"{opportunity.get('opportunity_title') or '—'}"
        )

        st.markdown(
            f"**Role:** "
            f"{request_data.get('role') or '—'}"
        )

        st.markdown(
            f"**Period:** "
            f"{request_data.get('start_date')} → "
            f"{request_data.get('end_date')}"
        )

        st.markdown(
            f"**OSR:** "
            f"{request_data.get('osr_id') or 'New OSR required'}"
        )

        st.markdown(
            f"**Requesting Manager:** "
            f"{request_data.get('requesting_manager') or '—'}"
        )

    rationale = request_data.get(
        "rationale",
        ""
    )

    opportunity_title = (
        opportunity.get("opportunity_title")
        or opportunity.get("opportunity_id")
        or "Staffing Opportunity"
    )

    subject_default = (
        f"StaffMatch | Resource Request | "
        f"{candidate.get('name', '')} | "
        f"{opportunity_title}"
    )

    osr_text = (
        request_data.get("osr_id")
        or "New OSR required"
    )

    manager_name = (
        request_data.get("requesting_manager")
        or "StaffMatch Manager"
    )

    body_default = (
        f"Hello,\n\n"
        f"I would like to request the following resource "
        f"for a staffing need.\n\n"
        f"Resource: {candidate.get('name', '')}\n"
        f"EID: {candidate.get('eid', '')}\n"
        f"Level: {candidate.get('level_name') or '—'}\n\n"
        f"Opportunity: {opportunity_title}\n"
        f"Role: {request_data.get('role') or '—'}\n"
        f"Requested period: "
        f"{request_data.get('start_date')} to "
        f"{request_data.get('end_date')}\n"
        f"OSR: {osr_text}\n\n"
        f"Selection rationale:\n"
        f"{rationale}\n\n"
        f"Please review this staffing request and confirm "
        f"the required next steps.\n\n"
        f"Best regards,\n"
        f"{manager_name}"
    )

    st.markdown("---")
    st.markdown("#### ✉️ Email Preview")

    recipient_email = st.text_input(
        "To *",
        placeholder="recipient@example.com",
        key="resource_request_page_to"
    )

    cc_email = st.text_input(
        "CC",
        placeholder="optional@example.com",
        key="resource_request_page_cc"
    )

    email_subject = st.text_input(
        "Subject",
        value=subject_default,
        key="resource_request_page_subject"
    )

    email_body = st.text_area(
        "Email Body",
        value=body_default,
        height=420,
        key="resource_request_page_body"
    )

    st.info(
        "Email delivery will be connected in the next step. "
        "The recipient, subject and body are fully editable."
    )

    st.button(
        "📨 Send Resource Request",
        type="primary",
        use_container_width=True,
        disabled=True,
        key="send_resource_request_page"
    )
# ── MATCHING AI - NEW ─────────────────────────────────────────────────────────
def show_matching_ai(groups):
    results = st.session_state.get(
    "matching_ai_results"
    )
    st.markdown(
        '<p class="main-title">🤖 Match AI</p>',
        unsafe_allow_html=True
    )

    context_response = api(
        "GET",
        "/sm/matching-context"
    )

    if context_response is None:
        st.error("No response from backend.")
        return

    if context_response.status_code != 200:
        st.error(
            f"Unable to load Matching context: "
            f"{_api_detail(context_response)}"
        )
        return

    context = context_response.json()

    opportunities = context.get("opportunities", [])
    osr_rows = context.get("osr", [])
    roles = context.get("roles", [])
    skills = context.get("skills", [])
    certifications = context.get("certifications", [])
    languages = context.get("languages", [])

    if not opportunities:
        st.warning("No opportunities available.")
        return

    # ── MATCHING CONTEXT ──────────────────────────────────────────────────────
    st.markdown("### 1. Matching Context")

    opportunity_options = {
        (
            f"{item['opportunity_title']} "
            f"({item['opportunity_id']})"
        ): item
        for item in opportunities
    }

    selected_opportunity_label = st.selectbox(
        "Opportunity *",
        list(opportunity_options.keys()),
        key="matching_new_opportunity"
    )

    selected_opportunity = opportunity_options[
        selected_opportunity_label
    ]

    selected_opportunity_id = selected_opportunity[
        "opportunity_id"
    ]

    # Solo OSR appartenenti alla Opportunity selezionata
    opportunity_osr = [
        row
        for row in osr_rows
        if row.get("opportunity_id")
        == selected_opportunity_id
    ]

    osr_options = {
        "No OSR": None
    }

    for osr in opportunity_osr:
        osr_label = (
            f"{osr.get('osr_id', '')} · "
            f"{osr.get('project_role', '')}"
        )

        osr_options[osr_label] = osr

    context_col1, context_col2 = st.columns(2)

    with context_col1:
        selected_osr_label = st.selectbox(
            "OSR (optional)",
            list(osr_options.keys()),
            key="matching_new_osr"
        )

    selected_osr = osr_options[
        selected_osr_label
    ]

    with context_col2:
        selected_role = st.selectbox(
            "Role *",
            roles,
            key="matching_new_role"
        )

    # Date suggerite:
    # OSR selezionata -> date OSR
    # altrimenti -> date Opportunity
    if selected_osr:
        suggested_start = selected_osr.get("start_date")
        suggested_end = selected_osr.get("end_date")
    else:
        suggested_start = selected_opportunity.get(
            "start_date"
        )
        suggested_end = selected_opportunity.get(
            "end_date"
        )

    import datetime as _dt_matching

    try:
        default_start = _dt_matching.date.fromisoformat(
            suggested_start
        )
    except Exception:
        default_start = _dt_matching.date.today()

    try:
        default_end = _dt_matching.date.fromisoformat(
            suggested_end
        )
    except Exception:
        default_end = default_start

    date_col1, date_col2 = st.columns(2)

    with date_col1:
        matching_start_date = st.date_input(
            "Start Date *",
            value=default_start,
            key=(
                f"matching_start_"
                f"{selected_opportunity_id}_"
                f"{selected_osr_label}"
            )
        )

    with date_col2:
        matching_end_date = st.date_input(
            "End Date *",
            value=default_end,
            key=(
                f"matching_end_"
                f"{selected_opportunity_id}_"
                f"{selected_osr_label}"
            )
        )

    if matching_end_date < matching_start_date:
        st.error(
            "End Date must be equal to or later "
            "than Start Date."
        )

    st.markdown("---")

    # ── MATCHING CRITERIA ─────────────────────────────────────────────────────
    st.markdown("### 2. Matching Criteria")

    skills_options = [
        item.get("skill_name")
        for item in skills
        if item.get("skill_name")
    ]

    certification_options = {
        (
            f"{item.get('certification_name', '')} "
            f"({item.get('cert_id', '')})"
        ): item.get("cert_id")
        for item in certifications
    }

    language_options = [
        item.get("language_code")
        for item in languages
        if item.get("language_code")
    ]

    criteria_col1, criteria_col2, criteria_col3 = st.columns(3)

    with criteria_col1:
        selected_skills = st.multiselect(
            "Skills · max 3",
            skills_options,
            max_selections=3,
            key="matching_new_skills"
        )

    with criteria_col2:
        selected_certification_labels = st.multiselect(
            "Certifications · max 2",
            list(certification_options.keys()),
            max_selections=2,
            key="matching_new_certifications"
        )

    with criteria_col3:
        selected_languages = st.multiselect(
            "Languages · max 2",
            language_options,
            max_selections=2,
            key="matching_new_languages"
        )

    selected_certification_ids = [
        certification_options[label]
        for label in selected_certification_labels
    ]

    st.markdown("---")

    # ── WEIGHTS ───────────────────────────────────────────────────────────────
    st.markdown("### 3. Criteria Weights")

    active_criteria = []

    for skill in selected_skills:
        active_criteria.append({
            "key": f"skill:{skill}",
            "label": skill,
            "type": "Skill"
        })

    for cert_label in selected_certification_labels:
        cert_id = certification_options[cert_label]

        active_criteria.append({
            "key": f"certification:{cert_id}",
            "label": cert_label,
            "type": "Certification"
        })

    for language in selected_languages:
        active_criteria.append({
            "key": f"language:{language}",
            "label": language,
            "type": "Language"
        })

    suggest_weights_payload = {
        "opportunity": {
            "opportunity_id":
                selected_opportunity.get("opportunity_id"),

            "opportunity_title":
                selected_opportunity.get("opportunity_title"),

            "main_tech_cluster":
                selected_opportunity.get("main_tech_cluster"),

            "functional_area":
                selected_opportunity.get("functional_area")
        },

        "role":
            selected_role,

        "start_date":
            matching_start_date.isoformat(),

        "end_date":
            matching_end_date.isoformat(),

        "skills":
            selected_skills,

        "certifications":
            selected_certification_ids,

        "languages":
            selected_languages
    }

    if active_criteria:
            if st.button(
                "✨ Suggest AI Weights",
                use_container_width=True,
                key="matching_suggest_weights"
            ):
                with st.spinner(
                    "AI is analyzing the matching context..."
                ):
                    suggestion_response = api(
                        "POST",
                        "/sm/matching/suggest-weights",
                        json=suggest_weights_payload
                    )

                if suggestion_response is None:
                    st.error(
                        "No response from backend."
                    )

                elif suggestion_response.status_code != 200:
                    st.error(
                        f"Unable to generate AI suggestion: "
                        f"{_api_detail(suggestion_response)}"
                    )

                else:
                    suggestion = suggestion_response.json()

                    suggested_weights = suggestion.get(
                        "weights",
                        {}
                    )

                    for criterion in active_criteria:
                        criterion_key = criterion["key"]

                        suggested_value = int(
                            round(
                                suggested_weights.get(
                                    criterion_key,
                                    0
                                )
                            )
                        )

                        st.session_state[
                            f"weight_{criterion_key}"
                        ] = suggested_value

                    st.session_state[
                        "matching_weight_rationale"
                    ] = suggestion.get(
                        "rationale",
                        ""
                    )

                    st.rerun()

    else:
            st.caption(
                "Select at least one Skill, Certification or Language "
                "to enable AI weight suggestions."
            )

            
    ai_weight_rationale = st.session_state.get(
        "matching_weight_rationale"
    )

    if ai_weight_rationale:
        with st.container(border=True):
            st.markdown(
                "##### ✨ AI Weight Recommendation"
            )

            st.caption(
                ai_weight_rationale
            )

        
    raw_weights = {}

    if not active_criteria:
        st.info(
            "Select at least one matching criterion "
            "to configure relative importance."
        )

    else:
        for criterion in active_criteria:
            criterion_key = criterion["key"]

            default_value = int(
                st.session_state.get(
                    f"weight_{criterion_key}",
                    50
                )
            )

            raw_weights[criterion_key] = st.slider(
                f"{criterion['type']} · {criterion['label']}",
                min_value=0,
                max_value=100,
                value=default_value,
                step=5,
                key=f"weight_{criterion_key}"
            )

        raw_weight_total = sum(
            raw_weights.values()
        )

        normalized_weights = {}

        if raw_weight_total == 0:
            uniform_weight = (
                100 / len(active_criteria)
            )

            for criterion in active_criteria:
                normalized_weights[
                    criterion["key"]
                ] = uniform_weight

            st.caption(
                "All relative values are 0. "
                "Uniform weights are applied automatically."
            )

        else:
            for criterion in active_criteria:
                normalized_weights[
                    criterion["key"]
                ] = (
                    raw_weights[criterion["key"]]
                    / raw_weight_total
                    * 100
                )

        st.markdown("##### Effective Weights")

        for criterion in active_criteria:
            effective_weight = normalized_weights[
                criterion["key"]
            ]

            st.caption(
                f"{criterion['label']} · "
                f"**{effective_weight:.2f}%**"
            )
    st.markdown("---")

    # ── CURRENT CONFIGURATION ─────────────────────────────────────────────────
    with st.expander(
        "🔎 Review Matching Configuration",
        expanded=False
    ):
        st.markdown(
            f"**Opportunity:** "
            f"{selected_opportunity.get('opportunity_title', '')}"
        )

        st.markdown(
            f"**OSR:** "
            f"{selected_osr_label}"
        )

        st.markdown(
            f"**Role:** {selected_role}"
        )

        st.markdown(
            f"**Period:** "
            f"{matching_start_date} → {matching_end_date}"
        )

        st.markdown(
            "**Skills:** "
            + (
                ", ".join(selected_skills)
                if selected_skills
                else "None"
            )
        )

        st.markdown(
            "**Certifications:** "
            + (
                ", ".join(selected_certification_labels)
                if selected_certification_labels
                else "None"
            )
        )

        st.markdown(
            "**Languages:** "
            + (
                ", ".join(selected_languages)
                if selected_languages
                else "None"
            )
        )

    can_run_matching = (
        matching_end_date >= matching_start_date
        and bool(active_criteria)
    )

    if st.button(
        "✨ Run Matching",
        type="primary",
        use_container_width=True,
        disabled=not can_run_matching,
        key="run_matching_new"
    ):
        payload = {
            "opportunity_id": selected_opportunity_id,
            "osr_id": (
                selected_osr.get("osr_id")
                if selected_osr
                else None
            ),
            "role": selected_role,
            "start_date": matching_start_date.isoformat(),
            "end_date": matching_end_date.isoformat(),
            "skills": selected_skills,
            "certifications": selected_certification_ids,
            "languages": selected_languages,
            "weights": normalized_weights
        }

        with st.spinner(
            "Analyzing resources and availability..."
        ):
            matching_response = api(
                "POST",
                "/sm/matching",
                json=payload
            )

        if matching_response is None:
            st.error("No response from backend.")

        elif matching_response.status_code != 200:
            st.error(
                f"Matching error: "
                f"{_api_detail(matching_response)}"
            )

        else:
            st.session_state[
                "matching_ai_results"
            ] = matching_response.json()

            st.rerun()

    if results:
        st.markdown("---")
        st.markdown("### 4. Matching Results")

        summary = results.get(
            "summary",
            {}
        )

        summary_col1, summary_col2, summary_col3, summary_col4 = st.columns(4)

        summary_col1.metric(
            "Candidates",
            summary.get("total_candidates", 0)
        )

        summary_col2.metric(
            "🟢 Available",
            summary.get("available", 0)
        )

        summary_col3.metric(
            "🟠 Partial Availability",
            summary.get("partial", 0)
        )

        summary_col4.metric(
            "🔴 Unavailable",
            summary.get("unavailable", 0)
        )

        candidates = results.get(
            "candidates",
            []
        )
        def open_resource_request(candidate):
            requesting_user = st.session_state.user or {}

            requesting_manager = (
                f"{requesting_user.get('nome') or ''} "
                f"{requesting_user.get('cognome') or ''}"
            ).strip()

            selected_osr_id = (
                selected_osr.get("osr_id")
                if selected_osr
                else None
            )

            rationale_response = api(
                "POST",
                "/sm/matching/selection-rationale",
                json={
                    "candidate": candidate,
                    "opportunity": selected_opportunity,
                    "role": selected_role,
                    "start_date": matching_start_date.isoformat(),
                    "end_date": matching_end_date.isoformat(),
                    "osr_id": selected_osr_id
                }
            )

            if (
                rationale_response is not None
                and rationale_response.status_code == 200
            ):
                rationale = rationale_response.json().get(
                    "rationale",
                    ""
                )

            else:
                rationale = (
                    f"{candidate.get('name', '')} has been selected "
                    f"for this staffing request based on the current "
                    f"matching results and availability."
                )

            st.session_state["matching_resource_request"] = {
                "candidate": candidate,
                "opportunity": selected_opportunity,
                "role": selected_role,
                "start_date": matching_start_date.isoformat(),
                "end_date": matching_end_date.isoformat(),
                "osr_id": selected_osr_id,
                "requesting_manager": requesting_manager,
                "requesting_manager_email": requesting_user.get(
                    "email",
                    ""
                ),
                "rationale": rationale
            }

            st.session_state.page = "resource_request"
            st.rerun()
        st.caption(
            "Availability is evaluated for the entire requested period. "
            "Within each availability group, resources are ranked by match score."
        )

        # Mostriamo inizialmente i primi 20 risultati.
        visible_candidates = candidates[:20]
        if st.session_state.get(
            "matching_compare_view",
            False
        ):
            compare_eids = st.session_state.get(
                "matching_compare_eids",
                []
            )

            compared_candidates = [
                candidate
                for candidate in candidates
                if candidate.get("eid") in compare_eids
            ]

            st.markdown("### ⚖️ Resource Comparison")

            if st.button(
                "← Back to Matching Results",
                key="back_to_matching_results"
            ):
                st.session_state[
                    "matching_compare_view"
                ] = False

                st.rerun()

            comparison_columns = st.columns(
                len(compared_candidates)
            )

            for column, candidate in zip(
                comparison_columns,
                compared_candidates
            ):
                with column:
                    availability_status = candidate.get(
                        "availability_status"
                    )

                    if availability_status == "available":
                        availability_icon = "🟢"
                        availability_label = "Available"

                    elif availability_status == "partial":
                        availability_icon = "🟠"
                        availability_label = "Partial Availability"

                    else:
                        availability_icon = "🔴"
                        availability_label = "Unavailable"

                    with st.container(border=True):
                        st.markdown(
                            f"### {candidate.get('name', '')}"
                        )

                        st.caption(
                            f"EID {candidate.get('eid', '')}"
                        )

                        st.metric(
                            "Match Score",
                            f"{candidate.get('score', 0):.1f}/100"
                        )

                        st.markdown(
                            f"**{availability_icon} "
                            f"{availability_label}**"
                        )

                        st.markdown(
                            f"Available Capacity: "
                            f"**{candidate.get('available_capacity_pct', 0)}%**"
                        )

                        st.markdown(
                            f"Level: "
                            f"**{candidate.get('level_name') or '—'}**"
                        )

                        st.markdown(
                            f"Experience: "
                            f"**{candidate.get('years_of_experience', 0)} years**"
                        )
                        st.markdown("---")

                        st.markdown("##### 🏆 Matched Criteria")

                        matched = candidate.get(
                            "matched_criteria",
                            []
                        )

                        if matched:
                            for criterion in matched:
                                st.markdown(
                                    f"✨ {criterion.get('criterion')} "
                                    f"· {criterion.get('weight', 0):.2f}%"
                                )
                        else:
                            st.caption(
                                "No selected criteria matched."
                            )

                        st.markdown("##### 🚫 Missing Criteria")

                        missing = candidate.get(
                            "missing_criteria",
                            []
                        )

                        if missing:
                            for criterion in missing:
                                st.markdown(
                                    f"○ {criterion.get('criterion')} "
                                    f"· {criterion.get('weight', 0):.2f}%"
                                )
                        else:
                            st.caption(
                                "All selected criteria matched."
                            )

                        st.markdown("---")
                        st.markdown("##### Skills")

                        skills = [
                            item.get("skill_name")
                            for item in candidate.get("skills", [])
                            if item.get("skill_name")
                        ]

                        if skills:
                            st.caption(" · ".join(skills))
                        else:
                            st.caption("No skills available.")

                        st.markdown("##### Certifications")

                        certifications = [
                            item.get("nome_cert")
                            for item in candidate.get(
                                "certifications",
                                []
                            )
                            if item.get("nome_cert")
                        ]

                        if certifications:
                            for certification in certifications:
                                st.caption(
                                    f"🎓 {certification}"
                                )
                        else:
                            st.caption(
                                "No certifications available."
                            )

                        st.markdown("##### Languages")

                        languages = [
                            item.get("language_code")
                            for item in candidate.get(
                                "languages",
                                []
                            )
                            if item.get("language_code")
                        ]

                        if languages:
                            st.caption(" · ".join(languages))
                        else:
                            st.caption(
                                "No languages available."
                            )

                        st.markdown("---")
                        st.markdown(
                            "##### Current Assignments"
                        )

                        assignments = candidate.get(
                            "current_assignments",
                            []
                        )

                        if assignments:
                            for assignment in assignments:
                                osr_status = assignment.get(
                                    "osr_status"
                                )

                                if osr_status == "Active":
                                    osr_icon = "🟢"
                                elif osr_status == "Rolling-off":
                                    osr_icon = "🟠"
                                elif osr_status == "Closed":
                                    osr_icon = "🔴"
                                else:
                                    osr_icon = "⚪"

                                st.markdown(
                                    f"**{osr_icon} "
                                    f"{assignment.get('osr_id', '')} "
                                    f"· {osr_status or '—'}**"
                                )

                                st.caption(
                                    assignment.get(
                                        "opportunity_title"
                                    ) or "—"
                                )

                                st.caption(
                                    f"Allocation "
                                    f"{assignment.get('allocation_pct', 0)}% "
                                    f"· End "
                                    f"{assignment.get('end_date') or '—'}"
                                )
                        else:
                            st.caption(
                                "No current assignments."
                            )
                        

                        st.markdown("---")

                        if st.button(
                            "📩 Request Resource",
                            type="primary",
                            use_container_width=True,
                            key=f"compare_request_resource_{candidate.get('eid')}"
                        ):
                            open_resource_request(candidate)

            return
        st.markdown("#### ⚖️ Compare Resources")

        compare_options = {
            (
                f"#{candidate.get('rank', '')} · "
                f"{candidate.get('name', '')} · "
                f"Score {candidate.get('score', 0):.1f}"
            ): candidate.get("eid")
            for candidate in visible_candidates
        }

        selected_compare_labels = st.multiselect(
            "Select up to 3 resources to compare",
            list(compare_options.keys()),
            max_selections=3,
            key="matching_compare_resources"
        )

        selected_compare_eids = [
            compare_options[label]
            for label in selected_compare_labels
        ]

        if selected_compare_eids:
            if st.button(
                "⚖️ Compare Selected Resources",
                type="primary",
                use_container_width=True,
                key="open_resource_comparison"
            ):
                st.session_state[
                    "matching_compare_view"
                ] = True

                st.session_state[
                    "matching_compare_eids"
                ] = selected_compare_eids

                st.rerun()


        
        for candidate in visible_candidates:
            availability_status = candidate.get(
                "availability_status"
            )

            if availability_status == "available":
                availability_icon = "🟢"
                availability_label = "Available"

            elif availability_status == "partial":
                availability_icon = "🟠"
                availability_label = "Partial Availability"

            else:
                availability_icon = "🔴"
                availability_label = "Unavailable"

            candidate_label = (
                f"{availability_icon} "
                f"#{candidate.get('rank', '')} · "
                f"{candidate.get('name', '')} · "
                f"Score {candidate.get('score', 0):.1f}"
            )

            with st.expander(
                candidate_label
            ):

                profile_col, matching_col, availability_col = st.columns(
                    [1.2, 1.5, 1.3]
                )

                # ── RESOURCE PROFILE ──────────────────────────────────────────────
                with profile_col:
                    st.markdown("#### Resource Profile")

                    st.markdown(
                        f"**EID:** "
                        f"`{candidate.get('eid', '')}`"
                    )

                    st.markdown(
                        f"**Email:** "
                        f"`{candidate.get('email') or '—'}`"
                    )

                    st.markdown(
                        f"**Level:** "
                        f"{candidate.get('level_name') or '—'}"
                    )

                    st.markdown(
                        f"**Experience:** "
                        f"{candidate.get('years_of_experience', 0)} years"
                    )

                current_assignments = candidate.get(
                    "current_assignments",
                    []
                )

                if current_assignments:
                    st.markdown("---")
                    st.markdown(
                        "#### Current Assignments"
                    )

                    for assignment in current_assignments:
                        osr_status = assignment.get(
                            "osr_status"
                        )

                        if osr_status == "Active":
                            osr_icon = "🟢"

                        elif osr_status == "Rolling-off":
                            osr_icon = "🟠"

                        elif osr_status == "Closed":
                            osr_icon = "🔴"

                        else:
                            osr_icon = "⚪"

                        with st.container(border=True):
                            assignment_col1, assignment_col2, assignment_col3 = (
                                st.columns([1.4, 1.2, 1])
                            )

                            with assignment_col1:
                                st.markdown(
                                    f"**{osr_icon} "
                                    f"{assignment.get('osr_id', '')} "
                                    f"· {osr_status or '—'}**"
                                )

                                st.markdown(
                                    f"**Opportunity:** "
                                    f"{assignment.get('opportunity_title') or '—'}"
                                )

                                st.caption(
                                    f"Client: "
                                    f"{assignment.get('client_name') or '—'}"
                                )

                            with assignment_col2:
                                st.markdown(
                                    f"**Project Role:** "
                                    f"{assignment.get('project_role') or '—'}"
                                )

                                st.markdown(
                                    f"**Allocation:** "
                                    f"{assignment.get('allocation_pct', 0)}%"
                                )

                            with assignment_col3:
                                st.markdown(
                                    f"**Start Date:** "
                                    f"{assignment.get('start_date') or '—'}"
                                )

                                st.markdown(
                                    f"**End Date:** "
                                    f"{assignment.get('end_date') or '—'}"
                                )

                                manager_name = assignment.get(
                                    "manager_name"
                                )

                                if manager_name:
                                    st.caption(
                                        f"Manager: {manager_name}"
                                    )

                # ── MATCH DETAILS ─────────────────────────────────────────────────
                with matching_col:
                    st.markdown("#### Match Details")

                    st.metric(
                        "Match Score",
                        f"{candidate.get('score', 0):.1f}/100"
                    )

                    matched_criteria = candidate.get(
                        "matched_criteria",
                        []
                    )

                    missing_criteria = candidate.get(
                        "missing_criteria",
                        []
                    )

                                    # ── MATCHED CRITERIA ─────────────────────────────────────────
                with st.container(border=True):
                    st.markdown("##### 🏆 Matched Criteria")

                    if matched_criteria:
                        for criterion in matched_criteria:
                            st.markdown(
                                f"✨ **{criterion.get('criterion')}**  "
                                f"· {criterion.get('weight', 0):.2f}%"
                            )
                    else:
                        st.caption(
                            "No selected criteria matched."
                        )

                # ── MISSING CRITERIA ─────────────────────────────────────────
                with st.container(border=True):
                    st.markdown("##### 🚫 Missing Criteria")

                    if missing_criteria:
                        for criterion in missing_criteria:
                            st.markdown(
                                f"○ **{criterion.get('criterion')}**  "
                                f"· {criterion.get('weight', 0):.2f}%"
                            )
                    else:
                        st.caption(
                            "All selected criteria matched."
                        )

                # ── AVAILABILITY ──────────────────────────────────────────────────
                with availability_col:
                    st.markdown("#### Availability")

                    st.markdown(
                        f"**{availability_icon} "
                        f"{availability_label}**"
                    )

                    st.markdown(
                        f"Peak Allocation: "
                        f"**{candidate.get('peak_allocation_pct', 0)}%**"
                    )

                    st.markdown(
                        f"Available Capacity: "
                        f"**{candidate.get('available_capacity_pct', 0)}%**"
                    )

                    next_available_date = candidate.get(
                        "next_available_date"
                    )

                    if next_available_date:
                        st.markdown(
                            f"Next Available Date: "
                            f"**{next_available_date}**"
                        )

                    overlapping_osr = candidate.get(
                        "overlapping_osr",
                        []
                    )

                    if overlapping_osr:
                        st.markdown("**Overlapping OSRs**")

                        for osr in overlapping_osr:
                            st.caption(
                                f"{osr.get('osr_id')} · "
                                f"{osr.get('allocation_pct', 0)}% · "
                                f"{osr.get('start_date')} → "
                                f"{osr.get('end_date')}"
                            )
                st.markdown("---")

                if st.button(
                    "📩 Request Resource",
                    type="primary",
                    use_container_width=True,
                    key=f"request_resource_{candidate.get('eid')}"
                ):
                    open_resource_request(candidate)

    # ── MAIN ───────────────────────────────────────────────────────────────────────
def show_matching_v2(groups):
    st.markdown('<p class="main-title">🤖 Matching AI</p>', unsafe_allow_html=True)
    st.markdown("---")

    r = api("GET", "/sm/opportunities")
    if r is None or r.status_code != 200:
        st.error("Unable to load opportunities.")
        return
    opportunities = r.json()
    if not opportunities:
        st.warning("No opportunities found.")
        return

    options = {
        f"{o['titolo']} ({o['main_tech_cluster']})": o["opportunity_id"]
        for o in opportunities
    }
    selected_label = st.selectbox("Select an Opportunity", list(options.keys()))
    selected_id = options[selected_label]

    if st.button("Run Matching", type="primary"):
        with st.spinner("Matching in progress..."):
            r = api("GET", f"/sm/match/{selected_id}")
            if r is None or r.status_code != 200:
                st.error("Matching error.")
                return
            result = r.json()

        opp = result["opportunity"]
        st.subheader(f"📋 {opp['titolo']}")
        col1, col2, col3 = st.columns(3)
        col1.metric("Tech cluster", opp["main_tech_cluster"])
        col2.metric("Client", opp["cliente"] or "—")
        col3.metric("Candidates Found", len(result["candidati"]))

        st.markdown("---")
        st.subheader("🏆 Candidate Ranking")

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
    show_app_header()

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
        show_matching_ai(groups)
    elif page == "resource_request":
        show_resource_request(groups)
    elif page == "chatbot":
        show_chatbot(groups)
    elif page == "approvazioni":
        show_approvazioni(groups)
    elif page == "admin":
        show_admin(groups)

main()
