import streamlit as st
from pymongo import MongoClient

# Conectar ao servidor MongoDB local
client = MongoClient("mongodb+srv://leticia:ADMIN@m4u.5gwte.mongodb.net/?retryWrites=true&w=majority&appName=M4U")

# Selecionar o banco de dados
db = client["M4U"]

# Selecionar a coleção (tabela)
colecao = db["usuarios"]

def show():
    col1, col2 = st.columns([1, 1])
    with col1:
        st.title("🔒 Login")
        st.write("Faça login para acessar a plataforma.")

        email = st.text_input("📧 E-mail", placeholder="Ex: seuemail@gmail.com")
        password = st.text_input("🔑 Senha", type="password")

        col3, col4 = st.columns([1, 4])
        
        with col3:
            login_button = st.button("Entrar")
        with col4:
            register_button = st.button("Cadastrar")

        if login_button:
            # Verificar se o e-mail e senha existem no banco de dados
            documento = colecao.find_one({"email": email, "senha": password})
            if documento is None:
                st.error("❌ E-mail ou senha incorretos!")
            else:
                st.session_state["email"] = documento["email"]
                st.session_state["password"] = documento["senha"]
                st.session_state["name"] = documento["nome"]

                st.query_params["page"] = "home"
                st.rerun()

        if register_button:
            st.query_params["page"] = "register"
            st.rerun()
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