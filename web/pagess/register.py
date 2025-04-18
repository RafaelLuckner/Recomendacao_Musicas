import streamlit as st
from pymongo import MongoClient
from bson import ObjectId  # Importe ObjectId para trabalhar com IDs do MongoDB

# Conectar ao servidor MongoDB local
client = MongoClient("mongodb+srv://leticia:ADMIN@m4u.5gwte.mongodb.net/?retryWrites=true&w=majority&appName=M4U")

# Selecionar o banco de dados
db = client["M4U"]

# Selecionar as coleções
colecao_usuarios = db["usuarios"]
colecao_info_usuarios = db["info_usuarios"]

def show():
    col1, col2 = st.columns([1, 1])
    with col1:
        st.title("📝 Cadastro")
        st.write("Crie sua conta para acessar a plataforma.")
        
        name = st.text_input("👤 Nome Completo", placeholder="Ex: Liam Ribeiro")
        email = st.text_input("📧 E-mail", placeholder= "Ex: seuemail@gmail.com")
        password = st.text_input("🔑 Senha", type="password")
        confirm_password = st.text_input("🔑 Confirme sua Senha", type="password")

        col3, col4 = st.columns([1, 2])

        with col3:
            register_button = st.button("Cadastrar")
        with col4:
            back_to_login = st.button("Já tem conta? Faça Login")

        if register_button:
            # Verificar se todos os campos foram preenchidos
            if not (name and email and password and confirm_password):
                st.error("❌ Por favor, preencha todos os campos!")
            else:
                
                # Verificar se as senhas coincidem
                if password != confirm_password:
                    st.error("❌ As senhas não coincidem!")
                else:

                    # Verificar se o e-mail já foi cadastrado
                    if colecao_usuarios.find_one({"email": email}) is not None:
                        st.error("❌ Uma conta com esse e-mail já existe!")
                    else:

                        # Criar um documento (registro) para a coleção usuarios
                        documento_usuario = {
                            "nome": name,
                            "email": email,
                            "senha": password
                        }

                        # Inserir o documento na coleção usuarios
                        resultado = colecao_usuarios.insert_one(documento_usuario)

                        # Criar um documento vinculado na coleção info_usuarios
                        documento_info = {
                            "user_id": resultado.inserted_id,  # Usa o ID do usuário recém-criado
                            "historico": [],  
                            "generos_escolhidos": [],
                            "musicas_escolhidas": []
                        }

                        # Inserir o documento na coleção info_usuarios
                        colecao_info_usuarios.insert_one(documento_info)

                        st.success("✅ Conta criada com sucesso!")
                        st.query_params["page"] = "select_genres"
                        st.session_state["user_id"] = str(resultado.inserted_id)  # Armazena o ID na sessão
                        st.session_state["email"] = email
                        st.query_params["email"] = email
                        st.rerun()

        if back_to_login:
            st.query_params["page"] = "login"
            st.rerun()
        
        # Botão de teste (opcional - pode remover)
        test = st.button("test")
        if test:
            st.session_state['name'] = 'teste'
            st.query_params["page"] = "select_genres"
            st.rerun()

    with col2:
        import base64
        image_path = "web/assets/logo_vazada_m4u_laranja.png"

        # Lê e converte para base64
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