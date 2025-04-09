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
from st_click_detector import click_detector

@st.cache_data
def load_data():
    url_data = "https://drive.google.com/uc?export=download&id=1CpD3pt4kVryQ4jzb7tg0fOIaEG2mdrKg"
    return pd.read_csv(url_data)

def save_search_history(new_entry):
    if 'search_history' not in st.session_state:
        st.session_state['search_history'] = []
    st.session_state['search_history'].append(new_entry)

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

def generate_recommendations(selected_genres, data, sp, limit=20):
    """
    Para cada gênero selecionado, seleciona aleatoriamente 6 músicas e 
    retorna um dicionário em que a chave é o nome da música e o valor é 
    um dicionário com: song, genre, artist e cover_url.
    """
    # Limita o número de músicas por gênero
    limit = int(limit/len(selected_genres))
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
    

# HTML
def html_images_display(id, title, artist, cover_url):
    return f"""
        <div style='display: inline-block; text-align: center; margin-right: 20px; width: 200px; vertical-align: top;'>
            <a href='#' id='{id}' style='text-decoration: none; color: inherit;'>
                <div style='height: 250px; display: flex; flex-direction: column; justify-content: flex-start;'>
                    <div style='
                        width: 200px;
                        height: 200px;
                        overflow: hidden;
                        border-radius: 20px;
                        transition: transform 0.3s ease;
                    ' 
                    onmouseover="this.style.transform='scale(1.1)'" 
                    onmouseout="this.style.transform='scale(1)'">
                        <img src='{cover_url}' width='200px' 
                            style='
                                border-radius: 10px; 
                                display: block; 
                                height: 200px; 
                                object-fit: cover;
                                pointer-events: none;
                            '>
                    </div>                                            
                    <div style='
                        margin-top: 8px;
                        font-size: 14px;
                        white-space: normal;
                        word-wrap: break-word;
                        overflow-wrap: break-word;
                        height: 15px;
                        line-height: 1.2em;
                        overflow: hidden;
                    '>{title}</div>
                    <div style='font-size: 12px; color: #666;'>{artist}</div>
                </div>
            </a>
        </div>
    """

def html_scroll_container(scroll_amount=500):
    return f"""
            <div style='position: relative; padding: 20px; margin: 20px; overflow: hidden; background-color: transparent;'>

                <!-- Botão Esquerda -->
                <div style='position: absolute; top: 50%; left: -10px; transform: translateY(-100%); z-index: 10;'>
                    <button onclick="document.getElementById('history-scroll').scrollBy({{ left: {-scroll_amount}, behavior: 'smooth' }})"
                        style='background: none; border: none; font-size: 30px; color: #888888; cursor: pointer;'>❮</button>
                </div>

                <!-- Botão Direita -->
                <div style='position: absolute; top: 50%; right: -10px; transform: translateY(-100%); z-index: 10;'>
                    <button onclick="document.getElementById('history-scroll').scrollBy({{ left: {scroll_amount}, behavior: 'smooth' }})"
                        style='background: none; border: none; font-size: 30px; color: #888888; cursor: pointer;'>❯</button>
                </div>

                <div id='history-scroll' style='
                    overflow-x: auto;
                    white-space: nowrap;
                    padding: 0px 10px;
                    scroll-behavior: smooth;
                '>
            <style>
                #history-scroll::-webkit-scrollbar {{
                    height: 8px;
                    background: transparent; /* fundo da barra igual ao da tela */
                }}

                #history-scroll::-webkit-scrollbar-thumb {{
                    background: rgba(150, 150, 150, 0.4);  /* cor sutil e translúcida para o "thumb" */
                    border-radius: 4px;
                }}

                #history-scroll {{
                    scrollbar-color: rgba(150,150,150,0.4) transparent; /* Firefox */
                    scrollbar-width: thin; /* Firefox */
                }}
            </style>
        """
