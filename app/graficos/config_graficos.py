import plotly.express as px

PALETA = (
    px.colors.qualitative.Safe
    + px.colors.qualitative.Set2
    + px.colors.qualitative.Pastel
    + px.colors.qualitative.Dark24
)
#TODO - grafico de barras e lollipop com cores coloridas.
CONFIG_LAYOUT = {
    "template": "plotly_white",
    "height": max(330, min(480, 90 + 150 * 34)),
    "autosize": True,
    "dragmode": False,
    "xaxis": { "tickangle": 0, "automargin": True, },
    "margin": {"l": 24, "r": 24, "t": 24, "b": 90},
    "font": { "family": "Arial, sans-serif", "color": "#343434", "size": 12, },
    "paper_bgcolor": "rgba(0,0,0,0)",
    "plot_bgcolor": "rgba(0,0,0,0)",
    "legend": {
        "orientation": "h",
        "yanchor": "top",
        "y": -0.30,
        "xanchor": "left",
        "x": 0,
        "font": {"size": 10},
    },
    "hoverlabel": { "bgcolor": "#FFFFFF", "font": {"size": 12, "color": "#343434"}, },
}

#TODO depois - Editar. barras Dashboard não tem legenda, mas barras de cruzamento tem legenda. 

CONFIGURACOES_TIPOS = {
    "barv": {"legenda": "automatica"},
    "barh": {"legenda": "automatica"},
    "pie": {"legenda": "automatica"},
    "donut": {"legenda": "automatica"},
    "lollipop": {"legenda": "automatica"},
    "area": {"legenda": "automatica"},
    "line": {"legenda": "automatica"},
}

CONFIGURACOES_PAGINAS = {
    "dashboard": { # nao editar essa parte do dashboard
        "categorias": [
            { "label": "Perfil e acesso à internet", "value": "perfil-conectividade", },
            { "label": "Uso dos serviços digitais de saúde", "value": "servicos-saude", },
            { "label": "Experiência de uso e letramento digital", "value": "experiencia-letramento", },
            { "label": "Barreiras de acessibilidade", "value": "acessibilidade", },
            { "label": "Impactos no acesso à saúde", "value": "impactos-saude", },
        ],
        "perguntas": [
            { "numero": 1, "titulo": "Qual é a sua faixa etária?", "categoria": "perfil-conectividade", "tipo": "barv", },
            { "numero": 2, "titulo": "Em qual região você mora?", "categoria": "perfil-conectividade", "tipo": "barh", },
            { "numero": 3, "titulo": "Qual é o seu nível de escolaridade?", "categoria": "perfil-conectividade", "tipo": "barh", },
            { "numero": 4, "titulo": "Qual dispositivo você utiliza com maior frequência para acessar a internet?", "categoria": "perfil-conectividade", "tipo": "donut", },
            { "numero": 5, "titulo": "Como você acessa a internet com maior frequência?", "categoria": "perfil-conectividade", "tipo": "barv", },
            { "numero": 6, "titulo": "Com que frequência você fica sem internet quando precisa utilizá-la?", "categoria": "perfil-conectividade", "tipo": "barh", },
            { "numero": 7, "titulo": "Você já utilizou serviços públicos de saúde pela internet?", "categoria": "servicos-saude", "tipo": "pie", },
            { "numero": 8, "titulo": "Quais serviços digitais de saúde você já utilizou?", "categoria": "servicos-saude", "tipo": "lollipop", "multipla": True, },
            { "numero": 9, "titulo": "Com que frequência você tem dificuldade para encontrar informações ou realizar ações em sites e aplicativos de saúde pública?", "categoria": "experiencia-letramento", "tipo": "area", },
            { "numero": 10, "titulo": "Com que frequência você deixou de utilizar um serviço digital de saúde por não entender como realizar o procedimento?", "categoria": "experiencia-letramento", "tipo": "area", },
            { "numero": 11, "titulo": "Como você avalia sua facilidade para utilizar celular ou computador em tarefas pela internet?", "categoria": "experiencia-letramento", "tipo": "barv", },
            { "numero": 12, "titulo": "O que você costuma fazer quando encontra dificuldades ao utilizar serviços digitais?", "categoria": "experiencia-letramento", "tipo": "lollipop", },
            { "numero": 13, "titulo": "Quais dificuldades você encontra ao utilizar serviços digitais de saúde?", "categoria": "acessibilidade", "tipo": "lollipop", "multipla": True, },
            { "numero": 14, "titulo": "Você considera os sites e aplicativos públicos de saúde acessíveis?", "categoria": "acessibilidade", "tipo": "pie", },
            { "numero": 15, "titulo": "Com que frequência você deixou de realizar alguma ação relacionada à saúde por dificuldade com recursos digitais?", "categoria": "impactos-saude", "tipo": "area", },
        ],
    },
    "analise": { 
        "categorias": [
            # {
            #     "label": "Perfil e conectividade de exemplo",
            #     "value": "perfil-conectividade",
            # },
        ],
        "cruzamentos": [ 
            #Adicionar quantas perguntas quiser aqui no formato do exemplo abaixo.
            #perguntas que estao numeradas de 1 a 15 acima em "dashboard"
            #cada uma das perguntas/de onde veio o valor um será o eixo x e outro será o eixo y
            {   
                #devem ser o mesmo do html analise.html, cada dado é um grafico.
                "pergunta_1": 1,
                "pergunta_2": 7,

                #Sempre adicionar um titulo para o grafico nesse arquivo. 
                "titulo": "Faixa etária × Uso de serviços digitais de saúde",

                #escolher em qual categoria o grafico irá aparecer, da lista da analise -> categoria.
                "categoria": "perfil-conectividade",

                #Escolher o tipo de grafico que voce quer(barv, barh, pie, donut, lollipop, area, line,...)
                #verificar possibilidades do plotly dash
                "tipo": "barv",
            },
            # {   
            #     "pergunta_1": 1,
            #     "pergunta_2": 7,
            #     "titulo": "Faixa etária × Uso de serviços digitais de saúde",
            #     "categoria": "perfil-conectividade",
            #     "tipo": "barv",
            # },
        ],
    },
}

def obter_configuracao(pagina):
    pagina = pagina.strip().lower()

    if pagina not in CONFIGURACOES_PAGINAS:
        raise ValueError(
            f"Página desconhecida: {pagina}. "
            "Use 'dashboard' ou 'analise'."
        )

    return CONFIGURACOES_PAGINAS[pagina]
