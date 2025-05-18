import pandas as pd
import sources
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.metrics.pairwise import cosine_similarity


def load_docs():
    documentos = sources.load_all_history()
    todos_documentos = [doc for doc in documentos]
    return todos_documentos # lista com todos documentos


def colect_user_genres():
    todos_documentos = load_docs()
    df = pd.DataFrame(todos_documentos)
    df = df.drop(['_id', 'musicas_escolhidas'], axis=1)
    df = df[['user_id','generos_escolhidos']]
    df.index = df['user_id'].astype(str)
    df.drop('user_id', axis=1, inplace=True)
    return df


def recomendar_generos_por_user(id, top_n=6):
    id = str(id)
    df = colect_user_genres()
    mlb = MultiLabelBinarizer()

    # Transforma as listas em colunas binárias
    generos_binarios = pd.DataFrame(mlb.fit_transform(df['generos_escolhidos']),
                                    columns=mlb.classes_,
                                    index=df.index)

    # Junta com o DataFrame original
    generos_df = pd.concat([df.drop(columns=['generos_escolhidos']), generos_binarios], axis=1)

    similaridade = cosine_similarity(generos_df)
    similaridade_df = pd.DataFrame(similaridade, index=generos_df.index, columns=generos_df.index)

    top_ids_similares = similaridade_df[id].drop(id).sort_values(ascending=False).head(10)

    generos_similares = generos_df.loc[top_ids_similares.index]
    generos_similares = generos_similares.sum().sort_values(ascending=False)

    generos_user = [index for index, gender in zip(generos_df.loc[id].index, generos_df.loc[id]) if gender == 1]

    generos_recomendados = [index for index in generos_similares.index if index not in generos_user][:top_n]
    return generos_recomendados


def recomendar_musicas_por_user(id, df_url_musics,  top_k=30, top_ids_similares=5):
    id = str(id)

    todos_documentos = load_docs()
    df = pd.DataFrame(todos_documentos)
    df.index = df['user_id'].astype(str)
    df.drop('user_id', axis=1, inplace=True)
    df_historico = pd.DataFrame(df['historico'])
    df_historico['musicas_ouvidas'] = df_historico.map(lambda x: [f'{song['song'] + ' - ' + song['artist']}' for song in x])

    # define model 
    mlb = MultiLabelBinarizer()
    df_music_matrix = pd.DataFrame(
        mlb.fit_transform(df_historico['musicas_ouvidas']),
        index=df_historico.index,
        columns=mlb.classes_
    )

    # Calculo da similaridade

    similaridade_usuarios = cosine_similarity(df_music_matrix)

    # Junta com o DataFrame original
    similaridade_usuarios_df = pd.DataFrame(similaridade_usuarios, index=df_music_matrix.index, columns=df_music_matrix.index)

    similaridade = cosine_similarity(similaridade_usuarios_df)
    similaridade_df = pd.DataFrame(similaridade, index=df_music_matrix.index, columns=df_music_matrix.index)

    top_ids_similares = similaridade_df[id].drop(id).sort_values(ascending=False).head(5)
    musicas_similares = df_music_matrix.loc[top_ids_similares.index]
    musicas_similares = musicas_similares.sum().sort_values(ascending=False)

    musicas_user = [index for index, musica in zip(df_music_matrix.loc[id].index, df_music_matrix.loc[id]) if musica == 1]
    musicas_recomendadas = [index for index in musicas_similares.index if index not in musicas_user][:top_k]

    musicas_recomendadas = [{'track_name': musicas_recomendadas[i].split(' - ')[0], 'artists': musicas_recomendadas[i].split(' - ')[1]} for i in range(len(musicas_recomendadas))]
    musicas_recomendadas = pd.DataFrame(musicas_recomendadas)
    final_df_musics = pd.merge(musicas_recomendadas, df_url_musics[['track_name', 'artists', 'track_genre', 'cover_url']], how='left', on=['track_name', 'artists'])
    return final_df_musics


if __name__ == '__main__':
    recomendar_generos_por_user()
