import copy
import plotly.graph_objects as go
import pandas as pd

from app.graficos.config_graficos import CONFIG_LAYOUT, CONFIGURACOES_TIPOS, PALETA

def aplicar_layout(figura, titulo=None, *, tipo, quantidade_series=1, altura=None, margem=None, mostrar_legenda=None, fonte=None, fundo=None):
    layout = copy.deepcopy(CONFIG_LAYOUT)
    configuracao_tipo = CONFIGURACOES_TIPOS.get(tipo, {})

    if altura is not None:
        layout["height"] = altura

    if margem is not None:
        layout["margin"].update(margem)

    if fonte is not None:
        layout["font"].update(fonte)

    if fundo is not None:
        layout["paper_bgcolor"] = fundo
        layout["plot_bgcolor"] = fundo

    if mostrar_legenda is not None:
        layout["showlegend"] = mostrar_legenda
    else:
        regra_legenda = configuracao_tipo.get("legenda", "automatica" )

        if regra_legenda == "automatica":
            layout["showlegend"] = quantidade_series > 1
        else:
            layout["showlegend"] = regra_legenda

    figura.update_layout( title={ "text": titulo or "", "x": 0.02, "xanchor": "left", }, colorway=list(PALETA), **layout, )

    return figura

def normalizar_dados(dados):
    if isinstance(dados, pd.Series):
        tabela = dados.to_frame(name="Respostas")
    elif isinstance(dados, pd.DataFrame):
        tabela = dados.copy()
    else:
        tabela = pd.DataFrame(dados)

    tabela.index = tabela.index.map(str)
    tabela.columns = tabela.columns.map(str)

    for coluna in tabela.columns:
        tabela[coluna] = pd.to_numeric(tabela[coluna], errors="coerce" ).fillna(0)

    return tabela.astype(int)


def grafico_por_dados(dados, tipo, titulo=None, *, titulo_eixo_x=None, titulo_eixo_y=None, titulo_legenda=None, altura=None, mostrar_legenda=None, margem=None, fonte=None):
    #Gera os gráficos do dashboard e dos cruzamentos com padrões compartilhados.
    tabela = normalizar_dados(dados)
    tipo = str(tipo).lower()
    figura = go.Figure()

    categorias = tabela.index.tolist()
    series = tabela.columns.tolist()

    if tabela.empty or tabela.size == 0 or tabela.to_numpy().sum() == 0:
        figura.add_annotation(text="Nenhuma resposta disponível", x=0.5, y=0.5, xref="paper", yref="paper", showarrow=False)

    elif tipo in ("barv", "barh"):
        for indice, serie in enumerate(series):
            valores = tabela[serie].tolist()
            cor = PALETA[indice % len(PALETA)]

            cores = (
                [PALETA[i % len(PALETA)] for i in range(len(categorias))]
                if len(series) == 1
                else cor
            )

            figura.add_trace(
                go.Bar(
                    name=serie,
                    x=categorias if tipo == "barv" else valores,
                    y=valores if tipo == "barv" else categorias,
                    orientation="v" if tipo == "barv" else "h",
                    marker_color=cores,
                    text=valores,
                    textposition="outside",
                    cliponaxis=False,
                )
            )

        if len(series) > 1:
            figura.update_layout(barmode="group")

    elif tipo in ("pie", "donut"):
        rotulos = []
        valores = []

        for categoria in categorias:
            for serie in series:
                valor = int(tabela.loc[categoria, serie])

                if valor > 0:
                    rotulos.append(categoria if len(series) == 1 else f"{categoria} — {serie}" )
                    valores.append(valor)

        figura.add_trace(
            go.Pie(
                labels=rotulos,
                values=valores,
                hole=0.48 if tipo == "donut" else 0,
                textinfo="percent+label",
                marker={ "colors": [ PALETA[i % len(PALETA)] for i in range(len(rotulos)) ] },
            )
        )

    elif tipo == "lollipop":
        for indice, serie in enumerate(series):
            valores = tabela[serie].tolist()

            rotulos = [ categoria if len(series) == 1 else f"{categoria} — {serie}" for categoria in categorias ]
            cores = ( [PALETA[i % len(PALETA)] for i in range(len(rotulos))] if len(series) == 1 else [PALETA[indice % len(PALETA)]] * len(rotulos) )

            for rotulo, valor, cor in zip(rotulos, valores, cores):
                figura.add_trace(
                    go.Scatter(
                        x=[0, valor],
                        y=[rotulo, rotulo],
                        mode="lines",
                        line={"color": cor, "width": 3},
                        hoverinfo="skip",
                        showlegend=False,
                    )
                )

            figura.add_trace(
                go.Scatter(
                    x=valores,
                    y=rotulos,
                    mode="markers+text",
                    name=serie,
                    text=valores,
                    textposition="middle right",
                    marker={ "size": 10, "color": cores, "line": {"color": cores, "width": 1}, },
                )
            )

    elif tipo in ("area", "line"):
        for indice, serie in enumerate(series):
            figura.add_trace(
                go.Scatter(
                    x=categorias,
                    y=tabela[serie].tolist(),
                    name=serie,
                    mode="lines+markers",
                    fill="tozeroy" if tipo == "area" else None,
                    line={ "color": PALETA[indice % len(PALETA)], "width": 3, },
                    marker={"size": 8},
                )
            )

    else:
        figura.add_annotation(
            text=f"Tipo de gráfico não reconhecido: {tipo}",
            x=0.5,
            y=0.5,
            xref="paper",
            yref="paper",
            showarrow=False,
        )

    aplicar_layout(
        figura,
        titulo,
        tipo=tipo,
        quantidade_series=len(series),
        altura=altura,
        margem=margem,
        mostrar_legenda=mostrar_legenda,
        fonte=fonte,
    )

    figura.update_layout(xaxis_title=titulo_eixo_x, yaxis_title=titulo_eixo_y, legend_title_text=titulo_legenda)

    if tipo == "barh":
        figura.update_yaxes(automargin=True, categoryorder="array", categoryarray=categorias)
        figura.update_xaxes(rangemode="tozero", automargin=True)

    elif tipo in ("barv", "area", "line"):
        figura.update_xaxes(automargin=True, tickangle=-20)
        figura.update_yaxes(rangemode="tozero", automargin=True)

    elif tipo == "lollipop":
        figura.update_xaxes(rangemode="tozero", automargin=True)
        figura.update_yaxes(automargin=True)

    return figura
