import copy
import pandas as pd
import plotly.graph_objects as go
from app.graficos.config_graficos import ( CONFIG_LAYOUT, CONFIGURACOES_TIPOS, PALETA)

def quebrar_texto(texto, limite=12):
    palavras = str(texto).split()
    linhas = []
    linha = ""
    for palavra in palavras:
        if len(linha) + len(palavra) + bool(linha) <= limite:
            linha = f"{linha} {palavra}".strip()
        else:
            if linha:
                linhas.append(linha)
            linha = palavra
    if linha:
        linhas.append(linha)
    return "<br>".join(linhas)

def obter_cores(quantidade, indice_serie=0, uma_cor_por_categoria=False):
    if uma_cor_por_categoria:
        return [PALETA[i % len(PALETA)] for i in range(quantidade)]
    return PALETA[indice_serie % len(PALETA)]

def aplicar_layout( figura, titulo=None, *, tipo, quantidade_series=1, altura=None, margem=None, mostrar_legenda=None, fonte=None, fundo=None, ):
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
        regra = configuracao_tipo.get("legenda", "automatica")
        layout["showlegend"] = ( quantidade_series > 1 if regra == "automatica" else regra )
    figura.update_layout(**layout)
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
    tabela = tabela.apply(pd.to_numeric, errors="coerce")
    tabela = tabela.fillna(0).astype(int)
    return tabela

def adicionar_barras( figura, tabela, categorias, series, categorias_quebradas, series_quebradas, *, horizontal=False, barmode=None, ):
    quantidade_series = len(series)
    for indice, serie in enumerate(series):
        valores = tabela[serie].tolist()
        cores = obter_cores( len(categorias), indice_serie=indice, uma_cor_por_categoria=quantidade_series == 1, )
        configuracao = {
            "name": series_quebradas[indice],
            "marker_color": cores,
            "text": [ str(valor) if valor != 0 else "" for valor in valores ],
            "cliponaxis": False,
        }
        if horizontal:
            configuracao.update({
                "y": categorias_quebradas,
                "x": valores,
                "orientation": "h",
                "textposition": ( "inside" if barmode == "stack" else "outside" ),
                "hovertemplate": ( "Categoria: %{y}<br>" f"{serie}: %{{x}}" "<extra></extra>" ),
            })
        else:
            configuracao.update({ "x": categorias_quebradas, "y": valores, "textposition": "outside", })
        figura.add_trace(go.Bar(**configuracao))
    if quantidade_series > 1:
        figura.update_layout(barmode=barmode or "group")
    elif barmode is not None:
        figura.update_layout(barmode=barmode)
