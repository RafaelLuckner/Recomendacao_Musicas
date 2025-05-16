import streamlit as st
import pandas as pd
import pymongo
from pymongo import MongoClient
import sources
from bson import ObjectId
from sources import initial_save_mongodb

@st.cache_data
def load_data():
    url_data ="data/data.csv"
    return pd.read_csv(url_data)

def switch_page(page_name):
    st.session_state["page"] = page_name
    params = {"page": page_name}
    if "email" in st.session_state:
        params["email"] = st.session_state["email"]
    st.query_params.clear()
    st.query_params.update(params)
    st.rerun()

def show():


    # Carregar dados
    data = load_data()
    genres = data['track_genre'].unique()

    # Verificar se os estados existem
    if "selected_genres" not in st.session_state:
        st.session_state["selected_genres"] = []
    if "search_query" not in st.session_state:
        st.session_state["search_query"] = ""

    # Título da seção
    st.subheader("🎧 Escolha seus gêneros favoritos")

    # Limite de gêneros selecionados
    max_genres = 5

    
    if st.session_state["selected_genres"]:
        st.write("### Gêneros selecionados:")
        # Exibir os gêneros dentro de uma borda
        st.write(f"```{', '.join(st.session_state['selected_genres']).upper()}```")
        
        col1, col2 = st.columns(2)
        with col1:
            # Botão para limpar gêneros selecionados
            button = st.button("Limpar gêneros selecionados", use_container_width=True)
            if button:
                st.session_state["selected_genres"] = []
                st.rerun()

        # seguir para pagina inicial
        with col2:
            if st.button("Continuar", key="voltar", use_container_width=True):
                initial_save_mongodb("generos_escolhidos", st.session_state["selected_genres"])
                st.query_params["page"] = "home"
                st.rerun()
    else:
        st.write("### Gêneros selecionados:")
        st.write("Nenhum gênero selecionado.")

    st.write("---")  

    # Campo de busca para filtrar gêneros
    search_query = st.text_input("🔍 Filtrar gêneros", placeholder="Digite um gênero...").lower()

    # Filtrar gêneros com base na pesquisa
    import unicodedata

    def remove_acentos(texto):
        return ''.join(
            c for c in unicodedata.normalize('NFKD', texto)
            if not unicodedata.combining(c)
        )

    # Filtrar e ordenar gêneros com base na primeira palavra sem acento
    filtered_genres = sorted(
        [g for g in genres if search_query in remove_acentos(g.lower())] if search_query else genres,
        key=lambda x: remove_acentos(x.split()[0].lower()))
    # Criar layout em 3 colunas x 3 linhas
    rows = [filtered_genres[i:i+3] for i in range(0, len(filtered_genres), 3)]

    for row in rows:
        col1, col2, col3 = st.columns(3)
        for idx, genre in enumerate(row):
            col = [col1, col2, col3][idx]
            is_selected = genre in st.session_state["selected_genres"]
            
            # Verificar se o número de gêneros selecionados não ultrapassa o limite
            if len(st.session_state["selected_genres"]) < max_genres or is_selected:
                if col.button(f"{'✅' if is_selected else '🎶'} {genre.capitalize()}", key=genre, use_container_width=True, help=f"{'Remover' if is_selected else 'Adicionar'} {genre}"):
                    if is_selected:
                        st.session_state["selected_genres"].remove(genre)
                    else:
                        st.session_state["selected_genres"].append(genre)
                    st.rerun()
            elif not is_selected:
                col.button(f"{genre} (max: {max_genres})", key=f"{genre}_disabled", disabled=True, use_container_width=True)
