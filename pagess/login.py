import streamlit as st

def show():
    st.title("🔒 Login")
    st.write("Faça login para acessar a plataforma.")

    email = st.text_input("📧 E-mail")
    password = st.text_input("🔑 Senha", type="password")

    col1, col2 = st.columns([1, 1])
    
    with col1:
        login_button = st.button("Entrar")
    with col2:
        register_button = st.button("Cadastrar")

    if login_button:
        # Aqui entraria a autenticação com Firebase
        st.session_state["page"] = "home"
        st.rerun()

    if register_button:
        st.session_state["page"] = "register"
        st.rerun()
