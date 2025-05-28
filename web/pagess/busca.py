import os
import time
import base64
import yt_dlp
import spotipy
import difflib
import requests
import streamlit as st
import pandas as pd
from dotenv import load_dotenv
from st_click_detector import click_detector
from streamlit_star_rating import st_star_rating
from spotipy.oauth2 import SpotifyClientCredentials
from modelo_recomendacao import recomendar_musicas_input
import sources

load_dotenv()
client_id = os.getenv("SPOTIPY_CLIENT_ID")
client_secret = os.getenv("SPOTIPY_CLIENT_SECRET")

# -------------------------------
# FUNÇÕES PARA A API DO YOUTUBE
# -------------------------------
SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"

def save_search_history_mongodb(new_entry, user_id):
    sources.save_search_history(new_entry, user_id)

def switch_page(target_page: str):
    st.session_state["page"] = target_page
    params = {"page": target_page}
    if "email" in st.session_state:
        params["email"] = st.session_state["email"]
    st.query_params.update(params)
    st.rerun()

def search_youtube(query, max_videos=3):
    cache_key = f"youtube_cache_{query}"
    cache_timeout = 3600  # 1 hora
    if cache_key in st.session_state:
        cached = st.session_state[cache_key]
        if time.time() - cached['timestamp'] < cache_timeout:
            return cached['results']
    
    ydl_opts = {
        'quiet': True,
        'extract_flat': True,
        'force_generic_extractor': True,
        'noplaylist': True,
        'max_downloads': max_videos,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            resultados = ydl.extract_info(f"ytsearch{max_videos}:{query} official music video", download=False)
            entries = resultados.get('entries', [])
            
            if entries:
                st.session_state[cache_key] = {'results': entries[:max_videos], 'timestamp': time.time()}
                return entries[:max_videos]
            
            return []
    
    except Exception as e:
        st.error(f"Erro ao buscar vídeo: {e}")
        return []

def get_album_cover(song_name, artist_name):
    client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    query = f'track:{song_name} artist:{artist_name}'
    results = sp.search(q=query, limit=1, type='track')
    if results['tracks']['items']:
        track = results['tracks']['items'][0]
        return track['album']['images'][0]['url'] if track['album']['images'] else None
    return None

# -------------------------------
# FUNÇÕES PARA A API DO DEEZER
# -------------------------------
def get_deezer_playlist_tracks(playlist_id, limit=50):
    url = f"https://api.deezer.com/playlist/{playlist_id}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        tracks = data.get("tracks", {}).get("data", [])
        return [
            {
                "title": track["title"],
                "artist": track["artist"]["name"],
                "album_cover": track["album"].get("cover_medium", None),
            }
            for track in tracks[:limit]
        ]
    except requests.exceptions.RequestException as e:
        st.error(f"Erro ao acessar a playlist do Deezer: {e}")
        return []
    except Exception as e:
        st.error(f"Erro inesperado: {e}")
        return []

DEEZER_PLAYLIST_IDS = {
    "Top 50 Brasil": "3830710402",
    "Top 50 Global": "10064140302"
}

def link_musica_deezer(musica_completa, limiar_similaridade=0.5):
    partes = musica_completa.split(" - ")
    if len(partes) > 2:
        nome_musica = partes[0].strip() + " - " + partes[1].strip()
        nome_artista = partes[-1].strip()
    elif len(partes) == 1:
        nome_musica = partes[0].strip()
        nome_artista = ""
    elif len(partes) == 2:
        nome_musica = partes[0].strip()
        nome_artista = partes[1].strip()

    query = f"{nome_musica} {nome_artista}".strip().replace(" ", "+")
    url = f"https://api.deezer.com/search?q={query}"
    resposta = requests.get(url)

    if resposta.status_code != 200:
        return None

    dados = resposta.json()
    if not dados['data']:
        return None

    resultado = dados['data'][0]
    titulo_retornado = resultado['title']
    if nome_artista == "":
        artista_retornado = ""
    else:
        artista_retornado = resultado['artist']['name']

    sim_nome = difflib.SequenceMatcher(None, nome_musica.lower(), titulo_retornado.lower()).ratio()
    sim_artista = difflib.SequenceMatcher(None, nome_artista.lower(), artista_retornado.lower()).ratio()

    if sim_nome >= limiar_similaridade and sim_artista >= limiar_similaridade:
        return resultado['link']
    else:
        return None

def link_musica_spotify(musica_completa, client_id, client_secret, limiar_similaridade=0.5):
    partes = musica_completa.split(" - ")
    if len(partes) > 2:
        nome_musica = partes[0].strip() + " - " + partes[1].strip()
        nome_artista = partes[-1].strip()
    elif len(partes) == 1:
        nome_musica = partes[0].strip()
        nome_artista = ""
    elif len(partes) == 2:
        nome_musica = partes[0].strip()
        nome_artista = partes[1].strip()

    auth = f'{client_id}:{client_secret}'
    auth_b64 = base64.b64encode(auth.encode()).decode('utf-8')
    headers = {
        'Authorization': f'Basic {auth_b64}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    data = {'grant_type': 'client_credentials'}
    
    token_url = 'https://accounts.spotify.com/api/token'
    token_resposta = requests.post(token_url, headers=headers, data=data)
    
    if token_resposta.status_code != 200:
        return None

    token = token_resposta.json()['access_token']
    query = f"{nome_musica} {nome_artista}".strip().replace(" ", "+")
    search_url = f"https://api.spotify.com/v1/search?q={query}&type=track&limit=1"
    search_headers = {'Authorization': f'Bearer {token}'}
    search_resposta = requests.get(search_url, headers=search_headers)

    if search_resposta.status_code != 200:
        return None

    dados = search_resposta.json()
    if not dados['tracks']['items']:
        return None

    resultado = dados['tracks']['items'][0]
    nome_retornado = resultado['name']
    if nome_artista == "":
        artistas_retornados = ""
    else:
        artistas_retornados = ", ".join([a['name'] for a in resultado['artists']])

    sim_nome = difflib.SequenceMatcher(None, nome_musica.lower(), nome_retornado.lower()).ratio()
    sim_artista = difflib.SequenceMatcher(None, nome_artista.lower(), artistas_retornados.lower()).ratio()

    if sim_nome >= limiar_similaridade and sim_artista >= limiar_similaridade:
        return resultado['external_urls']['spotify']
    else:
        return None

def atualizar_avaliacao(nota):
    st.session_state.avaliacao = nota

# -------------------------------
# FUNÇÕES PARA O CARROSSEL
# -------------------------------
def html_scroll_container(scroll_amount=500, msg=None):
    title_html = f"<h1 style='margin: 0 0 30px 0px; font-size: 2.5em; '>{msg}</h1>" if msg else ""
    return f"""
        <div style='position: relative; padding: 20px 0; margin: 0; overflow: hidden; background-color: transparent; width: 100%;'>
            {title_html}
            <!-- Botão Esquerda -->
            <div style='position: absolute; top: {58 if msg else 50}%; left: 0px; transform: translateY(-100%); z-index: 10;'>
                <button onclick="document.getElementById('recommendations-scroll').scrollBy({{ left: {-scroll_amount}, behavior: 'smooth' }})"
                    style='background: none; border: none; font-size: 30px; color: #888888; cursor: pointer;'>❮</button>
            </div>
            <!-- Botão Direita -->
            <div style='position: absolute; top: {58 if msg else 50}%; right: 0px; transform: translateY(-100%); z-index: 10;'>
                <button onclick="document.getElementById('recommendations-scroll').scrollBy({{ left: {scroll_amount}, behavior: 'smooth' }})"
                    style='background: none; border: none; font-size: 30px; color: #888888; cursor: pointer;'>❯</button>
            </div>
            <div id='recommendations-scroll' style='
                overflow-x: auto;
                white-space: nowrap;
                padding: 0px;
                scroll-behavior: smooth;
                width: 100%;
            '>
            <style>
                #recommendations-scroll::-webkit-scrollbar {{
                    height: 8px;
                    background: transparent;
                }}
                #recommendations-scroll::-webkit-scrollbar-thumb {{
                    background: rgba(150, 150, 150, 0.4);
                    border-radius: 4px;
                }}
                #recommendations-scroll {{
                    scrollbar-color: rgba(150,150,150,0.4) transparent;
                    scrollbar-width: thin;
                }}
            </style>
    """

def html_images_display(id, title, artist, cover_url):
    display_title = title[:20] + "..." if len(title) > 20 else title
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
                        font-size: 15px;
                        white-space: normal;
                        word-wrap: break-word;
                        overflow-wrap: break-word;
                        height: 17px;
                        line-height: 1.4em;
                        overflow: hidden;
                    '>{display_title}</div>
                    <div style='font-size: 12px; color: #666;'>{artist.split(";")[0]}</div>
                </div>
            </a>
        </div>
    """

# -------------------------------
# CARREGAR DADOS PARA ACESSO À COLUNA cover_url
# -------------------------------
@st.cache_data
def load_data():
    try:
        df = pd.read_csv('data/data.csv')
        # Verificar colunas esperadas
        required_columns = ['track_name', 'artists', 'track_genre', 'cover_url']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"Colunas faltando no dataset: {missing_columns}")
        return df
    except Exception as e:
        st.error(f"Erro ao carregar data.csv: {e}")
        return pd.DataFrame()  # Retorna DataFrame vazio em caso de erro

# -------------------------------
# INTERFACE STREAMLIT
# -------------------------------
def show():
    # Inicializar todas as chaves do session_state no início
    if 'user_id' not in st.session_state or st.session_state["user_id"] is None:
        user_id = sources.search_user_id_mongodb(st.session_state["email"])
        st.session_state["user_id"] = user_id
    if 'search_query' not in st.session_state:
        st.session_state['search_query'] = ''
    if 'search_history' not in st.session_state:
        st.session_state['search_history'] = []
    if 'last_processed_query' not in st.session_state:
        st.session_state['last_processed_query'] = None
    if 'new_entry' not in st.session_state:
        st.session_state['new_entry'] = None
    if 'avaliacao' not in st.session_state:
        st.session_state['avaliacao'] = 0
    if 'cover_cache' not in st.session_state:
        st.session_state['cover_cache'] = {}
    if 'same_genre' not in st.session_state:
        st.session_state['same_genre'] = False

    # Layout: duas colunas
    col_left, col_right = st.columns([2, 1])
    
    # -------- COLUNA ESQUERDA: Busca e vídeo no YouTube --------
    with col_left:
        st.title("🎵 Reprodutor de Músicas do YouTube")
        search_query = st.text_input("🔎 Pesquise uma música ou artista:", 
                                     value=st.session_state.get('search_query', ''),
                                     placeholder="Ex: Photograph - Ed Sheeran",
                                     help="Formato de pesquisa recomendado: \nNome da Música - Nome do Artista")

        if search_query != st.session_state.get('search_query', ''):
            st.session_state['search_query'] = search_query
            st.session_state['last_processed_query'] = None
            st.session_state['avaliacao'] = 0
            st.rerun()

        if search_query:
            st.write(f"Você está buscando por: **{search_query}**")
            videos = search_youtube('musica ' + search_query)

            if not videos:
                st.warning("Nenhum vídeo encontrado ou erro na busca.")
            else:
                video_id = videos[0].get('id')
                st.video(f"https://www.youtube.com/watch?v={video_id}", loop=True, autoplay=True)

            partes = search_query.split(" - ")
            if len(partes) > 2:
                nome_musica = partes[0].strip() + " - " + partes[1].strip()
                nome_artista = partes[-1].strip()
            elif len(partes) == 1:
                nome_musica = partes[0].strip()
                nome_artista = None
            elif len(partes) == 2:
                nome_musica = partes[0].strip()
                nome_artista = partes[1].strip()

            cover_url = None
            if st.session_state.get('new_entry') and st.session_state['new_entry'].get('cover_url'):
                cover_url = st.session_state['new_entry']['cover_url']
            elif nome_artista:
                cover_url = get_album_cover(nome_musica, nome_artista)

            if nome_artista and st.session_state['last_processed_query'] != search_query:
                existing_rating = sources.load_rating(nome_musica, nome_artista, st.session_state["user_id"])
                if existing_rating is not None:
                    st.session_state['avaliacao'] = existing_rating['rating']
                    cover_url = existing_rating.get('cover_url', cover_url)
                else:
                    st.session_state['avaliacao'] = 0
                st.session_state['last_processed_query'] = search_query

            musica_deezer = link_musica_deezer(search_query, limiar_similaridade=0.5)
            musica_spotify = link_musica_spotify(search_query, client_id, client_secret, limiar_similaridade=0.5)

            col_links, col_avaliacao = st.columns([1, 1])

            with col_links:
                if musica_deezer or musica_spotify:
                    st.markdown(
                        """
                        <style>
                        .link-musica {{
                            display: flex;
                            gap: 50px;
                            align-items: center;
                            justify-content: center;
                            margin-top: 10px;
                        }}
                        .link-musica a {{
                            display: inline-block;
                            padding: 10px;
                            border-radius: 16px;
                            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
                            transition: transform 0.2s ease, box-shadow 0.2s ease;
                        }}
                        .link-musica a:hover {{
                            transform: scale(1.08);
                            box-shadow: 0 6px 12px rgba(0, 0, 0, 0.2);
                            cursor: pointer;
                        }}
                        .link-musica img {{
                            width: 75px;
                        }}
                        </style>
                        <div class="link-musica">
                            {deezer}
                            {spotify}
                        </div>
                        """.format(
                            deezer=f'<a href="{musica_deezer}" target="_blank"><img src="https://www.deezer.com/favicon.ico" alt="Deezer"></a>' if musica_deezer else '<span></span>',
                            spotify=f'<a href="{musica_spotify}" target="_blank"><img src="https://upload.wikimedia.org/wikipedia/commons/thumb/5/54/2024_Spotify_logo_without_text.svg/1024px-2024_Spotify_logo_without_text.svg.png" alt="Spotify"></a>' if musica_spotify else '<span></span>'
                        ),
                        unsafe_allow_html=True
                    )

            with col_avaliacao:
                if nome_artista and search_query:
                    st.write("Avalie a música:")
                    avaliacao = st_star_rating(
                        "",
                        maxValue=5,
                        defaultValue=st.session_state['avaliacao'],
                        key=f"star_rating_{search_query}_{st.session_state['user_id']}"
                    )
                    if avaliacao != st.session_state['avaliacao']:
                        st.session_state['avaliacao'] = avaliacao
                        rating_entry = {
                            "song": nome_musica,
                            "artist": nome_artista,
                            "rating": avaliacao,
                            "timestamp": int(time.time()),
                            "cover_url": cover_url
                        }
                        sources.save_rating(rating_entry, st.session_state["user_id"])
                        st.session_state["rating_history"] = sources.load_rating_history(st.session_state["user_id"])

        else:
            st.warning("Digite o nome de uma música e artista para iniciar a busca.")

        # -------- CARROSSEL DE RECOMENDAÇÕES --------
        with st.container():
            if search_query:
                try:
                    # Carregar dados para acessar cover_url
                    data = load_data()
                    if data.empty:
                        st.error("Dataset não carregado. Não é possível gerar recomendações.")
                        return

                    # Validar search_query
                    if not isinstance(search_query, str) or not search_query.strip():
                        st.error("Consulta de busca inválida.")
                        return

                    # Obter gêneros favoritos
                    selected_genres = st.session_state.get("selected_genres", [])
                    if not isinstance(selected_genres, list):
                        st.warning("Gêneros favoritos não encontrados ou em formato inválido. Usando lista vazia.")
                        selected_genres = []

                    # Gerar recomendações
                    recommendations = recomendar_musicas_input(
                        input_usuario=search_query,
                        n_recomendacoes=10,
                        mesmo_genero=st.session_state['same_genre'],
                        generos_favoritos=selected_genres,
                        peso_genero=0.075
                    )

                    # Verificar se há recomendações
                    if recommendations.empty:
                        st.warning("Nenhuma recomendação encontrada para esta consulta.")
                        return

                    # Inicializar lista de recomendações com capas
                    rec_list = []
                    for _, rec in recommendations.iterrows():
                        song = rec['track_name']
                        artist = rec['artists'].split(";")[0]
                        # Verificar cover_url no dataset
                        song_data = data[(data['track_name'] == song) & (data['artists'].str.contains(artist, case=False))]
                        cover_url = None
                        if not song_data.empty and not pd.isna(song_data.iloc[0]['cover_url']):
                            cover_url = song_data.iloc[0]['cover_url']
                        else:
                            # Verificar cache
                            cache_key = f"{song}_{artist}"
                            if cache_key in st.session_state['cover_cache']:
                                cover_url = st.session_state['cover_cache'][cache_key]
                            else:
                                cover_url = get_album_cover(song, artist)
                                if cover_url:
                                    st.session_state['cover_cache'][cache_key] = cover_url
                        cover_url = cover_url or "https://via.placeholder.com/200"
                        rec_list.append({
                            "song": song,
                            "artist": artist,
                            "genre": rec['track_genre'],
                            "cover_url": cover_url
                        })
                    # Criar carrossel
                    html = html_scroll_container(scroll_amount=600, msg="🎶 Músicas Recomendadas")
                    for idx, rec in enumerate(rec_list):
                        song_id = f"rec_{rec['song']}_{rec['artist']}_{idx}".replace(" ", "_")
                        html += html_images_display(song_id, rec['song'], rec['artist'], rec['cover_url'])
                    html += "</div></div>"
                    clicked = click_detector(html, key="recommendations_click")
                    if clicked:
                        for idx, rec in enumerate(rec_list):
                            expected_id = f"rec_{rec['song']}_{rec['artist']}_{idx}".replace(" ", "_")
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
                                st.rerun()
                    # Botão de alternância de gênero
                    st.session_state['same_genre'] = st.radio(
                        "Tipo de recomendações:",
                        options=[False, True],
                        format_func=lambda x: "Mesmo gênero" if not x else "Gêneros variados",
                        horizontal=True,
                        key="same_genre_toggle"
                    )
                except Exception as e:
                    st.error(f"Erro ao gerar recomendações: {str(e)}")
            
            else:
                st.info("Pesquise uma música para ver recomendações personalizadas.")

    # -------- COLUNA DIREITA: Top 50 com Tabs --------
    with col_right:
        st.title("")
        st.subheader("🔥 Top 50")

        def display_tracks(playlist_key, playlist_id, expanded=False):
            if f"{playlist_key}_tracks" in st.session_state:
                tracks = st.session_state[f"{playlist_key}_tracks"]
            else:
                tracks = get_deezer_playlist_tracks(playlist_id, limit=50)
                st.session_state[f"{playlist_key}_tracks"] = tracks

            if not tracks:
                st.error("Não foi possível carregar a playlist.")
                return

            with st.expander(playlist_key, expanded=expanded):
                with st.container(height=500, border = False):
                    html = """
                        <div style='
                            display: flex;
                            justify-content: center;
                            flex-wrap: wrap;
                            gap: 20px;
                        '>
                        """
                    for idx, track in enumerate(tracks):
                        title = track["title"]
                        artist = track["artist"]
                        cover_url = track["album_cover"]
                        track_id = f"{title} - {artist}".replace("'", "").replace('"', "").replace(" ", "_") + f"_{idx}"
                        display_title = title[:30] + "..." if len(title) > 20 else title
                        html += f"""
                            <div style='text-align: center; width: 125px;'>
                                <a href='javascript:void(0);' id='{track_id}' style='text-decoration: none; color: inherit;'>
                                    <div style='height: 200px; display: flex; flex-direction: column; justify-content: flex-start;'>
                                        <div style='
                                            width: 140px;
                                            height: 140px;
                                            overflow: hidden;
                                            border-radius: 20px;
                                            transition: transform 0.3s ease;
                                        ' 
                                        onmouseover="this.style.transform='scale(1.1)'" 
                                        onmouseout="this.style.transform='scale(1)'">
                                            <img src='{cover_url}' width='140px' style='border-radius: 10px; display: block; height: 140px; object-fit: cover;'>
                                        </div> 
                                        <div style='
                                            margin-top: 8px;
                                            font-size: 14px;
                                            white-space: normal;
                                            word-wrap: break-word;
                                            overflow-wrap: break-word;
                                            line-height: 1em;
                                            overflow: hidden;
                                        '>{display_title}</div>
                                        <div style='font-size: 12px; color: #666;'>{artist}</div>
                                    </div>
                                </a>
                            </div>
                        """
                    clicked = click_detector(html, key=f"{playlist_key}_click_detector")
                    click_key = f"{playlist_key}_last_click_id"
                    if clicked and st.session_state.get(click_key) != clicked:
                        st.session_state[click_key] = clicked
                        for idx, track in enumerate(tracks):
                            expected_id = f"{track['title']} - {track['artist']}".replace("'", "").replace('"', "").replace(" ", "_") + f"_{idx}"
                            if clicked == expected_id:
                                new_entry = {
                                    "song": track["title"],
                                    "artist": track["artist"],
                                    "cover_url": track["album_cover"],
                                    "timestamp": time.time(),
                                }
                                st.session_state['new_entry'] = new_entry
                                st.session_state["search_query"] = f"{track['title']} - {track['artist']}"
                                st.rerun()

        display_tracks("Top50Brasil", DEEZER_PLAYLIST_IDS["Top 50 Brasil"], expanded=True) 
        display_tracks("Top50Global", DEEZER_PLAYLIST_IDS["Top 50 Global"])

    if 'old_entry' not in st.session_state or st.session_state['old_entry'] is None:
        st.session_state['old_entry'] = {'timestamp': time.time() - 10}

    if time.time() - st.session_state['old_entry'].get('timestamp', 0) > 4:
        if st.session_state.get('new_entry') is not None:
            if st.session_state.get('user_id') is None:
                user_id = sources.search_user_id_mongodb(st.session_state.get("email"))
                if user_id is None:
                    st.error("Erro: Usuário não autenticado. Redirecionando para login...")
                    switch_page("login")
                    return
                st.session_state["user_id"] = user_id
            try:
                sources.save_search_history(st.session_state['new_entry'], st.session_state["user_id"])
                st.session_state['old_entry'] = st.session_state['new_entry']
                st.session_state['new_entry'] = None
                st.session_state["search_history"] = sources.search_history_user(st.session_state["user_id"])
            except Exception as e:
                st.error(f"Erro ao salvar histórico: {e}")

if __name__ == "__main__":
    show()