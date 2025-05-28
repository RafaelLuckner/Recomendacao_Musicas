import os 
import time
import dotenv
import spotipy
import unicodedata
import pandas as pd
import streamlit as st
from datetime import datetime, date
from spotipy.oauth2 import SpotifyClientCredentials

from st_click_detector import click_detector

import sources
import re

@st.cache_data
def load_data():
    url_data = "data/data.csv"
    return pd.read_csv(url_data)

def switch_page(target_page: str):
    st.session_state["page"] = target_page
    params = {"page": target_page}
    if "email" in st.session_state:
        params["email"] = st.session_state["email"]
    st.query_params.update(params)
    st.rerun()

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

def get_album_cover_and_artist(song_name, artist_name, sp):
    query = f'track:{song_name} artist:{artist_name}'
    results = sp.search(q=query, limit=1, type='track')
    if results['tracks']['items']:
        track = results['tracks']['items'][0]
        album_cover_url = track['album']['images'][0]['url']
        artist_name = track['artists'][0]['name']  # nome padronizado do Spotify
        return album_cover_url, artist_name
    return None, None


def generate_recommendations(selected_genres, data, sp, limit=10):
    """
    Para cada gênero selecionado, seleciona aleatoriamente músicas e 
    retorna um dicionário em que a chave é o nome da música e o valor é 
    um dicionário com: song, genre, artist e cover_url. 
    Se a música já tem a cover_url, a requisição não será feita.
    """
    limit = int(limit / len(selected_genres))
    recommendations = {}
    for genre in selected_genres:
        genre_songs = data[data['track_genre'] == genre]
        if not genre_songs.empty:
            sampled_rows = genre_songs.sample(limit)
            
            for _, row in sampled_rows.iterrows():
                song = row['track_name']
                artist = row['artists']
                
                # Verifica se a música já tem a cover_url
                if song not in recommendations:
                    cover_url = row.get('cover_url', None)  # Verifica se já existe cover_url na linha
                    
                    # Verifica se o cover_url está ausente (NaN ou None)
                    if pd.isna(cover_url):  
                        cover_url, resolved_artist = get_album_cover_and_artist(song, artist, sp)
                    else:
                        resolved_artist = artist  # Já tem o artista da música
                    
                    # Se obteve a cover_url e o artista, adiciona ao dicionário
                    if cover_url and resolved_artist:
                        recommendations[song] = {
                            "song": song,
                            "genre": genre,
                            "artist": resolved_artist,
                            "cover_url": cover_url
                        }
    
    return recommendations

