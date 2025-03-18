import streamlit as st

def show():
    st.title("🎵 Recomendações Personalizadas")

    # Criar abas para navegação
    tab1, tab2 = st.tabs(["🎧 Gêneros", "🎶 Recomendações"])

    genres = [
        'Pop', 'Rock', 'Hip-Hop', 'Jazz', 'Classical', 'Electronic',
        'Reggae', 'Blues', 'Funk', 'R&B', 'Country', 'Metal',
        'Indie', 'Gospel', 'Forró', 'Sertanejo', 'MPB', 'Rap'
    ]

    if "selected_genres" not in st.session_state:
        st.session_state["selected_genres"] = []

    with tab1:
        st.subheader("🎧 Escolha seus gêneros favoritos")

        # Adicionar campo de busca para filtrar gêneros
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
                if col.button(f"{'✅' if is_selected else '❌'} {genre}", key=genre, use_container_width=True, help=f"{'Remover' if is_selected else 'Adicionar'} {genre}"):
                    if is_selected:
                        st.session_state["selected_genres"].remove(genre)
                    else:
                        st.session_state["selected_genres"].append(genre)
                    st.rerun()  

        if not st.session_state["selected_genres"]:
            st.warning("Selecione pelo menos um gênero para obter recomendações.")

    with tab2:
        st.subheader("🎶 Recomendações de Música")

        recommendations = {
            'Pop': ['Blinding Lights - The Weeknd', 'Levitating - Dua Lipa'],
            'Rock': ['Bohemian Rhapsody - Queen', 'Smells Like Teen Spirit - Nirvana'],
            'Hip-Hop': ['Sicko Mode - Travis Scott', 'God’s Plan - Drake'],
            'Jazz': ['Take Five - Dave Brubeck', 'So What - Miles Davis'],
            'Classical': ['Fur Elise - Beethoven', 'Clair de Lune - Debussy'],
            'Electronic': ['Strobe - Deadmau5', 'Wake Me Up - Avicii'],
            'Reggae': ['No Woman No Cry - Bob Marley'],
            'Blues': ['The Thrill Is Gone - B.B. King'],
            'Funk': ['Superstition - Stevie Wonder'],
            'R&B': ['No Scrubs - TLC'],
            'Country': ['Take Me Home, Country Roads - John Denver'],
            'Metal': ['Master of Puppets - Metallica'],
            'Indie': ['Fluorescent Adolescent - Arctic Monkeys'],
            'Gospel': ['Amazing Grace - Aretha Franklin'],
            'Forró': ['Asa Branca - Luiz Gonzaga'],
            'Sertanejo': ['Evidências - Chitãozinho & Xororó'],
            'MPB': ['Águas de Março - Tom Jobim'],
            'Rap': ['Lose Yourself - Eminem']
        }

        if st.session_state["selected_genres"]:
            recommended_songs = []
            for genre in st.session_state["selected_genres"]:
                recommended_songs.extend(recommendations.get(genre, []))

            for song in recommended_songs:
                if st.button(f"🔊 {song}", key=song):
                    st.session_state["search_query"] = song
                    st.session_state["page"] = "search"
                    st.rerun()

        else:
            st.warning("Selecione gêneros na aba 'Gêneros' para ver recomendações.")

