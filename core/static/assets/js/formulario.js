function realFloat(real) {
    const valor = String(real).replace(".", "").replace(",", ".");
    return parseFloat(valor);
}

/*Funcao que adiciona todos os campos de uma linha do formulario*/
function addFields({
    k,
    dados = ["", 1, 1, 1, "Litros/pessoa/dia"],
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
                    class="form-control"
                    required `;

    let porcentagem = `type="text" 
                    id="id_${interesse}${k}-%"
                    name="${interesse}-${k}-%"
                    maxlength="100"
                    value="10,89"
                    class="form-control"
                    style="position: relative; font-weight: bold; min-width: 3.5em; padding-left: 6px; padding-right: 6px"
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
        "Litros/m??/dia": "Litros/pessoa/dia",
        "Litros/pessoa/dia": "Litros/m??/dia",
    };

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
                                                    <span class="input-group-text">Vezes ao m??s</span>
                                                </div>
                                            </div>
                                        </td>
                                        <td>
                                            <div class="input-group">
                                                <input ${indicador}>
                                                <div class="input-group-append">
                                                    <select id="id_${interesse}${k}-unidade" name="${interesse}-${k}-unidade" class="input-group-text">
                                                        <option value="${unidade_de_medida}">${unidade_de_medida}</option>
                                                        <option value="${unidades[unidade_de_medida]}">${unidades[unidade_de_medida]}</option>
                                                    </select>
                                                </div>
                                            </div>
                                        </td>
                                        <td>
                                            <div class="input-group">
                                                <input ${consumo}>
                                                <div class="input-group-append">
                                                    <span class="input-group-text">m??/m??s</span>
                                                </div>
                                            </div>
                                        </td>
                                        <td>
                                            <input ${porcentagem}>
                                            <div class="input-group">
                                                
                                                <div class="input-group-append">
                                                    <span class="input-group-text" style="min-width: 3.5em;">%</span>
                                                </div>
                                            </div>
                                            
                                        </td>
                                        <td>
                                            <button id="del_${interesse}${k}" class="btn btn-light" type="button">Deletar</button>
                                        </td>
                                     </tr>`);

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
