import os
import streamlit as st
import requests

st.set_page_config(page_title="Matching AI v2 (test)", page_icon="🧪")

BACKEND_URL = os.environ.get(
    "BACKEND_URL",
    "https://staffmatch-ai-backend-dev.cfapps.eu10-004.hana.ondemand.com"
)

st.title("🧪 Matching AI v2 — Test nuovo modello dati")
st.caption(f"Backend: {BACKEND_URL}  ·  Ambiente: DEV")
st.warning("Pagina di test interno, senza autenticazione. Nuovo modello dati SM_*.")

try:
    resp = requests.get(f"{BACKEND_URL}/sm/opportunities", timeout=15)
    resp.raise_for_status()
    opportunities = resp.json()
except Exception as e:
    st.error(f"Errore nel caricare le opportunity: {e}")
    st.stop()

if not opportunities:
    st.warning("Nessuna opportunity trovata.")
    st.stop()

options = {
    f"{o['titolo']} ({o['main_tech_cluster']})": o["opportunity_id"]
    for o in opportunities
}
selected_label = st.selectbox("Scegli un'opportunity", list(options.keys()))
selected_id = options[selected_label]

if st.button("Esegui matching", type="primary"):
    with st.spinner("Calcolo in corso..."):
        try:
            resp = requests.get(f"{BACKEND_URL}/sm/match/{selected_id}", timeout=30)
            resp.raise_for_status()
            result = resp.json()
        except Exception as e:
            st.error(f"Errore durante il matching: {e}")
            st.stop()

    opp = result["opportunity"]
    st.subheader(f"📋 {opp['titolo']}")
    col1, col2, col3 = st.columns(3)
    col1.metric("Tech cluster", opp["main_tech_cluster"])
    col2.metric("Cliente", opp["cliente"] or "—")
    col3.metric("Candidati trovati", len(result["candidati"]))

    st.divider()
    st.subheader("🏆 Classifica candidati")

    for i, c in enumerate(result["candidati"], start=1):
        emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
        with st.container(border=True):
            col_a, col_b, col_c = st.columns([1, 3, 2])
            col_a.markdown(f"### {emoji}")
            col_b.markdown(f"**{c['nome']}**")
            col_b.caption(c["motivazione"])
            col_c.metric("Score", f"{c['score']}/100")
