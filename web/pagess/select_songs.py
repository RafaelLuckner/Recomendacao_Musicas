import streamlit as st
import pandas as pd
import pymongo
from sources import initial_save_mongodb

# Cache para carregar os dados uma única vez
@st.cache_data
def load_data():
    url_data = "data/data.csv"

    return pd.read_csv(url_data)[['track_name', 'track_genre']].drop_duplicates()

def switch_page(page_name):
    st.session_state["page"] = page_name
    st.query_params.clear()
    st.query_params.update({
        "page": page_name,
        "email": st.session_state.get("email", "")
    })
    st.rerun()

def show():
    # Carregar dados
    data = load_data()

    # Inicializar estados se não existirem
    if "selected_songs" not in st.session_state:
        st.session_state["selected_songs"] = []
    if "selected_genres" not in st.session_state:
        st.session_state["selected_genres"] = []

    st.subheader("🎶 Escolha suas músicas favoritas")

    max_songs = 3
    
    # ======== Seção de Músicas ========

    # Campo de busca para músicas
    search_query = st.text_input("🔎 Buscar música", key="song_search")

    # Filtrar músicas
    if search_query:
        filtered_songs = data[data['track_name'].str.contains(search_query, case=False, na=False)]
    else:
        filtered_songs = data.head(50)  # Mostrar 50 músicas iniciais

    song_options = filtered_songs['track_name'].tolist()

    # Garantir que músicas selecionadas ainda existam
    selected_songs = [song for song in st.session_state["selected_songs"] if song in song_options]

    # Criar seletor de músicas
    selected_songs = st.multiselect(
        "Escolha até 3 músicas",
        options=song_options,
        default=selected_songs,
        max_selections=max_songs,
        help="Digite para filtrar músicas ou selecione até 3"
    )

    st.session_state["selected_songs"] = selected_songs


    # Exibir músicas selecionadas
    st.write("### Músicas selecionadas:")
    if selected_songs:
        st.write(f"`{', '.join(selected_songs).upper()}`")
    else:
        st.write("Nenhuma música selecionada.")

    st.write("---")
    # ======== Botões de Ação ========
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Limpar Seleção", use_container_width=True):
            st.session_state["selected_songs"] = []
            st.rerun()

    with col2:
        if st.button("Continuar", use_container_width=True):
            initial_save_mongodb("musicas_escolhidas", st.session_state["selected_songs"])
            switch_page("home")