
(() => {
    "use strict";

    const lista = document.getElementById("lista-graficos");
    const filtro = document.getElementById("filtro-categoria");
    const limpar = document.getElementById("limpar-filtros");
    const status = document.getElementById("status-cruzamentos");

    if (!lista) {
        console.error("Elemento #lista-graficos não encontrado.");
        return;
    }

    if (typeof window.Plotly === "undefined") {
        if (status) {
            status.textContent = "A biblioteca Plotly não foi carregada. Verifique o script CDN.";
        }
        return;
    }

    let requisicaoAtual = 0;

    const config = {
        responsive: true,
        displaylogo: false,
        scrollZoom: false,
        displayModeBar: true,
        modeBarButtonsToRemove: [
            "pan2d",
            "resetScale2d",
            "select2d",
            "lasso2d",
            "zoom2d",
            "toImage"
        ]
    };

    async function carregarGraficos() {
        const id = ++requisicaoAtual;
        const parametros = new URLSearchParams();

        if (filtro && filtro.value) {
            parametros.set("categoria", filtro.value);
        }

        if (status) {
            status.textContent = "Carregando gráficos...";
        }

        lista.replaceChildren();

        try {
            const resposta = await fetch( `/api/dashboard?${parametros.toString()}`, { headers: { Accept: "application/json" } } );

            const resultado = await resposta.json();

            if (id !== requisicaoAtual) return;

            if (!resposta.ok || resultado.erro) {
                throw new Error( resultado.erro || `Falha HTTP ${resposta.status}` );
            }

            if ( !Array.isArray(resultado.graficos) || resultado.graficos.length === 0 ) {
                if (status) {
                    status.textContent = "Nenhum gráfico disponível. Verifique as colunas do CSV.";
                }
                return;
            }

            const fragmento = document.createDocumentFragment();

            for (const grafico of resultado.graficos) {
                const cartao = document.createElement("article");
                cartao.className = "grafico-card";

                const titulo = document.createElement("h3");
                titulo.className = "grafico-titulo";
                titulo.textContent = grafico.titulo;

                const area = document.createElement("div");
                area.id = `grafico-${grafico.numero}`;
                area.className = "grafico-plot";

                cartao.append(titulo, area);
                fragmento.appendChild(cartao);
            }

            lista.replaceChildren(fragmento);

            await Promise.all(
                resultado.graficos.map((grafico) => {
                    const area = document.getElementById( `grafico-${grafico.numero}` );

                    const layout = { ...(grafico.figure.layout || {}), autosize: true };

                    delete layout.width;

                    return window.Plotly.newPlot( area, grafico.figure.data || [], layout, config );
                })
            );

            if (id !== requisicaoAtual) return;

            lista.querySelectorAll(".grafico-plot").forEach((elemento) => { window.Plotly.Plots.resize(elemento); });

            if (status) {
                status.textContent = `${resultado.graficos.length} gráfico(s) carregado(s).`;
            }

        } catch (erro) {
            if (id !== requisicaoAtual) return;

            console.error("Erro ao carregar os gráficos:", erro);
            lista.replaceChildren();

            if (status) {
                status.textContent = `Erro ao carregar os gráficos: ${erro.message}`;
            }
        }
    }

    if (filtro) {
        filtro.addEventListener("change", carregarGraficos);
    }

    if (limpar) {
        limpar.addEventListener("click", () => {
            if (filtro) {
                filtro.value = "";
            }
            carregarGraficos();
        });
    }

    window.addEventListener("resize", () => {
        lista.querySelectorAll(".grafico-plot").forEach((elemento) => {
            if (elemento.data) {
                window.Plotly.Plots.resize(elemento);
            }
        });
    });

    carregarGraficos();
})();
