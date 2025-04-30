import streamlit as st
from pymongo import MongoClient
from bson import ObjectId
from passlib.context import CryptContext  # Importação para hashing
import sources
import re  # Para validação de e-mail

# Configuração do hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Conectar ao servidor MongoDB local
colecao_usuarios = sources.select_colection("usuarios")
colecao_info_usuarios = sources.select_colection("info_usuarios")

def switch_page(page_name):
    st.session_state["page"] = page_name
    params = {"page": page_name}
    if "email" in st.session_state:
        params["email"] = st.session_state["email"]
    st.query_params.clear()
    st.query_params.update(params)
    st.rerun()

def is_valid_email(email):
    """Valida o formato do e-mail"""
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None

def is_strong_password(password):
    """Verifica se a senha é forte o suficiente"""
    if len(password) < 8:
        return False, "A senha deve ter pelo menos 8 caracteres"
    if not any(char.isdigit() for char in password):
        return False, "A senha deve conter pelo menos um número"
    if not any(char.isupper() for char in password):
        return False, "A senha deve conter pelo menos uma letra maiúscula"
    if not any(char.islower() for char in password):
        return False, "A senha deve conter pelo menos uma letra minúscula"
    return True, ""

def show():
    col1, col2 = st.columns([1, 1])
    with col1:
        st.title("📝 Cadastro")
        st.write("Crie sua conta para acessar a plataforma.")
        
        name = st.text_input("👤 Nome Completo", placeholder="Ex: Liam Ribeiro")
        email = st.text_input("📧 E-mail", placeholder="Ex: seuemail@gmail.com")
        password = st.text_input("🔑 Senha", type="password", 
                                help="A senha deve ter pelo menos 8 caracteres, incluindo letras maiúsculas, minúsculas e números")
        confirm_password = st.text_input("🔑 Confirme sua Senha", type="password")

        col3, col4 = st.columns([1, 2])

        with col3:
            register_button = st.button("Cadastrar")
        with col4:
            back_to_login = st.button("Já tem conta? Faça Login")

        if register_button:
            # Validação dos campos
            if not all([name, email, password, confirm_password]):
                st.error("❌ Por favor, preencha todos os campos!")
            elif not is_valid_email(email):
                st.error("❌ Por favor, insira um e-mail válido!")
            elif password != confirm_password:
                st.error("❌ As senhas não coincidem!")
            else:
                # Verificar força da senha
                is_strong, msg = is_strong_password(password)
                if not is_strong:
                    st.error(f"❌ Senha fraca: {msg}")
                else:
                    # Verificar se o e-mail já existe
                    if colecao_usuarios.find_one({"email": email}):
                        st.error("❌ Uma conta com esse e-mail já existe!")
                    else:
                        try:
                            # Criar hash da senha
                            hashed_password = pwd_context.hash(password)
                            
                            # Criar documento do usuário
                            documento_usuario = {
                                "nome": name.strip(),
                                "email": email.lower().strip(),  # Normaliza o e-mail
                                "senha": hashed_password  # Armazena apenas o hash
                            }

                            # Inserir no banco de dados
                            resultado = colecao_usuarios.insert_one(documento_usuario)

                            # Criar perfil do usuário
                            documento_info = {
                                "user_id": resultado.inserted_id,
                                "historico": [],
                                "generos_escolhidos": [],
                                "musicas_escolhidas": []
                            }

                            colecao_info_usuarios.insert_one(documento_info)

                            # Configurar sessão
                            st.session_state["user_id"] = str(resultado.inserted_id)
                            st.session_state["name"] = name
                            st.session_state["email"] = email
                            st.query_params["email"] = email
                            
                            st.success("✅ Conta criada com sucesso!")
                            st.balloons()
                            switch_page("select_genres")

                        except Exception as e:
                            st.error(f"❌ Ocorreu um erro ao criar a conta: {str(e)}")

        if back_to_login:
            switch_page("login")

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