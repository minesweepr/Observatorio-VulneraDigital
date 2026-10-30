import plotly.graph_objects as go

from app.graficos.config_graficos import obter_configuracao
from app.graficos.dados_graficos import contar_respostas
from app.graficos.gerar_graficos import grafico_por_dados

def grafico_individual(dados, pergunta, *, mostrar_legenda=None, altura=370, margem=None, fonte=None):
    perguntas = obter_configuracao("dashboard")["perguntas"]

    if isinstance(pergunta, int):
        pergunta = next((item for item in perguntas if item["numero"] == pergunta ), None)

    if not pergunta:
        figura = go.Figure()
        figura.add_annotation(
            text="Pergunta não encontrada",
            x=0.5, y=0.5,
            xref="paper", yref="paper",
            showarrow=False,
        )
        return figura

    contagens = contar_respostas(dados, pergunta["numero"], pergunta.get("multipla", False))

    return grafico_por_dados(
        contagens,
        pergunta["tipo"],
        None,
        altura=altura,
        mostrar_legenda=mostrar_legenda,
        margem=margem,
        fonte=fonte,
        altura_barh_dinamica=False
    )