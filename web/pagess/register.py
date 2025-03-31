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
    st.title("📝 Cadastro")
    st.write("Crie sua conta para acessar a plataforma.")
    
    name = st.text_input("👤 Nome Completo")
    email = st.text_input("📧 E-mail")
    password = st.text_input("🔑 Senha", type="password")
    confirm_password = st.text_input("🔑 Confirme sua Senha", type="password")

    col1, col2 = st.columns([1, 1])

    with col1:
        register_button = st.button("Cadastrar")
    with col2:
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
                        "usuario_id": resultado.inserted_id,  # Usa o ID do usuário recém-criado
                        "historico": [],  # Os campos iniciam vazios
                        "generos_escolhidos": [],
                        "musicas_fav": []  
                    }

                    # Inserir o documento na coleção info_usuarios
                    colecao_info_usuarios.insert_one(documento_info)

                    st.success("✅ Conta criada com sucesso!")
                    st.session_state["page"] = "select_genres"
                    st.session_state["user_id"] = str(resultado.inserted_id)  # Armazena o ID na sessão
                    st.rerun()

    if back_to_login:
        st.session_state["page"] = "login"
        st.rerun()
    
    # Botão de teste (opcional - pode remover)
    test = st.button("test")
    if test:
        st.session_state['name'] = 'teste'
        st.session_state["page"] = "select_genres"
        st.rerun()