def show():
    dotenv.load_dotenv()

    # Criar abas para navegação
    tab1, tab2, tab3 = st.tabs(["Para você ", " Histórico", " Gêneros"])

    # data = pd.read_csv('data/data_traduct.csv')
    data = load_data()
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

    with tab1:
        st.subheader("🎶 Recomendações de Música")

        if st.session_state.get("selected_genres"):
            selected_genres = st.session_state["selected_genres"]
            sp = authenticate_spotify()

            if not st.session_state["recommended_songs"]:
                st.session_state["recommended_songs"] = generate_recommendations(selected_genres, data, sp, limit=15)

            rec_dict = st.session_state["recommended_songs"]
            recommended_list = list(rec_dict.values())
            recommended_subset = recommended_list

            html = html_scroll_container(scroll_amount=600)

            # Adiciona os álbuns dinamicamente
            for idx, rec in enumerate(recommended_subset):
                song = rec["song"]
                artist = rec["artist"]
                cover_url = rec["cover_url"]
                song_id = f"{song} - {artist}".replace("'", "").replace('"', "").replace(" ", "_") + f"_{idx}"
                display_title = song[:20] + "..." if len(song) > 20 else song

                html += html_images_display(song_id, display_title, artist, cover_url)


            # html += "</div></div>"

            clicked = click_detector(html)

            if clicked:
                # Recupera o item clicado pela ID
                for idx, rec in enumerate(recommended_subset):
                    expected_id = f"{rec['song']} - {rec['artist']}".replace("'", "").replace('"', "").replace(" ", "_") + f"_{idx}"
                    if clicked == expected_id:
                        new_entry = {
                            "song": rec["song"],
                            "artist": rec["artist"],
                            "cover_url": rec["cover_url"],
                            "timestamp": time.time(),
                            "genre": rec["genre"]
                        }
                        save_search_history(new_entry)
                        st.session_state["search_query"] = f"{rec['song']} - {rec['artist']}"
                        st.query_params["page"] = "busca"
                        st.rerun()
            
            if st.button("Novas recomendações"):
                sp = authenticate_spotify()
                st.session_state["recommended_songs"] = generate_recommendations(selected_genres, data, sp, limit=10)
                st.rerun()

        else:
            st.warning("Selecione gêneros na aba 'Gêneros' para ver recomendações.")
        
    with tab2:
        st.subheader("📜 Histórico de Pesquisas")

        if "search_history" not in st.session_state:
            st.session_state["search_history"] = []

        if st.session_state["search_history"]:
            # Inverte antes de iterar e mantém apenas a entrada mais recente para cada música
            unique_songs = {}
            for entry in reversed(st.session_state["search_history"]):
                if entry['song'] not in unique_songs:
                    unique_songs[entry['song']] = entry

            unique_history = list(unique_songs.values())

            html = html_scroll_container(scroll_amount=600)

            for idx, entry in enumerate(unique_history):
                song = entry['song']
                artist = entry['artist']
                cover_url = entry.get("cover_url", "")
                timestamp = time_ago(entry['timestamp'])
                display_title = song[:20] + "..." if len(song) > 20 else song
                item_id = f"history_{song}_{idx}".replace(" ", "_")

                html += html_images_display(item_id, display_title, artist, cover_url)

            # html += "</div></div>"

            clicked = click_detector(html, key="history_scroll_click")

            if clicked:
                for idx, entry in enumerate(unique_history):
                    song = entry['song']
                    item_id = f"history_{song}_{idx}".replace(" ", "_")
                    if clicked == item_id:
                        st.session_state["search_query"] = f"{entry['song']} - {entry['artist']}"
                        st.query_params["page"] = "busca"
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
                        if len(st.session_state['selected_genres']) <= 1:
                            pass
                        else:
                            if st.button("✕", key=f"remove_{genre}"):
                                st.session_state["selected_genres"].remove(genre)
                                if "genre_recommendations" in st.session_state and genre in st.session_state["genre_recommendations"]:
                                    del st.session_state["genre_recommendations"][genre]
                                st.rerun()
                st.markdown("---")
            
            # Seção 2: Todos os Gêneros (com busca)
            st.markdown("### Explorar Gêneros")
            genre_search = st.text_input("Buscar gêneros", placeholder="Digite um gênero...", key="genre_search").lower()
            
            # Normaliza os gêneros antes de aplicar o filtro
            filtered_genres = [g for g in genres if genre_search in g.lower()] if genre_search else genres


            with st.container(border=True, height=400):
                for genre in filtered_genres:
                    if genre not in st.session_state.get("selected_genres", []):
                        if st.button(f"+ {genre.capitalize()}", key=f"add_{genre}", use_container_width=True):
                            st.session_state["selected_genres"].append(genre)
                            st.rerun()
            
            # Seção 3: Recomendações baseadas em Gêneros Selecionados
            st.markdown("---")
            st.markdown("### 💡 Recomendados para Você")
            if st.session_state.get("selected_genres"):
                selected = st.session_state["selected_genres"]
                genre_similarity = {
                    "rock": ["rock alternativo", "indie rock", "hard rock", "metal", "punk"],
                    "pop": ["pop rock", "indie pop", "dance pop", "synth pop", "k-pop"],
                    "jazz": ["blues", "soul", "funk", "r&b", "lounge"],
                    "eletrônica": ["edm", "techno", "house", "trance", "dubstep"],
                    "hip-hop": ["rap", "trap", "grime", "drill", "r&b"],
                    "clássica": ["ópera", "orquestral", "piano", "barroca", "câmara"],
                    "country": ["folk", "bluegrass", "americana", "southern rock"],
                    "reggae": ["dub", "ska", "dancehall", "reggaeton"],
                    "brasileiro": ["mpb", "samba", "sertanejo", "forró", "pagode"],
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
                            if st.button(f"{genre}", key=f"rec_{genre}", help=f"Relacionado a {reason.capitalize()}", use_container_width=True):
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

            if st.session_state.get("selected_genres"):
                sp = authenticate_spotify()

                for genre in st.session_state["selected_genres"]:
                    with st.expander(f"**{genre.capitalize()}**", expanded=True):
                    
                        # Gera recomendações se não existirem
                        if st.session_state["genre_recommendations"].get(genre) is None:
                            st.session_state["genre_recommendations"][genre] = generate_recommendations([genre], data, sp, limit=10)

                        genre_songs = st.session_state["genre_recommendations"][genre]

                        html = html_scroll_container(scroll_amount=400)


                        for idx, (song_title, info) in enumerate(genre_songs.items()):
                            artist_name = info["artist"]
                            cover_url = info["cover_url"] or ""
                            song_id = f"{genre}_{song_title}_{idx}".replace(" ", "_")

                            display_title = song_title[:20] + "..." if len(song_title) > 20 else song_title

                            html += html_images_display(song_id, display_title, artist_name, cover_url) 

                        # html += "</div></div>"

                        clicked = click_detector(html)

                        if clicked:
                            for idx, (song_title, info) in enumerate(genre_songs.items()):
                                expected_id = f"{genre}_{song_title}_{idx}".replace(" ", "_")
                                if clicked == expected_id:
                                    new_entry = {
                                        "song": song_title,
                                        "artist": info["artist"],
                                        "cover_url": info["cover_url"],
                                        "timestamp": time.time(),
                                        "genre": genre
                                    }
                                    save_search_history(new_entry)
                                    st.session_state["search_query"] = song_title + " - " + info["artist"]
                                    st.query_params["page"] = "busca"
                                    st.rerun()

                        if st.button("🔁 Novas recomendações", key=f"refresh_{genre}"):
                            st.session_state["genre_recommendations"][genre] = generate_recommendations([genre], data, sp, limit=8)
                            st.rerun()
            else:
                st.info("Selecione gêneros à esquerda para ver recomendações")


