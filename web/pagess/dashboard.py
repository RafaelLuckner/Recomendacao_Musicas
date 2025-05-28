import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sources
import pytz
from io import BytesIO
from datetime import datetime, timedelta
import numpy as np

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

def apply_custom_css():
    """Aplica CSS personalizado para a dashboard"""
    st.markdown("""
    <style>
    .main-header {
        text-align: center;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3rem;
        font-weight: bold;
        margin-bottom: 2rem;
    }
    
    .metric-card {
        background: transparent;
        padding: 1.5rem;
        border-radius: 15px;
        border: 1px solid rgba(128, 128, 128, 0.2);
        text-align: center;
        margin-bottom: 1rem;
        transition: transform 0.2s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        border-color: rgba(128, 128, 128, 0.4);
    }
    
    .chart-container {
        background: transparent;
        padding: 1rem;
        border-radius: 15px;
        border: none;
        margin-bottom: 2rem;
    }
    
    .section-header {
        color: #2c3e50;
        font-size: 1.5rem;
        font-weight: 600;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #667eea;
    }
    
    .ad-banner {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        margin: 2rem 0;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
    }
    
    .ad-sidebar {
        background: #f8f9fa;
        border: 2px dashed #dee2e6;
        border-radius: 10px;
        padding: 1.5rem;
        text-align: center;
        color: #6c757d;
        margin-bottom: 2rem;
    }
    
    .highlight-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        margin-bottom: 1rem;
        text-align: center;
    }
    
    .quick-actions {
        display: flex;
        gap: 1rem;
        margin-bottom: 2rem;
    }
    
    .action-btn {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.8rem 1.5rem;
        border-radius: 25px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .action-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
    }
    
    .insight-box {
        background: transparent;
        padding: 1.5rem;
        border-radius: 15px;
        margin-bottom: 1rem;
        border: none;
        border-left: 3px solid #1f77b4;
    }
    
    .progress-bar {
        background: #e9ecef;
        border-radius: 10px;
        height: 8px;
        overflow: hidden;
        margin: 0.5rem 0;
    }
    
    .progress-fill {
        background: linear-gradient(90deg, #667eea, #764ba2);
        height: 100%;
        border-radius: 10px;
        transition: width 0.3s ease;
    }
    </style>
    """, unsafe_allow_html=True)

def create_enhanced_wordcloud(df, coluna):
    """Cria nuvem de palavras melhorada"""
    frequencias = df[coluna].value_counts().to_dict()
    nuvem = WordCloud(
        width=800,
        height=400,
        background_color=None,
        mode='RGBA',
        colormap='tab10',
        max_words=50,
        relative_scaling=0.5,
        min_font_size=10
    ).generate_from_frequencies(frequencias)

    buffer = BytesIO()
    nuvem.to_image().save(buffer, format='PNG')
    buffer.seek(0)
    
    st.image(buffer, use_container_width=True)

def create_modern_barchart(df, coluna, BAR_COLOR="#1f77b4", title=""):
    """Cria gráfico de barras moderno"""
    df_data = df[coluna].value_counts().reset_index()
    df_data.columns = [coluna, "count"]
    df_data = df_data.sort_values("count", ascending=False).head(5)
    
    # Cortar títulos longos
    df_data[coluna + "_short"] = df_data[coluna].apply(lambda x: (x[:25] + "...") if len(x) > 28 else x)
    
    fig = px.bar(df_data,
                 y=coluna + "_short",
                 x="count",
                 text="count",
                 color_discrete_sequence=[BAR_COLOR],
                 orientation='h')
    
    fig.update_layout(
        yaxis={'categoryorder': 'total ascending', 'title': None},
        xaxis={'visible': False, 'title': None},
        margin=dict(l=0, r=0, t=30, b=0),
        hoverlabel=dict(bgcolor="rgba(255,255,255,0.8)"),
        showlegend=False,
        height=400
    )
    
    fig.update_traces(
        textposition='inside',
        textfont_size=12,
        hovertemplate="<b>%{y}</b><br>Reproduções: %{x}<extra></extra>"
    )
    
    st.plotly_chart(fig, use_container_width=True)

