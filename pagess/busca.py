import streamlit as st
import requests
from dotenv import load_dotenv
import os

load_dotenv()

def show():
    # Carregar as chaves de API
    senha1 = os.getenv('API_YOUTUBE1')
    senha2 = os.getenv('API_YOUTUBE2')

    # Definir a URL da API
    SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"

    # Função para buscar músicas no YouTube
    def search_youtube(query, api_key):
        params = {
            "part": "snippet",
            "q": 'musica ' + query,
            "type": "video",
            "key": api_key,
            "maxResults": 2
        }
        response = requests.get(SEARCH_URL, params=params)
        return response.json()

    # Função para verificar se a resposta contém erro de quota
    def is_quota_error(response):
        if 'error' in response:
            error_message = response['error'].get('message', '')
            # Verifica se o erro é relacionado a quota
            if 'quota' in error_message.lower():
                return True
        return False

    # Interface do Streamlit
    st.title("🎵 Reprodutor de Músicas do YouTube")

    # Inicializa a query de pesquisa, caso não exista na session_state
    if 'search_query' not in st.session_state:
        st.session_state['search_query'] = ''

    # Se o usuário chegou diretamente na página de busca
    search_query = st.text_input("🔎 Pesquise uma música ou artista:", value=st.session_state['search_query'])

    # Atualiza a query de pesquisa na sessão somente quando o campo de texto mudar
    if search_query != st.session_state['search_query']:
        st.session_state['search_query'] = search_query
        st.rerun()

    if search_query:
        # Exibe o termo pesquisado
        st.write(f"Você está buscando por: **{search_query}**")

        # Realiza a busca na API do YouTube, tentando com a primeira chave
        data = search_youtube(search_query, senha1)

        # Verifica se a primeira chave atingiu o limite de quota
        if is_quota_error(data):
            print("A quota da chave 1 foi excedida. Tentando com a chave 2...")
            data = search_youtube(search_query, senha2)

            # Verifica se a segunda chave também falhou
            if is_quota_error(data):
                print("A quota das duas chaves de API foi excedida. Tente novamente mais tarde.")
                return

        videos = data.get("items", [])

        if videos:
            st.subheader("🔽 Selecione uma música para tocar:")
            for video in videos:
                title = video["snippet"]["title"]
                video_id = video["id"]["videoId"]
                thumbnail_url = video["snippet"]["thumbnails"]["high"]["url"]

                col1, col2 = st.columns([1, 4])
                with col1:
                    st.image(thumbnail_url, width=200)
                with col2:
                    if st.button(title, key=video_id):
                        st.session_state["selected_video"] = video_id

            # Exibir player do vídeo selecionado
            if "selected_video" in st.session_state:
                selected_video = st.session_state["selected_video"]
                st.subheader("▶️ Tocando agora:")
                st.video(f"https://www.youtube.com/embed/{selected_video}?autoplay=1")

        else:
            st.warning("Nenhum resultado encontrado. Tente outra pesquisa.")
            print(data)
    else:
        st.warning("Nenhuma música foi selecionada para a busca.")