def generate_recomendations_by_user_simmilarity(selected_genres, data, sp, limit=30):
    import recomendacao_por_user
    musics_recommendations = recomendacao_por_user.recomendar_musicas_por_user(st.session_state["user_id"], data, top_k=limit)

    recommendations = {}
    for song, artist,genre, cover_url in zip(musics_recommendations["track_name"], musics_recommendations["artists"],musics_recommendations["track_genre"],  musics_recommendations["cover_url"]): #musics_recommendations:
        # Verifica se o cover_url esta ausente (NaN ou None)
        if pd.isna(cover_url) or pd.isna(artist):  
            # cover_url, resolved_artist = get_album_cover_and_artist(song, artist, sp)
            cover_url = ''
            resolved_artist =''
        else:
            resolved_artist = artist  # Já tem o artista da música

        if pd.isna(cover_url) or pd.isna(resolved_artist):
            pass

        else:
            recommendations[song] = {
                "song": song,
                "genre": genre,
                "artist": resolved_artist,
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
def html_images_display(id, title, artist, cover_url, time_watch=0, show_time=False, rating=None):
    full_star = "★"
    empty_star = "☆"
    if rating is not None:
        stars_html = full_star * int(rating) + empty_star * (5 - int(rating))
    else:
        stars_html = ""

    return f"""
        <div style='display: inline-block; text-align: center; margin-right: 20px; width: 200px; vertical-align: top;'>
            <a href='javascript:void(0);' id='{id}' onclick='event.preventDefault();' style='text-decoration: none; color: inherit;'>
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
                        <img src='{cover_url}' width='{190 if rating else 200}px' 
                            style='
                                border-radius: 10px; 
                                display: block; 
                                height: {190 if rating else 200}px; 
                                object-fit: cover;
                                pointer-events: none;
                            '>
                    </div>
                    <div style='font-size: {20 if rating else 0}px; color: #ffcc00'> {stars_html}</div>
                    <div style='
                        font-size: 15px;
                        white-space: normal;
                        word-wrap: break-word;
                        overflow-wrap: break-word;
                        height: 17px;
                        line-height: 1.4em;
                        overflow: hidden;
                    '>{title}</div>
                    <div style='font-size: 12px; color: #666;'>{time_watch if show_time else artist.split(";")[0] }</div>
                </div>
            </a>
        </div>
    """

def html_scroll_container(scroll_amount=500, msg = None):
    if msg:
        title_html = f"<h1 style='margin: 0 0 30px 0px; font-size: 2.5em; '>{msg}</h1>" if msg else ""

    return f"""
            <div style='position: relative; padding: 20px; margin: 20px; overflow: hidden; background-color: transparent;'>
                
                {title_html if msg else ""}
                
                <!-- Botão Esquerda -->
                <div style='position: absolute; top: {58 if msg else 50}%; left: -8px; transform: translateY(-100%); z-index: 10;'>
                    <button onclick="document.getElementById('history-scroll').scrollBy({{ left: {-scroll_amount}, behavior: 'smooth' }})"
                        style='background: none; border: none; font-size: 30px; color: #888888; cursor: pointer;'>❮</button>
                </div>

                <!-- Botão Direita -->
                <div style='position: absolute; top: {58 if msg else 50}%; right: -8px; transform: translateY(-100%); z-index: 10;'>
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

    data = load_data()
    genres = data['track_genre'].unique()

    if 'user_id' not in st.session_state or st.session_state["user_id"] == None:
        user_id = sources.search_user_id_mongodb(st.session_state["email"])
        st.session_state["user_id"] = user_id
    if "selected_genres" not in st.session_state or st.session_state["selected_genres"] == []:
        st.session_state["selected_genres"] = sources.load_info_user(st.session_state["user_id"], "generos_escolhidos")
    if "search_query" not in st.session_state:
        st.session_state["search_query"] = ""
    if "search_history" not in st.session_state or st.session_state["search_history"] == []:
        st.session_state["search_history"] = sources.search_history_user(st.session_state["user_id"])
    if "rating_history" not in st.session_state or st.session_state["rating_history"] == []:
        st.session_state["rating_history"] = sources.load_rating_history(st.session_state["user_id"])

    # Inicializa nosso dicionário de recomendações
    if "recommended_songs" not in st.session_state:
        st.session_state["recommended_songs"] = {}
    if "genre_recommendations" not in st.session_state:
        st.session_state["genre_recommendations"] = {}



    with tab1:

        if st.session_state.get("selected_genres"):
            selected_genres = st.session_state["selected_genres"]
            sp = authenticate_spotify()

            if not st.session_state["recommended_songs"]:
                st.session_state["recommended_songs"] = generate_recomendations_by_user_simmilarity(selected_genres, data, sp, limit=20)

            rec_dict = st.session_state["recommended_songs"]
            recommended_list = list(rec_dict.values())
            recommended_subset = recommended_list

            html = html_scroll_container(scroll_amount=600, msg="🎶 Recomendações de Música")

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
                        st.session_state['new_entry'] = new_entry
                        st.session_state["search_query"] = f"{rec['song']} - {rec['artist']}"
                        switch_page("busca")
                        st.rerun()
            
            if st.button("Novas recomendações"):
                sp = authenticate_spotify()
                st.session_state["recommended_songs"] = generate_recommendations(selected_genres, data, sp, limit=10)
                st.rerun()

        else:
            st.warning("Selecione gêneros na aba 'Gêneros' para ver recomendações.")
        
    with tab2:
        if "search_history" not in st.session_state:
            st.session_state["search_history"] = sources.search_history_user(st.session_state["user_id"])

        if st.session_state["search_history"]:
            # Dicionário para guardar apenas a última pesquisa de cada música (considerando música + artista)
            unique_songs = {}

            # Ordena por timestamp decrescente (mais recente primeiro)
            sorted_history = sorted(
                st.session_state["search_history"],
                key=lambda x: x.get("timestamp", 0),
                reverse=True
            )

            for entry in sorted_history:
                # Normaliza nome da música e artista para comparação
                song_key = f"{entry['song'].strip().lower()}|{entry['artist'].strip().lower()}"
                if song_key not in unique_songs:
                    unique_songs[song_key] = entry  # Salva apenas a primeira (mais recente) ocorrência

            # Lista final com uma entrada por música (a mais recente)
            unique_history = list(unique_songs.values())

            # Controla quantas entradas mostrar na tela
            if "history_display_limit" not in st.session_state:
                st.session_state["history_display_limit"] = 20

            displayed_history = unique_history[:st.session_state["history_display_limit"]]

            html = html_scroll_container(scroll_amount=600, msg="📜 Histórico de Pesquisas")

            for idx, entry in enumerate(displayed_history):
                song = entry['song']
                artist = entry['artist']
                cover_url = entry.get("cover_url", "")
                entry['genre'] = entry.get("genre")
                timestamp = time_ago(entry['timestamp'])
                display_title = song[:20] + "..." if len(song) > 20 else song
                item_id = f"history_{song}_{artist}_{idx}".replace(" ", "_")
                html += html_images_display(item_id, display_title, artist, cover_url, timestamp, show_time=True)

            clicked = click_detector(html, key="history_scroll_click")
            if clicked:
                for idx, entry in enumerate(displayed_history):
                    song = entry['song']
                    artist = entry['artist']
                    item_id = f"history_{song}_{artist}_{idx}".replace(" ", "_")
                    if clicked == item_id:
                        st.session_state["search_query"] = f"{song} - {artist}"
                        new_entry = {
                            "song": song,
                            "artist": artist,
                            "cover_url": entry.get("cover_url", ""),
                            "timestamp": time.time(),
                            "genre": entry.get("genre", None)
                        }
                        st.session_state['new_entry'] = new_entry
                        switch_page("busca")

            # Botão para carregar mais entradas
            remaining_songs = len(unique_history) - st.session_state["history_display_limit"]
            if remaining_songs > 0:
                if st.button(f"Carregar mais ({min(remaining_songs, 1000)} restantes)"):
                    st.session_state["history_display_limit"] += 20
                    st.rerun()
        else:
            st.write("Nenhuma música pesquisada ainda.")
            

        rating_history = st.session_state.get("rating_history", [])

        if rating_history:
            unique_ratings = {}
            for entry in sorted(rating_history, key=lambda x: x.get("timestamp", 0), reverse=True):
                if entry['song'] not in unique_ratings:
                    unique_ratings[entry['song']] = entry
            unique_rating_history = list(unique_ratings.values())

            if "rating_display_limit" not in st.session_state:
                st.session_state["rating_display_limit"] = 20

            displayed_ratings = unique_rating_history[:st.session_state["rating_display_limit"]]

            html = html_scroll_container(scroll_amount=600, msg="⭐ Histórico de Avaliações")
            for idx, entry in enumerate(displayed_ratings):
                song = entry['song']
                artist = entry['artist']
                rating = entry['rating']
                cover_url = entry.get("cover_url", "")
                display_title = song[:20] + "..." if len(song) > 20 else song
                item_id = f"rating_{song}_{idx}".replace(" ", "_")
                html += html_images_display(item_id, display_title, artist, cover_url, rating=rating)

            clicked = click_detector(html, key="rating_scroll_click")
            if clicked:
                for idx, entry in enumerate(displayed_ratings):
                    song = entry['song']
                    item_id = f"rating_{song}_{idx}".replace(" ", "_")
                    if clicked == item_id:
                        st.session_state["search_query"] = f"{entry['song']} - {entry['artist']}"
                        st.session_state['avaliacao'] = entry['rating']
                        new_entry = {
                            "song": entry["song"],
                            "artist": entry["artist"],
                            "cover_url": entry.get("cover_url", ""),
                            "timestamp": time.time(),
                        }
                        st.session_state['new_entry'] = new_entry
                        switch_page("busca")

            remaining_ratings = len(unique_rating_history) - st.session_state["rating_display_limit"]
            if remaining_ratings > 0:
                if st.button(f"Carregar mais avaliações ({min(remaining_ratings, 1000)} restantes)"):
                    st.session_state["rating_display_limit"] += 20
                    st.rerun()
        else:
            st.write("Nenhuma música avaliada ainda.")



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
                        if len(st.session_state['selected_genres']) <= 0:
                            pass
                        else:
                            if st.button("✕", key=f"remove_{genre}"):
                                st.session_state["selected_genres"].remove(genre)
                                if "genre_recommendations" in st.session_state and genre in st.session_state["genre_recommendations"]:
                                    del st.session_state["genre_recommendations"][genre]
                                    sources.initial_save_mongodb("generos_escolhidos", st.session_state["selected_genres"])

                                st.rerun()
                st.markdown("---")
            

            # Seção 2: Recomendações baseadas em Gêneros Selecionados
            st.markdown("### 💡 Recomendados para Você")
            if st.session_state.get("selected_genres"):

                import recomendacao_por_user
                recommended_genres = recomendacao_por_user.recomendar_generos_por_user(st.session_state['user_id'])

                if recommended_genres:
                    cols = st.columns(2)
                    for i, genre in enumerate(recommended_genres):
                            col = cols[i % 2]  # Alterna entre col[0] e col[1]
                            with col:
                                if st.button(f"{genre.capitalize()}", key=f"rec_{genre}", use_container_width=True):
                                    st.session_state["selected_genres"].append(genre)
                                    sources.initial_save_mongodb("generos_escolhidos", st.session_state["selected_genres"])
                                    st.rerun()
                else:
                    st.info("Adicione mais gêneros para receber recomendações personalizadas")
            else:
                popular_genres = ["pop", "rock", "electronic", "hiphop", "jazz", 'sertanejo']
                st.info("Experimente começar com:")
                cols = st.columns(2)
                for i, genre in enumerate(popular_genres):
                    with cols[i % 2]:
                        if st.button(f"{genre.capitalize()}", key=f"starter_{genre}", use_container_width=True):
                            st.session_state["selected_genres"].append(genre)
                            st.rerun()

            # Seção 3: Todos os Gêneros (com busca)
            st.markdown("---")

            st.markdown("### Explorar Gêneros")
            genre_search = st.text_input("Buscar gêneros", placeholder="Digite um gênero...", key="genre_search").lower()
            

            def remove_acentos(texto):
                return ''.join(
                    c for c in unicodedata.normalize('NFKD', texto)
                    if not unicodedata.combining(c)
                )

            # Filtrar e ordenar gêneros com base na primeira palavra sem acento
            filtered_genres = sorted(
                [g for g in genres if genre_search in remove_acentos(g.lower())] if genre_search else genres,
                key=lambda x: remove_acentos(x.split()[0].lower()))

            with st.container(border=True, height=300):
                for genre in filtered_genres:
                    if genre not in st.session_state.get("selected_genres", []):
                        if st.button(f"+ {genre.capitalize()}", key=f"add_{genre}", use_container_width=True):
                            st.session_state["selected_genres"].append(genre)
                            sources.initial_save_mongodb("generos_escolhidos", st.session_state["selected_genres"])

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
                                    
                                    st.session_state['new_entry'] = new_entry
                                    st.session_state["search_query"] = song_title + " - " + info["artist"]
                                    switch_page("busca")

                        if st.button("🔁 Novas recomendações", key=f"refresh_{genre}"):
                            st.session_state["genre_recommendations"][genre] = generate_recommendations([genre], data, sp, limit=20)
                            st.rerun()
            else:
                st.info("Selecione gêneros à esquerda para ver recomendações")


