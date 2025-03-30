from datetime import date
import datetime
from datetime import datetime
import streamlit as st
import time
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import os 
import dotenv
import pandas as pd

def clean_session_state():
    valid_keys = ["selected_genres",
                  "selected_songs",
                  "page", 
                  "search_query", 
                  "recommended_songs",
                  "genre_recommendations",
                  'search_history', 
                  'name',
                  'email',
                  'password',
                  'image_cache',
                  "tab",
                  "avaliacao"]
    for key in list(st.session_state.keys()):
        if key not in valid_keys:
            del st.session_state[key]

def authenticate_spotify():
    client_id = os.getenv("SPOTIPY_CLIENT_ID")
    client_secret = os.getenv("SPOTIPY_CLIENT_SECRET")
    client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    return sp

def get_album_cover_and_artist(song_name, sp):
    results = sp.search(q=song_name, limit=1, type='track')
    if results['tracks']['items']:
        track = results['tracks']['items'][0]
        album_cover_url = track['album']['images'][0]['url']
        artist_name = track['artists'][0]['name']
        return album_cover_url, artist_name
    return None, None

def generate_recommendations(selected_genres, data, sp, limit=6):
    """
    Para cada gênero selecionado, seleciona aleatoriamente 6 músicas e 
    retorna um dicionário em que a chave é o nome da música e o valor é 
    um dicionário com: song, genre, artist e cover_url.
    """
    recommendations = {}
    for genre in selected_genres:
        genre_songs = data[data['track_genre'] == genre]
        if not genre_songs.empty:
            sampled = genre_songs['track_name'].sample(limit).tolist()
            for song in sampled:
                # Evita sobrescrever caso já exista (de outro gênero, por exemplo)
                if song not in recommendations:
                    cover_url, artist = get_album_cover_and_artist(song, sp)
                    # Só adiciona se conseguir obter os dados
                    if cover_url and artist:
                        recommendations[song] = {
                            "song": song,
                            "genre": genre,
                            "artist": artist,
                            "cover_url": cover_url
                        }
    return recommendations

def time_ago(timestamp):

    now = time.time()
    diff = now - timestamp
    if diff < 60:
        return f"Agora mesmo"
    elif diff < 3600:
        return f"{int(diff/60)} minutos atrás"
    elif diff < 86400:
        return f"{int(diff/3600)} horas atrás"
    else:
        return f"{int(diff/86400)} dias atrás"

