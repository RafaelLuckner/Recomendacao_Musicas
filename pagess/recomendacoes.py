import streamlit as st

def show():
    st.title("🎵 Recomendações Personalizadas")

    st.write("Escolha os gêneros de música que você mais gosta:")

    # Gêneros de música disponíveis para o usuário escolher
    genres = ['Pop', 'Rock', 'Hip-Hop', 'Jazz', 'Classical', 'Electronic']
    
    # Exibir opções de gênero com múltiplas seleções
    selected_genres = st.multiselect("Selecione os gêneros de música", genres)

    # Salvar a escolha do usuário na sessão
    if selected_genres:
        st.session_state["selected_genres"] = selected_genres

        st.write(f"Você escolheu os gêneros: {', '.join(selected_genres)}")
    else:
        # Se nenhum gênero for selecionado, mostrar um aviso
        st.warning("Selecione pelo menos um gênero para ver as recomendações.")

    if "selected_genres" in st.session_state:
        # Simulação de músicas recomendadas com base no gênero escolhido
        recommendations = {
            'Pop': ['Blinding Lights - The Weeknd', 'Levitating - Dua Lipa', 'Save Your Tears - The Weeknd'],
            'Rock': ['Bohemian Rhapsody - Queen', 'Smells Like Teen Spirit - Nirvana', 'Hotel California - Eagles'],
            'Hip-Hop': ['Sicko Mode - Travis Scott', 'God’s Plan - Drake', 'HUMBLE. - Kendrick Lamar'],
            'Jazz': ['Take Five - Dave Brubeck', 'So What - Miles Davis', 'What A Wonderful World - Louis Armstrong'],
            'Classical': ['Fur Elise - Beethoven', 'Clair de Lune - Debussy', 'Canon in D - Pachelbel'],
            'Electronic': ['Strobe - Deadmau5', 'Wake Me Up - Avicii', 'Titanium - David Guetta ft. Sia']
        }

        # Exibir recomendações de músicas com base nos gêneros selecionados
        st.write("🎶 **Recomendações para os gêneros escolhidos:**")
        
        recommended_songs = []
        for genre in selected_genres:
            recommended_songs.extend(recommendations.get(genre, []))
        
        # Exibir as músicas recomendadas
        for song in recommended_songs:
            if st.button(f"🔊 {song}", key=song):
                # Redireciona para a página de busca e pesquisa a música automaticamente
                st.session_state["search_query"] = song
                st.session_state["page"] = "search"
                st.rerun()  # Recarrega a página para efetivar a navegação

