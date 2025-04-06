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

        email = st.text_input("📧 E-mail")
        password = st.text_input("🔑 Senha", type="password")

        col3, col4 = st.columns([1, 3])
        
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

                st.session_state["page"] = "home"
                st.rerun()

        if register_button:
            st.session_state["page"] = "register"
            st.rerun()
    with col2:
        import base64
        image_path = "web/assets/logo_vazada_m4u_laranja.png"

        # Lê e converte para base64
        with open(image_path, "rb") as img_file:
            img_base64 = base64.b64encode(img_file.read()).decode()

            st.markdown(
                f"""
                <div style="display: flex; justify-content: center; align-items: center;">
                    <img src="data:image/png;base64,{img_base64}" style="max-width: 700px;">
                </div>
                """,
                unsafe_allow_html=True
            )