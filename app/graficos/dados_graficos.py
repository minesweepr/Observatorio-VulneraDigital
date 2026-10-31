from pathlib import Path
from io import BytesIO
from vercel.blob import sync as blob
import re
import pandas as pd

CAMINHO_CSV = "dados/respostas.csv"
_cache = {}

def carregar_dados(caminho=CAMINHO_CSV):
    # consulta os metadados do etag pra verificar se o arquivo mudou sem precisar baixar
    modificacao=blob.head_blob(caminho).etag

    cache = _cache.get(caminho)
    if cache and cache["modificacao"] == modificacao:
        return cache["dados"].copy()

    original = pd.read_csv( BytesIO(blob.get_blob(caminho, access="private").body), dtype=str, keep_default_na=False, encoding="utf-8-sig", )

    colunas = {}

    for coluna in original.columns:
        nome = str(coluna).strip()

        if nome.lower() == "carimbo de data/hora":
            colunas[coluna] = "data_resposta"
            continue

        resultado = re.match(r"^\s*(\d+)\s*[.)-]", nome)

        if resultado:
            colunas[coluna] = f"Q{resultado.group(1)}"

    dados = original.rename(columns=colunas)
    dados = dados.loc[:, ~dados.columns.duplicated()].copy()

    for coluna in dados.columns:
        dados[coluna] = dados[coluna].astype(str).str.strip()

    _cache[caminho] = { "modificacao": modificacao, "dados": dados, }

    return dados.copy()


def localizar_coluna(dados, numero):
    coluna = f"Q{numero}"
    return coluna if coluna in dados.columns else None

def contar_respostas(dados, numero, multipla=False):
    coluna = localizar_coluna(dados, numero)

    if coluna is None:
        return pd.Series(dtype="int64")

    respostas = dados[coluna].astype(str).str.strip()
    respostas = respostas[respostas.ne("")]

    if multipla:
        respostas = respostas.str.split(";").explode().str.strip()
        respostas = respostas[respostas.ne("")]

    return respostas.value_counts()