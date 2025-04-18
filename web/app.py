import streamlit as st
import importlib
import sources
import time

st.set_page_config(
    page_title="M4U",
    page_icon='web/assets/logo_icon.png',
    layout="wide",
    initial_sidebar_state="expanded"
)

# 🚀 Recuperar parâmetros da URL
query_params = st.query_params
page_from_url = query_params.get("page", "login")
email_from_url = query_params.get("email")

# ✅ Sincronizar email com session_state
if "email" not in st.session_state and email_from_url:
    st.session_state["email"] = email_from_url

# ✅ Sincronizar página com session_state
if st.session_state.get("page") != page_from_url:
    st.session_state["page"] = page_from_url

# 🔄 Trocar de página e manter email na URL
def switch_page(page_name):
    st.query_params["page"] = page_name
    if "email" in st.session_state:
        st.query_params["email"] = st.session_state["email"]
    st.rerun()

# 🔘 Menu lateral (só após login/cadastro)
if st.session_state["page"] not in ["login", "register", "select_genres", "select_songs"]:
    st.sidebar.image("web/assets/logo_vazada_m4u_laranja.png", width=300, use_container_width=True)
    
    if st.sidebar.button("🏠 Página Inicial", use_container_width=True):
        switch_page("home")
    if st.sidebar.button("🎶 Suas Músicas", use_container_width=True):
        switch_page("recommendations")
    if st.sidebar.button("🔎 Pesquisar", use_container_width=True):
        switch_page("busca")
    if st.sidebar.button("📊 Suas Preferências", use_container_width=True):
        switch_page("dashboard")
    if st.sidebar.button("⚙️ Configurações", use_container_width=True):
        switch_page("configuracoes")  # Redireciona para a página de configurações


# 🧩 Mapeamento de páginas
page_module_map = {
    "login": "pagess.login",
    "register": "pagess.register",
    "select_genres": "pagess.select_genres",
    "select_songs": "pagess.select_songs",
    "home": "pagess.home",
    "recommendations": "pagess.recomendacoes",
    "busca": "pagess.busca",
    "dashboard": "pagess.dashboard",
    "configuracoes": "pagess.configuracoes" 
}

# ✅ Importar e carregar página
if st.session_state["page"] in page_module_map:
    page_module = importlib.import_module(page_module_map[st.session_state["page"]])
    page_module.show()
else:
    st.error("Página não encontrada.")
