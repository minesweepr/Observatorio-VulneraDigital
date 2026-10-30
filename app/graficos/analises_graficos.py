import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from app.graficos.config_graficos import obter_configuracao, PALETA
from app.graficos.dados_graficos import localizar_coluna
from app.graficos.gerar_graficos import grafico_por_dados
TIPOS_HORIZONTAIS = ("barh", "barh_100")
def obter_pergunta(numero):
    perguntas = obter_configuracao("dashboard")["perguntas"]
    return next( (pergunta for pergunta in perguntas if pergunta["numero"] == numero), None)

def tabela_cruzamento(dados, numero_1, numero_2):
    coluna_1 = localizar_coluna(dados, numero_1)
    coluna_2 = localizar_coluna(dados, numero_2)

    pergunta_1 = obter_pergunta(numero_1)
    pergunta_2 = obter_pergunta(numero_2)

    if ( coluna_1 is None or coluna_2 is None or pergunta_1 is None or pergunta_2 is None ):
        return pd.DataFrame()

    base = dados[[coluna_1, coluna_2]].copy()
    base.columns = ["resposta_1", "resposta_2"]

    for coluna in ("resposta_1", "resposta_2"):
        base[coluna] = base[coluna].fillna("").astype(str).str.strip()

    base = base[base["resposta_1"].ne("") & base["resposta_2"].ne("")]

    if pergunta_1.get("multipla", False):
        base["resposta_1"] = base["resposta_1"].str.split(";")
        base = base.explode("resposta_1")
        base["resposta_1"] = base["resposta_1"].str.strip()

    if pergunta_2.get("multipla", False):
        base["resposta_2"] = base["resposta_2"].str.split(";")
        base = base.explode("resposta_2")
        base["resposta_2"] = base["resposta_2"].str.strip()

    base = base[base["resposta_1"].ne("") & base["resposta_2"].ne("")]

    if base.empty:
        return pd.DataFrame()

    return pd.crosstab(base["resposta_1"], base["resposta_2"])

def grafico_cruzamento(dados, cruzamento, *, mostrar_legenda=None, altura=None):
    numero_1 = cruzamento["pergunta_1"]
    numero_2 = cruzamento["pergunta_2"]
    tipo = cruzamento["tipo"]
    numero_separacao = cruzamento.get("separar_por")
    valores_separacao = cruzamento.get("valores_separacao")
    if numero_separacao is None or not valores_separacao:
        tabela = tabela_cruzamento(dados, numero_1, numero_2)
        quantidade_categorias = len(tabela.index)

        if tipo in TIPOS_HORIZONTAIS:
            altura_grafico = altura or max( 450, min(1200, 250 + quantidade_categorias * 45) )
        else:
            altura_grafico = altura or 450

        return grafico_por_dados( tabela, tipo, None, titulo_eixo_x=None, titulo_eixo_y=None, mostrar_legenda=mostrar_legenda, altura=altura_grafico, barmode=cruzamento.get("barmode"), )

    coluna_separacao = localizar_coluna(dados, numero_separacao)

    if coluna_separacao is None:
        raise ValueError( f"Não foi encontrada a coluna da pergunta {numero_separacao}." )

    quantidade = len(valores_separacao)

    figura = make_subplots( rows=quantidade, cols=1, subplot_titles=valores_separacao, shared_xaxes=False, vertical_spacing=min(0.3, 0.30 / max(quantidade, 1)), )

    for indice, valor_separacao in enumerate(valores_separacao, start=1):
        dados_filtrados = dados[ dados[coluna_separacao] .fillna("") .astype(str) .str.strip() .eq(valor_separacao) ].copy()

        tabela = tabela_cruzamento(dados_filtrados, numero_1, numero_2)

        if tabela.empty:
            figura.add_annotation( text="Nenhuma resposta disponível", x=0.5, y=0.5, xref="x domain", yref="y domain", showarrow=False, row=indice, col=1, )
            continue
        for serie_indice, serie in enumerate(tabela.columns):
            valores = tabela[serie].tolist()
            textos = [str(valor) if valor != 0 else "" for valor in valores]
            cor = PALETA[serie_indice % len(PALETA)]

            if tipo in TIPOS_HORIZONTAIS:
                barra = go.Bar( name=str(serie), x=valores, y=tabela.index.astype(str).tolist(), orientation="h", marker_color=cor, text=textos, textposition="auto", cliponaxis=False, showlegend=(indice == 1), )
            else:
                barra = go.Bar( name=str(serie), x=tabela.index.astype(str).tolist(), y=valores, marker_color=cor, text=textos, textposition="auto", cliponaxis=False, showlegend=(indice == 1), )
            figura.add_trace(barra, row=indice, col=1)
    altura_por_grafico = 300 if tipo in TIPOS_HORIZONTAIS else 350
    altura_final = altura or min(1000, max(450, quantidade * altura_por_grafico))
    figura.update_layout( title_text=None, height=altura_final, barmode=cruzamento.get("barmode", "group"), bargap=0.05, bargroupgap=0.2, showlegend=mostrar_legenda if mostrar_legenda is not None else True, template="plotly_white", autosize=True, margin={"l": 60, "r": 25, "t": 80, "b": 55}, )
    figura.update_xaxes(title_text=None)
    figura.update_yaxes(title_text=None)

    return figura