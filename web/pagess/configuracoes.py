import streamlit as st
import time
import sources  # Importando a função para deletar usuário, se necessário

def show():
    st.title("Configurações")

    # Verifica se já foi solicitado o processo de deletação
    if "deletar_conta" not in st.session_state:
        st.session_state.deletar_conta = False  # Inicializa o estado da deleção como False

    # **Botão de Logout**
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.clear()  # Limpa tudo no session state (efetivamente desloga o usuário)
            st.success("Você foi deslogado com sucesso.")
            time.sleep(1)  # Aguarda um pouco antes de redirecionar
            switch_page("login")  # Redireciona para a página de login

    with col2:
        # **Botão de Deletar Conta**
        if st.button("🗑️ Deletar conta", use_container_width=True):
            st.session_state.deletar_conta = True  # Marca como verdadeiro para iniciar o processo de confirmação
            st.warning("Tem certeza de que deseja deletar sua conta?")

        # Se o usuário clicar em "Deletar conta", exibe a confirmação
        if st.session_state.deletar_conta:
            col1, col2 = st.columns(2)  # Criar duas colunas para os botões de confirmação
            with col1:
                if st.button("Sim", use_container_width=True):
                    print("Deletar conta sim clicado")

                    try:
                        # Lógica para deletar a conta
                        email = st.session_state["email"]
                        delete = sources.delete_user_by_email(email)  # Deletando a conta do usuário
                        if delete:
                            st.success("Conta deletada com sucesso.")
                            st.session_state.clear()  # Limpa tudo no session state
                            time.sleep(1)
                            switch_page("login")  # Redireciona para a página de login
                        else:
                            st.error("Erro ao deletar conta.")
                    except Exception as e:
                        st.error(f"❌ Erro ao deletar conta: {str(e)}")
                    st.session_state.deletar_conta = False  # Reseta o estado de deleção após execução

            with col2:
                if st.button("Não", use_container_width=True):
                    st.session_state.deletar_conta = False
                    st.rerun()

# Função para redirecionar para uma página específica
def switch_page(page_name):
    st.query_params["page"] = page_name
    if "email" in st.session_state:
        st.query_params["email"] = st.session_state["email"]
    st.rerun()
