import streamlit as st
import importlib

st.set_page_config(page_title="M4U", page_icon='▶️', layout="wide", initial_sidebar_state="expanded")

# 🚀 Recuperar parâmetro da URL com nova API
query_params = st.query_params
page_from_url = query_params.get("page", "login")

# 🧠 Definir página inicial com fallback
if "page" not in st.session_state:
    st.session_state["page"] = page_from_url

# 🔄 Função para trocar de página e atualizar a URL
def switch_page(page_name):
    st.session_state["page"] = page_name
    st.query_params["page"] = page_name
    st.rerun()

if "last_page_param" not in st.session_state:
    st.session_state["last_page_param"] = page_from_url
elif page_from_url != st.session_state["last_page_param"]:
    st.session_state["page"] = page_from_url
    st.session_state["last_page_param"] = page_from_url
    st.rerun()
    
# 🔘 Menu lateral (só após login)
if st.session_state["page"] not in ["login", "register", 'select_genres', 'select_songs']:
    st.sidebar.image("web/assets/logo_vazada_m4u_laranja.png", width=300)
    if st.sidebar.button("🏠 Página Inicial", use_container_width=True, help="Inicie por aqui"):
        switch_page("home")
    if st.sidebar.button("🎶 Suas Músicas", use_container_width=True, help="Seu perfil com suas músicas preferidas"):
        switch_page("recommendations")  
    if st.sidebar.button("🔎 Pesquisar", use_container_width=True, help="Ouça músicas e descubra as mais ouvidas do momento"):
        switch_page("busca")  
    if st.sidebar.button("📊 Suas Preferências", use_container_width=True, help="Descubra quais músicas e autores você costuma acompanhar"):
        switch_page("dashboard")
    if st.sidebar.button("🚪 Logout", use_container_width=True, help="Sair da conta"):
        switch_page("login")

# 🧩 Carregar a página correta
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

# ✅ Importar dinamicamente e chamar show()
page_module = importlib.import_module(page_module_map[st.session_state["page"]])
page_module.show()
