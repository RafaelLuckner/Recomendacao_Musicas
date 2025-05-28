import streamlit as st
from pymongo import MongoClient
from passlib.context import CryptContext
from sources import search_user_id_mongodb, search_history_user, select_colection
import secrets  # For generating random password for Google users

# Configuração do hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def switch_page(page_name):
    st.session_state["page"] = page_name
    params = {"page": page_name}
    if "email" in st.session_state:
        params["email"] = st.session_state["email"]
    st.query_params.clear()
    st.query_params.update(params)
    st.rerun()

colecao_users = select_colection("usuarios")
colecao_info_users = select_colection("info_usuarios")

def verify_password(plain_password, hashed_password):
    """Verifica se a senha plain corresponde ao hash armazenado"""
    return pwd_context.verify(plain_password, hashed_password)

def inicializar_sessao():
    """Inicializa as variáveis de sessão necessárias"""
    if "email" not in st.session_state:
        st.session_state.email = None
    if "name" not in st.session_state:
        st.session_state.name = None
    if "needs_username" not in st.session_state:
        st.session_state.needs_username = False
    if "google_user" not in st.session_state:
        st.session_state.google_user = None

def processar_login_google():
    """Processa o login via Google e verifica se precisa criar conta"""
    if st.user.is_logged_in:
        user_info = st.user
        email = user_info.get('email')
        nome = user_info.get('name')

        # Verifica se o usuário já existe
        user_data = colecao_users.find_one({"email": email})
        
        if user_data:
            # Usuário existente, faz login
            st.session_state.email = email
            st.session_state.name = user_data["nome"]
            st.query_params["email"] = email
            switch_page("home")
        else:
            # Novo usuário, cria conta automaticamente
            hashed_password = pwd_context.hash(secrets.token_urlsafe(16))  # Gera senha aleatória
            documento_usuario = {
                "nome": nome.strip(),
                "email": email.lower().strip(),
                "senha": hashed_password
            }
            resultado = colecao_users.insert_one(documento_usuario)
            
            # Criar perfil do usuário
            documento_info = {
                "user_id": resultado.inserted_id,
                "historico": [],
                "generos_escolhidos": [],
                "musicas_escolhidas": []
            }
            colecao_info_users.insert_one(documento_info)
            
            # Configurar sessão
            st.session_state.email = email
            st.session_state.name = nome
            st.query_params["email"] = email
            st.session_state.google_user = {
                'email': email,
                'name': nome,
                'picture': user_info.get('picture')
            }
            switch_page("select_genres")

def show():
    inicializar_sessao()
    
    # Verifica se o usuário está logado via Google
    if st.user.is_logged_in and not st.session_state.email:
        processar_login_google()

    col1, col2 = st.columns([1, 1])
    with col1:
        st.title("🔒 Login")
        st.write("Faça login para acessar a plataforma.")

        email = st.text_input("📧 E-mail", placeholder="Ex: seuemail@gmail.com")
        password = st.text_input("🔑 Senha", type="password")

        col3, col4, col5 = st.columns([3, 4, 6])
        
        with col3:
            login_button = st.button("Entrar")
        with col4:
            register_button = st.button("Cadastrar")
        with col5:
            esqueci_a_senha_button = st.button("Esqueci minha senha")

        # Adiciona botão de login com Google
        st.divider()
        st.subheader("Ou faça login com Google")
        if st.button("🔑 Entrar com Google", type="primary", use_container_width=True):
            st.login("google")

        if login_button:
            if not email or not password:
                st.error("❌ Por favor, preencha e-mail e senha!")
            else:
                # Busca apenas pelo email (não pela senha)
                user_data = colecao_users.find_one({"email": email})
                
                if user_data and verify_password(password, user_data["senha"]):
                    st.session_state.email = user_data["email"]
                    st.session_state.name = user_data["nome"]
                    st.query_params["email"] = user_data["email"]
                    switch_page("home")
                else:
                    st.error("❌ E-mail ou senha incorretos!")

        if register_button:
            switch_page("register")

        if esqueci_a_senha_button:
            switch_page("esqueceu_senha")

    with col2:
        import base64
        image_path = "web/assets/logo_vazada_m4u_laranja.png"

        with open(image_path, "rb") as img_file:
            img_base64 = base64.b64encode(img_file.read()).decode()

        st.markdown(
            f"""
            <style>
                .centered-container {{
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 60vh;
                }}
                .centered-container img {{
                    max-width: 100%;
                    height: auto;
                }}
            </style>
            <div class="centered-container">
                <img src="data:image/png;base64,{img_base64}" />
            </div>
            """,
            unsafe_allow_html=True
        )