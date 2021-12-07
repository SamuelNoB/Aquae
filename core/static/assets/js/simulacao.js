/*Soma elementos de um array*/
function add(accumulator, a) {
    return accumulator + a;
}


/*Transforma um valor tipo float em formatacao de R$*/
function parseReal(float){
    let valor = String(float).split(".")
    const inteiro = valor[0]
    let centavos = '00'
    if (valor.length == 2) {
        centavos = valor[1]
    }

    let inteiro_refactor = ""
    for (let i=-1; Math.abs(i) <= inteiro.length; i--) {
        if ((Math.abs(i) % 4) == 0 & inteiro.at(i) != "-") {
            inteiro_refactor = '.' + inteiro_refactor
        }
        inteiro_refactor = inteiro.at(i) + inteiro_refactor
    }

    valor = `${inteiro_refactor},${centavos}`
    return valor
}


/*Faz o enderecamento das tabelas de demanda e oferta,
alem de criar os EventListener's que tornam o grafico interativo*/
function address(parent_id, child_tag, id_names, type) {
    let parent = document.getElementById(parent_id)
    let child = parent.getElementsByTagName(child_tag)

    
    const nomes = []
    const indicadores = []
    const n = child.length/3
    for (let i = 0; i < n*3; i++){
        child[i].setAttribute('id', 'id_' + type + "-" + Math.floor(i / 3) + "-" + id_names[(i%3)])
        child[i].setAttribute('name', type + "-" + Math.floor(i / 3) + "-" + id_names[(i%3)])
        
        if (id_names[(i%3)] == 'indicador') {
            indicadores.push( parseFloat(child[i].value.replace(',', '.')))
        } else if (id_names[(i%3)] == 'nome') {
            nomes.push(child[i].value)
        } else if(id_names[(i%3)] == 'check') {
            child[i].addEventListener('click', function () {re_plot(child[i].id)}, false)
        }
    }

    return({n, nomes, indicadores})
}

/*Retorna casos diferentes de zero para que o grafico nao apresente o dado zerado*/
function clean_data(labels, values) {
    
    if (values.includes(0)) {
        var cleaned_values = []
        var cleaned_labels = []
        for (let i = 0; i < values.length; i++) {
            if (values[i] != 0) {
                cleaned_values.push(values[i])
                cleaned_labels.push(labels[i])
            }
        } 
    } else {
        var cleaned_labels = labels
        var cleaned_values = values
    }

    return ({cleaned_labels, cleaned_values})
}


function plot(x, y, type='bar', custom_opt='') {
    const clean = clean_data(labels = x, values = y)
    
    /*Deleta a canvas antiga para nao bugar a visualizacao*/
    document.getElementById('SimulChart').remove()
    
    /*Nova canvas*/
    const ChartDiv =  document.getElementById('ChartDiv')

    const canvas = ChartDiv.appendChild(document.createElement("canvas"))

    canvas.setAttribute('id', 'SimulChart')
    const ctx = canvas.getContext('2d');
    
    const SimulChart = new Chart(ctx, {
        type: type,
        data: {
            labels: clean.cleaned_labels,
            
            datasets: [{
                label: 'Economia de Água m³/ano',
                data: clean.cleaned_values,
                fill: false,
                backgroundColor: 'rgba(54, 162, 235, 1)',
                borderColor: 'rgba(54, 162, 235, 1)',
                borderWidth: 1
            }],
        },
        options: custom_opt   
    });
}

/*Retorna a possivel economia de cada demanda*/
function data_adjust(oferta_indicadores, demanda_indicadores) {
    const economia = []
    const oferta_total = oferta_indicadores.reduce(add, 0) * 12
    for (let i = 0; i < demanda_indicadores.length; i++) {
        economia.push(Math.min(demanda_indicadores[i] * 12, oferta_total))
    }
    return economia
}

/*Refaz o grafico, e outros elementos da pagina, toda vez que ocorre uma interacao com checkbox*/
function re_plot(id) {
    console.log(id)
    const index = id.replace(/[^0-9]/g, '')
    const checkbox = document.getElementById(id)
    const indicador = document.getElementById(id.replace('check', 'indicador')).value

}

/*Cria elementos da parte financeira e capacidade necessaria*/
function create_tabs(demanda, tarifa, juros) {
    /*Seletor de capacidade minima*/
    let volume_cap = Math.max(...volumes_cap)
    for (let i = 0; i < volumes_cap.length; i++) {
        if (volumes_cap[i] > demanda) {
            volume_cap = volumes_cap[i]
            break
        }
    }
    /*Seletor de caixa minima*/
    let volume_caixa = Math.max(...volumes_caixa)
    for (let i = 0; i < volumes_caixa.length; i++) {
        if (volumes_caixa[i] > demanda) {
            volume_caixa = volumes_caixa[i]
            break
        }
    }
    document.getElementById("Caixa_volume").innerHTML = `${String(volume_caixa)} L`

    const custo_op_final = Math.round((financeiro_cap[volume_cap][1] + custo_op_bomba + Number.EPSILON)*100)/100
    document.getElementById("custo_operacional").innerHTML = parseReal(custo_op_final) + ' R$/ano'

    const custo_cap = Math.round((financeiro_cap[volume_cap][0] + custo_bomba + financeiro_caixa[volume_caixa] + Number.EPSILON)*100)/100
    document.getElementById("Custo_cap").innerHTML = parseReal(custo_cap)

    document.getElementById("Capacidade").innerHTML = volume_cap
    
    const Beneficio = Math.round((tarifa * demanda * 30 * 12 / 1000 - custo_op_final + Number.EPSILON)*100) / 100
    document.getElementById("Beneficio").innerHTML = parseReal(Beneficio)

    let Payback = Math.ceil(custo_cap / Beneficio)
    Payback_span = document.getElementById("Payback")
    if (Payback < 0) {
        Payback = 'Inviável!';
        Payback_span.setAttribute("style", "color:red")
    } else {
        Payback_span.setAttribute("style", "color:black")
    }
    Payback_span.innerHTML = Payback


    /*Determina VPL*/
    const VPL_parcelas = []
    for (let i = 1; i <= 30; i++) {
        const parcela = Beneficio / ((1 + juros)**i)
        VPL_parcelas.push(parcela)
    }
    const VPL = Math.round((VPL_parcelas.reduce(add, 0) - custo_cap + Number.EPSILON)*100)/100
    const vpl_span = document.getElementById("VPL")
    vpl_span.innerHTML = parseReal(VPL)         
    if (VPL < 0) {vpl_span.setAttribute("style", "color:red")}
    else {vpl_span.setAttribute("style", "color:black")}

}

function addData(chart, labels, data) {
    chart.data.labels.push(...labels);
    chart.data.datasets.forEach((dataset) => {
        dataset.data.push(...data);
    })
    chart.update('none');
}

function removeData(chart) {
    chart.data.labels.length = 0;
    chart.data.datasets.forEach((dataset) => {
        dataset.data.length = 0;
    });
    chart.update('none');
}
