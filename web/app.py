import streamlit as st
import importlib
import sources

# Configuração da página
st.set_page_config(
    page_title="M4U",
    page_icon='web/assets/logo_icon.png',
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- ---
# 1. Recupera parâmetros da URL (sempre strings)
params = st.query_params
current_page = params.get("page", "login")
current_email = params.get("email")

if current_page != st.session_state.get("page"):
    # Evita sobrescrever com "login" prematuramente
    if current_page != "login" or st.session_state.get("page") is None:
        st.session_state["page"] = current_page

if current_email and "email" not in st.session_state:
    st.session_state["email"] = current_email

# --- ---
# Função de navegação: atualiza session_state e synchroniza URL
def switch_page(target_page: str):
    st.session_state["page"] = target_page
    params = {"page": target_page}
    if "email" in st.session_state:
        params["email"] = st.session_state["email"]
    # st.query_params.clear()
    st.query_params.update(params)
    st.rerun()

# --- ---
# Sidebar de navegação (só quando o usuário está logado)
if st.session_state["page"] not in ["login", "register", "select_genres", "select_songs"]:
    st.sidebar.image(
        "web/assets/logo_vazada_m4u_laranja.png",
        width=300,
        use_container_width=True
    )
    if st.sidebar.button("🏠 Página Inicial", use_container_width=True):
        switch_page("home")
    if st.sidebar.button("🎶 Suas Músicas", use_container_width=True):
        switch_page("recommendations")
    if st.sidebar.button("🔎 Pesquisar", use_container_width=True):
        switch_page("busca")
    if st.sidebar.button("📊 Suas Preferências", use_container_width=True):
        switch_page("dashboard")
    if st.sidebar.button("⚙️ Configurações", use_container_width=True):
        switch_page("configuracoes")

# --- ---
# Mapeamento de módulos de página
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

# --- ---
# Importa e exibe o módulo correspondente à página corrente
page_key = st.session_state.get("page", "login")
if page_key in page_module_map:
    module_path = page_module_map[page_key]
    page_module = importlib.import_module(module_path)
    page_module.show()
else:
    st.error(f"Página '{page_key}' não encontrada.")
