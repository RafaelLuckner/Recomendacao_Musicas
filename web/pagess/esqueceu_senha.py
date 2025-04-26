import streamlit as st
import re
import sources

def switch_page(target_page: str):
    st.session_state["page"] = target_page
    params = {"page": target_page}
    if "email" in st.session_state:
        params["email"] = st.session_state["email"]
    st.query_params.update(params)
    st.rerun()

def show():
    st.title("🔒 Esqueceu sua senha?")
    st.write("Informe seu e-mail cadastrado para receber as instruções de redefinição de senha.")

    with st.form("esqueci_senha_form"):
        email = st.text_input("E-mail", placeholder="seuemail@exemplo.com")
        submit = st.form_submit_button("Enviar")

        if submit:
            if not email:
                st.warning("Por favor, preencha o e-mail.")
            elif not is_valid_email(email):
                st.error("Formato de e-mail inválido.")
            else:
                # Aqui você pode chamar sua função de envio de e-mail
                st.error("O sistema de redefinição de senha ainda está em desenvolvimento.")
                token = sources.generate_token() # Gere um token para o e-mail
                st.error(token)
                sources.store_reset_token(email, token)  # Armazene o token no banco de dados
                st.error("Token armazenado com sucesso.")
                sources.send_reset_email(email, token)  # Envie o e-mail com o link de redefinição
                # st.success(f"Instruções de redefinição de senha foram enviadas para {email}.")

    # Botão voltar
    if st.button("Voltar"):
        switch_page("login")  # Altere "login" para o nome real da página anterior
        

def is_valid_email(email):
    """Valida formato básico de e-mail"""
    regex = r"^[\w\.-]+@[\w\.-]+\.\w{2,}$"
    return re.match(regex, email) is not None
