import pymongo
from pymongo import MongoClient
from bson import ObjectId 
import streamlit as st
import time
from datetime import datetime
from dotenv import load_dotenv
import os


def select_colection(colecao = "usuarios"):
    load_dotenv()

    mongo_client = os.getenv("MONGO_CLIENT")

    client = MongoClient(mongo_client)

    # Selecionar o banco de dados
    db = client["M4U"]

    if colecao == "usuarios":
        # Selecionar a coleção (tabela)
        collection = db["usuarios"]

    elif colecao == "info_usuarios":
        # Selecionar a coleção (tabela)
        collection = db["info_usuarios"]
    
    return collection

def load_info_user(user_id, campo):
    # Conectar ao MongoDB
    collection = select_colection("info_usuarios")
    user = collection.find_one({"user_id": user_id})
    if user is not None:
        return user.get(campo)
    return []



def search_user_id_mongodb(email):
    collection = select_colection("usuarios")
    user = collection.find_one({"email": email})
    if user is not None:
        return user.get("_id")
    return None

def search_history_user(user_id):
    collection = select_colection("info_usuarios")
    # Converter o id_user para ObjectId
    try:
        user_id = ObjectId(user_id)
    except Exception as e:
        print(f"Erro ao converter id_user para ObjectId: {e}")
        return []
    user = collection.find_one({"user_id": user_id})
    if user is not None:
        return user.get("historico")
    return 



def initial_save_mongodb(campo, info):
    user_id = search_user_id_mongodb(st.session_state["email"])

    if not user_id:
        st.error("Usuário não encontrado.")
        return
    collection_info = select_colection("info_usuarios")

    collection_info.update_one(
        {"user_id": ObjectId(user_id)},
        {"$set": {campo: info}})


def save_search_history(new_entry, user_id):
    collection = select_colection("info_usuarios")
    try:
        new_entry["timestamp"] = int(time.time())
        collection.update_one(
            {"user_id": user_id},  # Ajuste conforme necessário
            {"$push": {"historico": new_entry}},
            upsert=True
        )
    except Exception as e:
        st.error(f"Erro ao salvar histórico: {e}")
        
def delete_user_by_email(email):
    try:
        collection = select_colection("usuarios")

        # Verificar se o usuário existe
        user = collection.find_one({"email": email})
        
        if not user:
            st.error(f"Usuário com o email {email} não encontrado.")
            return False

        # Deletar o usuário da coleção "usuarios"
        result = collection.delete_one({"email": email})

        # Verificar se o usuário foi deletado
        if result.deleted_count > 0:
            st.success(f"Usuário com o email {email} foi deletado com sucesso.")
            return True  # Deleção bem-sucedida
        else:
            st.error(f"Falha ao deletar o usuário com o email {email}.")
            return False  # Nenhum documento foi deletado

    except Exception as e:
        st.error(f"Erro ao deletar conta: {e}")
        return False