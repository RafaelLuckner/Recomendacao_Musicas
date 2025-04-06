import streamlit as st
import pandas as pd
import plotly.express as px

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
                  "Top50Brasil_tracks",
                  "Top50Global_tracks",
                  "avaliacao"]
    for key in list(st.session_state.keys()):
        if key not in valid_keys:
            del st.session_state[key]


def show():
    tab1, tab2 = st.tabs(["Dashboard", "Dados da sessão"])

    with tab1:
        if 'search_history' not in st.session_state:
            st.session_state['search_history'] = []
        df = pd.DataFrame(st.session_state['search_history'])
        if df.empty:
            st.write("Nenhuma pesquisa realizada.")
            return
        else:
            df['genre'] = df["genre"].fillna('Desconhecido')

            # Convertendo timestamp para data legível
            df["timestamp"] = pd.to_datetime(df["timestamp"], unit="s")

            # Título do dashboard
            st.title("🎵 Dashboard de Músicas Reproduzidas")

            # Container para estatísticas gerais
            with st.container():
                st.subheader("📊 Estatísticas Gerais")
                col1, col2 = st.columns(2)
                col1.metric("Total de Músicas", len(df))
                col2.metric("Gêneros Únicos", df["genre"].nunique())

            # Layout de duas colunas para os gráficos
            col_left, col_right = st.columns(2)

            with col_left:
                # Gráfico de distribuição dos gêneros
                with st.container(border=True, height=600):
                    st.subheader("Gêneros mais ouvidos")
                    df_genres = df["genre"].dropna().sort_index(ascending=False)
                    df_genres.columns = ["genre", "count"]
        
                    fig_genres = px.pie(df_genres, names="genre")
                    st.plotly_chart(fig_genres, use_container_width=True)
                
                with st.container(border=True , height=600):
                    import pytz
                    st.subheader("📈 Evolução das Reproduções")

                    # Converter timestamp para datetime com fuso horário brasileiro
                    fuso_brasil = pytz.timezone("America/Sao_Paulo")
                    df['datetime'] = pd.to_datetime(df['timestamp'], unit='s').dt.tz_localize('UTC').dt.tz_convert(fuso_brasil)

                    # Opção de agrupamento
                    periodo = st.radio("Agrupar por:", ["Dia", "Hora"], horizontal=True)
                    freq = 'D' if periodo == "Dia" else 'H'
                    date_format = '%d/%m' if freq == 'D' else '%d/%m %Hh'

                    # Geração do período completo
                    time_range = pd.date_range(
                        start=df['datetime'].min().floor(freq),
                        end=pd.Timestamp.now(tz=fuso_brasil).ceil(freq),
                        freq=freq,
                        tz=fuso_brasil
                    )

                    df_time = (df.set_index('datetime')
                                .resample(freq)
                                .size()
                                .reindex(time_range, fill_value=0)
                                .reset_index(name='Reproduções'))

                    df_time.rename(columns={'index': 'Periodo'}, inplace=True)
                    df_time['Periodo'] = df_time['Periodo'].dt.strftime(date_format)

                    # Gráfico de barras
                    fig = px.bar(
                        df_time,
                        x='Periodo',
                        y='Reproduções',
                        labels={'Periodo': 'Período', 'Reproduções': 'Reproduções'}
                    )

                    fig.update_layout(
                        height=350,
                        margin=dict(t=20, b=20, l=10, r=10),
                        xaxis_title=None,
                        yaxis_title=None,
                        showlegend=False,
                        hovermode='x unified',
                    )

                    fig.update_traces(marker_color='#1a5276')  # Azul escuro

                    st.plotly_chart(fig, use_container_width=True)

            with col_right:
                # Gráfico de artistas mais ouvidos (horizontal)
                with st.container(border=True, height=600):
                    st.subheader("🎤 Top 5 Artistas Mais Ouvidos")
                    df_artists = df["artist"].dropna().value_counts().reset_index()
                    df_artists.columns = ["artist", "count"]
                    df_artists = df_artists.sort_values("count", ascending=False).head(5)
                    # Cortar nomes com mais de 30 caracteres
                    df_artists["artist_short"] = df_artists["artist"].apply(lambda x: x[:27] + "..." if len(x) > 30 else x)
                    
                    # Cor fixa azul escuro (em formato HEX)
                    BAR_COLOR = "#1a5276"  # Azul escuro
                    
                    fig_artists = px.bar(df_artists, 
                                    y="artist_short", 
                                    x="count", 
                                    orientation='h',
                                    color_discrete_sequence=[BAR_COLOR],  # Cor uniforme
                                    text="count")
                    
                    fig_artists.update_layout(
                        yaxis={
                            'categoryorder': 'total ascending',
                            'title': None
                        },
                        xaxis={
                            'title': None
                        },
                        margin=dict(l=20, r=20, t=40, b=20),
                        hovermode="y unified",
                        plot_bgcolor='rgba(0,0,0,0)',  # Fundo transparente
                        paper_bgcolor='rgba(0,0,0,0)'   # Fundo transparente
                    )
                    
                    fig_artists.update_traces(
                        textposition='inside',
                        hovertemplate="<b>%{y}</b><br>Reproduções: %{x}<extra></extra>",
                        marker=dict(line=dict(width=0)),
                        textfont_size=25,
                            # Remove bordas das barras
                    )
                    
                    st.plotly_chart(fig_artists, use_container_width=True)
                
                # Gráfico de músicas mais reproduzidas (horizontal)
                with st.container(border=True, height=600):
                    st.subheader("🎶 Top 5 Músicas Mais Reproduzidas")
                    df_songs = df["song"].value_counts().reset_index()
                    df_songs.columns = ["song", "count"]
                    df_songs = df_songs.sort_values("count", ascending=False).head(5)

                    
                    # Cortar títulos longos
                    df_songs["song_short"] = df_songs["song"].apply(lambda x: (x[:27] + "...") if len(x) > 30 else x)
                    
                    # Criar gráfico com cor sólida
                    fig_songs = px.bar(df_songs,
                                    y="song_short",
                                    x="count",
                                    text="count",
                                    color_discrete_sequence=[BAR_COLOR],
                                    orientation='h')  # Azul petróleo escuro
                    
                    # Ajustes finais
                    fig_songs.update_layout(
                        yaxis={'categoryorder': 'total ascending', 'title': None},
                        xaxis={'visible': False},  # Remove completamente o eixo X
                        margin=dict(l=0, r=0, t=30, b=0), 
                        hoverlabel=dict(bgcolor="white"),
                    )
                    
                    fig_songs.update_traces(
                        textposition='inside',  # Números fora da barra
                        textfont_size=25,
                        hovertemplate="<b>%{y}</b><br>Reproduções: %{x}<extra></extra>"
                    )
                    
                    st.plotly_chart(fig_songs, use_container_width=True)
            st.write(df)


    with tab2:

        clean_session_state()

        st.write("Dados de sessão:", st.session_state)

        st.write("Músicas disponíveis:")
        data = pd.read_csv('data/data_traduct.csv')
        st.write(pd.DataFrame(data[['track_name', 'track_genre', 'artists']]))
