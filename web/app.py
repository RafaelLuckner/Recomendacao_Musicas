import streamlit as st
import importlib

st.set_page_config(page_title="Recomendador de Músicas", page_icon='🎶', layout="wide", initial_sidebar_state="expanded")
if "page" not in st.session_state:
    st.session_state["page"] = "login"

def switch_page(page_name):
    st.session_state["page"] = page_name
    st.rerun()

if st.session_state["page"] not in ["login", "register", 'select_genres', 'select_songs']:
    # st.sidebar.title('Menu')
    st.sidebar.title('')
    st.sidebar.title('')
    st.sidebar.title('')
    st.sidebar.title('')
    st.sidebar.title('')
    if st.sidebar.button("🏠 Página Inicial", use_container_width=True):
        switch_page("home")
    if st.sidebar.button(" 🎶 Suas Músicas ", use_container_width=True, help= "Seu perfil com suas músicas preferidas"):
        switch_page("recommendations")  
    if st.sidebar.button(" 🔎 Pesquisar", use_container_width=True):
        switch_page("busca")  
    if st.sidebar.button(" 📊 Suas Preferências", use_container_width=True):
        switch_page("dashboard")

    if st.sidebar.button("🚪 Logout", use_container_width=True):
        switch_page("login")


if st.session_state["page"] == "login":
    import pagess.login as page
elif st.session_state["page"] == "register":
    import pagess.register as page
elif st.session_state["page"] == "select_genres":
    import pagess.select_genres as page
elif st.session_state["page"] == "select_songs":
    import pagess.select_songs as page


elif st.session_state["page"] == "home":
    import pagess.home as page
elif st.session_state["page"] == "recommendations": 
    import pagess.recomendacoes as page
elif st.session_state["page"] == "busca":
    import pagess.busca as page
elif st.session_state["page"] == "dashboard":
    import pagess.dashboard as page
    

page.show()
