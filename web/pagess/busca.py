import streamlit as st
import requests
from dotenv import load_dotenv
import os
import time

load_dotenv()

# -------------------------------
# FUNÇÕES PARA A API DO YOUTUBE
# -------------------------------
SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"

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
                "album_cover": track["album"].get("cover_medium", None)
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


# -------------------------------
# INTERFACE STREAMLIT
# -------------------------------
def show():
    # Chaves da API do YouTube definidas no .env
    api_key1 = os.getenv('API_YOUTUBE1')
    api_key2 = os.getenv('API_YOUTUBE2')
    
    if 'search_query' not in st.session_state:
        st.session_state['search_query'] = ''
    
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
            else:
                st.warning("Nenhum resultado encontrado. Tente outra pesquisa.")
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
            
            # Expander para permitir minimizar a lista
            with st.container(height=500):
                # Organiza os tracks em uma grade com 4 colunas por linha
                num_cols = 2
                rows = [tracks[i:i+num_cols] for i in range(0, len(tracks), num_cols)]
                for row in rows:
                    cols = st.columns(len(row))
                    for idx, track in enumerate(row):
                        with cols[idx]:
                            with st.container( border=False):
                                if track["album_cover"]:
                                    st.image(track["album_cover"], width=150)
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
                                    st.rerun()
        
        with tab_brasil:
            display_tracks("Top50Brasil", DEEZER_PLAYLIST_IDS["Top 50 Brasil"])
        with tab_global:
            display_tracks("Top50Global", DEEZER_PLAYLIST_IDS["Top 50 Global"])



if __name__ == "__main__":
    show()
