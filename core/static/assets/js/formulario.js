function geid(id) {
    // Macro para o document.getElementById quando jQuery causar problemas
    return document.getElementById(id);
}

function sFloat(num, digits = 2, format = "f") {
    /* 
    Limpa os floats de forma a remover NaNs ou valores invalídos
    Além de também converter para valores com vírgula ou o contrário
    */
    const normal_num_re = /^[0-9.,]/g;

    if (Number.isNaN(num) || !normal_num_re.test(String(num))) return 0;

    if (format === "f") return round_x(realFloat(num), digits);
    if (format === "r") return floatReal(round_x(num, digits));

    return num;
}

function delay(fn, ms = 300) {
    let timer = 0;
    return function (...args) {
        clearTimeout(timer);
        timer = setTimeout(fn.bind(this, ...args), ms || 0);
    };
}

function floatReal(float) {
    return String(float).replace(".", ",");
}

function realFloat(real) {
    let valor_str = String(real);
    if (valor_str.includes(","))
        valor_str = valor_str.replace(".", "").replace(",", ".");
    return parseFloat(valor_str);
}

function percent_ds() {
    const labels = [];
    const data = [];
    const consumo_mensal = sFloat($("#id_consumo_mensal").val());
    $("#table_body")
        .children("tr")
        .each(function () {
            const inputs = $(this).find("input");
            const uso = $(inputs[0]).val();
            const consumo_i = sFloat($(inputs[4]).val());
            const percent = sFloat((consumo_i / consumo_mensal) * 100);

            labels.push(uso);
            data.push(percent);
        });
    return { lab: labels, data: data };
}

