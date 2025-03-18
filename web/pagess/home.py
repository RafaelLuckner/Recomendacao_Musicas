import streamlit as st

def show():
    # Título da página inicial
    st.title("🎶 Bem-vindo ao Recomendador de Músicas!")

    # Texto de boas-vindas
    st.write("""
    Bem-vindo à plataforma onde você pode descobrir novas músicas baseadas em seus gostos pessoais.
    Selecione seus gêneros favoritos, receba recomendações e ouça músicas diretamente do YouTube!
    """)
    
    # Seção com imagem de música
    st.image("web/assets/musica.jpg", use_container_width=True)
    # Botões para navegação
    st.subheader("O que você quer fazer?")
    col1, col2 = st.columns(2)

    with col1:
        if st.button("🎧 Começar a explorar recomendações"):
            st.session_state["page"] = "recommendations"
            st.rerun()

    with col2:
        if st.button("🔎 Buscar uma música"):
            st.session_state["page"] = "search"
            st.rerun()

    # Detalhes adicionais sobre a plataforma (opcional)
    st.write("""
    A plataforma é simples e fácil de usar! Você pode:
    - **Receber recomendações personalizadas** de músicas com base nos gêneros que você gosta.
    - **Pesquisar suas músicas favoritas** diretamente do YouTube.
    - **Ouvir e descobrir novas músicas** enquanto navega por seu gosto musical.

    **Divirta-se explorando músicas e criando sua playlist personalizada!**
    """)

