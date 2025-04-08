import streamlit as st
import importlib

st.set_page_config(page_title="M4U", page_icon='▶️', layout="wide", initial_sidebar_state="expanded")

# 🚀 Recuperar parâmetro da URL com nova API
query_params = st.query_params
page_from_url = query_params.get("page", "login")

# ✅ Sempre sincronizar o estado com a URL
if st.session_state.get("page") != page_from_url:
    st.session_state["page"] = page_from_url

# 🔄 Trocar página e atualizar a URL
def switch_page(page_name):
    st.query_params["page"] = page_name  # Isso atualiza a URL
    # `st.session_state["page"]` será sincronizado no próximo rerun automaticamente
    st.rerun()

# 🔘 Menu lateral (só após login)
if st.session_state["page"] not in ["login", "register", 'select_genres', 'select_songs']:
    st.sidebar.image("web/assets/logo_vazada_m4u_laranja.png", width=300)
    if st.sidebar.button("🏠 Página Inicial", use_container_width=True):
        switch_page("home")
    if st.sidebar.button("🎶 Suas Músicas", use_container_width=True):
        switch_page("recommendations")  
    if st.sidebar.button("🔎 Pesquisar", use_container_width=True):
        switch_page("busca")  
    if st.sidebar.button("📊 Suas Preferências", use_container_width=True):
        switch_page("dashboard")
    if st.sidebar.button("🚪 Logout", use_container_width=True):
        switch_page("login")

# 🧩 Mapear páginas e carregar
page_module_map = {
    "login": "pagess.login",
    "register": "pagess.register",
    "select_genres": "pagess.select_genres",
    "select_songs": "pagess.select_songs",
    "home": "pagess.home",
    "recommendations": "pagess.recomendacoes",
    "busca": "pagess.busca",
    "dashboard": "pagess.dashboard"
}

# ✅ Importar e chamar a função principal
if st.session_state["page"] in page_module_map:
    page_module = importlib.import_module(page_module_map[st.session_state["page"]])
    page_module.show()
else:
    st.error("Página não encontrada.")
