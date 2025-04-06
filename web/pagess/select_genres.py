import streamlit as st
import pandas as pd

def show():
    # Carregar dados
    data = pd.read_csv('data/data_traduct.csv')
    genres = data['track_genre'].unique()

    # Verificar se os estados existem
    if "selected_genres" not in st.session_state:
        st.session_state["selected_genres"] = []
    if "search_query" not in st.session_state:
        st.session_state["search_query"] = ""

    # Título da seção
    st.subheader("🎧 Escolha seus gêneros favoritos")

    # Limite de gêneros selecionados
    max_genres = 5

    
    if st.session_state["selected_genres"]:
        st.write("### Gêneros selecionados:")
        # Exibir os gêneros dentro de uma borda
        st.write(f"```{', '.join(st.session_state['selected_genres']).upper()}```")
        
        col1, col2 = st.columns(2)
        with col1:
            # Botão para limpar gêneros selecionados
            button = st.button("Limpar gêneros selecionados", use_container_width=True)
            if button:
                st.session_state["selected_genres"] = []
                st.rerun()
        # seguir para pagina inicial
        with col2:
            if st.button("Continuar", key="voltar", use_container_width=True):
                st.session_state["page"] = "select_songs"
                st.rerun()
    else:
        st.write("### Gêneros selecionados:")
        st.write("Nenhum gênero selecionado.")

    st.write("---")  

    # Campo de busca para filtrar gêneros
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
            
            # Verificar se o número de gêneros selecionados não ultrapassa o limite
            if len(st.session_state["selected_genres"]) < max_genres or is_selected:
                if col.button(f"{'✅' if is_selected else '🎶'} {genre.capitalize()}", key=genre, use_container_width=True, help=f"{'Remover' if is_selected else 'Adicionar'} {genre}"):
                    if is_selected:
                        st.session_state["selected_genres"].remove(genre)
                    else:
                        st.session_state["selected_genres"].append(genre)
                    st.rerun()
            elif not is_selected:
                col.button(f"{genre} (max: {max_genres})", key=f"{genre}_disabled", disabled=True, use_container_width=True)
