/*Retorna a possivel economia de cada demanda*/
function data_adjust(oferta_total, demanda_indicadores, demanda_nomes) {
    const economia = [];
    for (let i = 0; i < demanda_indicadores.length; i++) {
        if (demanda_nomes[i] != "Irrigação de jardins") {
            economia.push(Math.min(demanda_indicadores[i] * 12, oferta_total));
        } else {
            /*A irrigacao so e contabilizada nos meses de estiagem*/
            economia.push(Math.min(demanda_indicadores[i] * 6, oferta_total));
        }
    }
    return economia;
}

/*Refaz o grafico, e outros elementos da pagina, toda vez que ocorre uma interacao com checkbox*/
function re_plot(id) {
    const index = id.replace(/[^0-9]/g, "");
    const checkbox = document.getElementById(id);
    const indicador = document.getElementById(
        id.replace("check", "indicador")
    ).value;

    if (id.includes("demanda")) {
        /*Cria novo indicador, valor do formulario ou zero, dependendo se o usuario acabou de marcar ou desmarcar a checkbox*/
        data_demanda.indicadores[index] =
            checkbox.checked * parseFloat(indicador.replace(",", "."));
    } else if (id.includes("oferta")) {
        data_oferta.indicadores[index] =
            checkbox.checked * parseFloat(indicador.replace(",", "."));
    }

    const oferta_total = data_oferta.indicadores.reduce(add, 0) * 12;
    const demanda_total = soma_dem(data_demanda.indicadores, data_demanda.nomes);
    const re_economia = data_adjust(
        oferta_total,
        data_demanda.indicadores,
        data_demanda.nomes
    );

    const clean = clean_data(data_demanda.nomes, re_economia);
    removeData(SimulChart);
    addData(SimulChart, clean.cleaned_labels, clean.cleaned_values);

    const demanda_possivel = Math.min(demanda_total, oferta_total);

    create_tabs(
        (demanda_possivel * 1000) / 30,
        demanda_total,
        oferta_total,
        tarifa,
        juros
    );
}

/*Cria elementos da parte financeira e capacidade necessaria*/
function create_tabs(demanda_p, demanda_t, oferta, tarifa) {

    document.getElementById("oferta_geral").innerHTML = `${parseReal(round_x(oferta, 2))} m³/ano`
    document.getElementById("demanda_geral").innerHTML = `${parseReal(round_x(demanda_t, 2))} m³/ano`


    /*Seletor de capacidade minima*/
    let volume_cap = Math.max(...volumes_cap)
    for (let i = 0; i < volumes_cap.length; i++) {
        if (volumes_cap[i] > demanda_p) {
            volume_cap = volumes_cap[i]
            break
        }
    }
    /*Seletor de caixa minima*/
    let volume_caixa = Math.max(...volumes_caixa)
    for (let i = 0; i < volumes_caixa.length; i++) {
        if (volumes_caixa[i] > demanda_p) {
            volume_caixa = volumes_caixa[i]
            break
        }
    }
    document.getElementById("Caixa_volume").innerHTML = `${String(volume_caixa)} L`

    const custo_op_final = round_x(financeiro_cap[volume_cap][1] + custo_op_bomba, 2)
    document.getElementById("custo_operacional").innerHTML = parseReal(custo_op_final) + ' R$/ano'

    const custo_cap = round_x(financeiro_cap[volume_cap][0] + custo_bomba + financeiro_caixa[volume_caixa], 2)
    document.getElementById("Custo_cap").innerHTML = parseReal(custo_cap)

    document.getElementById("Capacidade").innerHTML = volume_cap

    const Beneficio = round_x(tarifa * demanda_p * 30 / 1000 - custo_op_final, 2)
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
    const juros = document.getElementById("juros").value / 100
    const VPL_parcelas = []
    for (let i = 1; i <= 30; i++) {
        const parcela = Beneficio / ((1 + juros) ** i)
        VPL_parcelas.push(parcela)
    }
    const VPL = round_x(VPL_parcelas.reduce(add, 0) - custo_cap, 2)
    const vpl_span = document.getElementById("VPL")
    vpl_span.innerHTML = parseReal(VPL)
    if (VPL < 0) { vpl_span.setAttribute("style", "color:red") }
    else { vpl_span.setAttribute("style", "color:black") }
}