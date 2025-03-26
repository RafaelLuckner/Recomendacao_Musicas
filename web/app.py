import streamlit as st
import importlib

if "page" not in st.session_state:
    st.session_state["page"] = "login"

def switch_page(page_name):
    st.session_state["page"] = page_name
    st.rerun()

if st.session_state["page"] not in ["login", "register", 'select_genres', 'select_songs']:
    st.sidebar.title('Menu')
    if st.sidebar.button("🏠 Página Inicial", use_container_width=True):
        switch_page("home")
    if st.sidebar.button("🔎 Buscar Música", use_container_width=True):
        switch_page("search")
    if st.sidebar.button(" 🎶 Suas Músicas ", use_container_width=True, help= "Seu perfil com suas músicas preferidas"):
        switch_page("recommendations")  
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
elif st.session_state["page"] == "search":
    import pagess.busca as page
elif st.session_state["page"] == "recommendations": 
    import pagess.recomendacoes as page

page.show()
