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
                  'image_cache']
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
    # Verifica se já está no cache
    if song_name in st.session_state["image_cache"]:
        return st.session_state["image_cache"][song_name]
    
    # Se não estiver no cache, busca no Spotify
    results = sp.search(q=song_name, limit=1, type='track')
    if results['tracks']['items']:
        track = results['tracks']['items'][0]
        album_cover_url = track['album']['images'][0]['url']
        # Armazena no cache
        st.session_state["image_cache"][song_name] = album_cover_url
        return album_cover_url
    return None

def generate_recommendations(selected_genres, data):
    # Seleciona músicas aleatórias de cada gênero
    recommendations = []
    for genre in selected_genres:
        if data[data['track_genre'] == genre].notnull().any().any():
            genre_songs = data[data['track_genre'] == genre]
            recommendations.extend(genre_songs['track_name'].sample(6).tolist())
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
    tab1, tab2, tab3, tab4 = st.tabs(["Para você ", " Histórico", " Gêneros", 'Dados de Sessão / Músicas Disponiveis'])

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
    if "image_cache" not in st.session_state:
        st.session_state["image_cache"] = {}

    # Tab 1 - Gêneros
    with tab1:

        st.subheader("🎶 Recomendações de Música")

        # Verifica se os gêneros foram selecionados
        if st.session_state.get("selected_genres"):
            selected_genres = st.session_state["selected_genres"]

            # Autentica com o Spotify
            sp = authenticate_spotify()

            # Se já houver recomendações salvas, exibe as recomendadas anteriormente
            if len(st.session_state["recommended_songs"]) > 0:
                recommended_songs = st.session_state["recommended_songs"]
                st.write("Aqui estão suas recomendações:")
            else:
                recommended_songs = []

            # Gera novas recomendações
            if len(recommended_songs) == 0:
                recommended_songs = generate_recommendations(selected_genres, data)
                st.session_state["recommended_songs"] = recommended_songs

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
                # Dentro do loop que exibe as músicas recomendadas (Tab 1)
                for idx, song in enumerate(recommended_songs_line):
                    col = cols[idx]
                    album_cover_url = get_album_cover(song, sp)

                    if album_cover_url:
                        col.image(album_cover_url, width=200)
                        if col.button(f"{song}", key=f"song_{song}_{idx}"):
                            # Adiciona ao histórico
                            new_entry = {
                                "song": song,
                                "cover_url": album_cover_url,
                                "timestamp": time.time()
                            }
                            
                            st.session_state["search_history"].append(new_entry)
                            
                            st.session_state["search_query"] = song
                            st.session_state["page"] = "search"
                            st.rerun()  # Use experimental_rerun() para evitar looping inesperado

                # Adiciona uma linha horizontal após a primeira linha de recomendações
                if line == 0:
                    st.markdown('---')

            # Exibe as músicas recomendadas em formato de lista

        else:
            st.warning("Selecione gêneros na aba 'Gêneros' para ver recomendações.")

        # Condicional para só gerar novas recomendações quando o botão for clicado
        if st.button("Novas recomendações"):
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
            st.rerun() 
            
        
    # Tab 2 - Histórico
    with tab2:
        st.subheader("📜 Histórico de Pesquisas")
        
        if "search_history" not in st.session_state:
            st.session_state["search_history"] = []
        
        if st.session_state["search_history"]:
            st.write("Histórico de músicas pesquisadas:")
            
            for idx, entry in enumerate(reversed(st.session_state["search_history"])):
                col1, col2 = st.columns([1, 4])
                
                with col1:
                    # Usa o cache em vez de buscar novamente
                    cover_url = st.session_state["image_cache"].get(entry['song'])
                    if cover_url:
                        st.image(cover_url, width=100)
                    else:
                        st.write("Sem capa disponível")
                
                with col2:
                    st.write(f"**{entry['song']}**")
                    st.caption(f"Pesquisado {time_ago(entry['timestamp'])}")
                    if st.button("Pesquisar", key=f"hist_{idx}"):
                        st.session_state["search_query"] = entry["song"]
                        st.rerun()
                                
                st.markdown("---")
        else:
            st.write("Nenhuma música pesquisada ainda.")
        

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
            search_query = st.text_input("Buscar gêneros", placeholder="Digite um gênero...", key="genre_search").lower()
            
            filtered_genres = [g for g in genres if search_query in g.lower()] if search_query else genres
            
            with st.container(height=300):
                for genre in filtered_genres:
                    if genre not in st.session_state.get("selected_genres", []):
                        if st.button(f"+ {genre}", 
                                    key=f"add_{genre}",
                                    use_container_width=True):
                            if genre not in st.session_state["selected_genres"]:
                                st.session_state["selected_genres"].append(genre)
                                st.rerun()
            
            # Seção 3: Gêneros Recomendados (baseado nos selecionados)
            st.markdown("---")
            st.markdown("### 💡 Recomendados para Você")

            # Lógica avançada de recomendação
            if st.session_state.get("selected_genres"):
                selected = st.session_state["selected_genres"]
                
                # 1. Mapeamento de similaridade entre gêneros (pode ser expandido)
                genre_similarity = {
                    "rock": ["alternative-rock", "indie-rock", "hard-rock", "metal", "punk"],
                    "pop": ["pop-rock", "indie-pop", "dance-pop", "synth-pop", "k-pop"],
                    "jazz": ["blues", "soul", "funk", "r&b", "lounge"],
                    "electronic": ["edm", "techno", "house", "trance", "dubstep"],
                    "hiphop": ["rap", "trap", "grime", "drill", "r&b"],
                    "classical": ["opera", "orchestral", "piano", "baroque", "chamber"],
                    "country": ["folk", "bluegrass", "americana", "southern-rock"],
                    "reggae": ["dub", "ska", "dancehall", "reggaeton"]
                }
                
                # 2. Encontra gêneros similares baseados nos selecionados
                similar_genres = []
                for selected_genre in selected:
                    # Verifica similaridade direta
                    if selected_genre in genre_similarity:
                        similar_genres.extend(genre_similarity[selected_genre])
                    
                    # Verifica similaridade inversa (subgêneros)
                    for main_genre, subgenres in genre_similarity.items():
                        if selected_genre in subgenres and main_genre not in similar_genres:
                            similar_genres.append(main_genre)
                
                # 3. Remove duplicados e já selecionados
                recommended_genres = list(set([
                    g for g in similar_genres 
                    if g in genres and g not in selected
                ]))
                
                # 4. Ordena por relevância (frequência de aparição)
                genre_counts = {g: similar_genres.count(g) for g in recommended_genres}
                recommended_genres = sorted(recommended_genres, key=lambda x: -genre_counts.get(x, 0))
                
                # 5. Limita a 5 recomendações e mostra com explicação
                if recommended_genres:
                    cols = st.columns(2)
                    for i, genre in enumerate(recommended_genres[:6]):  # Mostra até 6 (2 linhas de 3)
                        with cols[i % 2]:
                            # Encontra o gênero "pai" que gerou a recomendação
                            reason = next(
                                (main_genre for main_genre, subgenres in genre_similarity.items() 
                                if genre in subgenres and main_genre in selected),
                                next((g for g in selected if g in genre), selected[0])
                            )
                  
                            if st.button(
                                f"{genre.capitalize()}",
                                key=f"rec_{genre}",
                                help=f"Relacionado a {reason.capitalize()}",
                                use_container_width=True
                            ):
                                st.session_state["selected_genres"].append(genre)
                                st.rerun()
                else:
                    st.info("Adicione mais gêneros para receber recomendações personalizadas")
            else:
                # Recomendações iniciais para novos usuários
                popular_genres = ["pop", "rock", "electronic", "hiphop", "jazz"]
                st.info("Experimente começar com:")
                cols = st.columns(2)
                for i, genre in enumerate(popular_genres):
                    with cols[i % 2]:
                        if st.button(f" {genre.capitalize()}", key=f"starter_{genre}", use_container_width=True):
                            st.session_state["selected_genres"].append(genre)
                            st.rerun()

        
        with col2:
            # [Mantém o mesmo código da coluna de recomendações musical]
            st.subheader(" Recomendações por Gênero")
            
            # Inicializa o dicionário de recomendações por gênero
            if "genre_recommendations" not in st.session_state:
                st.session_state["genre_recommendations"] = {}
            
            
            if st.session_state.get("selected_genres"):
                sp = authenticate_spotify()
                
                # Mostra recomendações para cada gênero selecionado
                for genre in st.session_state["selected_genres"]:
                    with st.expander(f"🎵 {genre.capitalize()}", expanded=True):
                        # Verifica se já tem recomendações para este gênero
                        if genre in st.session_state["genre_recommendations"]:
                            songs_data = st.session_state["genre_recommendations"][genre]
                        else:
                            # Gera recomendações novas se não existirem
                            genre_songs = data[data['track_genre'] == genre]['track_name'].sample(3).tolist()
                            songs_data = [
                                {
                                    "song": song,
                                    "cover_url": get_album_cover(song, sp)
                                } for song in genre_songs
                            ]
                            st.session_state["genre_recommendations"][genre] = songs_data
                        
                        # Exibe as músicas
                        cols = st.columns(3)
                        for idx, song_data in enumerate(songs_data):
                            with cols[idx]:
                                if song_data["cover_url"]:
                                    st.image(song_data["cover_url"], width=120)
                                    if st.button(song_data["song"], key=f"prev_{genre}_{song_data['song']}"):
                                        # Adiciona ao histórico
                                        new_entry = {
                                            "song": song_data["song"],
                                            "cover_url": song_data["cover_url"],
                                            "timestamp": time.time(),
                                            "genre": genre
                                        }
                                        if "search_history" not in st.session_state:
                                            st.session_state["search_history"] = []
                                        st.session_state["search_history"].append(new_entry)
                                        
                                        st.session_state["search_query"] = song_data["song"]
                                        st.rerun()
                                else:
                                    st.error(f"Capa não encontrada para: {song_data['song']}")
                        
                        # Botão para atualizar apenas este gênero
                        if st.button("Atualizar este gênero", key=f"refresh_{genre}"):
                            with st.spinner(f"Atualizando {genre}..."):
                                genre_songs = data[data['track_genre'] == genre]['track_name'].sample(3).tolist()
                                st.session_state["genre_recommendations"][genre] = [
                                    {
                                        "song": song,
                                        "cover_url": get_album_cover(song, sp)
                                    } for song in genre_songs
                                ]
                            st.rerun()
            else:
                st.info("Selecione gêneros à esquerda para ver recomendações")

    # Tab 4 - Dados de Sessão
    with tab4:
        clean_session_state()

        st.write("Dados de sessão:", st.session_state)

        st.write("Músicas disponíveis:")
        st.write(pd.DataFrame(data[['track_name', 'track_genre', 'artists']]))

