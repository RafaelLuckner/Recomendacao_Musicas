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
                  "Top50Global_tracks",]
    for key in list(st.session_state.keys()):
        if key not in valid_keys:
            del st.session_state[key]


def show():
    tab1, tab2 = st.tabs(["Dados de sessão", "dashboard"])
    with tab1:

        clean_session_state()

        st.write("Dados de sessão:", st.session_state)

        st.write("Músicas disponíveis:")
        data = pd.read_csv('data/dataset.csv')
        st.write(pd.DataFrame(data[['track_name', 'track_genre', 'artists']]))


    with tab2:
        df = pd.DataFrame(st.session_state['search_history'])


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
            with st.container(border=True):
                st.subheader("Gêneros mais ouvidos")
                fig_genres = px.pie(df, names="genre", hole=0.4)
                st.plotly_chart(fig_genres, use_container_width=True)
            
            # Gráfico de reproduções ao longo do tempo
            with st.container(border=True):
                st.subheader("⏳ Evolução Temporal das Reproduções")
                
                # Converter timestamp para datetime
                df['datetime'] = pd.to_datetime(df['timestamp'], unit='s')
                
                # Seletor de granularidade temporal
                periodo = st.radio("Agrupar por:", ["Dia", "Hora"], horizontal=True)
                
                # Determinar período de análise
                start_time = df['datetime'].min()
                end_time = pd.Timestamp.now()
                
                # Configurar frequência e formatação
                freq = 'D' if periodo == "Dia" else 'H'
                date_format = '%d/%m/%Y' if periodo == "Dia" else '%d/%m %H:%M'
                
                # Criar série temporal completa
                time_range = pd.date_range(start=start_time.floor(freq), end=end_time.ceil(freq), freq=freq)
                df_time = (df.set_index('datetime')
                        .resample(freq)
                        .size()
                        .reindex(time_range, fill_value=0)
                        .reset_index(name='Reproduções'))
                
                # Formatar rótulos
                df_time['Periodo'] = df_time['index'].dt.strftime(date_format)
                
                # Criar gráfico
                fig = px.bar(df_time, 
                            x='Periodo', 
                            y='Reproduções',
                            labels={'Reproduções': 'Músicas Ouvidas'},
                            color='Reproduções',
                            color_continuous_scale='Bluered')
                
                # Ajustes de layout
                fig.update_layout(
                    xaxis_title=None,
                    yaxis_title=None,
                    hovermode='x unified',
                    coloraxis_showscale=False,
                    xaxis={'type': 'category'},
                    height=400
                )
                
                # Tooltip personalizado
                hover_template = "<b>%{x}</b><br>Músicas: %{y}" if periodo == "Dia" else "<b>%{x}h</b><br>Músicas: %{y}"
                fig.update_traces(
                    hovertemplate=hover_template,
                    marker_line_width=0
                )
                
                st.plotly_chart(fig, use_container_width=True)

        with col_right:
            # Gráfico de artistas mais ouvidos (horizontal)
            with st.container(border=True):
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
            with st.container(border=True):
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
