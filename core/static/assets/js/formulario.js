function realFloat(real) {
    const valor = String(real).replace('.', '').replace(',', '.')
    return parseFloat(valor)
}

/*Funcao que adiciona todos os campos de uma linha do formulario*/
function addFields(k, dados=[], id="table_body", initial=Boolean(false), interesse) {
    let uso =  `type="text" 
                id="id_demandas${k}-nome"
                name="demandas-${k}-nome"
                maxlength="100"
                class="form-control"
                required `

    let freq = `type="numeric" 
                id="id_demandas${k}-frequencia_mensal"
                name="demandas-${k}-frequencia_mensal"
                min="1"
                class="form-control"
                required `

    let indicador = `type="numeric" 
                    id="id_demandas${k}-indicador"
                    name="demandas-${k}-indicador"
                    min="1"
                    class="form-control"
                    required `

    let unidade_de_medida = ""
    if (initial) {
        uso = uso + `readonly 
                    style="position: relative; font-weight: bold;" 
                    value="${dados[0]}"`
        
        freq = freq + `value="${dados[1]}"`
        indicador = indicador + `value="${dados[2]}"`
        unidade_de_medida = dados[3]

    } else {
        uso = uso + `style="position: relative;"
                    placeholder="Inserir uso"`

        freq = freq + `value="1"`
        indicador = indicador + `value="1"`
        unidade_de_medida = "Litros/pessoa/dia"
    }

    const unidades = {
        "Litros/m²/dia": "Litros/pessoa/dia",
        "Litros/pessoa/dia": "Litros/m²/dia"
        }
    
    const $row = $(`#${id}`).append(`<tr id="${interesse}${k}">
                                        <td><input ${uso}></td>
                                        <td>
                                            <div class="input-group">
                                                <input ${freq}>
                                                <div class="input-group-append">
                                                    <span class="input-group-text">Vezes ao mês</span>
                                                </div>
                                            </div>
                                        </td>
                                        <td>
                                            <div class="input-group">
                                                <input ${indicador}>
                                                <div class="input-group-append">
                                                    <select id="id_demandas${k}-unidade" name="demandas-${k}-unidade" class="input-group-text">
                                                        <option value="${unidade_de_medida}">${unidade_de_medida}</option>
                                                        <option value="${unidades[unidade_de_medida]}">${unidades[unidade_de_medida]}</option>
                                                    </select>
                                                </div>
                                            </div>
                                        </td>
                                        <td>
                                            <button id="del_${interesse}${k}" class="btn btn-light" type="button">Deletar</button>
                                        </td>
                                     </tr>`)
    
    $(`#del_${interesse}${k}`).click( function () {
        $(`#${interesse}${k}`).remove();
    });
}


/*Funcao para gerar o formulario ao usario fazer GET na pagina*/
function InitFields(k, tipo, padrao_freq, padrao_ind, escala, id="table_body", interesse="ofertas"){
    for (let i=0; i < tipo.length; i++){
        let padroes = [tipo[i], padrao_freq[i], padrao_ind[i], escala[i]]
        addFields(k, padroes, id, Boolean(true), interesse);
        k++
    }
    return k
}


/*Funcao que reendereca os campos da tabela pelo id e nome certo*/
/*A necessidade dessa funcao se faz no Django, que ao saber que tem X formularios procura os X primeiros formularios (no formset)*/
/*Em outras palavras, se o total de forms for 5 entao ele procura id_ofertas-0, id_ofertas-1, ..., id_ofertas-4*/
function readdres (id='table_body', interesse='ofertas') {
    let tab_user = document.getElementById(id)
    let rows = tab_user.getElementsByTagName('tr')
    let k_true = rows.length
    let total_forms = document.getElementById(`id_${interesse}-TOTAL_FORMS`)
    total_forms.setAttribute('value', k_true)

    const attr = ['-nome', '-frequencia_mensal', '-indicador']
    let inputs = tab_user.getElementsByTagName('input')
    let k_array = []
    for (let i = 0; i < k_true; i++){
        k_array.push(i)
        k_array.push(i)
        k_array.push(i)
    }
    for (let i=0; i < inputs.length; i++){
        inputs[i].setAttribute('name', `${interesse}-${k_array[i]}${attr[i % 3]}`)
        inputs[i].setAttribute('id', `id_${interesse}-${k_array[i]}${attr[i % 3]}`)
        
        /*Valores fracionarios devem ser informados com '.' e nao com ','*/
        if (inputs[i].value.includes(',') && i % 3 != 0) {
            inputs[i].value = realFloat(inputs[i].value)
        }
        /*Valores de frequencia mensal devem ser inteiros*/
        if (inputs[i].value.includes('.') && i % 3 == 1) {
            inputs[i].value = Math.ceil(inputs[i].value)
        }
    }

}

/*Funcao que reinicia o formulario, deletando os campos existentes e chamando InitFields outra vez*/
function reset_fields (tipo, padrao_freq, padrao_ind, escala, id='table_body', interesse="ofertas") {
    const table = document.getElementById(id)
    const rows = table.getElementsByTagName('tr')
    const rows_arr = [...rows]
    rows_arr.map(n => n && n.remove());

    let k = 0
    k = InitFields(k, tipo, padrao_freq, padrao_ind, escala, id, interesse)
    return k 
}

