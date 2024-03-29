/*Soma elementos de um array*/
function add(accumulator, a) {
    return accumulator + a;
}

/*Arredonda um valor para x casas decimais*/
function round_x(float, decimals = 1) {
    const p10 = 10 ** decimals;
    return Math.round(float * p10 + Number.EPSILON) / p10;
}

/*Transforma um valor tipo float em formatacao de R$*/
function parseReal(float) {
    let valor = String(float).split(".");
    const inteiro = valor[0];
    let centavos = "00";
    if (valor.length == 2) {
        centavos = valor[1];
    }

    let inteiro_refactor = "";
    for (let i = -1; Math.abs(i) <= inteiro.length; i--) {
        if ((Math.abs(i) % 4 == 0) & (inteiro.at(i) != "-")) {
            inteiro_refactor = "." + inteiro_refactor;
        }
        inteiro_refactor = inteiro.at(i) + inteiro_refactor;
    }

    valor = `${inteiro_refactor},${centavos}`;
    return valor;
}

/*Faz o enderecamento das tabelas de demanda e oferta,
alem de criar os EventListener's que tornam o grafico interativo*/
function address(parent_id, child_tag, id_names, type) {
    let parent = document.getElementById(parent_id);
    let child = parent.getElementsByTagName(child_tag);

    const nomes = [];
    const indicadores = [];
    const n = child.length / 3;
    for (let i = 0; i < n * 3; i++) {
        child[i].setAttribute(
            "id",
            "id_" + type + "-" + Math.floor(i / 3) + "-" + id_names[i % 3]
        );
        child[i].setAttribute(
            "name",
            type + "-" + Math.floor(i / 3) + "-" + id_names[i % 3]
        );

        if (id_names[i % 3] == "indicador") {
            indicadores.push(parseFloat(child[i].value.replace(",", ".")));
        } else if (id_names[i % 3] == "nome") {
            nomes.push(child[i].value);
        } else if (id_names[i % 3] == "check") {
            child[i].addEventListener(
                "click",
                function () {
                    re_plot(child[i].id);
                },
                false
            );
        }
    }

    return { n, nomes, indicadores };
}

/*Retorna casos diferentes de zero para que o grafico nao apresente o dado zerado*/
function clean_data(labels, values) {
    if (values.includes(0)) {
        var cleaned_values = [];
        var cleaned_labels = [];
        for (let i = 0; i < values.length; i++) {
            if (values[i] != 0) {
                cleaned_values.push(values[i]);
                cleaned_labels.push(labels[i]);
            }
        }
    } else {
        var cleaned_labels = labels;
        var cleaned_values = values;
    }

    return { cleaned_labels, cleaned_values };
}

/*Faz a soma dos indicadores da demanda*/
function soma_dem(indicadores, nomes) {
    let soma = 0;
    for (let i = 0; i < indicadores.length; i++) {
        let mensal = indicadores[i];
        if (nomes[i] != "Irrigação de jardins") {
            soma = soma + mensal * 12;
        } else {
            /*A irrigacao so e contabilizada nos meses de estiagem*/
            soma = soma + mensal * 6;
        }
    }
    return soma;
}

/*Refaz o grafico, e outros elementos da pagina, toda vez que ocorre uma interacao com checkbox*/
function re_plot(id) {
    console.log(id);
    const index = id.replace(/[^0-9]/g, "");
    const checkbox = document.getElementById(id);
    const indicador = document.getElementById(
        id.replace("check", "indicador")
    ).value;
}

function plotBg(n) {
    let azul = 235;
    let verde = 162;
    let vermelho = 54;
    if (n > 1) {
        const colors = [`rgb(${vermelho}, ${verde}, ${azul})`];
        for (let i = 0; i < n - 1; i++) {
            verde += 10;
            vermelho += 5;
            colors.push(`rgb(${vermelho}, ${verde}, ${azul})`);
        }
        return colors;
    }
    return `rgb(${vermelho}, ${verde}, ${azul})`;
}

function addData(chart, labels, data, color = false) {
    let colors = "";
    if (color) {
        colors = plotBg(data.length);
    } else {
        colors = plotBg(1);
    }
    chart.data.datasets.forEach((dataset) => {
        dataset.backgroundColor = colors;
    });

    chart.data.labels.push(...labels);
    chart.data.datasets.forEach((dataset) => {
        dataset.data.push(...data);
    });
    chart.update("");
}

function removeData(chart) {
    chart.data.labels.length = 0;
    chart.data.datasets.forEach((dataset) => {
        dataset.data.length = 0;
    });
    chart.update("");
}

function fixMEP(chart, index) {
    const annotation_opt = chart.options.plugins.annotation.annotations[0];
    annotation_opt.xMin = index;
    annotation_opt.xMax = index;
    chart.update("none");
}

function realFloat(real) {
    const valor = String(real).replace(".", "").replace(",", ".");
    return parseFloat(valor);
}
