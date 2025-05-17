# M4U - Music For You
## Visão Geral
M4U - Music For You é uma aplicação web desenvolvida com Streamlit que utiliza técnicas de Machine Learning para oferecer um sistema de recomendação de músicas personalizado. O projeto analisa o histórico de interações, preferências de gênero e artistas dos usuários, além de recomendar faixas com base em conteúdo, sugerindo músicas alinhadas aos seus gostos a partir de dados públicos.

## Objetivo
- Criar um sistema de recomendação que combine histórico de escuta, preferências de usuários e análise de conteúdo para sugerir músicas personalizadas.
- Fornecer uma interface visual intuitiva para exibir estatísticas de escuta e recomendações de músicas.

## Tecnologias
- **Python**: Linguagem principal de desenvolvimento.
- **Pandas**: Manipulação e análise de dados.
- **Scikit-Learn**: Modelos de Machine Learning para recomendações.
- **Streamlit**: Interface web interativa.
- **MongoDB**: Armazenamento e gestão de dados dos usuários.


## Telas e Componentes
- **Tela de Login**: Interface com campos para e-mail e senha, estilizada com o logotipo M4U, incluindo opções de cadastro e recuperação de senha.  
    <img src="img/tela_login.png" width="800" height="auto" />

- **Tela de Boas-Vindas**: Apresenta um texto introdutório sobre o sistema de recomendações.  
    <img src="img/tela_bem_vindo.png" width="800" height="auto" />

- **Tela de Recomendações**: Mostra um carrossel de músicas sugeridas com capas de álbuns, filtradas por gênero.  
    <img src="img/tela_pra_voce.png" width="800" height="auto" />

- **Tela de Gêneros**: Exibe gêneros selecionados e recomendações por gênero em um carrossel.  
    <img src="img/tela_generos.png" width="800" height="auto" />

- **Tela de Histórico de Pesquisas**: Exibe todas as músicas pesquisadas e avaliações realizadas.

    <img src="img/tela_historico.png" width="800" height="auto" />

- **Tela Dashboard**: Exibe gráficos e estatísticas gerais sobre seu histórico.  
    <img src="img/dashboard.png" width="800" height="auto" />

- **Tela do Reprodutor do YouTube**: Apresenta uma janela de reprodução com a música atual diretamente do YouTube, com controle de avaliação e exibição das músicas mais ouvidas no Brasil e no mundo. Inclui redirecionamento para Deezer e Spotify, além de um carrossel de recomendações baseado em conteúdo na parte inferior, permitindo ouvir músicas personalizadas sem interrupção.  
<img src="img/tela_pesquisar.png" width="800" height="auto" />


## Como as Recomendações São Feitas
...

## Estrutura de Pastas

```
/m4u-streamlit
    /docs                           # Documentação do projeto
        - TAP.docx
        - Definicao_Projeto.docx

    /src                  # Código fonte do projeto
        /ml                     # Modelos de Machine Learning
            - modelo_recomendacao.py  # Algoritmo de recomendação
        /utils                  # Funções auxiliares
            - helpers.py        # Pré-processamento de dados

    /data                 # Dados para treinamento
        - data.csv            # Dataset base (Spotify Tracks)

    /web                  # Interface web (Streamlit)
        - app.py
        /assets           # Arquivos estáticos
            - musica.png
        /pages            # Páginas do aplicativo
            - home.py
            - recomendacoes.py

    requirements.txt      # Dependências do projeto


```