/*Funcao que adiciona todos os campos de uma linha do formulario*/
function addFields({
    k,
    dados = ["", 1, 1, 1, "Litros/pessoa/dia", 1],
    id = "table_body",
    initial = Boolean(false),
    interesse,
} = {}) {
    let uso = `type="text" 
                id="id_${interesse}${k}-nome"
                name="${interesse}-${k}-nome"
                maxlength="100"
                value="${dados[0]}"
                class="form-control"
                required `;

    let vazao = `type="text" inputmode="numeric" pattern="[0-9]*"
                id="id_${interesse}${k}-vazao"
                name="${interesse}-${k}-vazao"
                min="1"
                value="${dados[1]}"
                class="form-control"
                required `;

    let freq = `type="text" inputmode="numeric" pattern="[0-9]*" 
                id="id_${interesse}${k}-frequencia_mensal"
                name="${interesse}-${k}-frequencia_mensal"
                min="1"
                value="${dados[2]}"
                class="form-control"
                required `;

    let indicador = `type="text" inputmode="numeric" pattern="[0-9]*" 
                    id="id_${interesse}${k}-indicador"
                    name="${interesse}-${k}-indicador"
                    min="1"
                    value="${dados[3]}"
                    class="form-control"
                    required `;

    let consumo = `type="text" inputmode="numeric" pattern="[0-9]*" 
                    id="id_${interesse}${k}-consumo"
                    name="${interesse}-${k}-consumo"
                    min="1e-8"
                    value="1"
                    data="1"
                    class="form-control"
                    required `;

    let freq_diaria = `type="hidden" 
                    id="id_${interesse}${k}-freq_diaria"
                    name="${interesse}-${k}-freq_diaria"
                    min="1e-8"
                    value="${dados[5]}"
                    class="form-control"
                    required `;

    let unidade_de_medida = "";
    if (initial) {
        uso =
            uso +
            `readonly 
            style="position: relative; font-weight: bold;"`;

        unidade_de_medida = dados[4];
    } else {
        uso =
            uso +
            `style="position: relative;"
                    placeholder="Inserir uso"`;

        unidade_de_medida = "Litros/pessoa/dia";
    }

    const unidades = {
        "Litros/m²/dia": "Litros/pessoa/dia",
        "Litros/pessoa/dia": "Litros/m²/dia",
    };

    // prettier-ignore
    const $row = $(`#${id}`).append(`<tr id="${interesse}${k}">
                                        <td><input ${uso}></td>
                                        <td>
                                            <div class="input-group">
                                                <input ${vazao}>
                                                <div class="input-group-append">
                                                    <span class="input-group-text">L/min</span>
                                                </div>
                                            </div>
                                        </td>
                                        <td>
                                            <div class="input-group">
                                                <input ${freq}>
                                                <div class="input-group-append">
                                                    <span class="input-group-text">&#10006; ao mês</span>
                                                </div>
                                            </div>
                                        </td>
                                        <td>
                                            <div class="input-group">
                                                <input ${indicador}>
                                                <div class="input-group-append">
                                                    <select id="id_${interesse}${k}-unidade" name="${interesse}-${k}-unidade" class="input-group-text">
                                                        <option value="${unidade_de_medida}">
                                                            ${unidade_de_medida.replace('Litros', 'L')}
                                                        </option>
                                                        <option value="${unidades[unidade_de_medida]}">
                                                            ${unidades[unidade_de_medida].replace('Litros', 'L')}
                                                        </option>
                                                    </select>
                                                </div>
                                            </div>
                                        </td>
                                        <td>
                                            <div class="input-group">
                                                <input ${consumo}>
                                                <div class="input-group-append">
                                                    <span class="input-group-text">m³/mês</span>
                                                </div>
                                            </div>
                                        </td>
                                        <td>
                                            <button id="del_${interesse}${k}" class="btn btn-light" type="button">Deletar</button>
                                            <input ${freq_diaria}>
                                        </td>
                                     </tr>`);

    function fator_unid(k) {
        /*
        Obtém o fator respectivo à unidade de medida,
        i.e. L/p/d retorna o número de pessoas e L/m²/d retorna
        a área de adequada (irrigação ou pisos).
        */
        const unid = $(`#id_usos${k}-unidade option:selected`).val();
        if (unid == "Litros/pessoa/dia") {
            fator = $(`#id_n_pessoas`).val();
        } else if (unid == "Litros/m²/dia") {
            const uso = $(`#id_usos${k}-nome`).val();
            if (uso == "Irrigação de jardins") {
                const area = sFloat($(`#id_area_irrigacao`).val());

                let meses_irr = 0;
                $("#div_estiagem")
                    .find("input")
                    .each(function () {
                        meses_irr += this.checked;
                    });
                fator = (area * meses_irr) / 12;
            } else {
                fator = $(`#id_area_pisos`).val();
            }
        }
        return sFloat(fator);
    }

    function pizza_no_forno() {
        /* Atualiza o gráfico de pizza no formulário geral.
         */
        const ds = percent_ds();
        removeData(pizza);
        addData(pizza, ds.lab, ds.data, true);
    }

    // TODO colocar a freq diaria real
    // TODO Se ocorrer mudança nos fatores (areas) ou nos meses de estiagem, então a tabela deve ser atualizada
    // TODO Se o consumo total for alterado, então deve haver algum tipo de "backpropagation"
    // TODO Adionar o consumo total em L/p/d
    $(`#id_usos${k}-vazao`).on("keyup js_trigger", function () {
        const vazao = sFloat($(`#id_usos${k}-vazao`).val());
        const freq_diaria = sFloat($(`#id_usos${k}-freq_diaria`).val());
        const indicador = vazao * freq_diaria;

        $(`#id_usos${k}-indicador`).val(sFloat(indicador, 2, "r"));
        $(`#id_usos${k}-frequencia_mensal`).trigger("js_trigger");
    });

    $(`#id_usos${k}-frequencia_mensal`).on("js_trigger keyup", function () {
        const freq_mensal = sFloat($(`#id_usos${k}-frequencia_mensal`).val());
        const indicador = sFloat($(`#id_usos${k}-indicador`).val());
        const fator = fator_unid(k);
        const consumo = (indicador * fator * freq_mensal) / 1000;

        $(`#id_usos${k}-consumo`)
            .val(sFloat(consumo, 2, "r"))
            .trigger("js_trigger");
    });

    $(`#id_usos${k}-indicador`).on("keyup", function () {
        $(`#id_usos${k}-frequencia_mensal`).trigger("js_trigger");

        const vazao = sFloat($(`#id_usos${k}-vazao`).val());
        const indicador = sFloat($(`#id_usos${k}-indicador`).val());
        const freq_diaria = sFloat(indicador / vazao);

        $(`#id_usos${k}-freq_diaria`).val(freq_diaria);
    });

    $(`#id_usos${k}-consumo`).on("js_trigger keyup", function (event) {
        const tab_body = $(this).parents()[3];
        let consumo_total = 0;
        $(tab_body)
            .children("tr")
            .each(function () {
                consumo_total += sFloat(
                    this.querySelectorAll("input")[4].value
                );
            });

        const pessoas = sFloat($("#id_n_pessoas").val());
        const cm_lpd = sFloat((consumo_total * 1000) / pessoas / 30);
        $("#id_consumo_mensal").val(consumo_total);
        $("#id_cm_lpd").val(cm_lpd);

        // prettier-ignore
        if (event.type == "keyup") {
                const vazao = sFloat($(`#id_usos${k}-vazao`).val());
                const freq_mensal = sFloat($(`#id_usos${k}-frequencia_mensal`).val());
                const consumo = sFloat($(`#id_usos${k}-consumo`).val());
                const fator = fator_unid(k);

                const freq_diaria = (consumo * 1000) / freq_mensal / fator / vazao;
                const indicador = vazao * freq_diaria;

                $(`#id_usos${k}-freq_diaria`).val(sFloat(freq_diaria, 2, "r"));
                $(`#id_usos${k}-indicador`).val(sFloat(indicador, 2, "r"));
            }

        pizza_no_forno();
    });

    $(`#id_usos${k}-nome`).on("keyup", function () {
        $(`#id_usos${k}-consumo`).trigger("js_trigger");
        pizza_no_forno();
    });

    $(`#del_${interesse}${k}`).click(function () {
        $(`#${interesse}${k}`).remove();
    });
}

