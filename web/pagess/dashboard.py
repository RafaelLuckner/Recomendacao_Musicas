import streamlit as st
import pandas as pd
import plotly.express as px
import sources
import pytz
from io import BytesIO

from wordcloud import WordCloud
import matplotlib.pyplot as plt

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
                  "avaliacao",
                  'user_id']
    for key in list(st.session_state.keys()):
        if key not in valid_keys:
            del st.session_state[key]

def nuvem_palavras(df, coluna):
            frequencias = df[coluna].value_counts().to_dict()
            # Criar a nuvem com fundo transparente
            nuvem = WordCloud(
                width=800,
                height=400,
                background_color=None,
                mode='RGBA',
                colormap='viridis',
                max_words=50
            ).generate_from_frequencies(frequencias)

            # Salvar a imagem em um buffer de memória
            buffer = BytesIO()
            nuvem.to_image().save(buffer, format='PNG')
            buffer.seek(0)

            # Mostrar no Streamlit
            st.image(buffer, use_container_width=True)


def barchart_top5(df, coluna, BAR_COLOR="#4B7BE5"):
    df_songs = df[coluna].value_counts().reset_index()
    df_songs.columns = [coluna, "count"]
    df_songs = df_songs.sort_values("count", ascending=False).head(5)
    
    # Cortar títulos longos
    df_songs[coluna + "_short"] = df_songs[coluna].apply(lambda x: (x[:27] + "...") if len(x) > 30 else x)
    
    # Criar gráfico com cor sólida
    fig_songs = px.bar(df_songs,
                        y=coluna + "_short",
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

def tree_map(df):
    # Contar quantas vezes cada música foi ouvida por gênero
    df_treemap = df[["genre", "song"]].dropna()
    df_treemap['genre'] = [genre.capitalize() for genre in df_treemap['genre']]
    df_treemap = df_treemap.value_counts().reset_index()
    df_treemap.columns = ["genre", "song", "count"]

    # Criar o treemap hierárquico
    fig = px.treemap(
        df_treemap,
        path=["genre", "song"],
        values="count",
    )

    # Deixar o hover limpo e profissional
    fig.update_traces(
        hovertemplate='<b>%{label}</b><br>Quantidade: %{value}<extra></extra>'
    )

    st.plotly_chart(fig, use_container_width=True)



def show():
    if 'user_id' not in st.session_state or st.session_state["user_id"] == None:
        user_id = sources.search_user_id_mongodb(st.session_state["email"])
        st.session_state["user_id"] = user_id
    if "search_history" not in st.session_state or st.session_state["search_history"] == []:
        st.session_state["search_history"] = sources.search_history_user(st.session_state["user_id"])


    st.session_state["search_history"] = sources.search_history_user(st.session_state["user_id"])
    # Calcular métricas para todas as músicas ouvidas
    full_history_df = pd.DataFrame(st.session_state['search_history'])
    if not full_history_df.empty:
        if "genre" not in full_history_df.columns:
            full_history_df["genre"] = None
        else:
            full_history_df['genre'] = full_history_df["genre"].fillna('Top 50')
        total_songs = len(full_history_df)
        unique_genres = full_history_df["genre"].nunique()
    else:
        total_songs = 0
        unique_genres = 0

    # Limitar às últimas 100 músicas reproduzidas, ordenando por timestamp
    recent_history = sorted(st.session_state['search_history'], key=lambda x: x['timestamp'], reverse=True)[:100]
    df = pd.DataFrame(recent_history)
    if df.empty:
        st.write("Nenhuma pesquisa realizada.")
        return
    else:
        if "genre" not in df.columns:
            df["genre"] = None
        else:
            df['genre'] = df["genre"].fillna('Top 50')

        # Convertendo timestamp para data legível
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="s")

        # Título do dashboard
        st.title("🎵 Dashboard Músicas Reproduzidas")

        # Container para estatísticas gerais
        with st.container():
            st.subheader("📊 Estatísticas Gerais")
            col1, col2 = st.columns(2)
            col1.metric("Total de Músicas", total_songs)
            col2.metric("Gêneros Únicos", unique_genres)

        # Layout de duas colunas para os gráficos
        col_left, col_right = st.columns(2)
        with col_left:

            with st.container(border=True, height=470):
                st.subheader("Músicas Mais Reproduzidas", divider='rainbow')
                nuvem_palavras(full_history_df, "song")

            # Gráfico de song mais ouvidos (horizontal)
            with st.container(border=True, height=600):
                st.subheader("Top 5 Músicas Mais Ouvidos")
                BAR_COLOR = "#1a5276"

                barchart_top5(full_history_df, "song", BAR_COLOR)

            # Treemap de músicas agrupadas por gênero
            with st.container(border=True, height=450):
                st.subheader("Músicas mais ouvidas por gênero")
                tree_map(full_history_df)

            # Fuso horário brasileiro
            fuso_brasil = pytz.timezone("America/Sao_Paulo")


        
        
        # Coluna da Direita
        with col_right:
            # Nu
            with st.container(border=True, height=470):
                st.subheader("Artistas Mais Reproduzidos", divider='rainbow')
                nuvem_palavras(full_history_df, 'artist')

                
            # Gráfico de artistas mais ouvidos (horizontal)
            with st.container(border=True, height=600):
                st.subheader("Top 5 Artistas Mais Ouvidos")
                BAR_COLOR = "#1a5276"

                barchart_top5(full_history_df, "artist", BAR_COLOR)
            

            with st.container(border=True, height=450):
                st.subheader("Evolução das Reproduções")

                # Conversão de timestamp
                full_history_df['datetime'] = pd.to_datetime(full_history_df['timestamp'], unit='s')\
                    .dt.tz_localize('UTC')\
                    .dt.tz_convert(fuso_brasil)

                # Agregação diária
                df_diario = (full_history_df.set_index('datetime')
                            .resample('D')
                            .size()
                            .reset_index(name='Reproduções'))

                df_diario['Data'] = df_diario['datetime'].dt.strftime('%d/%m')

                # Gráfico de área
                fig = px.area(
                    df_diario,
                    x='Data',
                    y='Reproduções',
                    labels={'Data': 'Dia', 'Reproduções': 'Reproduções'}
                )

                fig.update_layout(
                    height=350,
                    margin=dict(t=20, b=20, l=10, r=10),
                    xaxis_title=None,
                    yaxis_title=None,
                    showlegend=False,
                    hovermode='x unified',
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)'
                )

                fig.update_traces(
                    line_color='#1a5276',
                    fill='tozeroy',
                    hovertemplate='Dia: %{x}<br>Reproduções: %{y}<extra></extra>'
                )

                st.plotly_chart(fig, use_container_width=True)




        st.write('---')
        # st.write(df)

  