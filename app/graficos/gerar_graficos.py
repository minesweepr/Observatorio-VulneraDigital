
import copy

import pandas as pd
import plotly.graph_objects as go

from app.graficos.config_graficos import (
    CONFIG_LAYOUT,
    CONFIGURACOES_TIPOS,
    PALETA,
)


def aplicar_layout(
    figura,
    titulo=None,
    *,
    tipo,
    quantidade_series=1,
    altura=None,
    margem=None,
    mostrar_legenda=None,
    fonte=None,
    fundo=None,
):
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
        regra_legenda = configuracao_tipo.get(
            "legenda",
            "automatica",
        )

        if regra_legenda == "automatica":
            layout["showlegend"] = quantidade_series > 1
        else:
            layout["showlegend"] = regra_legenda

    figura.update_layout(
        title={
            "text": titulo or "",
            "x": 0.02,
            "xanchor": "left",
        },
        colorway=list(PALETA),
        **layout,
    )

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
        tabela[coluna] = pd.to_numeric(
            tabela[coluna],
            errors="coerce",
        ).fillna(0)

    return tabela.astype(int)


def grafico_por_dados(
    dados,
    tipo,
    titulo=None,
    *,
    titulo_eixo_x=None,
    titulo_eixo_y=None,
    titulo_legenda=None,
    altura=None,
    mostrar_legenda=None,
    margem=None,
    fonte=None,
):
    tabela = normalizar_dados(dados)
    tipo = str(tipo).lower()
    figura = go.Figure()

    categorias = tabela.index.tolist()
    series = tabela.columns.tolist()

    if tabela.empty or tabela.size == 0 or tabela.to_numpy().sum() == 0:
        figura.add_annotation(
            text="Nenhuma resposta disponível",
            x=0.5,
            y=0.5,
            xref="paper",
            yref="paper",
            showarrow=False,
        )

    # Barras verticais agrupadas
    elif tipo == "barv":
        for indice, serie in enumerate(series):
            valores = tabela[serie].tolist()

            cores = (
                [PALETA[i % len(PALETA)] for i in range(len(categorias))]
                if len(series) == 1
                else PALETA[indice % len(PALETA)]
            )

            figura.add_trace(
                go.Bar(
                    name=serie,
                    x=categorias,
                    y=valores,
                    marker_color=cores,
                    text=valores,
                    textposition="outside",
                    cliponaxis=False,
                )
            )

        if len(series) > 1:
            figura.update_layout(barmode="group")

    # Barras horizontais agrupadas
    elif tipo == "barh":
        for indice, serie in enumerate(series):
            valores = tabela[serie].tolist()

            cores = (
                [PALETA[i % len(PALETA)] for i in range(len(categorias))]
                if len(series) == 1
                else PALETA[indice % len(PALETA)]
            )

            figura.add_trace(
                go.Bar(
                    name=serie,
                    y=categorias,
                    x=valores,
                    orientation="h",
                    marker_color=cores,
                    text=valores,
                    textposition="auto",
                    cliponaxis=False,
                )
            )

        if len(series) > 1:
            figura.update_layout(barmode="group")

    # Barras horizontais empilhadas em 100%
    elif tipo == "barh_100":
        totais = tabela.sum(axis=1).replace(0, 1)
        percentuais = tabela.div(totais, axis=0) * 100

        for indice, serie in enumerate(series):
            valores = percentuais[serie].tolist()
            textos = [
                f"{valor:.1f}%" if valor >= 7 else ""
                for valor in valores
            ]

            figura.add_trace(
                go.Bar(
                    name=serie,
                    y=categorias,
                    x=valores,
                    orientation="h",
                    marker_color=PALETA[indice % len(PALETA)],
                    text=textos,
                    textposition="inside",
                    insidetextanchor="middle",
                    hovertemplate=(
                        "Categoria: %{y}<br>"
                        "Resposta: " + serie + "<br>"
                        "Percentual: %{x:.1f}%<extra></extra>"
                    ),
                )
            )

        figura.update_layout(barmode="stack")

        figura.update_xaxes(
            title_text=titulo_eixo_x or "Distribuição percentual",
            range=[0, 100],
            ticksuffix="%",
            automargin=True,
        )

        figura.update_yaxes(automargin=True)

    # Pizza e rosca
    elif tipo in ("pie", "donut"):
        rotulos = []
        valores = []

        for categoria in categorias:
            for serie in series:
                valor = int(tabela.loc[categoria, serie])

                if valor > 0:
                    rotulos.append(
                        categoria
                        if len(series) == 1
                        else f"{categoria} — {serie}"
                    )
                    valores.append(valor)

        figura.add_trace(
            go.Pie(
                labels=rotulos,
                values=valores,
                hole=0.48 if tipo == "donut" else 0,
                textinfo="percent+label",
                marker={
                    "colors": [
                        PALETA[i % len(PALETA)]
                        for i in range(len(rotulos))
                    ]
                },
            )
        )

    # Lollipop
    elif tipo == "lollipop":
        for indice, serie in enumerate(series):
            valores = tabela[serie].tolist()

            rotulos = [
                categoria
                if len(series) == 1
                else f"{categoria} — {serie}"
                for categoria in categorias
            ]

            cores = (
                [PALETA[i % len(PALETA)] for i in range(len(rotulos))]
                if len(series) == 1
                else [PALETA[indice % len(PALETA)]] * len(rotulos)
            )

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
                    marker={
                        "size": 10,
                        "color": cores,
                        "line": {"color": cores, "width": 1},
                    },
                )
            )

    # Área e linha
    elif tipo in ("area", "line"):
        for indice, serie in enumerate(series):
            figura.add_trace(
                go.Scatter(
                    x=categorias,
                    y=tabela[serie].tolist(),
                    name=serie,
                    mode="lines+markers",
                    fill="tozeroy" if tipo == "area" else None,
                    line={
                        "color": PALETA[indice % len(PALETA)],
                        "width": 3,
                    },
                    marker={"size": 8},
                )
            )

    # Mapa de calor
    elif tipo == "heatmap":
        valores = tabela.to_numpy()

        figura.add_trace(
            go.Heatmap(
                z=valores,
                x=series,
                y=categorias,
                colorscale="Blues",
                colorbar={"title": "Quantidade"},
                text=valores,
                texttemplate="%{text}",
                textfont={"size": 12},
                hovertemplate=(
                    "Resposta da primeira pergunta: %{y}<br>"
                    "Resposta da segunda pergunta: %{x}<br>"
                    "Quantidade: %{z}<extra></extra>"
                ),
                xgap=2,
                ygap=2,
            )
        )

        figura.update_xaxes(
            title_text=titulo_eixo_x or "Respostas da segunda pergunta",
            side="bottom",
            automargin=True,
            tickangle=-30,
        )

        figura.update_yaxes(
            title_text=titulo_eixo_y or "Respostas da primeira pergunta",
            automargin=True,
            autorange="reversed",
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

    margem_final = margem

    if margem_final is None and tipo == "heatmap":
        margem_final = {
            "l": 24,
            "r": 24,
            "t": 45,
            "b": 125,
        }

    aplicar_layout(
        figura,
        titulo,
        tipo=tipo,
        quantidade_series=len(series),
        altura=altura,
        margem=margem_final,
        mostrar_legenda=mostrar_legenda,
        fonte=fonte,
    )

    figura.update_layout(
        legend_title_text=titulo_legenda,
    )

    if tipo == "barh":
        figura.update_yaxes(
            automargin=True,
            categoryorder="array",
            categoryarray=categorias,
        )
        figura.update_xaxes(
            rangemode="tozero",
            automargin=True,
        )

    elif tipo in ("barv", "area", "line"):
        figura.update_xaxes(
            automargin=True,
            tickangle=-20,
        )
        figura.update_yaxes(
            rangemode="tozero",
            automargin=True,
        )

    elif tipo == "lollipop":
        figura.update_xaxes(
            rangemode="tozero",
            automargin=True,
        )
        figura.update_yaxes(automargin=True)

    elif tipo == "barh_100":
        figura.update_yaxes(
            categoryorder="array",
            categoryarray=categorias,
            automargin=True,
        )

    return figura
