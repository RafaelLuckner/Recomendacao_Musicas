# Sistema de Recomendação de Músicas

Este projeto desenvolve um sistema de recomendação de músicas utilizando técnicas de **Machine Learning** para sugerir faixas personalizadas para os usuários, baseando-se em seu histórico de interação e preferências de gênero/artista.

## Objetivo

- Implementar um sistema de recomendação baseado no histórico de interações e preferências dos usuários.
- Utilizar dados públicos como o  **Spotify Tracks Dataset**.

## Tecnologias

- **Python**
- **Pandas** (manipulação de dados)
- **Scikit-Learn** (modelos de Machine Learning)
- **Streamlit** (interface web)
- **MongoDB** (armazenamento e gestão dos dados)

## Funcionalidades

- Recomendações personalizadas com base no histórico do usuário.
- Interface simples para exibir as recomendações.

## Não Está no Escopo

- Processamento direto de arquivos de áudio.
- Sistema de recomendação em tempo real.
- Integração com plataformas como Spotify ou YouTube.
- Desenvolvimento de aplicativos móveis ou desktop.

## Estrutura de Pastas
```
/meu-projeto
    /docs                 # Documentação do projeto
        - TAP.docx
        - Definicao_Projeto.docx

    /src                  # Código fonte do projeto
        /db                    # Interação com o banco de dados
            - database.py       # Conexões e consultas ao banco de dados
        /ml                     # Modelos de Machine Learning
            - modelo_recomendacao.py  # Algoritmo de recomendação
        /utils                  # Funções auxiliares
            - helpers.py        # Funções utilitárias como pré-processamento de dados
        /api                    # API 
            - app.py            # Definir endpoints e lógica de interação

    /data                 # Dados para o treinamento do modelo
        - data.csv

    /web                  # Interface web (utilizando Streamlit)
        - app.py
        /assets           # Pasta para imagens, ícones e outros arquivos estáticos
            - musica.png
        /pages            # Páginas do aplicativo
            - home.py
            - recomendacoes.py

    requirements.txt      # Dependências do projeto


```