def show():
    dotenv.load_dotenv()

    # Criar abas para navegação
    tab1, tab2, tab3 = st.tabs(["Para você ", " Histórico", " Gêneros"])

    data = pd.read_csv('data/data_traduct.csv')
    genres = data['track_genre'].unique()

    if "selected_genres" not in st.session_state:
        st.session_state["selected_genres"] = []
    if "search_query" not in st.session_state:
        st.session_state["search_query"] = ""
    if "search_history" not in st.session_state:
        st.session_state["search_history"] = []
    # Inicializa nosso dicionário de recomendações
    if "recommended_songs" not in st.session_state:
        st.session_state["recommended_songs"] = {}
    if "genre_recommendations" not in st.session_state:
        st.session_state["genre_recommendations"] = {}

    # Tab 1 - Gêneros
    with tab1:
        st.subheader("🎶 Recomendações de Música")
        
        if st.session_state.get("selected_genres"):
            selected_genres = st.session_state["selected_genres"]
            sp = authenticate_spotify()

            # Se o dicionário estiver vazio, gera recomendações
            if not st.session_state["recommended_songs"]:
                st.session_state["recommended_songs"] = generate_recommendations(selected_genres, data, sp)

            rec_dict = st.session_state["recommended_songs"]
            recommended_list = list(rec_dict.values())

            st.write("Aqui estão suas recomendações:")

            # Organiza as músicas em uma grade com 3 colunas e 2 linhas (6 músicas)
            num_columns = 3
            num_lines = 2
            # Seleciona as 6 primeiras músicas (ou ajuste conforme necessário)
            recommended_subset = recommended_list[:num_columns * num_lines]
            rows = [recommended_subset[i:i+num_columns] for i in range(0, len(recommended_subset), num_columns)]
            
            for row in rows:
                cols = st.columns(len(row))
                for idx, rec in enumerate(row):
                    with cols[idx]:
                        st.image(rec["cover_url"])
                        if st.button(f"{rec['song']} - {rec['artist']}", key=f"song_{rec['song']}_{idx}", use_container_width=True):
                            new_entry = {
                                "song": rec["song"],
                                "artist": rec["artist"],
                                "cover_url": rec["cover_url"],
                                "timestamp": time.time(),
                                "genre": rec["genre"]
                            }
                            st.session_state["search_history"].append(new_entry)
                            st.session_state["search_query"] = f"{rec['song']} - {rec['artist']}"
                            ##########################st.session_state["page"] = "busca"

                            st.rerun()
                st.markdown('---')
        else:
            st.warning("Selecione gêneros na aba 'Gêneros' para ver recomendações.")

        if st.button("Novas recomendações"):
            # Gera novas recomendações dinamicamente (atualizando o dicionário)
            sp = authenticate_spotify()
            selected_genres = st.session_state["selected_genres"]
            st.session_state["recommended_songs"] = generate_recommendations(selected_genres, data, sp)
            st.rerun()
            
        
    with tab2:
        st.subheader("📜 Histórico de Pesquisas")
        
        if "search_history" not in st.session_state:
            st.session_state["search_history"] = []
            
        if st.session_state["search_history"]:
            # Mantém apenas a entrada mais recente para cada música
            unique_songs = {}
            for entry in st.session_state["search_history"]:
                unique_songs[entry['song']] = entry
            unique_history = sorted(unique_songs.values(), key=lambda x: x['timestamp'], reverse=True)
            
            # Configuração de paginação
            items_per_page = 4
            total_items = len(unique_history)
            total_pages = (total_items + items_per_page - 1) // items_per_page
            
            if "history_page" not in st.session_state:
                st.session_state.history_page = 0  # Começa na primeira página
            
            # Calcula os itens para a página atual
            start_idx = st.session_state.history_page * items_per_page
            end_idx = start_idx + items_per_page
            current_items = unique_history[start_idx:end_idx]
            
            # Exibe os itens em horizontal
            cols = st.columns(items_per_page)
            for idx, entry in enumerate(current_items):
                with cols[idx]:
                    with st.container():
                        # Usa diretamente o cover_url da entrada
                        cover_url = entry.get("cover_url")
                        if cover_url:
                            st.image(cover_url)
                        else:
                            st.write("Sem capa disponível")
                        # Exibe o nome da música (limitando o tamanho, se necessário)
                        if len(entry['song']) > 30:
                            st.write(f"**{entry['song'][:30]}...**")
                        else:
                            st.write(f"**{entry['song']}**")
                        st.caption(f"Pesquisado {time_ago(entry['timestamp'])}")
                        if st.button("Pesquisar", key=f"hist_{entry['song']}"):
                            st.session_state["search_query"] = entry["song"]
                            ################################ st.session_state["page"] = "busca"
                            st.rerun()
                            
            # Navegação
            col_nav1, col_nav2, col_nav3 = st.columns([1, 1, 4])
            with col_nav1:
                if st.session_state.history_page > 0:
                    if st.button("Anteriores"):
                        st.session_state.history_page -= 1
                        st.rerun()
            with col_nav2:
                st.caption(f"Página {st.session_state.history_page + 1} de {total_pages}")
            with col_nav3:
                if st.session_state.history_page < total_pages - 1:
                    if st.button("Próximas"):
                        st.session_state.history_page += 1
                        st.rerun()
        else:
            st.write("Nenhuma música pesquisada ainda.")
        

    # Tab 3 - Gêneros
    with tab3:
        col1, col2 = st.columns([1,2])
        
        with col1:
            # Seção 1: Gêneros Selecionados
            if st.session_state.get("selected_genres"):
                st.markdown("### Seus Gêneros")
                for genre in st.session_state["selected_genres"]:
                    cols = st.columns([4, 1])
                    with cols[0]:
                        st.markdown(f"- {genre.capitalize()}")
                    with cols[1]:
                        if st.button("✕", key=f"remove_{genre}"):
                            st.session_state["selected_genres"].remove(genre)
                            if "genre_recommendations" in st.session_state and genre in st.session_state["genre_recommendations"]:
                                del st.session_state["genre_recommendations"][genre]
                            st.rerun()
                st.markdown("---")
            
            # Seção 2: Todos os Gêneros (com busca)
            st.markdown("### Explorar Gêneros")
            genre_search = st.text_input("Buscar gêneros", placeholder="Digite um gênero...", key="genre_search").lower()
            filtered_genres = [g for g in genres if genre_search in g.lower()] if genre_search else genres
            with st.container(height=300):
                for genre in filtered_genres:
                    if genre not in st.session_state.get("selected_genres", []):
                        if st.button(f"+ {genre}", key=f"add_{genre}", use_container_width=True):
                            st.session_state["selected_genres"].append(genre)
                            st.rerun()
            
            # Seção 3: Recomendações baseadas em Gêneros Selecionados
            st.markdown("---")
            st.markdown("### 💡 Recomendados para Você")
            if st.session_state.get("selected_genres"):
                selected = st.session_state["selected_genres"]
                genre_similarity = {
                    "rock": ["alternative-rock", "indie-rock", "hard-rock", "metal", "punk"],
                    "pop": ["pop-rock", "indie-pop", "dance-pop", "synth-pop", "k-pop"],
                    "jazz": ["blues", "soul", "funk", "r&b", "lounge"],
                    "electronic": ["edm", "techno", "house", "trance", "dubstep"],
                    "hiphop": ["rap", "trap", "grime", "drill", "r&b"],
                    "classical": ["opera", "orchestral", "piano", "baroque", "chamber"],
                    "country": ["folk", "bluegrass", "americana", "southern-rock"],
                    "reggae": ["dub", "ska", "dancehall", "reggaeton"],
                    "brazil": ["mpb", "samba", "sertanejo", "forro", "pagode"],
                }
                similar_genres = []
                for sel in selected:
                    if sel in genre_similarity:
                        similar_genres.extend(genre_similarity[sel])
                    for main, subs in genre_similarity.items():
                        if sel in subs and main not in similar_genres:
                            similar_genres.append(main)
                recommended_genres = list(set([g for g in similar_genres if g in genres and g not in selected]))
                genre_counts = {g: similar_genres.count(g) for g in recommended_genres}
                recommended_genres = sorted(recommended_genres, key=lambda x: -genre_counts.get(x, 0))
                if recommended_genres:
                    cols = st.columns(2)
                    for i, genre in enumerate(recommended_genres[:6]):
                        with cols[i % 2]:
                            reason = next(
                                (main for main, subs in genre_similarity.items() if genre in subs and main in selected),
                                selected[0]
                            )
                            if st.button(f"{genre.capitalize()}", key=f"rec_{genre}", help=f"Relacionado a {reason.capitalize()}", use_container_width=True):
                                st.session_state["selected_genres"].append(genre)
                                st.rerun()
                else:
                    st.info("Adicione mais gêneros para receber recomendações personalizadas")
            else:
                popular_genres = ["pop", "rock", "electronic", "hiphop", "jazz"]
                st.info("Experimente começar com:")
                cols = st.columns(2)
                for i, genre in enumerate(popular_genres):
                    with cols[i % 2]:
                        if st.button(f"{genre.capitalize()}", key=f"starter_{genre}", use_container_width=True):
                            st.session_state["selected_genres"].append(genre)
                            st.rerun()
        
        with col2:
            st.subheader("Recomendações por Gênero")
            # Aqui não usamos cache para economizar processamento; as recomendações são geradas on demand
            if st.session_state.get("selected_genres"):
                sp = authenticate_spotify()
                for genre in st.session_state["selected_genres"]:
                    with st.expander(f"🎵 {genre.capitalize()}", expanded=True):
                        # Gera recomendações caso não existam
                        if st.session_state["genre_recommendations"].get(genre) is None:
                            st.session_state["genre_recommendations"][genre] = generate_recommendations([genre], data, sp, limit= 3)

                        genre_songs = st.session_state["genre_recommendations"][genre]
                        cols = st.columns(3)
                        for idx, song in enumerate(genre_songs):
                            with cols[idx]:
                                # Evita pesquisar caso a url da imagem já esteja disponível
                                if st.session_state["genre_recommendations"][genre][song]["cover_url"] is not None:
                                    cover_url = st.session_state["genre_recommendations"][genre][song]["cover_url"]
                                    artist_name = st.session_state["genre_recommendations"][genre][song]["artist"]
                     
                                else:
                                    cover_url, artist_name = get_album_cover_and_artist(song, sp)
                                if cover_url and cover_url.startswith("http"):
                                    st.image(cover_url)
                                else:
                                    st.write("Sem capa")
                                if len(song)>30:
                                    song = song[0:30]+'...'
                                st.markdown(f"**{song}**")
                                st.caption(f"{artist_name}")
                                if st.button(f"Tocar", key=f"prev_{genre}_{song}"):
                                    new_entry = {
                                        "song": song,
                                        "artist": artist_name,
                                        "cover_url": cover_url,
                                        "timestamp": time.time(),
                                        "genre": genre
                                    }
                                    if "search_history" not in st.session_state:
                                        st.session_state["search_history"] = []
                                    st.session_state["search_history"].append(new_entry)
                                    st.session_state["search_query"] = song
                                    ############# st.session_state["page"] = "busca"
                                    st.rerun()
                        if st.button("Atualizar este gênero", key=f"refresh_{genre}"):
                            st.session_state["genre_recommendations"][genre] = generate_recommendations([genre], data, sp, limit= 3)
                            st.rerun()
            else:
                st.info("Selecione gêneros à esquerda para ver recomendações")


