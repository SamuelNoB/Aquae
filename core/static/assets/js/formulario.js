
function addFields(k, dados=[], id="table_body", initial=Boolean(false), interesse) {
    let container = document.getElementById(id);
    let row = container.appendChild(document.createElement("tr"));
    row.setAttribute('id', interesse + k)

    let td1 = row.appendChild(document.createElement("td"));
    let tipo_de_uso = td1.appendChild(document.createElement("input"));

    function numericField(row, k, id, padrao='1', escala='Litros/dia'){
        let td = row.appendChild(document.createElement("td"));
        let div_in = td.appendChild(document.createElement("div"));
        let valor = div_in.appendChild(document.createElement("input"));
        let div_append = div_in.appendChild(document.createElement("div"));
        let span = div_append.appendChild(document.createElement("span"));

        div_in.setAttribute('class', 'input-group');
        div_append.setAttribute('class', 'input-group-append');
        span.innerHTML = escala;
        span.setAttribute('class', 'input-group-text');

        valor.setAttribute('type', 'numeric');
        valor.setAttribute('value', padrao);
        valor.setAttribute('class', 'form-control');
        valor.setAttribute('min', 1)
        valor.setAttribute('name', `${interesse}-${k}-${id}`)
        valor.setAttribute('id', `id_${interesse}-${k}-${id}`)
        valor.setAttribute('required', '')
    }



    tipo_de_uso.setAttribute('type', 'text');
    tipo_de_uso.setAttribute('class', 'form-control');
    tipo_de_uso.setAttribute('maxlength', '100')
    tipo_de_uso.setAttribute('id', `id_${interesse}${k}-nome`)
    tipo_de_uso.setAttribute('name', `${interesse}-${k}-nome`)
    tipo_de_uso.setAttribute('required', '')

    if (initial){
        tipo_de_uso.setAttribute('readonly', '');
        tipo_de_uso.setAttribute('style', 'position: relative;font-weight: bold;');
        tipo_de_uso.setAttribute('value', dados[0])
        numericField(row, k, 'frequencia_mensal', dados[1], 'Vezes ao mês')
        numericField(row, k, 'indicador', dados[2], dados[3])

    } else {
        tipo_de_uso.setAttribute('placeholder', 'Nome do uso aqui');
        numericField(row, k, 'frequencia_mensal', '1', 'Vezes ao mês');
        numericField(row, k, 'indicador', '1', 'Litros/pessoa/dia');
    }


    function delField(row_id) {
        let row_to_del = document.getElementById(row_id);
        row_to_del.parentNode.removeChild(row_to_del)
    }

    let td4 = row.appendChild(document.createElement("td"))
    let del_btn = td4.appendChild(document.createElement("button"))
    del_btn.setAttribute('class', 'btn btn-light')
    del_btn.setAttribute('type', 'button')
    del_btn.addEventListener('click', function(){delField(interesse+k)}, false)
    del_btn.innerHTML = 'Deletar'
}

function InitFields(k, tipo, padrao_freq, padrao_ind, escala, id="table_body", interesse="ofertas"){
    for (let i=0; i < tipo.length; i++){
        let padroes = [tipo[i], padrao_freq[i], padrao_ind[i], escala[i]]
        addFields(k, padroes, id, Boolean(true), interesse);
        k++
    }
    return k
}

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
    }

}

function reset_fields (tipo, padrao_freq, padrao_ind, escala, id='table_body', interesse="ofertas") {
    const table = document.getElementById(id)
    const rows = table.getElementsByTagName('tr')
    const rows_arr = [...rows]
    rows_arr.map(n => n && n.remove());

    let k = 0
    InitFields(k, tipo, padrao_freq, padrao_ind, escala, id, interesse)
}

