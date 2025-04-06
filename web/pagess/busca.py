import streamlit as st
import requests
from dotenv import load_dotenv
import os
import time
import base64
from streamlit_star_rating import st_star_rating


load_dotenv()
client_id = os.getenv("SPOTIPY_CLIENT_ID")
client_secret = os.getenv("SPOTIPY_CLIENT_SECRET")
# -------------------------------
# FUNÇÕES PARA A API DO YOUTUBE
# -------------------------------
SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"

def save_search_history(new_entry):
    if 'search_history' not in st.session_state:
        st.session_state['search_history'] = []
    st.session_state['search_history'].append(new_entry)


def search_youtube(query, api_key):
    params = {
        "part": "snippet",
        "q": 'musica ' + query,
        "type": "video",
        "key": api_key,
        "maxResults": 1
    }
    response = requests.get(SEARCH_URL, params=params)
    return response.json()

def is_quota_error(response):
    if 'error' in response:
        error_message = response['error'].get('message', '')
        if 'quota' in error_message.lower():
            return True
    return False

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

def link_musica_deezer(musica):
    url = f"https://api.deezer.com/search?q={musica}"
    resposta = requests.get(url)
    
    if resposta.status_code == 200:
        dados = resposta.json()
        if dados['data']:
            primeiro_resultado = dados['data'][0]  # Pegamos o primeiro resultado
            return primeiro_resultado['link']  # Link da música no Deezer
        else:
            return None
    else:
        return None
def link_musica_spotify(musica, client_id, client_secret):
    # Primeiro, obtém o token de autenticação
    auth = f'{client_id}:{client_secret}'
    auth_b64 = base64.b64encode(auth.encode()).decode('utf-8')
    headers = {
        'Authorization': f'Basic {auth_b64}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    data = {
        'grant_type': 'client_credentials'
    }
    
    # Obtenção do token de acesso
    token_url = 'https://accounts.spotify.com/api/token'
    token_resposta = requests.post(token_url, headers=headers, data=data)
    
    if token_resposta.status_code == 200:
        token = token_resposta.json()['access_token']
    else:
        return None

    # Agora faz a busca pela música no Spotify
    search_url = f"https://api.spotify.com/v1/search?q={musica}&type=track&limit=1"
    search_headers = {
        'Authorization': f'Bearer {token}'
    }
    search_resposta = requests.get(search_url, headers=search_headers)
    
    if search_resposta.status_code == 200:
        dados = search_resposta.json()
        if dados['tracks']['items']:
            primeiro_resultado = dados['tracks']['items'][0]  # Pegamos o primeiro resultado
            return primeiro_resultado['external_urls']['spotify']  # Link da música no Spotify
        else:
            return None
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
    
    if 'search_query' not in st.session_state:
        st.session_state['search_query'] = ''
    if 'search_history' not in st.session_state:
        st.session_state['search_history'] = []
    
    # Layout: duas colunas (esquerda: YouTube; direita: Top 50 em dois tabs)
    col_left, col_right = st.columns([2, 1])
    
    # -------- COLUNA ESQUERDA: Busca e vídeo no YouTube --------
    with col_left:
        st.title("🎵 Reprodutor de Músicas do YouTube")
        search_query = st.text_input("🔎 Pesquise uma música ou artista:", 
                                     value=st.session_state['search_query'])
        if search_query != st.session_state['search_query']:
            st.session_state['search_query'] = search_query
            st.rerun()
            
        if search_query:
            st.write(f"Você está buscando por: **{search_query}**")
            data = search_youtube(search_query, api_key1)    
            if is_quota_error(data):
                st.info("Cota da chave 1 excedida. Utilizando com a chave 2...")
                data = search_youtube(search_query, api_key2)
                if is_quota_error(data):
                    st.error("Quota das duas chaves excedida. Tente novamente mais tarde.")
                    st.stop()
            videos = data.get("items", [])
            if videos:
                video_id = videos[0]["id"]["videoId"]
                # st.subheader("▶️ Tocando agora:")
                st.video(f"https://www.youtube.com/embed/{video_id}?autoplay=0",autoplay=True)
                musica_deezer = link_musica_deezer(search_query)
                musica_spotify = link_musica_spotify(search_query, client_id, client_secret)
    
            else:
                st.warning("Conexão com a YouTube falhou, tente novamente mais tarde ou acesse nas plataformas abaixo.")

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
                            width: 70px;
                        }}
                        </style>

                        <div class="link-musica">
                            {deezer}
                            {spotify}
                        </div>
                        """.format(
                            deezer=f'<a href="{musica_deezer}" target="_blank"><img src="https://www.deezer.com/favicon.ico" alt="Deezer"></a>' if musica_deezer else '',
                            spotify=f'<a href="{musica_spotify}" target="_blank"><img src="https://upload.wikimedia.org/wikipedia/commons/thumb/b/bd/2024_Spotify_Logo.svg/1024px-2024_Spotify_Logo.svg.png" alt="Spotify"></a>' if musica_spotify else ''
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
            st.warning("Digite o nome de uma música ou artista para iniciar a busca.")




        # Recomendações de nosso sistema
        with st.expander("Recomendações"):
            st.write("Em desenvolvimento...")
    # -------- COLUNA DIREITA: Top 50 com Tabs e expanders --------
    with col_right:
        st.header("🔥 Top 50")
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
            
            
            with st.container(height=500):
                # Organiza os tracks em uma grade com 4 colunas por linha
                num_cols = 2
                rows = [tracks[i:i+num_cols] for i in range(0, len(tracks), num_cols)]
                for row in rows:
                    cols = st.columns(len(row))
                    for idx, track in enumerate(row):
                        with cols[idx]:
                            with st.container( border= False, height=350):
                                if track["album_cover"]:
                                    st.image(track["album_cover"], width=200)
                                else:
                                    st.text("Sem capa")
                                if len(track['title'])>10:
                                    st.markdown(f"**{track['title'][0:10]}...**")
                                else:
                                    st.markdown(f"**{track['title']}**")
                                st.caption(f"{track['artist']}")
                                # Chave única para cada botão
                                unique_key = f"{playlist_key}_{idx}_{track['title']}"
                                if st.button("▶️ Tocar", key=unique_key):
                                    st.session_state['search_query'] = f"{track['title']} {track['artist']}"
                                    new_entry = {
                                        "song": track["title"],
                                        "artist": track["artist"],
                                        "cover_url": track["album_cover"],
                                        "timestamp": time.time(),
                                        # "genre": track["genre"]
                                    }
                                    save_search_history(new_entry)
                                    st.rerun()
        
        with tab_brasil:
            display_tracks("Top50Brasil", DEEZER_PLAYLIST_IDS["Top 50 Brasil"])
        with tab_global:
            display_tracks("Top50Global", DEEZER_PLAYLIST_IDS["Top 50 Global"])



if __name__ == "__main__":
    show()
