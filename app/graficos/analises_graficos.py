import pandas as pd

from app.graficos.config_graficos import obter_configuracao
from app.graficos.dados_graficos import localizar_coluna
from app.graficos.gerar_graficos import grafico_por_dados

def obter_pergunta(numero):
    perguntas = obter_configuracao("dashboard")["perguntas"]
    return next((pergunta for pergunta in perguntas if pergunta["numero"] == numero), None)

def tabela_cruzamento(dados, numero_1, numero_2):
    # Cria uma tabela que cruza as duas perguntas 
    coluna_1 = localizar_coluna(dados, numero_1)
    coluna_2 = localizar_coluna(dados, numero_2)

    pergunta_1 = obter_pergunta(numero_1)
    pergunta_2 = obter_pergunta(numero_2)

    if (coluna_1 is None or coluna_2 is None or pergunta_1 is None or pergunta_2 is None):
        return pd.DataFrame()

    base = dados[[coluna_1, coluna_2]].copy()
    base.columns = ["resposta_1", "resposta_2"]

    for coluna in ("resposta_1", "resposta_2"):
        base[coluna] = base[coluna].astype(str).str.strip()

    base = base[
        base["resposta_1"].ne("")
        & base["resposta_2"].ne("")
    ]

    if pergunta_1.get("multipla", False):
        base["resposta_1"] = base["resposta_1"].str.split(";")
        base = base.explode("resposta_1")
        base["resposta_1"] = base["resposta_1"].str.strip()

    if pergunta_2.get("multipla", False):
        base["resposta_2"] = base["resposta_2"].str.split(";")
        base = base.explode("resposta_2")
        base["resposta_2"] = base["resposta_2"].str.strip()

    base = base[
        base["resposta_1"].ne("")
        & base["resposta_2"].ne("")
    ]

    if base.empty:
        return pd.DataFrame()

    return pd.crosstab(base["resposta_1"], base["resposta_2"])

def grafico_cruzamento(dados, cruzamento, *, mostrar_legenda=None, altura=None):
    numero_1 = cruzamento["pergunta_1"]
    numero_2 = cruzamento["pergunta_2"]

    tabela = tabela_cruzamento(dados, numero_1, numero_2)

    #Isa - Se precisar editar adicionar titulos, é abaixo
    return grafico_por_dados(
        tabela,
        cruzamento["tipo"],
        None,
        # titulo_eixo_x=" O que voce quiser, se quiser",
        # titulo_eixo_y="valor se voce quiser",
        mostrar_legenda=mostrar_legenda,
        altura=altura,
    )