def grafico_por_dados( dados, tipo, titulo=None, *, titulo_eixo_x=None, titulo_eixo_y=None, titulo_legenda=None, altura=None, mostrar_legenda=None, margem=None, fonte=None, barmode=None, altura_barh_dinamica=True):
    tabela = normalizar_dados(dados)
    tipo = str(tipo).lower()
    tabela = tabela.loc[ ~tabela.eq(0).all(axis=1), ~tabela.eq(0).all(axis=0), ] 
    categorias = tabela.index.tolist()
    series = tabela.columns.tolist()
    figura = go.Figure()
    altura_dinamica = altura or 650
    categorias_quebradas = [ quebrar_texto(categoria, 10) for categoria in categorias ]
    series_quebradas = [ quebrar_texto(serie, 20) for serie in series ]
    if tabela.empty or tabela.to_numpy().sum() == 0:
        figura.add_annotation(
            text="Nenhuma resposta disponível",
            x=0.5,
            y=0.5,
            xref="paper",
            yref="paper",
            showarrow=False,
        )
    elif tipo == "barv":
        adicionar_barras(
            figura,
            tabela,
            categorias,
            series,
            categorias_quebradas,
            series_quebradas,
            barmode=barmode,
        )
    elif tipo == "barh":
        if altura_barh_dinamica:
            altura_dinamica = max( altura_dinamica, 500 + len(categorias) * 55, )
        adicionar_barras(
            figura,
            tabela,
            categorias,
            series,
            categorias_quebradas,
            series_quebradas,
            horizontal=True,
            barmode=barmode,
        )
    elif tipo == "barh_100":
        totais = tabela.sum(axis=1).replace(0, 1)
        percentuais = tabela.div(totais, axis=0) * 100
        for indice, serie in enumerate(series):
            valores = percentuais[serie].tolist()
            figura.add_trace(
                go.Bar(
                    name=series_quebradas[indice],
                    y=categorias_quebradas,
                    x=valores,
                    orientation="h",
                    marker_color=obter_cores( 1, indice_serie=indice, ),
                    text=[ f"{valor:.1f}%" if valor >= 7 else "" for valor in valores ],
                    textposition="inside",
                    insidetextanchor="middle",
                    hovertemplate=( "Categoria: %{y}<br>" f"Resposta: {serie}<br>" "Percentual: %{x:.1f}%" "<extra></extra>" ),
                )
            )
        figura.update_layout(barmode="stack")
        figura.update_xaxes( title_text=titulo_eixo_x or "Distribuição percentual", range=[0, 100], ticksuffix="%", automargin=True, )
        figura.update_yaxes(automargin=True)
    elif tipo in ("pie", "donut"):
        rotulos = []
        valores = []
        for categoria in categorias:
            for serie in series:
                valor = int(tabela.loc[categoria, serie])
                if valor > 0:
                    rotulo = ( categoria if len(series) == 1 else f"{categoria} — {serie}" )
                    rotulos.append(quebrar_texto(rotulo, 20))
                    valores.append(valor)
        figura.add_trace(
            go.Pie(
                labels=rotulos,
                values=valores,
                hole=0.48 if tipo == "donut" else 0,
                textinfo="percent+label",
                marker={ "colors": obter_cores( len(rotulos), uma_cor_por_categoria=True, ) },
            )
        )
    elif tipo == "lollipop":
        for indice, serie in enumerate(series):
            valores = tabela[serie].tolist()
            rotulos = [ categoria if len(series) == 1 else f"{categoria} — {serie}" for categoria in categorias ] 
            cor = obter_cores( len(rotulos), indice_serie=indice, uma_cor_por_categoria=len(series) == 1, ) 
            cores = cor if isinstance(cor, list) else [cor] * len(rotulos)
            for rotulo, valor, cor_item in zip( rotulos, valores, cores, ):
                figura.add_trace(
                    go.Scatter(
                        x=[0, valor],
                        y=[rotulo, rotulo],
                        mode="lines",
                        line={"color": cor_item, "width": 3},
                        hoverinfo="skip",
                        showlegend=False,
                    )
                )
            figura.add_trace(
                go.Scatter(
                    x=valores,
                    y=rotulos,
                    mode="markers+text",
                    name=series_quebradas[indice],
                    text=[ str(valor) if valor != 0 else "" for valor in valores ],
                    textposition="middle right",
                    marker={ "size": 10, "color": cores, "line": {"color": cores, "width": 1}, },
                )
            )
    elif tipo in ("area", "line"):
        for indice, serie in enumerate(series):
            figura.add_trace(
                go.Scatter(
                    x=categorias_quebradas,
                    y=tabela[serie].tolist(),
                    name=series_quebradas[indice],
                    mode="lines+markers",
                    fill="tozeroy" if tipo == "area" else None,
                    line={ "color": obter_cores( 1, indice_serie=indice, ), "width": 3, },
                    marker={"size": 8},
                )
            )
    elif tipo == "heatmap":
        valores = tabela.to_numpy()
        categorias_heatmap = [ quebrar_texto(categoria, 10) for categoria in categorias ]
        series_heatmap = [ quebrar_texto(serie, 12) for serie in series ]
        valores_texto = [ [ str(valor) if valor != 0 else "" for valor in linha ] for linha in valores ]
        figura.add_trace(
            go.Heatmap(
                z=valores,
                x=series_heatmap,
                y=categorias_heatmap,
                colorscale="Blues",
                colorbar={"title": "Quantidade"},
                text=valores_texto,
                texttemplate="%{text}",
                textfont={"size": 11},
                xgap=2,
                ygap=2,
                hovertemplate=( "Categoria: %{y}<br>" "Resposta: %{x}<br>" "Quantidade: %{z}" "<extra></extra>" ),
            )
        )
    else:
        figura.add_annotation( text=f"Tipo de gráfico não reconhecido: {tipo}", x=0.5, y=0.5, xref="paper", yref="paper", showarrow=False, )
    margem_final = margem
    if margem_final is None and tipo == "heatmap":
        margem_final = { "l": 24, "r": 24, "t": 45, "b": 125, }
    aplicar_layout( figura, titulo, tipo=tipo, quantidade_series=len(series), altura=altura_dinamica, margem=margem_final, mostrar_legenda=mostrar_legenda, fonte=fonte, )
    figura.update_layout(legend_title_text=titulo_legenda)
    if tipo == "barh":
        figura.update_layout( bargap=0.08, bargroupgap=0.02, )
        figura.update_yaxes( automargin=True, categoryorder="array", categoryarray=categorias_quebradas, tickfont={"size": 11}, )
        figura.update_xaxes( rangemode="tozero", automargin=True, )
    elif tipo in ("barv", "area", "line"):
        figura.update_xaxes( automargin=True, tickangle=-20, )
        figura.update_yaxes( rangemode="tozero", automargin=True, )
    elif tipo == "lollipop":
        figura.update_xaxes( rangemode="tozero", automargin=True, )
        figura.update_yaxes(automargin=True)
    elif tipo == "barh_100":
        figura.update_yaxes( categoryorder="array", categoryarray=categorias_quebradas, automargin=True, tickfont={"size": 11}, )
    return figura
