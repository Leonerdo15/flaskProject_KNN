import numpy as np
import pandas as pd


def get_notas():
    # print(pd.read_csv("http://localhost:5000/spotsEvaluations.csv"))
    return pd.read_csv("http://localhost:5000/spotsEvaluations.csv")


def distancia_vetores(a, b):
    return np.linalg.norm(a - b) / len(a)


def notas_do_usuario(usuario):
    salvar_notas_do_usuario = get_notas().query(f"usuarioId == {usuario}")
    salvar_notas_do_usuario = salvar_notas_do_usuario[["filmeId", "nota"]].set_index("filmeId")
    return salvar_notas_do_usuario


def distancia_de_usuarios(user1, user2, minimo=0):
    notas1 = notas_do_usuario(user1)
    notas2 = notas_do_usuario(user2)
    juncao = notas1.join(notas2, lsuffix="_esquerda", rsuffix="_direita").dropna()

    if len(juncao) < minimo:
        return None

    distancia = distancia_vetores(juncao["nota_esquerda"], juncao["nota_direita"])
    return [user1, user2, distancia]


def distancia_de_todos(voce_id, n=None):
    todos_os_usuarios = get_notas().usuarioId.unique()
    if n:
        todos_os_usuarios = todos_os_usuarios[:n]
    distancias = [distancia_de_usuarios(voce_id, usuariosId) for usuariosId in todos_os_usuarios]
    distancias = list(filter(None, distancias))
    distancias = pd.DataFrame(distancias, columns=["voce", "outra_pessoa", "distancia"])
    return distancias


def knn(voce_id, k_mais_proximos=10, n=None):
    distancias = distancia_de_todos(voce_id, n=n)
    distancias = distancias.sort_values("distancia")
    distancias = distancias.set_index("outra_pessoa").drop(voce_id, errors='ignore')
    return distancias.head(k_mais_proximos)


def sugere_para(voce, k_mais_proximos=10, n=None):
    notas_de_voce = notas_do_usuario(voce)
    filmes_que_voce_ja_viu = notas_de_voce.index

    similares = knn(voce, k_mais_proximos=k_mais_proximos, n=n)
    usuarios_similares = similares.index
    notas_dos_similares = get_notas().set_index("usuarioId").loc[usuarios_similares]
    recomendacoes = notas_dos_similares.groupby("filmeId").mean()[["nota"]]
    aparicoes = notas_dos_similares.groupby("filmeId").count()[['nota']]

    recomendacoes = recomendacoes.join(aparicoes, lsuffix="_media_dos_usuarios", rsuffix="_aparicoes_nos_usuarios")
    recomendacoes = recomendacoes.sort_values("nota_media_dos_usuarios", ascending=False)
    recomendacoes = recomendacoes.drop(filmes_que_voce_ja_viu, errors='ignore')

    filmes = pd.read_csv("http://localhost:5000/spots.csv")
    filmes.columns = ["filmeId", "titulo", "generos"]
    filmes = filmes.set_index("filmeId")
    return recomendacoes.join(filmes)


if __name__ == '__main__':
    # print("Notas de 2:")
    # print(notas_do_usuario(2))
    # print("Notas de 1:")
    # print(notas_do_usuario(1))
    # print("Distancia entre 1 e 2:")
    # print(distancia_de_usuarios(1, 2))
    print(sugere_para(2).to_string())