/*Funcao para gerar o formulario ao usario fazer GET na pagina*/
function InitFields(
    k,
    tipo,
    vazao,
    padrao_freq,
    padrao_ind,
    escala,
    freq_diaria,
    id = "table_body",
    interesse = "ofertas"
) {
    const n = tipo.length;
    for (let i = 0; i < n; i++) {
        let padroes = [
            tipo[i],
            vazao[i],
            padrao_freq[i],
            padrao_ind[i],
            escala[i],
            freq_diaria[i],
        ];
        addFields({
            k: k,
            dados: padroes,
            id: id,
            initial: Boolean(true),
            interesse: interesse,
        });
        k++;
    }
    return k;
}

/*Funcao que reendereca os campos da tabela pelo id e nome certo*/
/*A necessidade dessa funcao se faz no Django, que ao saber que tem X formularios procura os X primeiros formularios (no formset)*/
/*Em outras palavras, se o total de forms for 5 entao ele procura id_ofertas-0, id_ofertas-1, ..., id_ofertas-4*/
function readdres(id = "table_body", interesse = "ofertas") {
    const tab_body = $(`#${id} tr`);
    $("#id_usos-TOTAL_FORMS").attr("value", tab_body.length);

    tab_body.each(function () {
        let index = this.rowIndex - 1;
        const cells = $(this).find("input");
        cells[0].setAttribute("name", `usos-${index}-nome`);
        /*Valores fracionarios devem ser informados com '.' e nao com ','*/
        /*Valores de frequencia mensal devem ser inteiros*/
        cells[1].setAttribute("name", `usos-${index}-frequencia_mensal`);
        cells[1].setAttribute(
            "value",
            `${Math.ceil(realFloat(cells[1].value))}`
        );
        cells[2].setAttribute("name", `usos-${index}-indicador`);
        cells[2].setAttribute("value", `${realFloat(cells[2].value)}`);
        const sel = $(this).find("select")[0];
        sel.setAttribute("name", `usos-${index}-unidade`);
    });
}

/*Funcao que reinicia o formulario, deletando os campos existentes e chamando InitFields outra vez*/
function reset_fields(
    tipo,
    padrao_freq,
    padrao_ind,
    escala,
    id = "table_body",
    interesse = "ofertas"
) {
    const table = document.getElementById(id);
    const rows = table.getElementsByTagName("tr");
    const rows_arr = [...rows];
    rows_arr.map((n) => n && n.remove());

    let k = 0;
    k = InitFields(k, tipo, padrao_freq, padrao_ind, escala, id, interesse);
    return k;
}

function gera_estiagem(id, chunk_meses) {
    const estiagem = $(`#${id}`);
    for (let i = 0; i < chunk_meses.length; i++) {
        let row = "";
        for (let j = 0; j < chunk_meses[i].length; j++) {
            row += `<div class="col">
                            <div class="input-group-text" style="width: 5.0em">
                                <span style="font-weight: bold; margin-right: 10px">${
                                    chunk_meses[i][j]
                                }</span>
                                <input 
                                    name="${chunk_meses[i][j].toLowerCase()}"
                                    id="estiagem-${
                                        i * chunk_meses[i].length + j
                                    }" type="checkbox"/>
                            </div>
                        </div>`;
        }
        estiagem.append(`<div class="row">
                            ${row}
                        </div>`);
    }
    estiagem.append("<small>Meses com pouca ou nenhuma chuva.</small>");
}
