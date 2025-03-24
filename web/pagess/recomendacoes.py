import streamlit as st
import time
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import os 
import dotenv
import pandas as pd

def clean_session_state():
    valid_keys = ["selected_genres", "selected_songs", "page", "search_query", "recommended_songs"]
    for key in list(st.session_state.keys()):
        if key not in valid_keys:
            del st.session_state[key]

def authenticate_spotify():
    client_id = os.getenv("SPOTIPY_CLIENT_ID")
    client_secret = os.getenv("SPOTIPY_CLIENT_SECRET")
    
    client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    return sp

# Função para buscar a capa do álbum com base na música
def get_album_cover(song_name, sp):
    # Pesquisar pela música no Spotify
    results = sp.search(q=song_name, limit=1, type='track')
    if results['tracks']['items']:
        track = results['tracks']['items'][0]
        album_cover_url = track['album']['images'][0]['url']  # Pega a imagem de maior qualidade
        return album_cover_url
    return None

def generate_recommendations(selected_genres, data):
    # Seleciona músicas aleatórias de cada gênero
    recommendations = []
    for genre in selected_genres:
        if data[data['track_genre'] == genre].notnull().any().any():
            genre_songs = data[data['track_genre'] == genre]
            recommendations.extend(genre_songs['track_name'].sample(5).tolist())
    return recommendations

def show():
    dotenv.load_dotenv()
    
    st.title("🎵 Recomendações Personalizadas")

    # Criar abas para navegação
    tab1, tab2, tab3 = st.tabs(["🎶 Recomendações", "🎧 Gêneros", 'Dados de Sessão / Músicas Disponiveis'])

    data = pd.read_csv('data/dataset.csv')
    genres = data['track_genre'].unique()

    if "selected_genres" not in st.session_state:
        st.session_state["selected_genres"] = []
    if "recommended_songs" not in st.session_state:
        st.session_state["recommended_songs"] = []
    if "search_query" not in st.session_state:
        st.session_state["search_query"] = ""
    if "search_results" not in st.session_state:
        st.session_state["search_results"] = []

    # Tab 1 - Gêneros
    with tab1:


        st.subheader("🎶 Recomendações de Música")

        # Verifica se os gêneros foram selecionados
        if st.session_state.get("selected_genres"):
            selected_genres = st.session_state["selected_genres"]

            # Autentica com o Spotify
            sp = authenticate_spotify()

            # Se já houver recomendações salvas, exibe as recomendadas anteriormente
            if "recommended_songs" in st.session_state and st.session_state["recommended_songs"]:
                recommended_songs = st.session_state["recommended_songs"]
                st.write("Aqui estão suas recomendações anteriores:")
            else:
                # Se não houver recomendações salvas, inicializa uma lista vazia
                recommended_songs = []

            # Caso o botão para gerar novas recomendações seja clicado
            if st.button("🔄 Recomendar novas músicas"):
                # Exibe uma barra de progresso
                progress_bar = st.progress(0)
                status_text = st.empty()

                # Simula o processo de carregamento
                for i in range(100):
                    progress_bar.progress(i + 1)
                    status_text.text(f"Gerando recomendações... {i + 1}%")
                    time.sleep(0.001)  # Simula o tempo de carregamento

                # Chama a função de geração de recomendações
                recommended_songs = generate_recommendations(selected_genres, data)

                # Salva as novas recomendações no session_state
                st.session_state["recommended_songs"] = recommended_songs

                # Exibe as músicas recomendadas de maneira organizada
                st.write("Aqui estão suas novas recomendações:")

            # Organiza as músicas recomendadas em duas linhas
            num_columns = 3  # Número de colunas por linha
            num_lines = 2  # Número de linhas

            # Divide as recomendações em duas linhas
            for line in range(num_lines):
                start_idx = line * num_columns
                end_idx = start_idx + num_columns
                recommended_songs_line = recommended_songs[start_idx:end_idx]

                # Cria as colunas para cada linha
                cols = st.columns(num_columns)

                # Exibe cada música na linha
                for idx, song in enumerate(recommended_songs_line):
                    col = cols[idx]  # Obtém a coluna correspondente à música
                    album_cover_url = get_album_cover(song, sp)  # Pega a capa do álbum

                    # Exibe a capa e nome da música
                    if album_cover_url:
                        col.image(album_cover_url, width=200)
                        if col.button(f"{song}", key=song):
                            st.session_state["search_query"] = song
                            st.session_state["page"] = "search"
                            st.rerun()
                    else:
                        col.write(f"Erro ao carregar capa do álbum para {song}")

                # Adiciona uma linha horizontal após a primeira linha de recomendações
                if line == 0:
                    st.markdown('---')

            # Exibe as músicas recomendadas em formato de lista
            st.write(recommended_songs)

        else:
            st.warning("Selecione gêneros na aba 'Gêneros' para ver recomendações.")


    with tab2:
        st.subheader("🎧 Escolha seus gêneros favoritos")

        # campo de busca para filtrar gêneros
        search_query = st.text_input("🔍 Filtrar gêneros", placeholder="Digite um gênero...").lower()

        # Filtrar gêneros com base na pesquisa
        filtered_genres = [g for g in genres if search_query in g.lower()] if search_query else genres

        # Criar layout em 3 colunas x 3 linhas
        rows = [filtered_genres[i:i+3] for i in range(0, len(filtered_genres), 3)]

        for row in rows:
            col1, col2, col3 = st.columns(3)
            for idx, genre in enumerate(row):
                col = [col1, col2, col3][idx]
                is_selected = genre in st.session_state["selected_genres"]
                if col.button(f"{'✅' if is_selected else '❌'} {genre}", key=genre, use_container_width=True, help=f"{'Remover' if is_selected else 'Adicionar'} {genre}"):
                    if is_selected:
                        st.session_state["selected_genres"].remove(genre)
                    else:
                        st.session_state["selected_genres"].append(genre)
                    st.rerun()


    # Tab 3 - Dados de Sessão
    with tab3:
        clean_session_state()

        st.write("Dados de sessão:", st.session_state)

        st.write("Músicas disponíveis:")
        st.write(pd.DataFrame(data[['track_name', 'track_genre', 'artists']]))
