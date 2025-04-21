import streamlit as st
from pymongo import MongoClient
from sources import search_user_id_mongodb
from sources import search_history_user
from sources import select_colection

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
            # Verificar se o e-mail e senha existem no banco de dados
            documento = colecao_users.find_one({"email": email, "senha": password})
            if documento is None:
                st.error("❌ E-mail ou senha incorretos!")
            else:
                st.session_state["email"] = documento["email"]
                st.session_state["password"] = documento["senha"]
                st.session_state["name"] = documento["nome"]
                st.query_params["email"] = documento["email"]
                switch_page("home")

        if register_button:
            switch_page("register")

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
                    height: 60vh;  /* Ocupa a altura da tela */
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