def create_enhanced_treemap(df):
    """Cria treemap aprimorado"""
    df_treemap = df[["genre", "song"]].dropna()
    df_treemap['genre'] = [genre.capitalize() for genre in df_treemap['genre']]
    df_treemap = df_treemap.value_counts().reset_index()
    df_treemap.columns = ["genre", "song", "count"]

    fig = px.treemap(
        df_treemap,
        path=["genre", "song"],
        values="count",
        color_discrete_sequence=px.colors.qualitative.Set3
    )

    fig.update_layout(
        margin=dict(t=30, l=0, r=0, b=0),
        height=400,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )

    fig.update_traces(
        hovertemplate='<b>%{label}</b><br>Reproduções: %{value}<extra></extra>',
        textinfo="label+value"
    )

    st.plotly_chart(fig, use_container_width=True)

def create_listening_timeline(df, fuso_brasil):
    """Cria timeline de escuta aprimorada"""
    df['datetime'] = pd.to_datetime(df['timestamp'], unit='s')\
        .dt.tz_localize('UTC')\
        .dt.tz_convert(fuso_brasil)

    # Agregação por hora do dia
    df_hourly = df.copy()
    df_hourly['hour'] = df_hourly['datetime'].dt.hour
    hourly_counts = df_hourly['hour'].value_counts().sort_index()
    
    # Criar gráfico polar
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=hourly_counts.values,
        theta=[f"{h}:00" for h in hourly_counts.index],
        fill='toself',
        name='Atividade por Hora',
        line_color='#1f77b4',
        fillcolor='rgba(31, 119, 180, 0.3)'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, max(hourly_counts.values) * 1.1])
        ),
        showlegend=False,
        height=400,
        title="Seus Horários de Escuta",
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig

def create_genre_donut(df):
    """Cria gráfico de rosca para gêneros"""
    genre_counts = df['genre'].value_counts().head(8)
    
    fig = go.Figure(data=[go.Pie(
        labels=genre_counts.index,
        values=genre_counts.values,
        hole=.3,
        textinfo='label+percent',
        textposition='outside',
        marker_colors=px.colors.qualitative.Set3
    )])
    
    fig.update_layout(
        showlegend=False,
        margin=dict(t=30, b=0, l=0, r=0),
        height=350
    )
    
    return fig

def translate_day_to_portuguese(day_name):
    """Traduz nomes dos dias da semana para português"""
    translation = {
        'Monday': 'Segunda-feira',
        'Tuesday': 'Terça-feira', 
        'Wednesday': 'Quarta-feira',
        'Thursday': 'Quinta-feira',
        'Friday': 'Sexta-feira',
        'Saturday': 'Sábado',
        'Sunday': 'Domingo'
    }
    return translation.get(day_name, day_name)

def create_discovery_insights(df):
    """Cria insights de descoberta musical"""
    insights = []
    
    # Análise temporal
    df['datetime'] = pd.to_datetime(df['timestamp'], unit='s')
    df['day_of_week'] = df['datetime'].dt.day_name()
    most_active_day = df['day_of_week'].value_counts().index[0]
    most_active_day_pt = translate_day_to_portuguese(most_active_day)
    
    # Análise de diversidade
    total_songs = len(df)
    unique_songs = df['song'].nunique()
    diversity_ratio = (unique_songs / total_songs) * 100 if total_songs > 0 else 0
    
    # Análise de gênero favorito
    top_genre = df['genre'].value_counts().index[0] if len(df) > 0 else "Nenhum"
    
    insights.append(f"🗓️ Você é mais ativo musicalmente às {most_active_day_pt}s")
    insights.append(f"🎯 Sua diversidade musical é de {diversity_ratio:.1f}%")
    insights.append(f"🎼 Seu gênero favorito atual é {top_genre}")
    
    if diversity_ratio < 30:
        insights.append("💡 Dica: Experimente mais gêneros para descobrir novas paixões!")
    elif diversity_ratio > 70:
        insights.append("🌟 Parabéns! Você tem um gosto musical muito diversificado!")
    
    return insights

