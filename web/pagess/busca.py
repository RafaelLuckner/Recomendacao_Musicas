import streamlit as st
import requests
from dotenv import load_dotenv
import os
import time
import base64
from streamlit_star_rating import st_star_rating
import yt_dlp
import difflib
from st_click_detector import click_detector
from pymongo import MongoClient
from concurrent.futures import ThreadPoolExecutor
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
    """Busca vídeos no YouTube usando yt-dlp com otimizações para velocidade."""
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

# -------------------------------
# FUNÇÕES PARA A API DO DEEZER
# -------------------------------
def get_deezer_playlist_tracks(playlist_id, limit=50):
    """
    Busca os tracks de uma playlist no Deezer e retorna os primeiros 'limit' tracks com imagem do álbum.
    """
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
                # 'genre': track['album']['genre']
            }
            for track in tracks[:limit]
        ]
    except requests.exceptions.RequestException as e:
        st.error(f"Erro ao acessar a playlist do Deezer: {e}")
        return []
    except Exception as e:
        st.error(f"Erro inesperado: {e}")
        return []

# IDs para playlists do Deezer (verifique e atualize conforme necessário)
DEEZER_PLAYLIST_IDS = {
    "Top 50 Brasil": "3830710402",  # ID atualizado para Top 50 Brasil
    "Top 50 Global": "10064140302"   # ID para Top 50 Global
}

def link_musica_deezer(musica_completa, limiar_similaridade=0.5):
    # Separar nome da música e artista
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

    # Fazer a requisição à API do Deezer
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

    # Medir similaridade com o nome da música e artista
    sim_nome = difflib.SequenceMatcher(None, nome_musica.lower(), titulo_retornado.lower()).ratio()
    sim_artista = difflib.SequenceMatcher(None, nome_artista.lower(), artista_retornado.lower()).ratio()

    if sim_nome >= limiar_similaridade and sim_artista >= limiar_similaridade:
        return resultado['link']  # link da música no Deezer
    else:
        return None
    
def link_musica_spotify(musica_completa, client_id, client_secret, limiar_similaridade=0.5):
    # Separa o nome da música e artista
    partes = musica_completa.split(" - ")
    # Se houver mais de duas partes, considera a primeira parte como o nome da música
    # e a ultima parte como o artista
    # Ex: "Photograph  - ao vivo- Ed Sheeran"
    if len(partes) > 2:
        nome_musica = partes[0].strip() + " - " + partes[1].strip()
        nome_artista = partes[-1].strip()
    elif len(partes) == 1:
        nome_musica = partes[0].strip()
        nome_artista = ""
    elif len(partes) == 2:
        nome_musica = partes[0].strip()
        nome_artista = partes[1].strip()

    # Autenticação
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

    # Busca no Spotify usando nome da música e artista
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

    # Verificar similaridade
    sim_nome = difflib.SequenceMatcher(None, nome_musica.lower(), nome_retornado.lower()).ratio()
    sim_artista = difflib.SequenceMatcher(None, nome_artista.lower(), artistas_retornados.lower()).ratio()

    if sim_nome >= limiar_similaridade and sim_artista >= limiar_similaridade:
        return resultado['external_urls']['spotify']
    else:
        return None

def atualizar_avaliacao(nota):
    st.session_state.avaliacao = nota
    
# -------------------------------
# INTERFACE STREAMLIT
# -------------------------------
def show():


    # Chaves da API do YouTube definidas no .env
    api_key1 = os.getenv('API_YOUTUBE1')
    api_key2 = os.getenv('API_YOUTUBE2')
    

    if 'user_id' not in st.session_state or st.session_state["user_id"] == None:
        user_id = sources.search_user_id_mongodb(st.session_state["email"])
        st.session_state["user_id"] = user_id
    if 'search_query' not in st.session_state:
        st.session_state['search_query'] = ''
    if 'search_history' not in st.session_state:
        st.session_state['search_history'] = []
    if 'user_id' not in st.session_state:
        user_id = sources.search_user_id_mongodb(st.session_state["email"])
        st.session_state["user_id"] = user_id
    if 'new_entry' not in st.session_state:
        st.session_state['new_entry'] = None

    # Layout: duas colunas (esquerda: YouTube; direita: Top 50 em dois tabs)
    col_left, col_right = st.columns([2, 1])
    
    # -------- COLUNA ESQUERDA: Busca e vídeo no YouTube --------
    with col_left:
        st.title("🎵 Reprodutor de Músicas do YouTube")
        search_query = st.text_input("🔎 Pesquise uma música ou artista:", 
                                     value=st.session_state.get('search_query', '')
                                     ,placeholder="Ex: Photograph - Ed Sheeran",
                                      help="""Formato de pesquisa recomendado: \n
                        Nome da Música - Nome do Artista""")

        if search_query != st.session_state.get('search_query', ''):
            st.session_state['search_query'] = search_query
            st.rerun()
        
        if search_query:
            st.write(f"Você está buscando por: **{search_query}**")
            videos = search_youtube('musica ' + search_query)
            
            if not videos:
                st.warning("Nenhum vídeo encontrado ou erro na busca.")
            else:
                video_id = videos[0].get('id')
                st.video(f"https://www.youtube.com/watch?v={video_id}",loop=True)

            musica_deezer = link_musica_deezer(search_query, limiar_similaridade=0.5)
            musica_spotify = link_musica_spotify(search_query, client_id, client_secret, limiar_similaridade=0.5)

            # Criação da linha com duas colunas principais
            col_links, col_avaliacao = st.columns([1, 1])

            # Coluna com os links das músicas
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

            # Coluna com a avaliação
            with col_avaliacao:
                st.write(" Avalie a música:")
                avaliacao = st_star_rating("", maxValue=5, defaultValue=0, key="star_rating"   )


                if avaliacao:
                    # st.success(f"Você deu {avaliacao} estrela(s)! ⭐")
                    st.session_state.avaliacao = avaliacao

        else:
            st.warning("Digite o nome de uma música e artista para iniciar a busca.")




        # Recomendações de nosso sistema
        with st.expander("Recomendações"):
            st.write("Em desenvolvimento...")
    # -------- COLUNA DIREITA: Top 50 com Tabs e expanders --------
    with col_right:
        st.title("🔥 Top 50")
        tab_brasil, tab_global = st.tabs(["Top 50 Brasil", "Top 50 Global"])


        def display_tracks(playlist_key, playlist_id):
            if f"{playlist_key}_tracks" in st.session_state:
                tracks = st.session_state[f"{playlist_key}_tracks"]
            else:
                tracks = get_deezer_playlist_tracks(playlist_id, limit=50)
                st.session_state[f"{playlist_key}_tracks"] = tracks

            if not tracks:
                st.error("Não foi possível carregar a playlist.")
                return

            with st.container(height=700):
                html = """
                        <div style='
                            display: flex;
                            justify-content: center;
                            flex-wrap: wrap;
                            gap: 20px;  /* espaço entre os cards */
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

                # Processa o clique apenas se ele ainda não foi registrado
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


        
        with tab_brasil:
            display_tracks("Top50Brasil", DEEZER_PLAYLIST_IDS["Top 50 Brasil"])
            
        with tab_global:
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
                print("DEBUG: Histórico salvo com sucesso")
                st.session_state['old_entry'] = st.session_state['new_entry']
                st.session_state['new_entry'] = None
                st.session_state["search_history"] = sources.search_history_user(st.session_state["user_id"])
            except Exception as e:
                st.error(f"Erro ao salvar histórico: {e}")

        
if __name__ == "__main__":
    show()
