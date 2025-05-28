import streamlit as st
import pandas as pd
import plotly.express as px
import sources
from sources import search_user_id_mongodb

def switch_page(page_name):
    st.session_state["page"] = page_name
    params = {"page": page_name}
    if "email" in st.session_state:
        params["email"] = st.session_state["email"]
    if 'name' not in st.session_state:
        st.session_state["name"] = search_user_id_mongodb(st.session_state["email"])
    st.query_params.update(params)
    st.rerun()

def get_user_stats():
    """Coleta estatísticas reais do usuário"""
    try:
        # Verificar e obter user_id
        if 'user_id' not in st.session_state or st.session_state.get("user_id") is None:
            if "email" in st.session_state:
                user_id = sources.search_user_id_mongodb(st.session_state["email"])
                st.session_state["user_id"] = user_id
            else:
                return {
                    "total_songs": 0,
                    "unique_artists": 0,
                    "unique_genres": 0,
                    "top_song": "Nenhuma",
                    "top_artist": "Nenhum",
                    "has_data": False,
                    "error": "Email não encontrado"
                }
        
        # Obter histórico de pesquisas
        if "search_history" not in st.session_state or not st.session_state["search_history"]:
            st.session_state["search_history"] = sources.search_history_user(st.session_state["user_id"])
        
        # Sempre atualizar o histórico
        search_history = sources.search_history_user(st.session_state["user_id"])
        st.session_state["search_history"] = search_history
        
        # Verificar se há dados
        if not search_history or len(search_history) == 0:
            return {
                "total_songs": 0,
                "unique_artists": 0,
                "unique_genres": 0,
                "top_song": "Nenhuma música ainda",
                "top_artist": "Nenhum artista ainda",
                "has_data": False
            }
        
        # Converter para DataFrame
        full_history_df = pd.DataFrame(search_history)
        
        # Garantir que as colunas existem
        required_columns = ['song', 'artist', 'genre']
        for col in required_columns:
            if col not in full_history_df.columns:
                full_history_df[col] = "Desconhecido"
        
        # Limpar dados None/NaN
        full_history_df['genre'] = full_history_df['genre'].fillna('Top 50')
        full_history_df['artist'] = full_history_df['artist'].fillna('Artista Desconhecido')
        full_history_df['song'] = full_history_df['song'].fillna('Música Desconhecida')
        
        # Calcular estatísticas
        total_songs = len(full_history_df)
        unique_artists = full_history_df['artist'].nunique()
        unique_genres = full_history_df['genre'].nunique()
        
        # Top música e artista (mais seguros)
        song_counts = full_history_df['song'].value_counts()
        artist_counts = full_history_df['artist'].value_counts()
        
        top_song = song_counts.index[0] if len(song_counts) > 0 else "Nenhuma música"
        top_artist = artist_counts.index[0] if len(artist_counts) > 0 else "Nenhum artista"
        
        return {
            "total_songs": total_songs,
            "unique_artists": unique_artists,
            "unique_genres": unique_genres,
            "top_song": top_song,
            "top_artist": top_artist,
            "has_data": True,
            "dataframe": full_history_df
        }
        
    except Exception as e:
        st.error(f"Erro ao carregar estatísticas: {str(e)}")
        return {
            "total_songs": 0,
            "unique_artists": 0,
            "unique_genres": 0,
            "top_song": "Erro ao carregar",
            "top_artist": "Erro ao carregar",
            "has_data": False,
            "error": str(e)
        }