def show():
    # Aplicar CSS personalizado
    apply_custom_css()
    
    if 'user_id' not in st.session_state or st.session_state["user_id"] == None:
        user_id = sources.search_user_id_mongodb(st.session_state["email"])
        st.session_state["user_id"] = user_id
    if "search_history" not in st.session_state or st.session_state["search_history"] == []:
        st.session_state["search_history"] = sources.search_history_user(st.session_state["user_id"])

    st.session_state["search_history"] = sources.search_history_user(st.session_state["user_id"])
    
    # Obter dados
    full_history_df = pd.DataFrame(st.session_state['search_history'])
    if not full_history_df.empty:
        if "genre" not in full_history_df.columns:
            full_history_df["genre"] = None
        else:
            full_history_df['genre'] = full_history_df["genre"].fillna('Top 50')
        total_songs = len(full_history_df)
        unique_genres = full_history_df["genre"].nunique()
        unique_artists = full_history_df["artist"].nunique()
        unique_songs = full_history_df["song"].nunique()
    else:
        st.markdown("### 🎵 Comece sua jornada musical!")
        st.info("Você ainda não tem histórico de músicas. Explore nossa plataforma para ver suas estatísticas aqui!")
        return

    # Header principal
    st.markdown('<h1 >🎵 Dashboard Musical Personalizado</h1>', unsafe_allow_html=True)
    
    
    # Métricas principais em cards modernos
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h2 style="color: #1f77b4; margin: 0;">🎵</h2>
            <h3 style="margin: 0.5rem 0;">{total_songs}</h3>
            <p style="margin: 0; opacity: 0.7;">Músicas Ouvidas</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h2 style="color: #ff7f0e; margin: 0;">🎸</h2>
            <h3 style="margin: 0.5rem 0;">{unique_artists}</h3>
            <p style="margin: 0; opacity: 0.7;">Artistas Únicos</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <h2 style="color: #2ca02c; margin: 0;">🎼</h2>
            <h3 style="margin: 0.5rem 0;">{unique_genres}</h3>
            <p style="margin: 0; opacity: 0.7;">Gêneros Explorados</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        diversity_score = (unique_songs / total_songs * 100) if total_songs > 0 else 0
        st.markdown(f"""
        <div class="metric-card">
            <h2 style="color: #d62728; margin: 0;">🌟</h2>
            <h3 style="margin: 0.5rem 0;">{diversity_score:.1f}%</h3>
            <p style="margin: 0; opacity: 0.7;">Diversidade</p>
        </div>
        """, unsafe_allow_html=True)

    # Banner publicitário principal
    st.markdown("""
    <div class="ad-banner">
        <h3></h3>
        <p></p>
    </div>
    """, unsafe_allow_html=True)

    # Layout principal com sidebar
    main_col, sidebar_col = st.columns([3, 1])
    
    with main_col:
        # Seção de insights personalizados
        st.markdown('<h2 class="section-header">🧠 Seus Insights Musicais</h2>', unsafe_allow_html=True)
        
        insights = create_discovery_insights(full_history_df)
        for insight in insights:
            st.markdown(f"""
            <div class="insight-box">
                <p style="margin: 0; font-weight: 500;">{insight}</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Gráficos principais
        chart_col1, chart_col2 = st.columns(2)
        
        with chart_col1:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.markdown('<h3 class="section-header">🎵 Suas Músicas Favoritas</h3>', unsafe_allow_html=True)
            create_enhanced_wordcloud(full_history_df, "song")
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.markdown('<h3 class="section-header">📊 Top Músicas</h3>', unsafe_allow_html=True)
            create_modern_barchart(full_history_df, "song", "#335e7e")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with chart_col2:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.markdown('<h3 class="section-header">🎤 Seus Artistas Favoritos</h3>', unsafe_allow_html=True)
            create_enhanced_wordcloud(full_history_df, 'artist')
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.markdown('<h3 class="section-header">🌟 Top Artistas</h3>', unsafe_allow_html=True)
            create_modern_barchart(full_history_df, "artist", "#1e7069")
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Gráficos de linha completa
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<h3 class="section-header">🎼 Mapa de Gêneros Musicais</h3>', unsafe_allow_html=True)
        create_enhanced_treemap(full_history_df)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Timeline e análise temporal
        timeline_col1, timeline_col2 = st.columns(2)
        
        fuso_brasil = pytz.timezone("America/Sao_Paulo")
        
        with timeline_col1:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.markdown('<h3 class="section-header">⏰ Padrão de Escuta</h3>', unsafe_allow_html=True)
            fig_timeline = create_listening_timeline(full_history_df.copy(), fuso_brasil)
            st.plotly_chart(fig_timeline, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with timeline_col2:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.markdown('<h3 class="section-header">🎨 Distribuição de Gêneros</h3>', unsafe_allow_html=True)
            fig_donut = create_genre_donut(full_history_df)
            st.plotly_chart(fig_donut, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Evolução temporal
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<h3 class="section-header">📈 Evolução das Suas Descobertas</h3>', unsafe_allow_html=True)
        
        full_history_df['datetime'] = pd.to_datetime(full_history_df['timestamp'], unit='s')\
            .dt.tz_localize('UTC')\
            .dt.tz_convert(fuso_brasil)

        df_diario = (full_history_df.set_index('datetime')
                    .resample('D')
                    .size()
                    .reset_index(name='Reproduções'))

        df_diario['Data'] = df_diario['datetime'].dt.strftime('%d/%m')

        fig = px.area(
            df_diario,
            x='Data',
            y='Reproduções',
            labels={'Data': 'Dia', 'Reproduções': 'Reproduções'},
            color_discrete_sequence=['#1f77b4']
        )

        fig.update_layout(
            height=350,
            margin=dict(t=20, b=20, l=10, r=10),
            xaxis_title=None,
            yaxis_title="Reproduções",
            showlegend=False,
            hovermode='x unified',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )

        fig.update_traces(
            line_color='#1f77b4',
            fill='tozeroy',
            hovertemplate='Dia: %{x}<br>Reproduções: %{y}<extra></extra>'
        )

        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with sidebar_col:

            # Card de destaque
        top_song = full_history_df['song'].value_counts().index[0] if len(full_history_df) > 0 else "Nenhuma"
        st.markdown(f"""
        <div class="highlight-card">
            <h4>🏆 Sua Música #1</h4>
            <p style="font-size: 1.1rem; font-weight: bold;">{top_song}</p>
            <p>Você não se cansa dessa!</p>
        </div>
        """, unsafe_allow_html=True)

        # Anúncio lateral
        st.markdown("""
        <div class="ad-sidebar" style="background: linear-gradient(135deg, #667eea, #764ba2); color: white; border: none;">
            <h4></h4>
            <h4></h4>
            <h4></h4>
            <p style="font-size: 0.9rem;"></p>
        </div>
        """, unsafe_allow_html=True)
        

        
        # Progresso de descoberta
        st.markdown("### 🎯 Metas de Descoberta")
        
        goals = [
            {"name": "Artistas", "current": unique_artists, "target": 50},
            {"name": "Gêneros", "current": unique_genres, "target": 15},
            {"name": "Músicas", "current": unique_songs, "target": 200}
        ]
        
        for goal in goals:
            progress = min(goal["current"] / goal["target"] * 100, 100)
            st.markdown(f"""
            <div style="margin-bottom: 1rem;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 0.2rem;">
                    <span>{goal["name"]}</span>
                    <span>{goal["current"]}/{goal["target"]}</span>
                </div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {progress}%"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Anúncio final
        st.markdown("""
        <div class="ad-sidebar" style="background: linear-gradient(135deg, #667eea, #764ba2); color: white; border: none;">
            <h4></h4>
            <h4></h4>
            <h4></h4>
            <p style="font-size: 0.9rem;"></p>
        </div>
        """, unsafe_allow_html=True)

    # Footer com informações adicionais
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #6c757d; padding: 2rem;">
        <p>📊 Dashboard atualizado em tempo real | 🔄 Última atualização: agora</p>
        <p>💡 <strong>Dica:</strong> Continue explorando música para obter insights ainda melhores!</p>
    </div>
    """, unsafe_allow_html=True)