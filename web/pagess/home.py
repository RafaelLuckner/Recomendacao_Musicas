import streamlit as st


def switch_page(page_name):
    st.session_state["page"] = page_name
    params = {"page": page_name}
    if "email" in st.session_state:
        params["email"] = st.session_state["email"]
    st.query_params.update(params)
    st.rerun()

def show():
    # Título da página inicial
    st.title("🎶 Bem-vindo ao Recomendador de Músicas!")

    if 'name' not in st.session_state:
        st.session_state["name"] = "Usuário" 

    # Texto de boas-vindas
    st.write(f"""
    Bem vindo(a) {st.session_state["name"].capitalize()}!
    Aqui você pode descobrir novas músicas baseadas em seus gostos pessoais.
    Selecione seus gêneros favoritos, receba recomendações e ouça músicas diretamente do YouTube!
    """)
    
    # Seção com imagem de música
    st.image("web/assets/musica.jpg", width=900, )
    # Botões para navegação
    st.subheader("O que você quer fazer?")
    col1, col2 = st.columns([1, 1])

    with col1:


        col3, col4 = st.columns([1, 1])
        with col3:
            if st.button("🎧 Encontre Músicas para Você"):
                switch_page("recommendations")

        with col4:
            if st.button("🔎 Pesquisar Músicas"):
                switch_page("busca")


    with col2:
        pass
    # Detalhes adicionais sobre a plataforma (opcional)
    st.write("""
    A plataforma é simples e fácil de usar! Você pode:
    - **Receber recomendações personalizadas** de músicas com base nos gêneros que você gosta.
    - **Pesquisar suas músicas favoritas** diretamente do YouTube.
    - **Ouvir e descobrir novas músicas** enquanto navega por seu gosto musical.
    - **Acompanhar o seu histórico** e ver quais músicas você costuma ouvir.
    - **Acompanhar suas preferências** e ver quais músicas e artistas você costuma ouvir.
             
     **Divirta-se explorando músicas e seus gêneros favoritos!**
    """)

