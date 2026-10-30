import json

import pandas as pd
import plotly.io as pio
from flask import jsonify, render_template, request

from app import app
from app.graficos.config_graficos import obter_configuracao
from app.graficos.dados_graficos import ( CAMINHO_CSV, carregar_dados, localizar_coluna, )
from app.graficos.dashboard_graficos import grafico_individual
from app.graficos.analises_graficos import grafico_cruzamento

@app.route("/")
def index():
    return render_template("inicio.html")

@app.route("/analise")
def analise():
    return render_template("analise.html")

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

@app.route("/api/analise")
def api_cruzamentos():
    categoria = request.args.get("categoria", "").strip()
    configuracao = obter_configuracao("analise")

    categorias = configuracao["categorias"]
    cruzamentos_configurados = configuracao["cruzamentos"]

    try:
        dados = carregar_dados(CAMINHO_CSV)
        graficos = []

        for cruzamento in cruzamentos_configurados:
            if categoria and cruzamento["categoria"] != categoria:
                continue

            figura = grafico_cruzamento(dados, cruzamento)

            graficos.append({
                "pergunta_1": cruzamento["pergunta_1"],
                "pergunta_2": cruzamento["pergunta_2"],
                "titulo": cruzamento["titulo"],
                "figure": json.loads( pio.to_json(figura, validate=True) ),
            })

        return jsonify({ "graficos": graficos, "categorias": categorias, })

    except ( OSError, UnicodeError, pd.errors.ParserError, ValueError, ) as erro:
        app.logger.exception( "Falha ao montar os gráficos de cruzamentos" )
        return jsonify({ "erro": str(erro), "graficos": [], }), 500

@app.route("/api/dashboard")
def api_graficos():
    categoria = request.args.get("categoria", "").strip()
    configuracao = obter_configuracao("dashboard")

    categorias = configuracao["categorias"]
    perguntas_configuradas = configuracao["perguntas"]

    try:
        dados = carregar_dados(CAMINHO_CSV)

        perguntas = [
            pergunta
            for pergunta in perguntas_configuradas
            if ( not categoria or pergunta["categoria"] == categoria )
            and localizar_coluna( dados, pergunta["numero"] ) is not None
        ]

        graficos = []

        for pergunta in perguntas:
            figura = grafico_individual(dados, pergunta)

            if pergunta["tipo"] in ("pie", "donut"):
                figura.update_layout(showlegend=True)

            graficos.append({
                "numero": pergunta["numero"],
                "titulo": pergunta["titulo"],
                "categoria": pergunta["categoria"],
                "figure": json.loads( pio.to_json(figura, validate=True) ),
            })

        return jsonify({ "graficos": graficos, "categorias": categorias, })

    except ( OSError, UnicodeError, pd.errors.ParserError, ValueError, ) as erro:
        app.logger.exception( "Falha ao montar os gráficos do dashboard" )
        return jsonify({ "erro": str(erro), "graficos": [], }), 500