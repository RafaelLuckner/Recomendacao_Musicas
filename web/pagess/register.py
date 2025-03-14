import streamlit as st

def show():
    st.title("📝 Cadastro")
    st.write("Crie sua conta para acessar a plataforma.")

    name = st.text_input("👤 Nome Completo")
    email = st.text_input("📧 E-mail")
    password = st.text_input("🔑 Senha", type="password")
    confirm_password = st.text_input("🔑 Confirme sua Senha", type="password")

    col1, col2 = st.columns([1, 1])

    with col1:
        register_button = st.button("Cadastrar")
    with col2:
        back_to_login = st.button("Já tem conta? Faça Login")

    if register_button:
        if password == confirm_password:
            # Aqui entraria a lógica de criação de usuário no Firebase
            st.success("✅ Conta criada com sucesso!")
            st.session_state["page"] = "login"
            st.rerun()
        else:
            st.error("❌ As senhas não coincidem!")

    if back_to_login:
        st.session_state["page"] = "login"
        st.rerun()
