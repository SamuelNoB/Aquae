function realFloat(real) {
    const valor = String(real).replace(".", "").replace(",", ".");
    return parseFloat(valor);
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

    let vazao = `type="numeric" 
                id="id_${interesse}${k}-vazao"
                name="${interesse}-${k}-vazao"
                min="1"
                value="${dados[1]}"
                class="form-control"
                required `;

    let freq = `type="numeric" 
                id="id_${interesse}${k}-frequencia_mensal"
                name="${interesse}-${k}-frequencia_mensal"
                min="1"
                value="${dados[2]}"
                class="form-control"
                required `;

    let indicador = `type="numeric" 
                    id="id_${interesse}${k}-indicador"
                    name="${interesse}-${k}-indicador"
                    min="1"
                    value="${dados[3]}"
                    class="form-control"
                    required `;

    let consumo = `type="numeric" 
                    id="id_${interesse}${k}-consumo"
                    name="${interesse}-${k}-consumo"
                    min="1e-8"
                    value="1"
                    data="1"
                    class="form-control"
                    required `;

    let porcentagem = `type="text" 
                    id="id_${interesse}${k}-porcento"
                    name="${interesse}-${k}-porcento"
                    maxlength="100"
                    value="20"
                    id_linha = "${k}"
                    class="form-control"
                    style="position: relative; font-weight: bold; min-width: 3.5em; padding-left: 6px; padding-right: 6px"
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
                fator = $(`#id_area_irrigacao`).val();
            } else {
                fator = $(`#id_area_pisos`).val();
            }
        }
        return fator;
    }

    $(`#id_usos${k}-vazao`).change(function () {
        const vazao = $(`#id_usos${k}-vazao`).val();
        const freq_diaria = $(`#id_usos${k}-freq_diaria`).val();
        const indicador = parseFloat(vazao) * parseFloat(freq_diaria);

        $(`#id_usos${k}-indicador`).val(indicador);
        $(`#id_usos${k}-frequencia_mensal`).change();
    });

    $(`#id_usos${k}-frequencia_mensal`).change(function () {
        const freq_mensal = parseFloat(
            $(`#id_usos${k}-frequencia_mensal`).val()
        );
        const indicador = parseFloat($(`#id_usos${k}-indicador`).val());
        const fator = fator_unid(k);
        const consumo = (indicador * fator * freq_mensal) / 1000;

        $(`#id_usos${k}-consumo`).val(consumo);
        $(`#id_usos${k}-consumo`).change();
    });

    $(`#id_usos${k}-indicador`).on("keyup", function () {
        $(`#id_usos${k}-frequencia_mensal`).change();

        const vazao = $(`#id_usos${k}-vazao`).val();
        const indicador = $(`#id_usos${k}-indicador`).val();
        const freq_diaria = indicador / vazao;
        $(`#id_usos${k}-freq_diaria`).val(freq_diaria);
    });

    $(`#id_usos${k}-consumo`).on("keyup", function () {
        // TODO mudar a porcentagem
        const vazao = $(`#id_usos${k}-vazao`).val();
        const freq_mensal = parseFloat(
            $(`#id_usos${k}-frequencia_mensal`).val()
        );
        const consumo = $(`#id_usos${k}-consumo`).val();
        const fator = fator_unid(k);
        const freq_diaria = (consumo * 1000) / freq_mensal / fator / vazao;
        $(`#id_usos${k}-freq_diaria`).val(freq_diaria);

        array_linhas = [];
        array_linhas.push($("input[id_linha]"));
        var soma = 0;
        $.each(array_linhas[0], function () {
            soma =
                parseFloat(
                    $(`#id_usos${$(this).attr("id_linha")}-consumo`).val()
                ) + soma;
        });
        $(`#id_consumo_mensal`).val(soma);
        var consumo_total = parseFloat($(`#id_consumo_mensal`).val());
        $.each(array_linhas[0], function () {
            var total =
                $(`#id_usos${$(this).attr("id_linha")}-consumo`).val() /
                consumo_total;
        });
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
}
