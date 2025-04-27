import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import NearestNeighbors

df = pd.read_csv('data/data_traduct_clean.csv', index_col=0)

colunas_para_modelo = [
    'danceability', 'energy', 'key', 'loudness', 'mode', 'speechiness',
    'acousticness', 'instrumentalness', 'valence', 'tempo', 'duration_ms'
]

X = df[colunas_para_modelo]

X_scaled = pd.DataFrame(StandardScaler().fit_transform(X), columns=colunas_para_modelo)

modelo_knn = NearestNeighbors(metric='cosine', algorithm='brute')
modelo_knn.fit(X_scaled)

def encontrar_idx_por_input(input_usuario):
    input_usuario = input_usuario.lower()
    
    # Primeiro, tenta encontrar onde tanto música quanto artista batem
    mask_track = df['track_name'].str.lower().apply(lambda x: x in input_usuario)
    mask_artist = df['artists'].str.lower().apply(lambda x: any(artist in input_usuario for artist in x.split(';')))

    combinacao = df[mask_track & mask_artist]
    if not combinacao.empty:
        return combinacao.index[0]
    
    # Se não achar, tenta só pela música
    apenas_musica = df[mask_track]
    if not apenas_musica.empty:
        return apenas_musica.index[0]
    
    # Se ainda não achar, tenta só pelo artista
    apenas_artista = df[mask_artist]
    if not apenas_artista.empty:
        return apenas_artista.index[0]

    return None # Se não encontrar nada

def recomendar_musicas(track_index, n_recomendacoes=10, mesmo_genero=False,
                        generos_favoritos=None, peso_genero=0.75):
    if mesmo_genero:
        genero = df.loc[track_index, 'track_genre']
        filtro_genero = df['track_genre'] == genero
        df_filtrado = df[filtro_genero]
        X_filtrado = X_scaled[filtro_genero]

        idx_relativo = df_filtrado.index.get_loc(track_index)

        modelo_knn.fit(X_filtrado)

        distancias, indices = modelo_knn.kneighbors(X_filtrado.iloc[[idx_relativo]], n_neighbors=n_recomendacoes + 1)
        recomendacoes = df_filtrado.iloc[indices[0][1:]].copy() # Exclui a própria música
        recomendacoes['similaridade'] = 1 - distancias[0][1:]
        
    else:
        distancias, indices = modelo_knn.kneighbors(X_scaled.iloc[[track_index]], n_neighbors=X_scaled.shape[0])
        recomendacoes = df.iloc[indices[0]].copy()
        recomendacoes['similaridade'] = 1 - distancias[0]
        
        # Excluir a própria música (primeira linha)
        recomendacoes = recomendacoes.iloc[1:]
    
    # Se o usuário quer ajustar pela afinidade de gêneros
    if generos_favoritos:
        recomendacoes['ajuste_genero'] = recomendacoes['track_genre'].apply(
            lambda x: 1 + peso_genero if any(genero.lower() in x.lower() for genero in generos_favoritos) else 1
        )
        recomendacoes['similaridade_ajustada'] = recomendacoes['similaridade'] * recomendacoes['ajuste_genero']
        recomendacoes = recomendacoes.sort_values(by='similaridade_ajustada', ascending=False)
        return recomendacoes[['track_name', 'artists', 'track_genre', 'similaridade_ajustada']].head(n_recomendacoes)
    
    else:
        # Sem ajuste de gênero
        recomendacoes = recomendacoes.sort_values(by='similaridade', ascending=False)
        return recomendacoes[['track_name', 'artists', 'track_genre', 'similaridade']].head(n_recomendacoes)

# recomendação por nome e artista
def recomendar_musicas_input(input_usuario, n_recomendacoes=10, mesmo_genero=False,
                             generos_favoritos=None, peso_genero=0.075):
    # Encontrar o índice da música correspondente ao input do usuário
    idx = encontrar_idx_por_input(input_usuario)
    
    if idx is None:
        raise ValueError("Música não encontrada no dataset.")
    
    # Caso contrário, usa a recomendação normal
    return recomendar_musicas(idx, n_recomendacoes, mesmo_genero,
                              generos_favoritos, peso_genero)