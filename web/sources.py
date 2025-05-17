import pymongo
from pymongo import MongoClient
from bson import ObjectId 
import streamlit as st
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
import re
import string
import secrets
import codecs

def select_colection(colecao = "usuarios"):
    load_dotenv()

    mongo_client = os.getenv("MONGO_CLIENT")
    mongo_client = codecs.decode(mongo_client, 'unicode_escape')


    client = MongoClient(mongo_client)

    # Selecionar o banco de dados
    db = client["M4U"]

    if colecao == "usuarios":
        # Selecionar a coleção (tabela)
        collection = db["usuarios"]

    elif colecao == "info_usuarios":
        # Selecionar a coleção (tabela)
        collection = db["info_usuarios"]
        
    elif colecao == "reset_tokens":
        collection = db["reset_tokens"]

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
    try:
        user_id = ObjectId(user_id)
    except Exception as e:
        print(f"Erro ao converter id_user para ObjectId: {e}")
        return []
    user = collection.find_one({"user_id": user_id})
    return user.get("historico", []) if user else []



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
        # Validar user_id
        if not user_id:
            raise ValueError("user_id não fornecido")
        user_id = ObjectId(user_id)  # Converter para ObjectId
        # Validar new_entry
        if not isinstance(new_entry, dict) or not all(key in new_entry for key in ["song", "artist", "timestamp"]):
            raise ValueError("new_entry inválido ou incompleto")
        new_entry["timestamp"] = int(time.time())  # Garantir timestamp atualizado
        collection.update_one(
            {"user_id": user_id},
            {"$push": {"historico": new_entry}},
            upsert=True
        )
    except Exception as e:
        st.error(f"Erro ao salvar histórico: {e}")
        raise  # Re-raise para depuração

def save_rating(rating_entry, user_id):
    """
    Salva ou atualiza a avaliação de uma música no MongoDB, incluindo cover_url.
    Se a música já tiver sido avaliada, atualiza a nota e cover_url; caso contrário, adiciona uma nova entrada.
    
    Args:
        rating_entry (dict): Dicionário com as chaves 'song', 'artist', 'rating', 'timestamp', 'cover_url'.
        user_id (str): ID do usuário no MongoDB.
    """
    collection = select_colection("info_usuarios")
    try:
        if not user_id:
            raise ValueError("user_id não fornecido")
        user_id = ObjectId(user_id)
        if not isinstance(rating_entry, dict) or not all(key in rating_entry for key in ["song", "artist", "rating", "timestamp", "cover_url"]):
            raise ValueError("rating_entry inválido ou incompleto")
        if not isinstance(rating_entry["rating"], int) or not (1 <= rating_entry["rating"] <= 5):
            raise ValueError("Nota inválida: deve ser um inteiro entre 1 e 5")
        
        rating_entry["timestamp"] = int(time.time())
        
        existing_rating = collection.find_one(
            {"user_id": user_id, "avaliacoes": {"$elemMatch": {"song": rating_entry["song"], "artist": rating_entry["artist"]}}}
        )
        
        if existing_rating:
            collection.update_one(
                {"user_id": user_id, "avaliacoes.song": rating_entry["song"], "avaliacoes.artist": rating_entry["artist"]},
                {"$set": {
                    "avaliacoes.$.rating": rating_entry["rating"],
                    "avaliacoes.$.timestamp": rating_entry["timestamp"],
                    "avaliacoes.$.cover_url": rating_entry["cover_url"]
                }}
            )
        else:
            collection.update_one(
                {"user_id": user_id},
                {"$push": {"avaliacoes": rating_entry}},
                upsert=True
            )
    except Exception as e:
        st.error(f"Erro ao salvar avaliação: {e}")
        raise

def load_rating(song, artist, user_id):
    """
    Carrega a avaliação existente de uma música para um usuário.
    
    Args:
        song (str): Nome da música.
        artist (str): Nome do artista.
        user_id (str): ID do usuário no MongoDB.
    
    Returns:
        dict or None: Dicionário com a avaliação (incluindo rating e cover_url) se existir, None caso contrário.
    """
    collection = select_colection("info_usuarios")
    try:
        user_id = ObjectId(user_id)
        user = collection.find_one(
            {"user_id": user_id, "avaliacoes": {"$elemMatch": {"song": song, "artist": artist}}}
        )
        if user:
            for rating in user.get("avaliacoes", []):
                if rating["song"] == song and rating["artist"] == artist:
                    print(f"DEBUG: Avaliação encontrada: {rating['rating']}, music: {song}, artist: {artist}")
                    return rating
        return None
    except Exception as e:
        st.error(f"Erro ao carregar avaliação: {e}")
        return None

def load_rating_history(user_id):
    collection = select_colection("info_usuarios")
    try:
        user_id = ObjectId(user_id)
        user = collection.find_one({"user_id": user_id})
        return user.get("avaliacoes", []) if user else []
    except Exception as e:
        st.error(f"Erro ao carregar histórico de avaliações: {e}")
        return []
        
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
    
def store_reset_token(email, token):
        print(f"Armazenando token: {token} para o email: {email}")
        password_reset_tokens = select_colection("reset_tokens")
        print("Selecionando coleção")
        password_reset_tokens.delete_many({"email": email})
        password_reset_tokens.insert_one({
            "email": email,
            "token": token,
            "expires_at": datetime.now() + timedelta(hours=1),
            "used": False
})
        
def is_valid_token(token):
    password_reset_tokens = select_colection("reset_tokens")
    return password_reset_tokens.find_one({
        "token": token,
        "used": False,
        "expires_at": {"$gt": datetime.now()}
    }) is not None

def update_password(token, new_password):
    password_reset_tokens = select_colection("reset_tokens")
    token_data = password_reset_tokens.find_one({"token": token})
    if token_data:
        # Atualiza a senha do usuário (use bcrypt em produção)
        users = select_colection("usuarios")
        users.update_one(
            {"email": token_data["email"]},
            {"$set": {"password": new_password}}
        )
        # Marca o token como usado
        password_reset_tokens.update_one(
            {"token": token},
            {"$set": {"used": True}}
        )
        return True
    return False

def is_valid_email(email):
    regex = r"^[\w\.-]+@[\w\.-]+\.\w{2,}$"
    return re.match(regex, email) is not None

def generate_token(length=8):
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

