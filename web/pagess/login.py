import streamlit as st
from pymongo import MongoClient
from passlib.context import CryptContext
from sources import search_user_id_mongodb
from sources import search_history_user
from sources import select_colection

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

def show():
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

        if login_button:
            if not email or not password:
                st.error("❌ Por favor, preencha e-mail e senha!")
            else:
                # Busca apenas pelo email (não pela senha)
                user_data = colecao_users.find_one({"email": email})
                
                if user_data and verify_password(password, user_data["senha"]):
                    st.session_state["email"] = user_data["email"]
                    st.session_state["name"] = user_data["nome"]
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