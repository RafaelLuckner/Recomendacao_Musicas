import streamlit as st
from pymongo import MongoClient

# Conectar ao servidor MongoDB local
client = MongoClient("mongodb+srv://leticia:ADMIN@m4u.5gwte.mongodb.net/?retryWrites=true&w=majority&appName=M4U")

# Selecionar o banco de dados
db = client["M4U"]

# Selecionar a coleção (tabela)
colecao = db["usuarios"]

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

                # Verificar se o e-mail ja foi cadastrado
                if colecao.find_one({"email": email}) is not None:
                    st.error("❌ Uma conta com esse e-mail já existe!")
                else:

                    # Criar um documento (registro)
                    documento = {
                        "nome": name,
                        "email": email,
                        "senha": password
                    }

                    # Inserir o documento na coleção
                    resultado = colecao.insert_one(documento)

                    # Exibir o ID do documento inserido
                    print("Documento inserido com ID:", resultado.inserted_id)

                    st.success("✅ Conta criada com sucesso!")
                    st.session_state["page"] = "home"
                    st.rerun()

    if back_to_login:
        st.session_state["page"] = "login"
        st.rerun()
