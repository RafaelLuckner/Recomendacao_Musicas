import streamlit as st
import sources
from utils.auth_utils import is_valid_token, update_password

def show():
    st.title("🔑 Redefinir Senha")
    
    # Obtém o token da URL
    params = st.query_params
    token = params.get("token", [None])[0]
    
    if not token or not is_valid_token(token):
        st.error("Link inválido ou expirado.")
        if st.button("Voltar para Login"):
            sources.switch_page("login")
        return
    
    with st.form("reset_password_form"):
        new_password = st.text_input("Nova Senha", type="password")
        confirm_password = st.text_input("Confirmar Nova Senha", type="password")
        submit = st.form_submit_button("Atualizar Senha")
        
        if submit:
            if not new_password or not confirm_password:
                st.warning("Por favor, preencha todos os campos.")
            elif new_password != confirm_password:
                st.error("As senhas não coincidem.")
            elif len(new_password) < 8:
                st.error("A senha deve ter pelo menos 8 caracteres.")
            else:
                if update_password(token, new_password):
                    st.success("Senha atualizada com sucesso!")
                    sources.switch_page("login")
                else:
                    st.error("Erro ao atualizar senha. Tente novamente.")