def create_mini_chart(df, column, chart_type="bar"):
    """Cria gráficos pequenos para a sidebar"""
    try:
        if df is None or df.empty or column not in df.columns:
            return None
        
        # Limpar dados nulos/vazios
        clean_data = df[column].dropna()
        if clean_data.empty:
            return None
            
        data = clean_data.value_counts().head(5)
        
        if len(data) == 0:
            return None
        
        if chart_type == "bar":
            fig = px.bar(
                x=data.values,
                y=data.index,
                orientation='h',
                color_discrete_sequence=["#667eea"]
            )
            fig.update_layout(
                height=200,
                margin=dict(l=0, r=0, t=0, b=0),
                showlegend=False,
                xaxis={'visible': False},
                yaxis={'title': None},
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            fig.update_traces(textposition='inside', textfont_size=10)
            return fig
        
        elif chart_type == "pie":
            fig = px.pie(values=data.values, names=data.index, color_discrete_sequence=px.colors.qualitative.Set3)
            fig.update_layout(
                height=200,
                margin=dict(l=0, r=0, t=0, b=0),
                showlegend=False
            )
            fig.update_traces(textinfo='percent', textfont_size=10)
            return fig
            
    except Exception as e:
        st.error(f"Erro ao criar gráfico: {str(e)}")
        return None

def show():
    # Obter estatísticas do usuário
    user_stats = get_user_stats()
    
    # CSS personalizado para estilização
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
    
    .welcome-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
    }
    
    .feature-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #667eea;
        margin-bottom: 1rem;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    
    .stats-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        color: white;
        margin-bottom: 1rem;
    }
    
    .ad-space {
        background: #f8f9fa;
        border: 2px dashed #dee2e6;
        border-radius: 10px;
        padding: 2rem;
        text-align: center;
        color: #6c757d;
        margin-bottom: 2rem;
    }
    
    .action-button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 1rem 2rem;
        border-radius: 10px;
        font-weight: bold;
        width: 100%;
        margin-bottom: 1rem;
        transition: transform 0.2s;
    }
    
    .action-button:hover {
        transform: translateY(-2px);
    }
    </style>
    """, unsafe_allow_html=True)
    
    
    # Header principal
    st.markdown('<h1 >🎶 Recomendador de Músicas</h1>', unsafe_allow_html=True)
    
    # Buscar nome do usuário se não existir
    if 'name' not in st.session_state:
        st.session_state["name"] = search_user_id_mongodb(st.session_state["email"], name=True)
    
    # Layout principal com 3 colunas
    col_main, col_sidebar = st.columns([2, 1])
    
    with col_main:
        # Card de boas-vindas
        st.markdown(f"""
        <div class="welcome-card">
            <h2>👋 Bem-vindo(a), {st.session_state["name"].capitalize()}!</h2>
            <p>Descubra novas músicas baseadas em seus gostos pessoais. 
            Explore gêneros, receba recomendações inteligentes e ouça suas descobertas diretamente do YouTube!</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Imagem principal
        st.image("web/assets/musica.jpg", 
                caption="🎵 Sua jornada musical começa aqui!", 
                use_container_width=True)
        
        # Seção de ações principais
        st.markdown("### 🚀 O que você quer fazer hoje?")
        
        action_col1, action_col2 = st.columns(2)
        
        with action_col1:
            if st.button("🎧 Descobrir Músicas", 
                        help="Receba recomendações personalizadas baseadas em seus gostos",
                        use_container_width=True):
                switch_page("recommendations")
                
        with action_col2:
            if st.button("🔍 Pesquisar Músicas", 
                        help="Busque por suas músicas favoritas diretamente",
                        use_container_width=True):
                switch_page("busca")
        
        # Cards de funcionalidades com dados dinâmicos
        st.markdown("""
            <style>
            .feature-card {
                background-color: var(--background-color);  /* cor do tema */
                border: 1px solid var(--secondary-background-color);  /* contorno discreto */
                border-radius: 10px;
                padding: 15px;
                margin-bottom: 15px;
            }
            .feature-card h4 {
                margin-top: 0;
                color: var(--text-color);
            }
            .feature-card p {
                margin-bottom: 0;
                color: var(--text-color);
            }
            </style>
        """, unsafe_allow_html=True)
        
        features = [
            {
                "icon": "🎯",
                "title": "Recomendações Personalizadas",
                "description": f"Algoritmo inteligente baseado em {user_stats['unique_genres']} gêneros que você já explorou" if user_stats['has_data'] else "Algoritmo inteligente que aprende com seus gostos musicais"
            },
            {
                "icon": "🔍",
                "title": "Busca Avançada",
                "description": "Encontre qualquer música ou artista rapidamente"
            },
            {
                "icon": "▶️",
                "title": "Reprodução Direta",
                "description": "Ouça músicas diretamente do YouTube sem sair da plataforma"
            },
            {
                "icon": "📈",
                "title": "Dashboard Inteligente",
                "description": f"Acompanhe suas {user_stats['total_songs']} músicas e {user_stats['unique_artists']} artistas favoritos" if user_stats['has_data'] else "Acompanhe suas músicas e artistas mais ouvidos"
            }
        ]
        
        for feature in features:
            st.markdown(f"""
            <div class="feature-card">
                <h4>{feature["icon"]} {feature["title"]}</h4>
                <p>{feature["description"]}</p>
            </div>
            """, unsafe_allow_html=True)
    
    with col_sidebar:
        st.markdown("""
        <div class="ad-sidebar" style="background: linear-gradient(135deg, #667eea, #764ba2); border-radius: 15px;">
            <h4></h4>
            <h2></h2>
            <h4></h4>
            <h2></h2>
            <p style="font-size: 0.9rem;"></p>
        </div>
        """, unsafe_allow_html=True)
        
        # Cards de estatísticas
        st.markdown("### 📊 Suas Estatísticas")
        
        # Exemplo de estatísticas (substitua pelos dados reais)
        st.markdown(f"""
        <div class="stats-card">
            <h3>🎵</h3>
            <h4>{user_stats['total_songs']}</h4>
            <p>Músicas Descobertas</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="stats-card">
            <h3>🎸</h3>
            <h4>{user_stats['unique_artists']}</h4>
            <p>Artistas Descobertos</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="stats-card">
            <h3>🎼</h3>
            <h4>{user_stats['unique_genres']}</h4>
            <p>Gêneros Ouvidos</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Card de dicas dinâmicas
        with st.container():
            st.markdown("### 💡 Dica Personalizada")
            
            # Dicas baseadas no histórico do usuário
            if user_stats["has_data"]:
                if user_stats["unique_genres"] < 3:
                    tip = "🎯 Experimente gêneros que você nunca ouviu! Você pode descobrir sua próxima música favorita."
                elif user_stats["total_songs"] > 100:
                    tip = "🏆 Parabéns! Você já explorou muitas músicas. Que tal conferir o seu dashboard completo?"
                else:
                    tip = "📈 Continue explorando! Cada música que você ouve nos ajuda a melhorar suas recomendações."
            else:
                tip = "🌟 Bem-vindo! Comece descobrindo músicas personalizadas para você."
            
            st.info(tip)
        
        # Ação rápida baseada no perfil
        if user_stats["has_data"] and user_stats["total_songs"] > 1:
            if st.button("📊 Ver Dashboard Completo", use_container_width=True):
                switch_page("dashboard")
        
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #6c757d; padding: 2rem;">
        <p>🎶 <strong>Recomendador de Músicas</strong> - Sua trilha sonora perfeita te espera!</p>
        <p>Desenvolvido com ❤️ para amantes da música</p>
    </div>
    """, unsafe_allow_html=True)